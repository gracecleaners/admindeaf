from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .models import RideRequest, Ride, Rating, FeedBack


@receiver(post_save, sender=RideRequest)
def ride_request_status_changed(sender, instance, created, **kwargs):
    """
    Signal to handle ride request status changes and create rides
    """
    if created:
        # New ride request created - could send notification to nearby drivers
        print(f"New ride request #{instance.id} created by {instance.client.username}")
        # TODO: Implement notification system to alert nearby drivers
        # Example: send_notification_to_nearby_drivers(instance)
    else:
        # Existing ride request updated
        if instance.status == 'Accepted' and instance.driver:
            # Driver accepted the ride - create actual Ride object if not exists
            if not instance.ride:
                ride = Ride.objects.create(
                    driver=instance.driver,
                    client=instance.client,
                    vehicle=instance.vehicle,
                    route=None,  # Will be set if route exists
                    start_location=instance.start_location,
                    end_location=instance.end_location,
                    start_time=timezone.now(),
                    end_time=timezone.now() + timezone.timedelta(hours=1)  # Estimated end time
                )
                instance.ride = ride
                instance.save()
                
                print(f"Ride #{ride.id} created from accepted request #{instance.id}")
                # TODO: Send notification to client that driver accepted
                # Example: notify_client_ride_accepted(instance.client, instance.driver)
        
        elif instance.status == 'Completed' and instance.ride:
            # Ride completed - update ride end_time and process payment
            if instance.ride:
                instance.ride.end_time = timezone.now()
                instance.ride.save()
                print(f"Ride #{instance.ride.id} marked as completed")
                
                # Process wallet transfer from client to driver
                try:
                    process_ride_payment(instance)
                except Exception as e:
                    print(f"Error processing payment for ride #{instance.ride.id}: {str(e)}")
                
                # TODO: Send notification to request rating/feedback
                # Example: request_rating_from_client(instance.client, instance.ride)
        
        elif instance.status == 'Cancelled':
            # Ride cancelled
            print(f"Ride request #{instance.id} cancelled")
            # TODO: Send cancellation notifications
            # Example: notify_cancellation(instance)


@receiver(post_save, sender=Ride)
def ride_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal to handle ride creation and updates
    """
    if created:
        print(f"New ride #{instance.id} started")
        # TODO: Implement real-time tracking initialization
        # Example: initialize_ride_tracking(instance)
    else:
        # Check if ride ended
        if instance.end_time and instance.end_time <= timezone.now():
            print(f"Ride #{instance.id} ended")
            # TODO: Send notification to client to rate the ride
            # Example: prompt_rating(instance.client, instance)


@receiver(post_save, sender=Rating)
def rating_created(sender, instance, created, **kwargs):
    """
    Signal to handle rating creation
    """
    if created:
        print(f"New rating created for ride #{instance.ride.id}: {instance.rating} stars")
        # TODO: Update driver's average rating
        # TODO: Send thank you notification to client
        # Example: update_driver_rating(instance.ride.driver)


@receiver(post_save, sender=FeedBack)
def feedback_created(sender, instance, created, **kwargs):
    """
    Signal to handle feedback creation
    """
    if created:
        print(f"New feedback created for ride #{instance.ride.id}")
        # TODO: Analyze feedback sentiment
        # TODO: Flag negative feedback for admin review
        # Example: analyze_feedback_sentiment(instance)


@receiver(pre_save, sender=RideRequest)
def validate_ride_request_status_transition(sender, instance, **kwargs):
    """
    Validate status transitions for ride requests
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = RideRequest.objects.get(pk=instance.pk)
            old_status = old_instance.status
            new_status = instance.status
            
            # Define valid status transitions
            valid_transitions = {
                'Pending': ['Accepted', 'Cancelled'],
                'Accepted': ['Completed', 'Cancelled'],
                'Completed': [],  # Cannot transition from completed
                'Cancelled': []   # Cannot transition from cancelled
            }
            
            # Check if transition is valid
            if new_status != old_status:
                if new_status not in valid_transitions.get(old_status, []):
                    print(f"Invalid status transition from {old_status} to {new_status}")
                    # Optionally raise an exception
                    # raise ValueError(f"Cannot transition from {old_status} to {new_status}")
                else:
                    print(f"Status transition: {old_status} -> {new_status}")
        except RideRequest.DoesNotExist:
            pass


