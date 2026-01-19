from rest_framework import permissions


class IsDriver(permissions.BasePermission):
    """
    Permission to check if user is a driver
    """
    message = "You must be a driver to perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_driver


class IsClient(permissions.BasePermission):
    """
    Permission to check if user is a client
    """
    message = "You must be a client to perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_client


class IsDriverOrClient(permissions.BasePermission):
    """
    Permission to check if user is either a driver or client
    """
    message = "You must be either a driver or client to perform this action."

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_driver or request.user.is_client)
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is the owner based on object type
        if hasattr(obj, 'client'):
            return obj.client.user == request.user
        elif hasattr(obj, 'driver'):
            return obj.driver.user == request.user
        
        return False


class IsRideParticipant(permissions.BasePermission):
    """
    Permission to check if user is a participant (driver or client) in the ride
    """
    message = "You must be a participant in this ride to perform this action."

    def has_object_permission(self, request, view, obj):
        # For Ride objects
        if hasattr(obj, 'driver') and hasattr(obj, 'client'):
            return (
                (obj.driver and obj.driver.user == request.user) or
                (obj.client and obj.client.user == request.user)
            )
        
        # For RideRequest objects
        if hasattr(obj, 'client'):
            if request.user.is_client:
                try:
                    return obj.client.user == request.user
                except:
                    return False
            elif request.user.is_driver:
                # Drivers can view and accept any pending ride request
                return True
        
        return False


class CanAcceptRideRequest(permissions.BasePermission):
    """
    Permission to check if a driver can accept a ride request
    """
    message = "Only verified and active drivers can accept ride requests."

    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.is_driver:
            return False
        
        try:
            driver_profile = request.user.diver_profile
            return driver_profile.is_verified and driver_profile.is_active and not driver_profile.is_banned
        except:
            return False

    def has_object_permission(self, request, view, obj):
        # Check if ride request is still pending
        if hasattr(obj, 'status'):
            return obj.status == 'Pending'
        return False


class CanCancelRideRequest(permissions.BasePermission):
    """
    Permission to check if a user can cancel a ride request
    """
    message = "You can only cancel your own ride requests or accepted rides."

    def has_object_permission(self, request, view, obj):
        # Clients can cancel their own requests if pending or accepted
        if request.user.is_client:
            try:
                if obj.client.user == request.user:
                    return obj.status in ['Pending', 'Accepted']
            except:
                return False
        
        # Drivers can cancel accepted rides
        if request.user.is_driver:
            try:
                if obj.driver and obj.driver.user == request.user:
                    return obj.status == 'Accepted'
            except:
                return False
        
        return False


class CanRateRide(permissions.BasePermission):
    """
    Permission to check if a client can rate a ride
    """
    message = "Only clients who completed a ride can rate it."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client

    def has_object_permission(self, request, view, obj):
        # For Rating objects
        if hasattr(obj, 'ride'):
            ride = obj.ride
            try:
                return (
                    ride.client.user == request.user and
                    ride.end_time is not None  # Ride must be completed
                )
            except:
                return False
        
        # For Ride objects (when creating a rating)
        if hasattr(obj, 'client'):
            try:
                return (
                    obj.client.user == request.user and
                    obj.end_time is not None
                )
            except:
                return False
        
        return False


class CanProvideFeedback(permissions.BasePermission):
    """
    Permission to check if a client can provide feedback
    """
    message = "Only clients can provide feedback on completed rides."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client

    def has_object_permission(self, request, view, obj):
        # For FeedBack objects
        if hasattr(obj, 'ride'):
            ride = obj.ride
            try:
                return ride.client.user == request.user
            except:
                return False
        
        return False


class IsVehicleOwner(permissions.BasePermission):
    """
    Permission to check if user owns the vehicle
    """
    message = "You must be the owner of this vehicle."

    def has_object_permission(self, request, view, obj):
        # Check if the user is a driver and owns the vehicle
        if request.user.is_driver:
            try:
                driver_profile = request.user.diver_profile
                return obj.driverprofile_set.filter(id=driver_profile.id).exists()
            except:
                return False
        return False


class IsDriverOnline(permissions.BasePermission):
    """
    Permission to check if driver is online and available
    """
    message = "You must be online to accept ride requests."

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_driver:
            try:
                driver_profile = request.user.diver_profile
                return driver_profile.is_online and driver_profile.is_active
            except:
                return False
        return False

