import logging

logger = logging.getLogger(__name__)

from django.db.models import Sum
from django.db import transaction

"""
REST API Views for RideNow
All API endpoints using Django REST Framework
"""
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import (
    VehicleType, Vehicle, VehiclePhoto, VehicleDocument,
    Route, Ride, Rating, FeedBack, RideRequest, DriverLocation, RideMatching, DriverLocationHistory
)
from .serializers import (
    VehicleTypeSerializer, VehicleSerializer, VehicleListSerializer,
    VehiclePhotoSerializer, VehicleDocumentSerializer,
    RouteSerializer, RideSerializer, RatingSerializer,
    FeedBackSerializer, RideRequestSerializer, RideRequestCreateSerializer,
    RideRequestUpdateSerializer, AvailableDriverSerializer,
    DriverLocationSerializer, DriverLocationUpdateSerializer,
    RideMatchingSerializer, NearbyDriversSerializer
)
from .permissions import (
    IsDriver, IsClient, IsDriverOrClient, IsRideParticipant,
    CanAcceptRideRequest, CanCancelRideRequest, CanRateRide, IsDriverOnline
)
from accounts.models import DriverProfile, ClientProfile


def send_websocket_message(group_name, message_type, data):
    """Helper function to send WebSocket messages"""
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': message_type,
                'data': data
            }
        )


class VehicleTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing vehicle types"""
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [AllowAny]  # Public endpoint
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing vehicles"""
    queryset = Vehicle.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_air_conditioned', 'is_insured']
    search_fields = ['name', 'registration_number']
    ordering_fields = ['created', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return VehicleListSerializer
        return VehicleSerializer

    def get_queryset(self):
        queryset = Vehicle.objects.all()
        
        # Drivers can only see their own vehicles
        if self.request.user.is_driver:
            try:
                driver_profile = self.request.user.driver_profile
                if driver_profile.vehicle:
                    queryset = queryset.filter(id=driver_profile.vehicle.id)
                else:
                    queryset = queryset.none()
            except DriverProfile.DoesNotExist:
                queryset = queryset.none()
        
        return queryset

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available vehicles"""
        available_vehicles = Vehicle.objects.filter(
            is_insured=True
        ).exclude(
            driverprofile__is_online=False
        )
        serializer = self.get_serializer(available_vehicles, many=True)
        return Response(serializer.data)


class RideRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ride requests"""
    permission_classes = [IsAuthenticated, IsDriverOrClient]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'driver', 'vehicle']
    search_fields = ['start_location', 'end_location']
    ordering_fields = ['requested_at', 'created']

    def get_queryset(self):
        queryset = RideRequest.objects.all().order_by('-requested_at')
        
        if self.request.user.is_client:
            try:
                queryset = queryset.filter(client=self.request.user.client_profile)
            except ClientProfile.DoesNotExist:
                queryset = queryset.none()
        elif self.request.user.is_driver:
            try:
                driver_profile = self.request.user.driver_profile
                # Show pending requests and driver's own requests
                queryset = queryset.filter(
                    Q(status='Pending') | Q(driver=driver_profile)
                )
            except DriverProfile.DoesNotExist:
                queryset = queryset.filter(status='Pending')
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return RideRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RideRequestUpdateSerializer
        return RideRequestSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsDriver, CanAcceptRideRequest])
    def accept(self, request, pk=None):
        """Driver accepts a ride request"""
        ride_request = self.get_object()
        
        if ride_request.status != 'Pending':
            return Response(
                {'error': 'This ride request is no longer available.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            driver_profile = request.user.driver_profile
        except DriverProfile.DoesNotExist:
            return Response(
                {'error': 'Driver profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehicle_id = request.data.get('vehicle')
        if vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
                ride_request.vehicle = vehicle
            except Vehicle.DoesNotExist:
                return Response(
                    {'error': 'Vehicle not found.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif driver_profile.vehicle:
            ride_request.vehicle = driver_profile.vehicle
        
        ride_request.driver = driver_profile
        ride_request.status = 'Accepted'
        ride_request.save()
        
        serializer = self.get_serializer(ride_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanCancelRideRequest])
    def cancel(self, request, pk=None):
        """Cancel a ride request"""
        ride_request = self.get_object()
        
        if ride_request.status not in ['Pending', 'Accepted']:
            return Response(
                {'error': 'Cannot cancel this ride request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ride_request.status = 'Cancelled'
        ride_request.save()
        
        # Send WebSocket notifications for cancellation
        if ride_request.driver:
            # If driver was assigned, notify them about the cancellation
            driver_group = f"ride_matching_{ride_request.driver.user.id}"
            ride_group = f"ride_request_{ride_request.id}"
            
            websocket_data = {
                'ride_request_id': ride_request.id,
                'client_id': ride_request.client.id,
                'client_name': ride_request.client.user.get_user_names,
                'status': 'cancelled',
                'message': f'Client {ride_request.client.user.get_user_names} cancelled the ride request',
                'cancelled_by': 'client'
            }
            
            # Send to driver-specific group and ride-specific group
            send_websocket_message(driver_group, 'ride_cancelled', websocket_data)
            send_websocket_message(ride_group, 'ride_cancelled', websocket_data)
        else:
            # If no driver assigned yet, notify any pending matches
            from .models import RideMatching
            pending_matches = RideMatching.objects.filter(
                ride_request=ride_request,
                status='pending'
            )
            
            for match in pending_matches:
                driver_group = f"ride_matching_{match.driver.user.id}"
                websocket_data = {
                    'ride_request_id': ride_request.id,
                    'ride_matching_id': match.id,
                    'client_id': ride_request.client.id,
                    'client_name': ride_request.client.user.get_user_names,
                    'status': 'cancelled',
                    'message': f'Client {ride_request.client.user.get_user_names} cancelled the ride request',
                    'cancelled_by': 'client'
                }
                
                send_websocket_message(driver_group, 'ride_cancelled', websocket_data)
        
        serializer = self.get_serializer(ride_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsDriver])
    def complete(self, request, pk=None):
        """Mark ride as completed"""
        ride_request = self.get_object()
        
        if ride_request.status != 'Accepted':
            return Response(
                {'error': 'Only accepted rides can be marked as completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if ride_request.driver.user != request.user:
                return Response(
                    {'error': 'You can only complete your own rides.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except:
            return Response(
                {'error': 'Invalid ride request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ride_request.status = 'Completed'
        ride_request.save()
        
        serializer = self.get_serializer(ride_request)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsDriver])
    def pending(self, request):
        """Get all pending ride requests for drivers"""
        pending_requests = RideRequest.objects.filter(status='Pending').order_by('-requested_at')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)


class RideViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing rides"""
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated, IsRideParticipant]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['driver', 'client', 'vehicle']
    ordering_fields = ['start_time', 'end_time', 'created']

    def get_queryset(self):
        queryset = Ride.objects.all().order_by('-created')
        
        if self.request.user.is_client:
            try:
                queryset = queryset.filter(client=self.request.user.client_profile)
            except ClientProfile.DoesNotExist:
                queryset = queryset.none()
        elif self.request.user.is_driver:
            try:
                queryset = queryset.filter(driver=self.request.user.driver_profile)
            except DriverProfile.DoesNotExist:
                queryset = queryset.none()
        
        return queryset


class RatingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ratings"""
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ride', 'rating']
    ordering_fields = ['created', 'rating']

    def get_queryset(self):
        queryset = Rating.objects.all().order_by('-created')
        
        if self.request.user.is_client:
            try:
                queryset = queryset.filter(client=self.request.user.client_profile)
            except ClientProfile.DoesNotExist:
                queryset = queryset.none()
        elif self.request.user.is_driver:
            try:
                queryset = queryset.filter(ride__driver=self.request.user.driver_profile)
            except DriverProfile.DoesNotExist:
                queryset = queryset.none()
        
        return queryset

    def perform_create(self, serializer):
        try:
            client_profile = self.request.user.client_profile
            serializer.save(client=client_profile)
        except ClientProfile.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Client profile not found.")


class FeedBackViewSet(viewsets.ModelViewSet):
    """ViewSet for managing feedback"""
    serializer_class = FeedBackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ride', 'client']
    ordering_fields = ['created']

    def get_queryset(self):
        queryset = FeedBack.objects.all().order_by('-created')
        
        if self.request.user.is_client:
            try:
                queryset = queryset.filter(client=self.request.user.client_profile)
            except ClientProfile.DoesNotExist:
                queryset = queryset.none()
        elif self.request.user.is_driver:
            try:
                queryset = queryset.filter(ride__driver=self.request.user.driver_profile)
            except DriverProfile.DoesNotExist:
                queryset = queryset.none()
        
        return queryset

    def perform_create(self, serializer):
        try:
            client_profile = self.request.user.client_profile
            serializer.save(client=client_profile)
        except ClientProfile.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Client profile not found.")


# ==================== CUSTOM API ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow guest users to see available drivers
def available_drivers(request):
    """Get available drivers near a location"""
    # Get location from query params
    lat = request.query_params.get('lat')
    lng = request.query_params.get('lng')
    radius = float(request.query_params.get('radius', 10))  # Default 10km radius
    
    # Get all online and active drivers with vehicles
    drivers = DriverProfile.objects.filter(
        is_online=True,
        is_active=True,
        is_verified=True,
        is_banned=False,
        vehicle__isnull=False
    ).select_related('user', 'vehicle', 'vehicle__type')
    
    # TODO: Filter by location if coordinates provided
    # if lat and lng:
    #     point = Point(float(lng), float(lat), srid=4326)
    #     drivers = drivers.filter(
    #         current_location__distance_lte=(point, D(km=radius))
    #     )
    
    serializer = AvailableDriverSerializer(drivers, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Require authentication
def quick_ride_request(request):
    """Create a quick ride request from the map interface"""
    from finance.models import Ledger
    from decimal import Decimal
    
    try:
        pickup_location = request.data.get('pickup_location')  # [lng, lat]
        destination_location = request.data.get('destination_location')  # [lng, lat]
        pickup_address = request.data.get('pickup_address')
        destination_address = request.data.get('destination_address')
        ride_type = request.data.get('ride_type', 'standard')
        estimated_cost = request.data.get('estimated_cost', 0)
        
        # Validate required data
        if not all([pickup_location, destination_location, pickup_address, destination_address]):
            return Response({
                'success': False,
                'error': 'Missing required location data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has client profile
        try:
            client = request.user.client_profile
        except ClientProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Client profile not found. Please complete your profile.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check wallet balance
        credits = Ledger.objects.filter(
            user_to=request.user,
            is_credit=True,
            is_valid=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        debits = Ledger.objects.filter(
            user_from=request.user,
            is_debit=True,
            is_valid=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        balance = credits - debits
        estimated_cost_decimal = Decimal(str(estimated_cost))
        
        if balance < estimated_cost_decimal:
            return Response({
                'success': False,
                'error': 'Insufficient wallet balance',
                'balance': float(balance),
                'required': float(estimated_cost_decimal)
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        with transaction.atomic():
            # Create route
            route = Route.objects.create(
                pickup_location=Point(float(pickup_location[0]), float(pickup_location[1]), srid=4326),
                destination=Point(float(destination_location[0]), float(destination_location[1]), srid=4326),
                eta=timezone.now() + timezone.timedelta(minutes=15)
            )
            
            # Create ride request with cost stored and route linked
            ride_request = RideRequest.objects.create(
                client=client,
                route=route,  # Link the route to the ride request
                start_location=pickup_address,
                end_location=destination_address,
                status='Pending',
                cost=estimated_cost_decimal  # Store the cost for later payment
            )
            
            # Note: Payment will be processed when ride is completed via signal
            
            return Response({
                'success': True,
                'ride_request_id': ride_request.id,
                'status': ride_request.status,
                'message': 'Ride request created successfully',
                'estimated_cost': float(estimated_cost_decimal),
                'note': 'Payment will be processed when ride is completed'
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Quick ride request error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_statistics(request):
    """Get driver statistics"""
    if not request.user.is_driver:
        return Response(
            {'error': 'Only drivers can access this endpoint.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        driver_profile = request.user.driver_profile
    except DriverProfile.DoesNotExist:
        return Response(
            {'error': 'Driver profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Calculate statistics
    total_rides = Ride.objects.filter(driver=driver_profile).count()
    completed_rides = RideRequest.objects.filter(driver=driver_profile, status='Completed').count()
    cancelled_rides = RideRequest.objects.filter(driver=driver_profile, status='Cancelled').count()
    
    ratings = Rating.objects.filter(ride__driver=driver_profile)
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0
    rating_count = ratings.count()
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[f'{i}_star'] = ratings.filter(rating=i).count()
    
    return Response({
        'total_rides': total_rides,
        'completed_rides': completed_rides,
        'cancelled_rides': cancelled_rides,
        'average_rating': round(avg_rating, 2),
        'total_ratings': rating_count,
        'rating_distribution': rating_distribution
    })


class DriverLocationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing driver locations"""
    serializer_class = DriverLocationSerializer
    permission_classes = [IsAuthenticated, IsDriver]
    
    def get_queryset(self):
        # Drivers can only see their own locations
        try:
            driver_profile = self.request.user.driver_profile
            return DriverLocation.objects.filter(driver=driver_profile).order_by('-last_updated')
        except DriverProfile.DoesNotExist:
            return DriverLocation.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DriverLocationUpdateSerializer
        return DriverLocationSerializer
    
    def perform_create(self, serializer):
        # Automatically set the driver
        try:
            driver_profile = self.request.user.driver_profile
            serializer.save(driver=driver_profile)
        except DriverProfile.DoesNotExist:
            raise serializers.ValidationError("Driver profile not found.")
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsDriver])
    def update_location(self, request):
        """Update driver's current location"""
        try:
            driver_profile = request.user.driver_profile
        except DriverProfile.DoesNotExist:
            return Response(
                {'error': 'Driver profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DriverLocationUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # Get or create driver location
            location, created = DriverLocation.objects.get_or_create(
                driver=driver_profile,
                defaults=serializer.validated_data
            )
            
            if not created:
                # Update existing location
                for key, value in serializer.validated_data.items():
                    setattr(location, key, value)
                location.save()
            
            response_serializer = DriverLocationSerializer(location)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsDriver])
    def go_offline(self, request):
        """Set driver as offline"""
        try:
            driver_profile = request.user.driver_profile
            location = DriverLocation.objects.filter(driver=driver_profile).first()
            
            if location:
                location.is_online = False
                location.is_available = False
                location.save()
                
                return Response({
                    'message': 'Driver set to offline',
                    'is_online': False,
                    'is_available': False
                })
            else:
                return Response(
                    {'error': 'Driver location not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except DriverProfile.DoesNotExist:
            return Response(
                {'error': 'Driver profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsDriver])
    def go_online(self, request):
        """Set driver as online"""
        try:
            driver_profile = request.user.driver_profile
            location = DriverLocation.objects.filter(driver=driver_profile).first()
            
            if location:
                location.is_online = True
                location.is_available = True
                location.save()
                
                return Response({
                    'message': 'Driver set to online',
                    'is_online': True,
                    'is_available': True
                })
            else:
                return Response(
                    {'error': 'Driver location not found. Please update your location first.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except DriverProfile.DoesNotExist:
            return Response(
                {'error': 'Driver profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class RideMatchingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ride matching"""
    serializer_class = RideMatchingSerializer
    permission_classes = [IsAuthenticated, IsDriverOrClient]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_client:
            try:
                client_profile = user.client_profile
                return RideMatching.objects.filter(
                    ride_request__client=client_profile
                ).order_by('-created')
            except ClientProfile.DoesNotExist:
                return RideMatching.objects.none()
        elif user.is_driver:
            try:
                driver_profile = user.driver_profile
                return RideMatching.objects.filter(
                    driver=driver_profile
                ).order_by('-created')
            except DriverProfile.DoesNotExist:
                return RideMatching.objects.none()
        
        return RideMatching.objects.none()


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def find_nearby_drivers(request):
    """Find nearby available drivers for a ride request"""
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        return Response(
            {'error': 'Client profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get location parameters
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    radius_km = request.data.get('radius_km', 10)  # Default 10km radius
    vehicle_type_id = request.data.get('vehicle_type_id')
    
    if not latitude or not longitude:
        return Response(
            {'error': 'Latitude and longitude are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        client_point = Point(float(longitude), float(latitude), srid=4326)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid coordinates.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find available drivers within radius
    available_locations = DriverLocation.objects.filter(
        is_online=True,
        is_available=True,
        driver__is_active=True,
        driver__is_verified=True
    ).select_related('driver', 'driver__vehicle', 'driver__vehicle__type')
    
    # Filter by vehicle type if specified
    if vehicle_type_id:
        available_locations = available_locations.filter(
            driver__vehicle__type_id=vehicle_type_id
        )
    
    # Calculate distances and filter by radius
    nearby_drivers = []
    for location in available_locations:
        # Calculate distance using PostGIS (if available) or simple calculation
        if hasattr(location.location, 'distance'):
            distance_km = location.location.distance(client_point) * 100  # Convert to km
        else:
            # Simple distance calculation (approximate)
            import math
            lat_diff = abs(location.latitude - float(latitude))
            lng_diff = abs(location.longitude - float(longitude))
            distance_km = math.sqrt(lat_diff**2 + lng_diff**2) * 111  # Rough conversion
        
        if distance_km <= float(radius_km):
            # Calculate ETA (rough estimate: 2 minutes per km in city traffic)
            eta_minutes = max(5, int(distance_km * 2))
            
            # Calculate matching score (higher is better)
            # Factors: distance (closer is better), rating (higher is better)
            driver_rating = 4.0  # Default rating
            try:
                ratings = Rating.objects.filter(ride__driver=location.driver)
                if ratings.exists():
                    driver_rating = ratings.aggregate(Avg('rating'))['rating__avg']
            except:
                pass
            
            # Score calculation (0-100)
            distance_score = max(0, 100 - (distance_km * 10))  # Penalty for distance
            rating_score = driver_rating * 20  # Rating contribution
            matching_score = min(100, distance_score + rating_score)
            
            # Add calculated fields to the object
            location.calculated_distance = round(distance_km, 2)
            location.calculated_eta = eta_minutes
            location.matching_score = round(matching_score, 2)
            
            nearby_drivers.append(location)
    
    # Sort by matching score (highest first)
    nearby_drivers.sort(key=lambda x: x.matching_score, reverse=True)
    
    # Limit results
    limit = request.data.get('limit', 10)
    nearby_drivers = nearby_drivers[:int(limit)]
    
    serializer = NearbyDriversSerializer(nearby_drivers, many=True)
    
    return Response({
        'count': len(nearby_drivers),
        'results': serializer.data,
        'client_location': {
            'latitude': float(latitude),
            'longitude': float(longitude)
        },
        'search_radius_km': float(radius_km)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def start_driver_matching(request):
    """Start intelligent driver matching for a ride request"""
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        return Response(
            {'error': 'Client profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    ride_request_id = request.data.get('ride_request_id')
    if not ride_request_id:
        return Response(
            {'error': 'Ride request ID is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ride_request = RideRequest.objects.get(
            id=ride_request_id, 
            client=client_profile,
            status='Pending'
        )
    except RideRequest.DoesNotExist:
        return Response(
            {'error': 'Ride request not found or not available.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if matching has already started
    if ride_request.matching_started_at:
        return Response(
            {'error': 'Driver matching has already started for this request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get location parameters
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    radius_km = request.data.get('radius_km', 10)
    vehicle_type_id = request.data.get('vehicle_type_id')
    
    if not latitude or not longitude:
        return Response(
            {'error': 'Latitude and longitude are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        client_point = Point(float(longitude), float(latitude), srid=4326)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid coordinates.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find available drivers with enhanced filtering
    available_locations = DriverLocation.objects.filter(
        is_online=True,
        is_available=True,
        driver__is_active=True,
        driver__is_verified=True,
        driver__is_banned=False
    ).select_related('driver', 'driver__vehicle', 'driver__vehicle__type')
    
    # Filter by vehicle type if specified
    if vehicle_type_id:
        available_locations = available_locations.filter(
            driver__vehicle__type_id=vehicle_type_id
        )
    
    # Filter out drivers with active rides
    active_drivers = Ride.objects.filter(
        driver__in=[loc.driver for loc in available_locations],
        is_active=True
    ).values_list('driver_id', flat=True)
    
    available_locations = available_locations.exclude(driver_id__in=active_drivers)
    
    # Calculate distances and matching scores
    matches = []
    for location in available_locations:
        # Calculate distance
        if hasattr(location.location, 'distance'):
            distance_km = location.location.distance(client_point) * 100
        else:
            import math
            lat_diff = abs(location.latitude - float(latitude))
            lng_diff = abs(location.longitude - float(longitude))
            distance_km = math.sqrt(lat_diff**2 + lng_diff**2) * 111
        
        if distance_km <= float(radius_km):
            # Get driver score
            try:
                driver_score = location.driver.score
                reliability_score = driver_score.reliability_score
                acceptance_rate = driver_score.acceptance_rate
                response_time_avg = driver_score.response_time_avg
            except:
                reliability_score = 100.0
                acceptance_rate = 100.0
                response_time_avg = 0.0
            
            # Calculate ETA
            eta_minutes = max(5, int(distance_km * 2))
            
            # Calculate matching score (0-100)
            distance_score = max(0, 100 - (distance_km * 10))
            reliability_factor = reliability_score * 0.4
            acceptance_factor = acceptance_rate * 0.3
            response_factor = max(0, (120 - response_time_avg) / 120) * 30  # 30% weight for response time
            
            matching_score = min(100, distance_score + reliability_factor + acceptance_factor + response_factor)
            
            matches.append({
                'location': location,
                'distance_km': round(distance_km, 2),
                'eta_minutes': eta_minutes,
                'matching_score': round(matching_score, 2),
                'reliability_score': reliability_score
            })
    
    # Sort by matching score (highest first)
    matches.sort(key=lambda x: x['matching_score'], reverse=True)
    
    if not matches:
        return Response({
            'success': False,
            'error': 'No drivers available in the area'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Store all available drivers for user selection
    ride_request.potential_drivers = [match['location'].driver.id for match in matches]
    ride_request.current_driver_index = 0
    ride_request.matching_started_at = timezone.now()
    ride_request.save()
    
    # Prepare driver data for frontend display
    available_drivers = []
    for match in matches:
        driver_location = match['location']
        driver_data = {
            'id': driver_location.driver.id,
            'name': f"{driver_location.driver.first_name} {driver_location.driver.last_name or ''}".strip(),
            'phone': driver_location.driver.phone,
            'photo': driver_location.driver.photo.url if driver_location.driver.photo else None,
            'rating': match.get('reliability_score', 4.0),
            'distance_km': match['distance_km'],
            'eta_minutes': match['eta_minutes'],
            'matching_score': match['matching_score'],
            'latitude': driver_location.latitude,
            'longitude': driver_location.longitude,
            'address': driver_location.address,
            'vehicle_info': {
                'id': driver_location.driver.vehicle.id if driver_location.driver.vehicle else None,
                'name': driver_location.driver.vehicle.name if driver_location.driver.vehicle else None,
                'type': driver_location.driver.vehicle.type.name if driver_location.driver.vehicle and driver_location.driver.vehicle.type else None,
                'capacity': driver_location.driver.vehicle.type.vehicle_capacity if driver_location.driver.vehicle and driver_location.driver.vehicle.type else None,
                'is_air_conditioned': driver_location.driver.vehicle.is_air_conditioned if driver_location.driver.vehicle else None,
                'registration_number': driver_location.driver.vehicle.registration_number if driver_location.driver.vehicle else None
            }
        }
        available_drivers.append(driver_data)
    
    return Response({
        'success': True,
        'message': f'Found {len(matches)} available drivers',
        'available_drivers': available_drivers,
        'total_count': len(matches),
        'ride_request_id': ride_request.id
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def select_driver(request):
    """User selects a specific driver from available drivers"""

    print(request.data)
    print("--------------------------------")
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        return Response(
            {'error': 'Client profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    ride_request_id = request.data.get('ride_request_id')
    driver_id = request.data.get('driver_id')
    
    if not ride_request_id or not driver_id:
        return Response(
            {'error': 'Ride request ID and driver ID are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ride_request = RideRequest.objects.get(
            id=ride_request_id, 
            client=client_profile,
            status='Pending'
        )
    except RideRequest.DoesNotExist:
        return Response(
            {'error': 'Ride request not found or not available.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify the selected driver is in the available drivers list
    # If potential_drivers is empty (map selection), find all actual potential drivers
    if not ride_request.potential_drivers:
        # This happens when driver is selected directly from map
        # Find all available drivers using the same logic as start_driver_matching
        
        # Get client location
        client_location = Point(
            float(request.data.get('client_longitude', 0)),
            float(request.data.get('client_latitude', 0))
        )
        
        # Find drivers within radius (same logic as start_driver_matching)
        radius_km = 10
        radius_meters = radius_km * 1000
        
        # Find driver locations within radius
        driver_locations = DriverLocation.objects.filter(
            location__distance_lte=(client_location, Distance(m=radius_meters)),
            is_online=True
        ).select_related('driver')
        
        # Filter for available drivers (no active rides)
        available_driver_ids = []
        for driver_location in driver_locations:
            driver = driver_location.driver
            
            # Check if driver has any active rides
            active_rides = RideRequest.objects.filter(
                driver=driver,
                status__in=['Pending', 'Confirmed', 'In Progress']
            ).exists()
            
            if not active_rides and driver.is_active:
                available_driver_ids.append(driver.id)
        
        # Add all available drivers to potential_drivers
        ride_request.potential_drivers = available_driver_ids
        ride_request.current_driver_index = 0
        ride_request.save()
        
        # Verify selected driver is in the available drivers
        if driver_id not in available_driver_ids:
            return Response(
                {'error': 'Selected driver is not available for this ride request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    elif driver_id not in ride_request.potential_drivers:
        return Response(
            {'error': 'Selected driver is not available for this ride request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        selected_driver = DriverProfile.objects.get(id=driver_id)
    except DriverProfile.DoesNotExist:
        return Response(
            {'error': 'Driver not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get driver location for distance calculation
    try:
        driver_location = DriverLocation.objects.get(
            driver=selected_driver,
            is_online=True,
            is_available=True
        )
    except DriverLocation.DoesNotExist:
        return Response(
            {'error': 'Selected driver is not currently available.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Calculate distance and ETA
    client_lat = request.data.get('client_latitude')
    client_lng = request.data.get('client_longitude')
    
    if client_lat and client_lng:
        try:
            client_point = Point(float(client_lng), float(client_lat), srid=4326)
            if hasattr(driver_location.location, 'distance'):
                distance_km = driver_location.location.distance(client_point) * 100
            else:
                import math
                lat_diff = abs(driver_location.latitude - float(client_lat))
                lng_diff = abs(driver_location.longitude - float(client_lng))
                distance_km = math.sqrt(lat_diff**2 + lng_diff**2) * 111
        except (ValueError, TypeError):
            distance_km = 5.0  # Default fallback
    else:
        distance_km = 5.0  # Default fallback
    
    eta_minutes = max(5, int(distance_km * 2))
    matching_score = 85.0  # Default score for user-selected driver
    
    # Create RideMatching for the selected driver
    expires_at = timezone.now() + timezone.timedelta(minutes=5)
    ride_matching, created = RideMatching.objects.get_or_create(
        ride_request=ride_request,
        driver=selected_driver,
        defaults={
            'distance_km': distance_km,
            'estimated_eta_minutes': eta_minutes,
            'matching_score': matching_score,
            'expires_at': expires_at,
            'status': 'pending'
        }
    )
    
    if not created:
        # Update existing match
        ride_matching.distance_km = distance_km
        ride_matching.estimated_eta_minutes = eta_minutes
        ride_matching.matching_score = matching_score
        ride_matching.expires_at = expires_at
        ride_matching.status = 'pending'
        ride_matching.save()
    
    # Update ride request to point to selected driver
    ride_request.current_driver_index = ride_request.potential_drivers.index(driver_id)
    ride_request.save()
    
    # Serialize the selected match
    serializer = RideMatchingSerializer(ride_matching)
    
    # Send WebSocket message to user and driver
    user_group = f"ride_matching_{request.user.id}"
    driver_group = f"ride_matching_{selected_driver.user.id}"
    ride_group = f"ride_request_{ride_request.id}"
    
    # Data for client
    client_websocket_data = {
        'ride_request_id': ride_request.id,
        'driver_id': selected_driver.id,
        'driver_name': selected_driver.user.get_user_names,
        'status': 'pending',
        'expires_at': expires_at.isoformat(),
        'timeout_minutes': 5,
        'message': f'Request sent to {selected_driver.user.get_user_names}'
    }
    
    # Data for driver
    driver_websocket_data = {
        'ride_request_id': ride_request.id,
        'ride_matching_id': ride_matching.id,
        'client_id': client_profile.id,
        'client_name': client_profile.user.get_user_names,
        'start_location': ride_request.start_location,
        'end_location': ride_request.end_location,
        'distance_km': distance_km,
        'estimated_eta_minutes': eta_minutes,
        'matching_score': matching_score,
        'expires_at': expires_at.isoformat(),
        'timeout_minutes': 5,
        'status': 'pending',
        'message': f'New ride request from {client_profile.user.get_user_names}'
    }
    
    # Send to user-specific group, driver-specific group, and ride-specific group
    send_websocket_message(user_group, 'driver_response', client_websocket_data)
    send_websocket_message(driver_group, 'ride_request', driver_websocket_data)
    send_websocket_message(ride_group, 'driver_response', client_websocket_data)
    
    return Response({
        'success': True,
        'message': f'Request sent to {selected_driver.user.get_user_names}',
        'selected_match': serializer.data,
        'expires_at': expires_at.isoformat(),
        'timeout_minutes': 5
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def try_next_driver(request):
    """Try the next driver with similar vehicle capacity automatically"""
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        return Response(
            {'error': 'Client profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    ride_request_id = request.data.get('ride_request_id')
    if not ride_request_id:
        return Response(
            {'error': 'Ride request ID is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ride_request = RideRequest.objects.get(
            id=ride_request_id, 
            client=client_profile,
            status='Pending'
        )
    except RideRequest.DoesNotExist:
        return Response(
            {'error': 'Ride request not found or not available.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get the current driver's vehicle capacity for matching similar vehicles
    current_driver_id = ride_request.potential_drivers[ride_request.current_driver_index] if ride_request.current_driver_index < len(ride_request.potential_drivers) else None
    current_vehicle_capacity = None
    
    if current_driver_id:
        try:
            current_driver = DriverProfile.objects.get(id=current_driver_id)
            if current_driver.vehicle and current_driver.vehicle.type:
                current_vehicle_capacity = current_driver.vehicle.type.vehicle_capacity
        except DriverProfile.DoesNotExist:
            pass
    
    # Find next driver with similar vehicle capacity
    next_driver = None
    for i in range(ride_request.current_driver_index + 1, len(ride_request.potential_drivers)):
        try:
            candidate_driver = DriverProfile.objects.get(id=ride_request.potential_drivers[i])
            
            # Check if driver is available
            try:
                driver_location = DriverLocation.objects.get(
                    driver=candidate_driver,
                    is_online=True,
                    is_available=True
                )
            except DriverLocation.DoesNotExist:
                continue
            
            # If we have a vehicle capacity preference, match it
            if current_vehicle_capacity and candidate_driver.vehicle and candidate_driver.vehicle.type:
                if candidate_driver.vehicle.type.vehicle_capacity == current_vehicle_capacity:
                    next_driver = candidate_driver
                    ride_request.current_driver_index = i
                    break
            else:
                # No capacity preference, take any available driver
                next_driver = candidate_driver
                ride_request.current_driver_index = i
                break
                
        except DriverProfile.DoesNotExist:
            continue
    
    if not next_driver:
        return Response({
            'success': False,
            'error': 'No more drivers with similar vehicle capacity available',
            'suggest_manual_selection': True
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get driver location for calculations
    driver_location = DriverLocation.objects.get(
        driver=next_driver,
        is_online=True,
        is_available=True
    )
    
    # Calculate distance and ETA
    client_lat = request.data.get('client_latitude')
    client_lng = request.data.get('client_longitude')
    
    if client_lat and client_lng:
        try:
            client_point = Point(float(client_lng), float(client_lat), srid=4326)
            if hasattr(driver_location.location, 'distance'):
                distance_km = driver_location.location.distance(client_point) * 100
            else:
                import math
                lat_diff = abs(driver_location.latitude - float(client_lat))
                lng_diff = abs(driver_location.longitude - float(client_lng))
                distance_km = math.sqrt(lat_diff**2 + lng_diff**2) * 111
        except (ValueError, TypeError):
            distance_km = 5.0
    else:
        distance_km = 5.0
    
    eta_minutes = max(5, int(distance_km * 2))
    matching_score = 75.0  # Lower score for auto-selected next driver
    
    # Create new RideMatching for the next driver
    expires_at = timezone.now() + timezone.timedelta(minutes=5)
    ride_matching, created = RideMatching.objects.get_or_create(
        ride_request=ride_request,
        driver=next_driver,
        defaults={
            'distance_km': distance_km,
            'estimated_eta_minutes': eta_minutes,
            'matching_score': matching_score,
            'expires_at': expires_at,
            'status': 'pending'
        }
    )
    
    if not created:
        # Update existing match
        ride_matching.distance_km = distance_km
        ride_matching.estimated_eta_minutes = eta_minutes
        ride_matching.matching_score = matching_score
        ride_matching.expires_at = expires_at
        ride_matching.status = 'pending'
        ride_matching.save()
    
    # Update ride request to point to next driver
    ride_request.current_driver_index += 1
    ride_request.save()
    
    # Serialize the current match
    serializer = RideMatchingSerializer(ride_matching)
    
    # Send WebSocket message to user and driver
    user_group = f"ride_matching_{request.user.id}"
    driver_group = f"ride_matching_{next_driver.user.id}"
    ride_group = f"ride_request_{ride_request.id}"
    
    # Data for client
    client_websocket_data = {
        'ride_request_id': ride_request.id,
        'driver_id': next_driver.id,
        'driver_name': next_driver.user.get_user_names,
        'status': 'pending',
        'expires_at': expires_at.isoformat(),
        'timeout_minutes': 5,
        'drivers_remaining': len(ride_request.potential_drivers) - ride_request.current_driver_index,
        'message': f'Contacting next driver (Driver #{ride_request.current_driver_index})'
    }
    
    # Data for driver
    driver_websocket_data = {
        'ride_request_id': ride_request.id,
        'ride_matching_id': ride_matching.id,
        'client_id': client_profile.id,
        'client_name': client_profile.user.get_user_names,
        'start_location': ride_request.start_location,
        'end_location': ride_request.end_location,
        'distance_km': distance_km,
        'estimated_eta_minutes': eta_minutes,
        'matching_score': matching_score,
        'expires_at': expires_at.isoformat(),
        'timeout_minutes': 5,
        'status': 'pending',
        'message': f'New ride request from {client_profile.user.get_user_names}'
    }
    
    # Send to user-specific group, driver-specific group, and ride-specific group
    send_websocket_message(user_group, 'next_driver_selected', client_websocket_data)
    send_websocket_message(driver_group, 'ride_request', driver_websocket_data)
    send_websocket_message(ride_group, 'next_driver_selected', client_websocket_data)
    
    return Response({
        'success': True,
        'message': f'Contacting next driver (Driver #{ride_request.current_driver_index})',
        'current_match': serializer.data,
        'drivers_remaining': len(ride_request.potential_drivers) - ride_request.current_driver_index,
        'expires_at': expires_at.isoformat(),
        'timeout_minutes': 5
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def accept_ride_match(request):
    """Driver accepts a ride match"""
    try:
        driver_profile = request.user.driver_profile
    except DriverProfile.DoesNotExist:
        return Response(
            {'error': 'Driver profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    ride_request_id = request.data.get('ride_request_id')
    if not ride_request_id:
        return Response(
            {'error': 'Ride request ID is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ride_request = RideRequest.objects.get(id=ride_request_id, status='Pending')
    except RideRequest.DoesNotExist:
        return Response(
            {'error': 'Ride request not found or not available.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if driver is available
    driver_location = DriverLocation.objects.filter(
        driver=driver_profile,
        is_online=True,
        is_available=True
    ).first()
    
    if not driver_location:
        return Response(
            {'error': 'Driver is not available for new rides.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find the ride matching record
    try:
        ride_matching = RideMatching.objects.get(
            ride_request=ride_request,
            driver=driver_profile,
            status='pending'
        )
        
        # Check if match has expired
        if ride_matching.is_expired():
            return Response(
                {'error': 'This ride match has expired.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Accept the match
        ride_matching.accept()
        
    except RideMatching.DoesNotExist:
        return Response(
            {'error': 'No matching record found for this ride request.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update ride request
    ride_request.driver = driver_profile
    ride_request.vehicle = driver_profile.vehicle
    ride_request.status = 'Accepted'
    ride_request.driver_confirmed_at = timezone.now()
    ride_request.pickup_eta = timezone.now() + timezone.timedelta(minutes=ride_matching.estimated_eta_minutes)
    ride_request.save()
    
    # Update driver availability
    driver_location.is_available = False
    driver_location.save()
    
    # Update driver score
    from .models import DriverScore
    driver_score, created = DriverScore.objects.get_or_create(
        driver=driver_profile,
        defaults={
            'total_requests': 0,
            'accepted_requests': 0,
            'response_time_avg': 0.0
        }
    )
    
    # Update statistics
    driver_score.total_requests += 1
    driver_score.accepted_requests += 1
    
    # Update response time average
    if ride_matching.response_time_seconds:
        if driver_score.response_time_avg == 0:
            driver_score.response_time_avg = ride_matching.response_time_seconds
        else:
            # Calculate rolling average
            total_requests = driver_score.accepted_requests
            driver_score.response_time_avg = (
                (driver_score.response_time_avg * (total_requests - 1) + ride_matching.response_time_seconds) / total_requests
            )
    
    driver_score.update_scores()
    
    # Serialize response
    serializer = RideRequestSerializer(ride_request)
    
    # Send WebSocket message to client
    user_group = f"ride_matching_{ride_request.client.user.id}"
    ride_group = f"ride_request_{ride_request.id}"
    
    websocket_data = {
        'ride_request_id': ride_request.id,
        'driver_id': driver_profile.id,
        'driver_name': driver_profile.user.get_user_names,
        'status': 'accepted',
        'pickup_eta': ride_request.pickup_eta.isoformat(),
        'estimated_eta_minutes': ride_matching.estimated_eta_minutes,
        'message': f'Driver {driver_profile.user.get_user_names} accepted your ride request!'
    }
    
    # Send to client-specific group and ride-specific group
    send_websocket_message(user_group, 'ride_confirmed', websocket_data)
    send_websocket_message(ride_group, 'ride_confirmed', websocket_data)
    
    return Response({
        'message': 'Ride request accepted successfully.',
        'ride_request': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def decline_ride_match(request):
    """Driver declines a ride match"""
    try:
        driver_profile = request.user.driver_profile
    except DriverProfile.DoesNotExist:
        return Response(
            {'error': 'Driver profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    ride_request_id = request.data.get('ride_request_id')
    if not ride_request_id:
        return Response(
            {'error': 'Ride request ID is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ride_request = RideRequest.objects.get(id=ride_request_id, status='Pending')
    except RideRequest.DoesNotExist:
        return Response(
            {'error': 'Ride request not found or not available.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Find the ride matching record
    try:
        ride_matching = RideMatching.objects.get(
            ride_request=ride_request,
            driver=driver_profile,
            status='pending'
        )
        
        # Decline the match
        ride_matching.decline()
        
    except RideMatching.DoesNotExist:
        return Response(
            {'error': 'No matching record found for this ride request.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update driver score
    from .models import DriverScore
    driver_score, created = DriverScore.objects.get_or_create(
        driver=driver_profile,
        defaults={
            'total_requests': 0,
            'declined_requests': 0
        }
    )
    
    # Update statistics
    driver_score.total_requests += 1
    driver_score.declined_requests += 1
    driver_score.update_scores()
    
    # Send WebSocket message to client about decline
    user_group = f"ride_matching_{ride_request.client.user.id}"
    ride_group = f"ride_request_{ride_request.id}"
    
    websocket_data = {
        'ride_request_id': ride_request.id,
        'driver_id': driver_profile.id,
        'driver_name': driver_profile.user.get_user_names,
        'status': 'declined',
        'message': f'Driver {driver_profile.user.get_user_names} declined the ride request',
        'can_try_next': True,
        'drivers_remaining': len(ride_request.potential_drivers) - ride_request.current_driver_index if ride_request.potential_drivers else 0
    }
    
    # Send to client-specific group and ride-specific group
    send_websocket_message(user_group, 'driver_declined', websocket_data)
    send_websocket_message(ride_group, 'driver_declined', websocket_data)
    
    return Response({
        'success': True,
        'message': 'Ride request declined'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsClient])
def check_matching_status(request):
    """Check the status of driver matching for a ride request"""
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        return Response(
            {'error': 'Client profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    ride_request_id = request.query_params.get('ride_request_id')
    if not ride_request_id:
        return Response(
            {'error': 'Ride request ID is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ride_request = RideRequest.objects.get(
            id=ride_request_id, 
            client=client_profile
        )
    except RideRequest.DoesNotExist:
        return Response(
            {'error': 'Ride request not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if request has expired
    if ride_request.expires_at and timezone.now() > ride_request.expires_at:
        ride_request.status = 'Cancelled'
        ride_request.save()
        
        # Mark all pending matches as expired
        pending_matches = RideMatching.objects.filter(
            ride_request=ride_request,
            status='pending'
        )
        
        # Send WebSocket notifications to all pending drivers about timeout
        for match in pending_matches:
            driver_group = f"ride_matching_{match.driver.user.id}"
            websocket_data = {
                'ride_request_id': ride_request.id,
                'ride_matching_id': match.id,
                'client_id': ride_request.client.id,
                'client_name': ride_request.client.user.get_user_names,
                'status': 'timeout',
                'message': f'Ride request from {ride_request.client.user.get_user_names} has expired',
                'cancelled_by': 'timeout'
            }
            
            send_websocket_message(driver_group, 'ride_cancelled', websocket_data)
        
        # Update match statuses
        pending_matches.update(status='timeout')
        
        return Response({
            'success': True,
            'status': 'expired',
            'message': 'Ride request has expired. No drivers accepted in time.'
        }, status=status.HTTP_200_OK)
    
    # Get current matches
    matches = RideMatching.objects.filter(
        ride_request=ride_request
    ).order_by('-matching_score')
    
    # Check if any driver has accepted
    accepted_match = matches.filter(status='accepted').first()
    if accepted_match:
        return Response({
            'success': True,
            'status': 'accepted',
            'message': 'Driver has accepted your ride request',
            'match': RideMatchingSerializer(accepted_match).data,
            'ride_request': RideRequestSerializer(ride_request).data
        }, status=status.HTTP_200_OK)
    
    # Check current pending match
    current_match = matches.filter(status='pending').first()
    if current_match:
        # Check if current match has expired
        if current_match.is_expired():
            # Mark as timeout and try next driver
            current_match.status = 'timeout'
            current_match.save()
            
            # Check if there are more drivers to try
            if ride_request.current_driver_index < len(ride_request.potential_drivers):
                return Response({
                    'success': True,
                    'status': 'try_next_driver',
                    'message': 'Current driver did not respond in time. Trying next driver...',
                    'can_try_next': True,
                    'drivers_remaining': len(ride_request.potential_drivers) - ride_request.current_driver_index
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': True,
                    'status': 'no_drivers',
                    'message': 'No more drivers available. All drivers have been contacted.'
                }, status=status.HTTP_200_OK)
        
        # Current match is still pending
        time_remaining = None
        if current_match.expires_at:
            remaining = current_match.expires_at - timezone.now()
            time_remaining = max(0, int(remaining.total_seconds()))
        
        return Response({
            'success': True,
            'status': 'pending',
            'message': 'Waiting for current driver to respond...',
            'current_match': RideMatchingSerializer(current_match).data,
            'time_remaining': time_remaining,
            'drivers_remaining': len(ride_request.potential_drivers) - ride_request.current_driver_index
        }, status=status.HTTP_200_OK)
    
    # No pending matches - check if we can try next driver
    if ride_request.current_driver_index < len(ride_request.potential_drivers):
        return Response({
            'success': True,
            'status': 'try_next_driver',
            'message': 'Previous driver declined or timed out. Ready to try next driver.',
            'can_try_next': True,
            'drivers_remaining': len(ride_request.potential_drivers) - ride_request.current_driver_index
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': True,
            'status': 'no_drivers',
            'message': 'No drivers available. All drivers have been contacted.'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_statistics(request):
    """Get client statistics"""
    if not request.user.is_client:
        return Response(
            {'error': 'Only clients can access this endpoint.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        return Response(
            {'error': 'Client profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Calculate statistics
    total_rides = Ride.objects.filter(client=client_profile).count()
    pending_requests = RideRequest.objects.filter(client=client_profile, status='Pending').count()
    completed_rides = RideRequest.objects.filter(client=client_profile, status='Completed').count()
    cancelled_rides = RideRequest.objects.filter(client=client_profile, status='Cancelled').count()
    
    ratings_given = Rating.objects.filter(client=client_profile).count()
    feedback_given = FeedBack.objects.filter(client=client_profile).count()
    
    return Response({
        'total_rides': total_rides,
        'pending_requests': pending_requests,
        'completed_rides': completed_rides,
        'cancelled_rides': cancelled_rides,
        'ratings_given': ratings_given,
        'feedback_given': feedback_given
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_driver_location(request):
    """Update driver's current location during navigation"""
    if not request.user.is_driver:
        return Response({'error': 'Only drivers can update location'}, status=403)
    
    try:
        driver = request.user.driver
        longitude = request.data.get('longitude')
        latitude = request.data.get('latitude')
        ride_id = request.data.get('ride_id')
        
        if not longitude or not latitude:
            return Response({'error': 'Longitude and latitude are required'}, status=400)
        
        # Update or create driver location
        driver_location, created = DriverLocation.objects.update_or_create(
            driver=driver,
            defaults={
                'longitude': longitude,
                'latitude': latitude,
                'updated_at': timezone.now()
            }
        )
        
        # If this is during an active ride, update the ride status
        if ride_id:
            try:
                ride_match = RideMatching.objects.get(
                    id=ride_id,
                    driver=driver,
                    status__in=['accepted', 'driver_arrived', 'ride_started']
                )
                
                # Send location update via WebSocket
                send_websocket_message(
                    f"ride_{ride_id}",
                    "driver_location_update",
                    {
                        'ride_id': ride_id,
                        'driver_id': driver.id,
                        'longitude': longitude,
                        'latitude': latitude,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
            except RideMatching.DoesNotExist:
                pass
        
        return Response({
            'success': True,
            'message': 'Location updated successfully',
            'location': {
                'longitude': longitude,
                'latitude': latitude,
                'updated_at': driver_location.updated_at
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def driver_location_history(request, driver_id):
    try:
        # Add permissions as needed!
        data = [
            {
                'lon': p.location.x,
                'lat': p.location.y,
                'timestamp': p.timestamp.isoformat(),
            }
            for p in DriverLocationHistory.objects.filter(driver_id=driver_id).order_by('timestamp')
        ]
        return Response({'history': data})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def arrive_at_pickup(request, ride_id):
    """Mark driver as arrived at pickup location"""
    if not request.user.is_driver:
        return Response({'error': 'Only drivers can mark arrival'}, status=403)
    
    try:
        ride_match = RideMatching.objects.get(
            id=ride_id,
            driver=request.user.driver_profile,
            status='accepted'
        )
        
        ride_match.status = 'driver_arrived'
        ride_match.driver_arrived_at = timezone.now()
        ride_match.save()
        
        # Send WebSocket notification
        send_websocket_message(
            f"ride_{ride_id}",
            "driver_arrived",
            {
                'ride_id': ride_id,
                'driver_id': request.user.driver_profile.id,
                'driver_name': request.user.get_user_names,
                'arrived_at': ride_match.driver_arrived_at.isoformat()
            }
        )
        
        return Response({
            'success': True,
            'message': 'Arrived at pickup location',
            'ride_match': RideMatchingSerializer(ride_match).data
        })
        
    except RideMatching.DoesNotExist:
        return Response({'error': 'Ride not found or not accessible'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_ride(request, ride_id):
    """Start the ride (pickup completed, heading to destination)"""
    if not request.user.is_driver:
        return Response({'error': 'Only drivers can start rides'}, status=403)
    
    try:
        ride_match = RideMatching.objects.get(
            id=ride_id,
            driver=request.user.driver_profile,
            status='driver_arrived'
        )
        
        ride_match.status = 'ride_started'
        ride_match.ride_started_at = timezone.now()
        ride_match.save()
        
        # Send WebSocket notification
        send_websocket_message(
            f"ride_{ride_id}",
            "ride_started",
            {
                'ride_id': ride_id,
                'driver_id': request.user.driver_profile.id,
                'driver_name': request.user.get_user_names,
                'started_at': ride_match.ride_started_at.isoformat()
            }
        )
        
        return Response({
            'success': True,
            'message': 'Ride started successfully',
            'ride_match': RideMatchingSerializer(ride_match).data
        })
        
    except RideMatching.DoesNotExist:
        return Response({'error': 'Ride not found or not accessible'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_ride(request, ride_id):
    """Complete the ride"""
    if not request.user.is_driver:
        return Response({'error': 'Only drivers can complete rides'}, status=403)
    
    try:
        ride_match = RideMatching.objects.get(
            id=ride_id,
            driver=request.user.driver_profile,
            status='ride_started'
        )
        
        ride_match.status = 'completed'
        ride_match.completed_at = timezone.now()
        ride_match.save()
        
        # Update the ride request status as well
        ride_request = ride_match.ride_request
        ride_request.status = 'completed'
        ride_request.save()

        driver_location = DriverLocation.objects.get(driver=ride_request.driver)
        driver_location.is_available = True
        driver_location.save()
        
        # Send WebSocket notification
        send_websocket_message(
            f"ride_{ride_id}",
            "ride_completed",
            {
                'ride_id': ride_id,
                'driver_id': request.user.driver_profile.id,
                'driver_name': request.user.get_user_names,
                'completed_at': ride_match.completed_at.isoformat(),
                'ride_cost': str(ride_request.cost)
            }
        )
        
        return Response({
            'success': True,
            'message': 'Ride completed successfully',
            'ride_match': RideMatchingSerializer(ride_match).data,
            'ride_cost': ride_request.cost
        })
        
    except RideMatching.DoesNotExist:
        return Response({'error': 'Ride not found or not accessible'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_ride(request, ride_id):
    """Cancel the ride"""
    if not request.user.is_driver:
        return Response({'error': 'Only drivers can cancel rides'}, status=403)
    
    try:
        ride_match = RideMatching.objects.get(
            id=ride_id,
            driver=request.user.driver_profile,
            status__in=['accepted', 'driver_arrived', 'ride_started']
        )
        
        ride_match.status = 'cancelled'
        ride_match.cancelled_at = timezone.now()
        ride_match.save()
        
        # Update the ride request status as well
        ride_request = ride_match.ride_request
        ride_request.status = 'cancelled'
        ride_request.save()

        ride = ride_request.ride
        ride.is_active = False
        ride.save()
        
        # Send WebSocket notification
        send_websocket_message(
            f"ride_{ride_id}",
            "ride_cancelled",
            {
                'ride_id': ride_id,
                'driver_id': request.user.driver_profile.id,
                'driver_name': request.user.get_user_names,
                'cancelled_at': ride_match.cancelled_at.isoformat(),
                'reason': 'Driver cancelled'
            }
        )
        
        return Response({
            'success': True,
            'message': 'Ride cancelled successfully',
            'ride_match': RideMatchingSerializer(ride_match).data
        })
        
    except RideMatching.DoesNotExist:
        return Response({'error': 'Ride not found or not accessible'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_driver_location(request, ride_request_id):
    """Get driver's current location for a specific ride"""
    try:
        # Get the ride request
        ride_request = RideRequest.objects.get(id=ride_request_id)
        
        # Check if user is authorized to view this ride's location
        if request.user.is_client:
            # Client can only see location for their own rides
            if ride_request.client.user != request.user:
                return Response({'error': 'Not authorized to view this ride location'}, status=403)
        elif request.user.is_driver:
            # Driver can only see location for their own rides
            if ride_request.driver != request.user.driver:
                return Response({'error': 'Not authorized to view this ride location'}, status=403)
        else:
            return Response({'error': 'Invalid user type'}, status=403)
        
        # Get the driver's current location
        if ride_request.driver:
            try:
                driver_location = DriverLocation.objects.filter(
                    driver=ride_request.driver,
                    is_online=True
                ).latest('updated_at')
                
                return Response({
                    'success': True,
                    'location': {
                        'longitude': driver_location.longitude,
                        'latitude': driver_location.latitude,
                        'updated_at': driver_location.updated_at.isoformat()
                    }
                })
            except DriverLocation.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Driver location not available'
                }, status=404)
        else:
            return Response({
                'success': False,
                'error': 'No driver assigned to this ride'
            }, status=404)
            
    except RideRequest.DoesNotExist:
        return Response({'error': 'Ride request not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_rating(request):
    """Submit a rating for a completed ride"""
    if not request.user.is_client:
        return Response({'error': 'Only clients can submit ratings'}, status=403)
    
    try:
        ride_request_id = request.data.get('ride_request_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        if not ride_request_id or not rating:
            return Response({'error': 'Ride request ID and rating are required'}, status=400)
        
        # Get the ride request
        ride_request = RideRequest.objects.get(
            id=ride_request_id,
            client=request.user.client_profile,
            status='completed'
        )
        
        # Check if rating already exists
        from .models import Rating
        existing_rating = Rating.objects.filter(
            ride_request=ride_request,
            client=request.user.client_profile
        ).first()
        
        if existing_rating:
            return Response({'error': 'Rating already submitted for this ride'}, status=400)
        
        # Create the rating
        rating_obj = Rating.objects.create(
            ride_request=ride_request,
            driver=ride_request.driver,
            client=request.user.client_profile,
            rating=rating,
            comment=comment
        )
        
        return Response({
            'success': True,
            'message': 'Rating submitted successfully',
            'rating': {
                'id': rating_obj.id,
                'rating': rating_obj.rating,
                'comment': rating_obj.comment,
                'created_at': rating_obj.created_at.isoformat()
            }
        })
        
    except RideRequest.DoesNotExist:
        return Response({'error': 'Ride request not found or not accessible'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