# Helper functions for notifications (to be implemented with your notification system)

def send_notification_to_nearby_drivers(ride_request):
    """
    Send push notification to nearby available drivers
    """
    # TODO: Implement using your notification system (FCM, etc.)
    pass


def notify_client_ride_accepted(client, driver):
    """
    Notify client that their ride has been accepted
    """
    # TODO: Implement notification
    pass


def request_rating_from_client(client, ride):
    """
    Ask client to rate their completed ride
    """
    # TODO: Implement notification
    pass


def notify_cancellation(ride_request):
    """
    Notify relevant parties about ride cancellation
    """
    # TODO: Implement notification
    pass


def initialize_ride_tracking(ride):
    """
    Initialize real-time location tracking for the ride
    """
    # TODO: Implement real-time tracking
    pass


def prompt_rating(client, ride):
    """
    Prompt client to rate the ride
    """
    # TODO: Implement notification
    pass


def update_driver_rating(driver):
    """
    Recalculate and update driver's average rating
    """
    from django.db.models import Avg
    ratings = Rating.objects.filter(ride__driver=driver)
    if ratings.exists():
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        print(f"Driver {driver.username} average rating: {avg_rating:.2f}")
        # TODO: Store this in driver profile if you add an average_rating field
    pass


def analyze_feedback_sentiment(feedback):
    """
    Analyze feedback sentiment and flag negative reviews
    """
    # TODO: Implement sentiment analysis
    # TODO: Flag for admin review if negative
    pass


def process_ride_payment(ride_request):
    """
    Process payment transfer from client to driver when ride is completed
    """
    try:
        from finance.models import Ledger
        
        # Calculate ride cost (you may want to store this in the ride request or calculate it)
        # For now, we'll use a default calculation or get it from the ride request
        ride_cost = calculate_ride_cost(ride_request)
        
        client = ride_request.client.user
        driver = ride_request.driver.user
        
        if not client or not driver:
            raise ValueError("Client or driver not found")
        
        with transaction.atomic():
            # Create debit entry for client (money leaving client's wallet)
            Ledger.objects.create(
                user_from=client,
                amount=ride_cost,
                is_debit=True,
                is_valid=True,
                notes=f"Payment for completed ride #{ride_request.id}"
            )
            
            # Create credit entry for driver (money entering driver's wallet)
            Ledger.objects.create(
                user_to=driver,
                amount=ride_cost,
                is_credit=True,
                is_valid=True,
                notes=f"Earnings from completed ride #{ride_request.id}"
            )
            
            print(f"Payment processed: UGX {ride_cost} transferred from {client.username} to {driver.username} for ride #{ride_request.id}")
            
    except Exception as e:
        print(f"Error in process_ride_payment: {str(e)}")
        raise


def calculate_ride_cost(ride_request):
    """
    Calculate the cost of a completed ride
    Uses the stored cost from when the ride was requested
    """
    try:
        # Use the stored cost from the ride request
        if ride_request.cost:
            return ride_request.cost
        
        # Fallback calculation if cost is not stored
        base_price = Decimal('5000.00')  # Default base price
        price_per_km = Decimal('1000.00')  # Default price per km
        
        # If we have vehicle type information, use its pricing
        if ride_request.vehicle and ride_request.vehicle.type:
            vehicle_type = ride_request.vehicle.type
            if hasattr(vehicle_type, 'base_price'):
                base_price = vehicle_type.base_price
            if hasattr(vehicle_type, 'price_per_km'):
                price_per_km = vehicle_type.price_per_km
        
        # Estimate distance (this is simplified - in reality you'd calculate actual distance)
        estimated_distance = Decimal('5.0')  # Default 5km estimate
        
        total_cost = base_price + (estimated_distance * price_per_km)
        print(f"Warning: Using fallback cost calculation for ride #{ride_request.id}: UGX {total_cost}")
        return total_cost
        
    except Exception as e:
        print(f"Error calculating ride cost: {str(e)}")
        # Return a default cost if calculation fails
        return Decimal('5000.00')

