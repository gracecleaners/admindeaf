"""
Web Views for RideNow
All function-based views for web interface
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib.gis.geos import Point

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import RideRequest, Ride, Rating, FeedBack, Vehicle, RideMatching, Route
from .forms import (
    RideRequestForm, RatingForm, FeedBackForm,
    RideRequestAcceptForm, RideSearchForm
)
from accounts.models import DriverProfile, ClientProfile

User = get_user_model()


def get_user_from_request(request):
    """
    Get user from request using either JWT token or Django session authentication
    """
    # First try Django session authentication
    if request.user.is_authenticated:
        return request.user
    
    # Try JWT token authentication
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            # Use DRF SimpleJWT to validate the access token
            access_token = AccessToken(token)
            user_id = access_token.payload.get('user_id')
            if user_id:
                return User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            pass
    
    # Try refresh token from cookies
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            user_id = token.payload.get('user_id')
            if user_id:
                return User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            pass
    
    return None


def jwt_or_session_required(view_func):
    """
    Decorator that allows access with either JWT token or Django session authentication
    """
    def wrapper(request, *args, **kwargs):
        user = get_user_from_request(request)
        
        if user:
            request.user = user
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to login if no valid authentication
            return redirect('login')
    return wrapper

# ==================== HOME & LANDING ====================

def home(request):
    """Home page view"""
    context = {
        'message': 'Welcome to RideNow',
        'total_rides': Ride.objects.count(),
        'active_drivers': DriverProfile.objects.filter(is_online=True, is_active=True).count(),
        'total_clients': ClientProfile.objects.count(),
    }
    return render(request, 'rides/landing_page.html', context)


# ==================== RIDE REQUESTS ====================

@login_required
def request_ride(request):
    """Create a new ride request"""
    if not request.user.is_client:
        messages.error(request, "Only clients can request rides.")
        return redirect('rides:home')
    
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        messages.error(request, "You must have a client profile to request rides.")
        return redirect('rides:home')
    
    if request.method == 'POST':
        form = RideRequestForm(request.POST, user=request.user)
        if form.is_valid():
            ride_request = form.save(commit=False)
            ride_request.client = client_profile
            ride_request.save()
            messages.success(request, "Your ride request has been submitted successfully!")
            return redirect('rides:ride_requests')
    else:
        form = RideRequestForm(user=request.user)
    
    return render(request, 'rides/ride_request.html', {'form': form})


@login_required
def ride_request_list(request):
    """List all ride requests for the user"""
    # Get base queryset
    ride_requests = RideRequest.objects.all().order_by('-requested_at')
    
    # Filter based on user type
    if request.user.is_client:
        try:
            ride_requests = ride_requests.filter(client=request.user.client_profile)
        except ClientProfile.DoesNotExist:
            ride_requests = ride_requests.none()
    elif request.user.is_driver:
        try:
            driver_profile = request.user.driver_profile
            # Show pending requests and driver's own requests
            ride_requests = ride_requests.filter(
                Q(status='Pending') | Q(driver=driver_profile)
            )
        except DriverProfile.DoesNotExist:
            ride_requests = ride_requests.filter(status='Pending')
    
    # Apply search filters
    search_form = RideSearchForm(request.GET)
    if search_form.is_valid():
        start_location = search_form.cleaned_data.get('start_location')
        end_location = search_form.cleaned_data.get('end_location')
        status_filter = search_form.cleaned_data.get('status')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if start_location:
            ride_requests = ride_requests.filter(start_location__icontains=start_location)
        if end_location:
            ride_requests = ride_requests.filter(end_location__icontains=end_location)
        if status_filter:
            ride_requests = ride_requests.filter(status=status_filter)
        if date_from:
            ride_requests = ride_requests.filter(requested_at__gte=date_from)
        if date_to:
            ride_requests = ride_requests.filter(requested_at__lte=date_to)
    
    # Pagination
    paginator = Paginator(ride_requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'ride_requests': page_obj,
        'search_form': search_form,
        'page_obj': page_obj,
    }
    return render(request, 'rides/ride_request_list.html', context)


@login_required
def ride_request_detail(request, pk):
    """View details of a specific ride request"""
    ride_request = get_object_or_404(RideRequest, pk=pk)
    
    # Check if user has permission to view this ride request
    can = False
    if request.user.is_client:
        try:
            can = ride_request.client.user == request.user
        except:
            pass
    elif request.user.is_driver:
        try:
            can = (ride_request.status == 'Pending' or 
                       (ride_request.driver and ride_request.driver.user == request.user))
        except:
            pass
    
    if not can and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this ride request.")
        return redirect('rides:ride_requests')
    
    context = {
        'ride_request': ride_request,
    }
    
    # Add accept form for drivers if ride is pending
    if request.user.is_driver and ride_request.status == 'Pending':
        try:
            driver_profile = request.user.driver_profile
            context['accept_form'] = RideRequestAcceptForm(driver=driver_profile)
        except DriverProfile.DoesNotExist:
            pass
    
    return render(request, 'rides/ride_request_detail.html', context)


@login_required
def accept_ride_request(request, pk):
    """Driver accepts a ride request"""
    if not request.user.is_driver:
        messages.error(request, "Only drivers can accept ride requests.")
        return redirect('rides:ride_requests')
    
    ride_request = get_object_or_404(RideRequest, pk=pk, status='Pending')
    
    try:
        driver_profile = request.user.driver_profile
    except DriverProfile.DoesNotExist:
        messages.error(request, "Driver profile not found.")
        return redirect('rides:ride_requests')
    
    if request.method == 'POST':
        form = RideRequestAcceptForm(request.POST, driver=driver_profile)
        if form.is_valid():
            ride_request.driver = driver_profile
            ride_request.vehicle = form.cleaned_data['vehicle']
            ride_request.status = 'Accepted'
            ride_request.save()
            messages.success(request, "Ride request accepted successfully!")
            return redirect('rides:ride_request_detail', pk=pk)
    else:
        form = RideRequestAcceptForm(driver=driver_profile)
    
    return render(request, 'rides/accept_ride_request.html', {
        'form': form,
        'ride_request': ride_request
    })


@login_required
def cancel_ride_request(request, pk):
    """Cancel a ride request"""
    ride_request = get_object_or_404(RideRequest, pk=pk)
    
    # Check permissions
    can_cancel = False
    if request.user.is_client:
        try:
            if ride_request.client.user == request.user and ride_request.status in ['Pending', 'Accepted']:
                can_cancel = True
        except:
            pass
    elif request.user.is_driver:
        try:
            if ride_request.driver and ride_request.driver.user == request.user and ride_request.status == 'Accepted':
                can_cancel = True
        except:
            pass
    
    if not can_cancel:
        messages.error(request, "You don't have permission to cancel this ride request.")
        return redirect('rides:ride_requests')
    
    if request.method == 'POST':
        ride_request.status = 'Cancelled'
        ride_request.save()
        messages.success(request, "Ride request cancelled successfully.")
        return redirect('rides:ride_requests')
    
    return render(request, 'rides/cancel_ride_request.html', {
        'ride_request': ride_request
    })


@login_required
def complete_ride(request, pk):
    """Mark a ride as completed"""
    if not request.user.is_driver:
        messages.error(request, "Only drivers can mark rides as completed.")
        return redirect('rides:ride_requests')
    
    ride_request = get_object_or_404(RideRequest, pk=pk, status='Accepted')
    
    try:
        if ride_request.driver.user != request.user:
            messages.error(request, "You can only complete your own rides.")
            return redirect('rides:ride_requests')
    except:
        messages.error(request, "Invalid ride request.")
        return redirect('rides:ride_requests')
    
    if request.method == 'POST':
        ride_request.status = 'Completed'
        ride_request.save()
        messages.success(request, "Ride marked as completed!")
        return redirect('rides:ride_request_detail', pk=pk)
    
    return render(request, 'rides/complete_ride.html', {
        'ride_request': ride_request
    })


# ==================== RIDE TRACKING & HISTORY ====================

@login_required
def track_ride(request, ride_id):
    """Track a ride in real-time"""
    ride_request = get_object_or_404(RideRequest, pk=ride_id)
    
    # Check if user has permission to track this ride
    can_track = False
    if request.user.is_client:
        try:
            can_track = ride_request.client.user == request.user
        except:
            pass
    elif request.user.is_driver:
        try:
            can_track = ride_request.driver and ride_request.driver.user == request.user
        except:
            pass
    
    if not can_track and not request.user.is_staff:
        messages.error(request, "You don't have permission to track this ride.")
        return redirect('rides:ride_requests')
    
    context = {
        'ride_request': ride_request,
        'api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    return render(request, 'rides/track_ride.html', context)


@login_required
def ride_history(request):
    """View ride history"""
    rides = Ride.objects.all().order_by('-created')
    
    # Filter based on user type
    if request.user.is_client:
        try:
            rides = rides.filter(client=request.user.client_profile)
        except ClientProfile.DoesNotExist:
            rides = rides.none()
    elif request.user.is_driver:
        try:
            rides = rides.filter(driver=request.user.driver_profile)
        except DriverProfile.DoesNotExist:
            rides = rides.none()
    
    # Pagination
    paginator = Paginator(rides, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'rides': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'rides/ride_history.html', context)


# ==================== RATING & FEEDBACK ====================

@login_required
def rate_ride(request, pk):
    """Rate a completed ride"""
    if not request.user.is_client:
        messages.error(request, "Only clients can rate rides.")
        return redirect('rides:ride_requests')
    
    ride_request = get_object_or_404(RideRequest, pk=pk, status='Completed')
    
    try:
        client_profile = request.user.client_profile
        if ride_request.client != client_profile:
            messages.error(request, "You can only rate your own rides.")
            return redirect('rides:ride_requests')
    except ClientProfile.DoesNotExist:
        messages.error(request, "Client profile not found.")
        return redirect('rides:ride_requests')
    
    # Check if already rated
    if ride_request.ride and Rating.objects.filter(ride=ride_request.ride, client=client_profile).exists():
        messages.info(request, "You have already rated this ride.")
        return redirect('rides:ride_request_detail', pk=pk)
    
    if request.method == 'POST':
        rating_form = RatingForm(request.POST, ride=ride_request.ride, client=client_profile)
        feedback_form = FeedBackForm(request.POST, ride=ride_request.ride, client=client_profile)
        
        if rating_form.is_valid():
            rating = rating_form.save()
            
            if feedback_form.is_valid():
                feedback = feedback_form.save(commit=False)
                feedback.rating = rating
                feedback.save()
            
            messages.success(request, "Thank you for your feedback!")
            return redirect('rides:ride_request_detail', pk=pk)
    else:
        rating_form = RatingForm(ride=ride_request.ride, client=client_profile)
        feedback_form = FeedBackForm(ride=ride_request.ride, client=client_profile)
    
    context = {
        'ride_request': ride_request,
        'rating_form': rating_form,
        'feedback_form': feedback_form,
    }
    return render(request, 'rides/rate_ride.html', context)


# ==================== MAP VIEW ====================

@login_required
def map(request):
    """Display Google Maps view for ride booking"""
    context = {
        'api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    return render(request, 'rides/map.html', context)


# ==================== DASHBOARD/STATISTICS ====================

@login_required
def dashboard(request):
    """User dashboard with statistics"""
    context = {}

    # Check if this is an AJAX request for authentication check
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_client': request.user.is_client,
            'is_driver': request.user.is_driver,
            'user_id': request.user.id,
            'username': request.user.username
        })

    if request.user.is_client:
        try:
            client_profile = request.user.client_profile
            context['total_rides'] = Ride.objects.filter(client=client_profile).count()
            context['pending_requests'] = RideRequest.objects.filter(client=client_profile, status='Pending').count()
            context['completed_rides'] = RideRequest.objects.filter(client=client_profile, status='Completed').count()
            context['cancelled_rides'] = RideRequest.objects.filter(client=client_profile, status='Cancelled').count()
            context['ratings_given'] = Rating.objects.filter(client=client_profile).count()
            context['user_type'] = 'client'
        except ClientProfile.DoesNotExist:
            messages.error(request, "Client profile not found.")
            return redirect('rides:home')
    
    elif request.user.is_driver:
        try:
            driver_profile = request.user.driver_profile
            from django.db.models import Avg
            
            context['total_rides'] = Ride.objects.filter(driver=driver_profile).count()
            context['completed_rides'] = RideRequest.objects.filter(driver=driver_profile, status='Completed').count()
            context['cancelled_rides'] = RideRequest.objects.filter(driver=driver_profile, status='Cancelled').count()
            
            ratings = Rating.objects.filter(ride__driver=driver_profile)
            context['average_rating'] = ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0
            context['total_ratings'] = ratings.count()
            context['user_type'] = 'driver'
        except DriverProfile.DoesNotExist:
            messages.error(request, "Driver profile not found.")
            return redirect('rides:home')
    else:
        messages.error(request, "Invalid user type.")
        return redirect('rides:home')
    
    return render(request, 'rides/dashboard.html', context)

@login_required
def driver_dashboard(request):
    """Driver dashboard for managing ride requests and status"""
    # Check if this is an AJAX request for authentication check
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_client': request.user.is_client,
            'is_driver': request.user.is_driver,
            'user_id': request.user.id,
            'username': request.user.username
        })
    
    if not request.user.is_driver:
        messages.error(request, "Only drivers can access this page.")
        return redirect('rides:dashboard')
    
    try:
        driver_profile = request.user.driver_profile
    except DriverProfile.DoesNotExist:
        messages.error(request, "Driver profile not found.")
        return redirect('rides:dashboard')
    
    # Get driver statistics
    from django.db.models import Avg
    total_rides = RideRequest.objects.filter(driver=driver_profile).count()
    completed_rides = RideRequest.objects.filter(driver=driver_profile, status='Completed').count()
    cancelled_rides = RideRequest.objects.filter(driver=driver_profile, status='Cancelled').count()
    
    # Calculate average rating
    ratings = Rating.objects.filter(ride__driver=driver_profile)
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0
    
    # Get current active ride
    active_ride = RideRequest.objects.filter(
        driver=driver_profile,
        status__in=['Accepted', 'In Progress']
    ).first()
    
    # Get pending ride matches (rides waiting for driver response)
    from .models import RideMatching
    pending_matches = RideMatching.objects.filter(
        driver=driver_profile,
        status='pending',
        created__gte=timezone.now() - timezone.timedelta(minutes=10)  # Only recent matches
    ).select_related('ride_request', 'ride_request__client', 'ride_request__client__user')
    
    # Check driver availability status
    from .models import DriverLocation
    driver_location = DriverLocation.objects.filter(driver=driver_profile).first()
    is_online = driver_location.is_online if driver_location else False
    is_available = driver_location.is_available if driver_location else False
    
    context = {
        'driver_profile': driver_profile,
        'total_rides': total_rides,
        'completed_rides': completed_rides,
        'cancelled_rides': cancelled_rides,
        'average_rating': average_rating,
        'active_ride': active_ride,
        'pending_matches': pending_matches,
        'is_online': is_online,
        'is_available': is_available,
        'driver_location': driver_location,
    }
    
    return render(request, 'rides/driver_dashboard.html', context)


def driver_navigation(request, ride_id=None):
    """
    Driver navigation interface with GPS tracking and turn-by-turn directions
    """
    context = {
        'ride_id': ride_id,
        'mapbox_token': settings.MAPBOX_ACCESS_TOKEN,
    }
    
    if ride_id:
        try:
            # Get the specific ride for navigation
            # ride_match = RideMatching.objects.select_related(
            #     'ride_request', 'driver', 'driver__user'
            # ).get(
            #     id=ride_id,
            #     driver=request.user.driver_profile,
            #     status__in=['accepted', 'driver_arrived', 'ride_started']
            # )

            ride_match = RideMatching.objects.get(
                id=ride_id,
                driver=request.user.driver_profile,
            )
            
            # Get coordinates from route if available
            pickup_coords = None
            destination_coords = None
            
            if hasattr(ride_match.ride_request, 'route') and ride_match.ride_request.route:
                route = ride_match.ride_request.route
                pickup_coords = f"{route.pickup_location.x},{route.pickup_location.y}"
                destination_coords = f"{route.destination.x},{route.destination.y}"
                print(f"Route coordinates found: pickup={pickup_coords}, destination={destination_coords}")
            else:
                print(f"No route found for ride request {ride_match.ride_request.id}")
                # Fallback: Try to create a route from the addresses if coordinates are missing
                # This is a temporary solution for rides created before Route model was added
                try:
                    from geopy.geocoders import Nominatim
                    geolocator = Nominatim(user_agent="RideNow")
                    
                    # Try to geocode the addresses
                    pickup_location = geolocator.geocode(ride_match.ride_request.start_location, timeout=10)
                    destination_location = geolocator.geocode(ride_match.ride_request.end_location, timeout=10)
                    
                    if pickup_location and destination_location:
                        # Create a new route object
                        route = Route.objects.create(
                            pickup_location=Point(pickup_location.longitude, pickup_location.latitude, srid=4326),
                            destination=Point(destination_location.longitude, destination_location.latitude, srid=4326),
                            eta=timezone.now() + timezone.timedelta(minutes=30)
                        )
                        
                        # Link the route to the ride request
                        ride_match.ride_request.route = route
                        ride_match.ride_request.save()
                        
                        pickup_coords = f"{route.pickup_location.x},{route.pickup_location.y}"
                        destination_coords = f"{route.destination.x},{route.destination.y}"
                        print(f"Created fallback route: pickup={pickup_coords}, destination={destination_coords}")
                    else:
                        print(f"Could not geocode addresses: pickup={ride_match.ride_request.start_location}, destination={ride_match.ride_request.end_location}")
                except Exception as e:
                    print(f"Error creating fallback route: {str(e)}")
            
            context.update({
                'ride_match': ride_match,
                'ride_request': ride_match.ride_request,
                'passenger': ride_match.ride_request.client.user,
                'pickup_location': ride_match.ride_request.start_location,
                'destination': ride_match.ride_request.end_location,
                'pickup_coords': pickup_coords,
                'destination_coords': destination_coords,
                'current_status': ride_match.status,
            })
            print(context)
        except RideMatching.DoesNotExist:
            messages.error(request, 'Ride not found or not accessible.')
            return redirect('rides:driver_dashboard')
    else:
        # Get the current active ride for this driver
        active_ride = RideMatching.objects.select_related(
            'ride_request', 'ride_request__client', 'ride_request__client__user'
        ).filter(
            driver=request.user.driver_profile,
            status__in=['accepted', 'driver_arrived', 'ride_started']
        ).first()
        
        if active_ride:
            # Get coordinates from route if available
            pickup_coords = None
            destination_coords = None
            
            if hasattr(active_ride.ride_request, 'route') and active_ride.ride_request.route:
                route = active_ride.ride_request.route
                pickup_coords = f"{route.pickup_location.x},{route.pickup_location.y}"
                destination_coords = f"{route.destination.x},{route.destination.y}"
                print(f"Active ride route coordinates found: pickup={pickup_coords}, destination={destination_coords}")
            else:
                print(f"No route found for active ride request {active_ride.ride_request.id}")
                # Fallback: Try to create a route from the addresses if coordinates are missing
                try:
                    from geopy.geocoders import Nominatim
                    geolocator = Nominatim(user_agent="RideNow")
                    
                    # Try to geocode the addresses
                    pickup_location = geolocator.geocode(active_ride.ride_request.start_location, timeout=10)
                    destination_location = geolocator.geocode(active_ride.ride_request.end_location, timeout=10)
                    
                    if pickup_location and destination_location:
                        # Create a new route object
                        route = Route.objects.create(
                            pickup_location=Point(pickup_location.longitude, pickup_location.latitude, srid=4326),
                            destination=Point(destination_location.longitude, destination_location.latitude, srid=4326),
                            eta=timezone.now() + timezone.timedelta(minutes=30)
                        )
                        
                        # Link the route to the ride request
                        active_ride.ride_request.route = route
                        active_ride.ride_request.save()
                        
                        pickup_coords = f"{route.pickup_location.x},{route.pickup_location.y}"
                        destination_coords = f"{route.destination.x},{route.destination.y}"
                        print(f"Created fallback route for active ride: pickup={pickup_coords}, destination={destination_coords}")
                    else:
                        print(f"Could not geocode addresses for active ride: pickup={active_ride.ride_request.start_location}, destination={active_ride.ride_request.end_location}")
                except Exception as e:
                    print(f"Error creating fallback route for active ride: {str(e)}")
            
            context.update({
                'ride_match': active_ride,
                'ride_request': active_ride.ride_request,
                'passenger': active_ride.ride_request.client.user,
                'pickup_location': active_ride.ride_request.start_location,
                'destination': active_ride.ride_request.end_location,
                'pickup_coords': pickup_coords,
                'destination_coords': destination_coords,
                'current_status': active_ride.status,
            })
    
    return render(request, 'rides/driver_navigation.html', context)


# ==================== RIDE BOOKING ====================

def book_ride(request):
    """Full-featured ride booking page with interactive map"""
    context = {
        'page_title': 'Book a Ride',
    }
    return render(request, 'rides/ride.html', context)


@login_required
def user_rides(request):
    """User's ride history and active rides"""
    if not request.user.is_client:
        messages.error(request, "Only clients can view ride history.")
        return redirect('rides:home')
    
    try:
        client_profile = request.user.client_profile
        rides = RideRequest.objects.filter(client=client_profile).order_by('-created')
        
        # Paginate results
        paginator = Paginator(rides, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'rides': page_obj,
            'active_rides': rides.filter(status__in=['Pending', 'Accepted', 'In Progress']),
            'completed_rides': rides.filter(status='Completed').count(),
            'cancelled_rides': rides.filter(status='Cancelled').count(),
        }
        return render(request, 'rides/user_rides.html', context)
    except ClientProfile.DoesNotExist:
        messages.error(request, "Client profile not found.")
        return redirect('rides:home')
