
from django.db import models
from django.utils import timezone
from django.contrib.gis.geos import Point

from rest_framework import serializers

from accounts.models import ClientProfile, DriverProfile
from .models import (
    VehicleType, Vehicle, VehiclePhoto, VehicleDocument,
    Route, Ride, Rating, FeedBack, RideRequest, DriverLocation, RideMatching
)


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ['id', 'name', 'description', 'engine_type', 'vehicle_capacity', 'base_price', 'price_per_km']
        read_only_fields = ['id']


class VehiclePhotoSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = VehiclePhoto
        fields = ['id', 'vehicle', 'photo', 'photo_url', 'created', 'updated']
        read_only_fields = ['id', 'created', 'updated']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and hasattr(obj.photo, 'url'):
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


class VehicleDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = VehicleDocument
        fields = ['id', 'vehicle', 'file', 'file_url', 'created', 'updated']
        read_only_fields = ['id', 'created', 'updated']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class VehicleSerializer(serializers.ModelSerializer):
    type_details = VehicleTypeSerializer(source='type', read_only=True)
    photos = VehiclePhotoSerializer(many=True, read_only=True, source='vehiclephoto_set')
    documents = VehicleDocumentSerializer(many=True, read_only=True, source='vehicledocument_set')
    age_years = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'type', 'type_details', 'name', 'registration_number',
            'description', 'is_air_conditioned', 'is_insured', 'age', 'age_years',
            'manufacturing_year', 'photos', 'documents', 'created', 'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']

    def get_age_years(self, obj):
        return obj.get_age()


class VehicleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for vehicle lists"""
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'registration_number', 'type_name', 'is_air_conditioned', 'is_insured']
        read_only_fields = ['id']


class RouteSerializer(serializers.ModelSerializer):
    pickup_lat = serializers.FloatField(write_only=True, required=False)
    pickup_lng = serializers.FloatField(write_only=True, required=False)
    destination_lat = serializers.FloatField(write_only=True, required=False)
    destination_lng = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = Route
        fields = [
            'id', 'pickup_location', 'destination', 'eta',
            'pickup_lat', 'pickup_lng', 'destination_lat', 'destination_lng',
            'created', 'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']

    def create(self, validated_data):
        # Handle coordinate conversion for PointField
        pickup_lat = validated_data.pop('pickup_lat', None)
        pickup_lng = validated_data.pop('pickup_lng', None)
        destination_lat = validated_data.pop('destination_lat', None)
        destination_lng = validated_data.pop('destination_lng', None)

        if pickup_lat and pickup_lng:
            validated_data['pickup_location'] = Point(float(pickup_lng), float(pickup_lat), srid=4326)
        
        if destination_lat and destination_lng:
            validated_data['destination'] = Point(float(destination_lng), float(destination_lat), srid=4326)

        return super().create(validated_data)


class DriverProfileSerializer(serializers.ModelSerializer):
    """Simplified driver profile for ride display"""
    full_name = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    vehicle = VehicleListSerializer(read_only=True)

    class Meta:
        model = DriverProfile
        fields = ['id', 'username', 'full_name', 'photo', 'phone', 'rating', 'vehicle', 'is_online']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()

    def get_rating(self, obj):
        # Calculate average rating for the driver
        ratings = Rating.objects.filter(ride__driver=obj)
        if ratings.exists():
            return round(ratings.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0.0


class ClientProfileSerializer(serializers.ModelSerializer):
    """Simplified client profile for ride display"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ClientProfile
        fields = ['id', 'username', 'full_name', 'photo', 'phone']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()


class RideSerializer(serializers.ModelSerializer):
    driver_details = DriverProfileSerializer(source='driver', read_only=True)
    client_details = ClientProfileSerializer(source='client', read_only=True)
    vehicle_details = VehicleListSerializer(source='vehicle', read_only=True)
    route_details = RouteSerializer(source='route', read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = [
            'id', 'driver', 'driver_details', 'client', 'client_details',
            'vehicle', 'vehicle_details', 'route', 'route_details',
            'start_location', 'end_location', 'start_time', 'end_time',
            'duration', 'created', 'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']

    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            return str(duration)
        return None


class RatingSerializer(serializers.ModelSerializer):
    client_details = ClientProfileSerializer(source='client', read_only=True)
    ride_details = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ['id', 'ride', 'ride_details', 'client', 'client_details', 'rating', 'created', 'updated']
        read_only_fields = ['id', 'created', 'updated']

    def get_ride_details(self, obj):
        return {
            'id': obj.ride.id,
            'start_location': obj.ride.start_location,
            'end_location': obj.ride.end_location
        }

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value


class FeedBackSerializer(serializers.ModelSerializer):
    client_details = ClientProfileSerializer(source='client', read_only=True)
    rating_details = RatingSerializer(source='rating', read_only=True)

    class Meta:
        model = FeedBack
        fields = [
            'id', 'client', 'client_details', 'ride', 'message',
            'rating', 'rating_details', 'created', 'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']


class RideRequestSerializer(serializers.ModelSerializer):
    client_details = ClientProfileSerializer(source='client', read_only=True)
    driver_details = DriverProfileSerializer(source='driver', read_only=True)
    vehicle_details = VehicleListSerializer(source='vehicle', read_only=True)
    ride_details = RideSerializer(source='ride', read_only=True)

    class Meta:
        model = RideRequest
        fields = [
            'id', 'client', 'client_details', 'driver', 'driver_details',
            'vehicle', 'vehicle_details', 'start_location', 'end_location',
            'requested_at', 'status', 'ride', 'ride_details', 'cost', 'created', 'updated'
        ]
        read_only_fields = ['id', 'requested_at', 'created', 'updated']

    def validate_status(self, value):
        valid_statuses = ['Pending', 'Accepted', 'Completed', 'Cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value


class RideRequestCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating ride requests"""
    pickup_lat = serializers.FloatField(write_only=True, required=False)
    pickup_lng = serializers.FloatField(write_only=True, required=False)
    destination_lat = serializers.FloatField(write_only=True, required=False)
    destination_lng = serializers.FloatField(write_only=True, required=False)
    pickup_address = serializers.CharField(write_only=True, required=False)
    destination_address = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = RideRequest
        fields = [
            'id', 'start_location', 'end_location', 'vehicle', 'cost',
            'pickup_lat', 'pickup_lng', 'destination_lat', 'destination_lng',
            'pickup_address', 'destination_address', 'expires_at', 'matching_started_at',
            'driver_confirmed_at', 'pickup_eta'
        ]
        read_only_fields = ['id', 'expires_at', 'matching_started_at', 'driver_confirmed_at', 'pickup_eta']

    def create(self, validated_data):
        # Extract location data
        pickup_lat = validated_data.pop('pickup_lat', None)
        pickup_lng = validated_data.pop('pickup_lng', None)
        destination_lat = validated_data.pop('destination_lat', None)
        destination_lng = validated_data.pop('destination_lng', None)
        pickup_address = validated_data.pop('pickup_address', None)
        destination_address = validated_data.pop('destination_address', None)

        # Get client from request
        user = self.context['request'].user
        try:
            client = user.client_profile
        except ClientProfile.DoesNotExist:
            raise serializers.ValidationError("User must have a client profile to request rides.")

        # Create route if coordinates provided
        route = None
        if pickup_lat and pickup_lng and destination_lat and destination_lng:
            route = Route.objects.create(
                pickup_location=Point(float(pickup_lng), float(pickup_lat), srid=4326),
                destination=Point(float(destination_lng), float(destination_lat), srid=4326),
                eta=timezone.now() + timezone.timedelta(minutes=30)  # Default 30 min ETA
            )

        # Set addresses if provided
        if pickup_address:
            validated_data['start_location'] = pickup_address
        if destination_address:
            validated_data['end_location'] = destination_address

        # Set expiration time (5 minutes from now)
        from datetime import timedelta
        
        # Create ride request
        ride_request = RideRequest.objects.create(
            client=client,
            route=route,  # Link the route to the ride request
            expires_at=timezone.now() + timedelta(minutes=5),
            **validated_data
        )

        return ride_request


class RideRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for drivers to accept ride requests"""
    class Meta:
        model = RideRequest
        fields = ['status', 'driver', 'vehicle']

    def validate(self, data):
        user = self.context['request'].user
        
        if 'status' in data and data['status'] == 'Accepted':
            if not user.is_driver:
                raise serializers.ValidationError("Only drivers can accept ride requests.")
            
            # Set driver automatically
            try:
                data['driver'] = user.diver_profile
            except DriverProfile.DoesNotExist:
                raise serializers.ValidationError("User must have a driver profile.")
        
        return data


class AvailableDriverSerializer(serializers.ModelSerializer):
    """Serializer for showing available drivers near a location"""
    full_name = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    total_rides = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = DriverProfile
        fields = [
            'id', 'username', 'full_name', 'photo', 'phone',
            'rating', 'total_rides', 'vehicle_info', 'is_online'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()

    def get_rating(self, obj):
        from django.db.models import Avg
        ratings = Rating.objects.filter(ride__driver=obj)
        if ratings.exists():
            return round(ratings.aggregate(Avg('rating'))['rating__avg'], 2)
        return 0.0

    def get_total_rides(self, obj):
        return Ride.objects.filter(driver=obj).count()

    def get_vehicle_info(self, obj):
        if obj.vehicle:
            return {
                'id': obj.vehicle.id,
                'name': obj.vehicle.name,
                'type': obj.vehicle.type.name if obj.vehicle.type else None,
                'is_air_conditioned': obj.vehicle.is_air_conditioned
            }
        return None


class DriverLocationSerializer(serializers.ModelSerializer):
    """Serializer for driver location tracking"""
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    driver_name = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = DriverLocation
        fields = [
            'id', 'driver', 'driver_name', 'location', 'latitude', 'longitude',
            'address', 'is_online', 'is_available', 'last_updated', 'vehicle_info'
        ]
        read_only_fields = ['id', 'last_updated']
    
    def get_driver_name(self, obj):
        return obj.driver.user.get_user_names

    def get_vehicle_info(self, obj):
        if obj.driver.vehicle:
            return {
                'id': obj.driver.vehicle.id,
                'name': obj.driver.vehicle.name,
                'type': obj.driver.vehicle.type.name if obj.driver.vehicle.type else None,
                'registration_number': obj.driver.vehicle.registration_number
            }
        return None


class DriverLocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating driver location"""
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    class Meta:
        model = DriverLocation
        fields = ['latitude', 'longitude', 'address', 'is_online', 'is_available']

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        # Create Point from coordinates
        validated_data['location'] = Point(longitude, latitude, srid=4326)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        if latitude is not None and longitude is not None:
            validated_data['location'] = Point(longitude, latitude, srid=4326)
        
        return super().update(instance, validated_data)


class RideMatchingSerializer(serializers.ModelSerializer):
    """Serializer for ride matching attempts"""
    driver_name = serializers.SerializerMethodField()
    driver_phone = serializers.CharField(source='driver.phone', read_only=True)
    driver_rating = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()
    driver_score = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = RideMatching
        fields = [
            'id', 'ride_request', 'driver', 'driver_name', 'driver_phone',
            'driver_rating', 'distance_km', 'estimated_eta_minutes', 
            'matching_score', 'status', 'vehicle_info', 'driver_score',
            'expires_at', 'time_remaining', 'created'
        ]
        read_only_fields = ['id', 'created']
    
    def get_driver_name(self, obj):
        return obj.driver.user.get_user_names

    def get_driver_rating(self, obj):
        from django.db.models import Avg
        ratings = Rating.objects.filter(ride__driver=obj.driver)
        if ratings.exists():
            return round(ratings.aggregate(Avg('rating'))['rating__avg'], 2)
        return 0.0

    def get_vehicle_info(self, obj):
        if obj.driver.vehicle:
            return {
                'id': obj.driver.vehicle.id,
                'name': obj.driver.vehicle.name,
                'type': obj.driver.vehicle.type.name if obj.driver.vehicle.type else None,
                'registration_number': obj.driver.vehicle.registration_number
            }
        return None

    def get_driver_score(self, obj):
        """Get driver's reliability score"""
        try:
            score = obj.driver.score
            return {
                'reliability_score': score.reliability_score,
                'acceptance_rate': score.acceptance_rate,
                'response_time_avg': score.response_time_avg
            }
        except:
            return {
                'reliability_score': 100.0,
                'acceptance_rate': 100.0,
                'response_time_avg': 0.0
            }

    def get_time_remaining(self, obj):
        """Get time remaining until expiration"""
        from django.utils import timezone
        if obj.status in ['accepted', 'declined']:
            return None
        
        remaining = obj.expires_at - timezone.now()
        if remaining.total_seconds() <= 0:
            return 0
        return int(remaining.total_seconds())


class NearbyDriversSerializer(serializers.ModelSerializer):
    """Serializer for finding nearby available drivers"""
    driver_name = serializers.SerializerMethodField()
    driver_phone = serializers.CharField(source='driver.phone', read_only=True)
    driver_rating = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()
    vehicleType = serializers.SerializerMethodField()
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    distance_km = serializers.SerializerMethodField()
    estimated_eta_minutes = serializers.SerializerMethodField()

    class Meta:
        model = DriverLocation
        fields = [
            'id', 'driver', 'driver_name', 'driver_phone', 'driver_rating',
            'latitude', 'longitude', 'address', 'distance_km', 
            'estimated_eta_minutes', 'vehicle_info', 'vehicleType', 'last_updated'
        ]
    
    def get_driver_name(self, obj):
        return obj.driver.user.get_user_names

    def get_driver_rating(self, obj):
        from django.db.models import Avg
        ratings = Rating.objects.filter(ride__driver=obj.driver)
        if ratings.exists():
            return round(ratings.aggregate(Avg('rating'))['rating__avg'], 2)
        return 0.0

    def get_vehicle_info(self, obj):
        if obj.driver.vehicle:
            return {
                'id': obj.driver.vehicle.id,
                'name': obj.driver.vehicle.name,
                'type': obj.driver.vehicle.type.name if obj.driver.vehicle.type else None,
                'registration_number': obj.driver.vehicle.registration_number,
                'is_air_conditioned': obj.driver.vehicle.is_air_conditioned
            }
        return None
    
    def get_vehicleType(self, obj):
        if obj.driver.vehicle and obj.driver.vehicle.type:
            return obj.driver.vehicle.type.name
        return 'Standard Vehicle'  # Default fallback

    def get_distance_km(self, obj):
        # This will be calculated in the view based on client location
        return getattr(obj, 'calculated_distance', None)

    def get_estimated_eta_minutes(self, obj):
        # This will be calculated in the view based on distance and traffic
        return getattr(obj, 'calculated_eta', None)

