import 'package:hive/hive.dart';
import 'package:json_annotation/json_annotation.dart';

part 'ride_model.g.dart';


// Vehicle Type Model
@HiveType(typeId: 10)
@JsonSerializable()
class VehicleType {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  final String name;
  
  @HiveField(2)
  @JsonKey(name: 'vehicle_type')
  final String? vehicleType;
  
  @HiveField(3)
  final String description;
  
  @HiveField(4)
  @JsonKey(name: 'engine_type')
  final String? engineType;
  
  @HiveField(5)
  @JsonKey(name: 'vehicle_capacity')
  final String? vehicleCapacity;
  
  @HiveField(6)
  @JsonKey(name: 'base_price')
  final double basePrice;
  
  @HiveField(7)
  @JsonKey(name: 'price_per_km')
  final double pricePerKm;
  
  VehicleType({
    required this.id,
    required this.name,
    this.vehicleType,
    required this.description,
    this.engineType,
    this.vehicleCapacity,
    required this.basePrice,
    required this.pricePerKm,
  });
  
  factory VehicleType.fromJson(Map<String, dynamic> json) => 
      _$VehicleTypeFromJson(json);
  
  Map<String, dynamic> toJson() => _$VehicleTypeToJson(this);
}

// Vehicle Model
@HiveType(typeId: 11)
@JsonSerializable()
class Vehicle {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  final VehicleType? type;
  
  @HiveField(2)
  final String name;
  
  @HiveField(3)
  @JsonKey(name: 'registration_number')
  final String registrationNumber;
  
  @HiveField(4)
  final String description;
  
  @HiveField(5)
  @JsonKey(name: 'is_air_conditioned')
  final bool isAirConditioned;
  
  @HiveField(6)
  @JsonKey(name: 'is_insured')
  final bool isInsured;
  
  @HiveField(7)
  final String age;
  
  @HiveField(8)
  @JsonKey(name: 'manufacturing_year')
  final String? manufacturingYear;
  
  Vehicle({
    required this.id,
    this.type,
    required this.name,
    required this.registrationNumber,
    required this.description,
    required this.isAirConditioned,
    required this.isInsured,
    required this.age,
    this.manufacturingYear,
  });
  
  factory Vehicle.fromJson(Map<String, dynamic> json) => 
      _$VehicleFromJson(json);
  
  Map<String, dynamic> toJson() => _$VehicleToJson(this);
}

// Route Model
@HiveType(typeId: 12)
@JsonSerializable()
class Route {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  @JsonKey(name: 'pickup_location')
  final Map<String, dynamic> pickupLocation;
  
  @HiveField(2)
  final Map<String, dynamic> destination;
  
  @HiveField(3)
  final String eta;
  
  @HiveField(4)
  @JsonKey(name: 'is_active')
  final bool isActive;
  
  Route({
    required this.id,
    required this.pickupLocation,
    required this.destination,
    required this.eta,
    required this.isActive,
  });
  
  factory Route.fromJson(Map<String, dynamic> json) => 
      _$RouteFromJson(json);
  
  Map<String, dynamic> toJson() => _$RouteToJson(this);
}

// Ride Model
@HiveType(typeId: 13)
@JsonSerializable()
class Ride {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  final Map<String, dynamic>? driver;
  
  @HiveField(2)
  final Map<String, dynamic>? client;
  
  @HiveField(3)
  final Vehicle? vehicle;
  
  @HiveField(4)
  final Route? route;
  
  @HiveField(5)
  @JsonKey(name: 'start_location')
  final String startLocation;
  
  @HiveField(6)
  @JsonKey(name: 'end_location')
  final String endLocation;
  
  @HiveField(7)
  @JsonKey(name: 'start_time')
  final String startTime;
  
  @HiveField(8)
  @JsonKey(name: 'end_time')
  final String endTime;
  
  @HiveField(9)
  @JsonKey(name: 'is_active')
  final bool isActive;
  
  @HiveField(10)
  final String status;
  
  Ride({
    required this.id,
    this.driver,
    this.client,
    this.vehicle,
    this.route,
    required this.startLocation,
    required this.endLocation,
    required this.startTime,
    required this.endTime,
    required this.isActive,
    required this.status,
  });
  
  factory Ride.fromJson(Map<String, dynamic> json) => 
      _$RideFromJson(json);
  
  Map<String, dynamic> toJson() => _$RideToJson(this);
}

// Ride Request Model
@HiveType(typeId: 14)
@JsonSerializable()
class RideRequest {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  final Map<String, dynamic>? client;
  
  @HiveField(2)
  final Map<String, dynamic>? driver;
  
  @HiveField(3)
  final Vehicle? vehicle;
  
  @HiveField(4)
  final Route? route;
  
  @HiveField(5)
  @JsonKey(name: 'start_location')
  final String startLocation;
  
  @HiveField(6)
  @JsonKey(name: 'end_location')
  final String endLocation;
  
  @HiveField(7)
  @JsonKey(name: 'requested_at')
  final String? requestedAt;
  
  @HiveField(8)
  final String? status; // Pending, Accepted, Completed, Cancelled
  
  @HiveField(9)
  final Ride? ride;
  
  @HiveField(10)
  final double? cost;
  
  @HiveField(11)
  @JsonKey(name: 'expires_at')
  final String? expiresAt;
  
  @HiveField(12)
  @JsonKey(name: 'matching_started_at')
  final String? matchingStartedAt;
  
  @HiveField(13)
  @JsonKey(name: 'driver_confirmed_at')
  final String? driverConfirmedAt;
  
  @HiveField(14)
  @JsonKey(name: 'pickup_eta')
  final String? pickupEta;
  
  @HiveField(15)
  @JsonKey(name: 'potential_drivers')
  final List<dynamic>? potentialDrivers;
  
  @HiveField(16)
  @JsonKey(name: 'current_driver_index')
  final int currentDriverIndex;
  
  RideRequest({
    required this.id,
    this.client,
    this.driver,
    this.vehicle,
    this.route,
    required this.startLocation,
    required this.endLocation,
    this.requestedAt,
    this.status,
    this.ride,
    this.cost,
    this.expiresAt,
    this.matchingStartedAt,
    this.driverConfirmedAt,
    this.pickupEta,
    this.potentialDrivers,
    this.currentDriverIndex = 0,
  });
  
  factory RideRequest.fromJson(Map<String, dynamic> json) => 
      _$RideRequestFromJson(json);
  
  Map<String, dynamic> toJson() => _$RideRequestToJson(this);
  
  bool get isPending => status == 'Pending';
  bool get isAccepted => status == 'Accepted';
  bool get isCompleted => status == 'Completed';
  bool get isCancelled => status == 'Cancelled';
}

// Ride Matching Model
@HiveType(typeId: 15)
@JsonSerializable()
class RideMatching {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  @JsonKey(name: 'ride_request')
  final RideRequest rideRequest;
  
  @HiveField(2)
  final Map<String, dynamic> driver;
  
  @HiveField(3)
  @JsonKey(name: 'distance_km')
  final double distanceKm;
  
  @HiveField(4)
  @JsonKey(name: 'estimated_eta_minutes')
  final int estimatedEtaMinutes;
  
  @HiveField(5)
  @JsonKey(name: 'matching_score')
  final double matchingScore;
  
  @HiveField(6)
  final String status; // pending, accepted, declined, expired, timeout
  
  @HiveField(7)
  @JsonKey(name: 'expires_at')
  final String expiresAt;
  
  @HiveField(8)
  @JsonKey(name: 'responded_at')
  final String? respondedAt;
  
  @HiveField(9)
  @JsonKey(name: 'response_time_seconds')
  final int? responseTimeSeconds;
  
  RideMatching({
    required this.id,
    required this.rideRequest,
    required this.driver,
    required this.distanceKm,
    required this.estimatedEtaMinutes,
    required this.matchingScore,
    required this.status,
    required this.expiresAt,
    this.respondedAt,
    this.responseTimeSeconds,
  });
  
  factory RideMatching.fromJson(Map<String, dynamic> json) => 
      _$RideMatchingFromJson(json);
  
  Map<String, dynamic> toJson() => _$RideMatchingToJson(this);
  
  bool get isPending => status == 'pending';
  bool get isAccepted => status == 'accepted';
  bool get isDeclined => status == 'declined';
  bool get isExpired => status == 'expired';
  bool get isTimeout => status == 'timeout';
}

// Driver Location Model
@HiveType(typeId: 16)
@JsonSerializable()
class DriverLocation {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  final Map<String, dynamic> driver;
  
  @HiveField(2)
  final Map<String, dynamic> location; // GeoJSON Point
  
  @HiveField(3)
  final String? address;
  
  @HiveField(4)
  @JsonKey(name: 'is_online')
  final bool isOnline;
  
  @HiveField(5)
  @JsonKey(name: 'on_active_ride')
  final bool onActiveRide;
  
  @HiveField(6)
  @JsonKey(name: 'is_available')
  final bool isAvailable;
  
  @HiveField(7)
  @JsonKey(name: 'last_updated')
  final String lastUpdated;
  
  DriverLocation({
    required this.id,
    required this.driver,
    required this.location,
    this.address,
    required this.isOnline,
    required this.onActiveRide,
    required this.isAvailable,
    required this.lastUpdated,
  });
  
  factory DriverLocation.fromJson(Map<String, dynamic> json) => 
      _$DriverLocationFromJson(json);
  
  Map<String, dynamic> toJson() => _$DriverLocationToJson(this);
  
  double get latitude {
    if (location.containsKey('coordinates')) {
      return location['coordinates'][1];
    }
    return 0.0;
  }
  
  double get longitude {
    if (location.containsKey('coordinates')) {
      return location['coordinates'][0];
    }
    return 0.0;
  }
}

// Rating Model
@HiveType(typeId: 17)
@JsonSerializable()
class Rating {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  final Map<String, dynamic>? ride;
  
  @HiveField(2)
  final Map<String, dynamic>? client;
  
  @HiveField(3)
  final int rating;
  
  @HiveField(4)
  final String created;
  
  Rating({
    required this.id,
    this.ride,
    this.client,
    required this.rating,
    required this.created,
  });
  
  factory Rating.fromJson(Map<String, dynamic> json) => 
      _$RatingFromJson(json);
  
  Map<String, dynamic> toJson() => _$RatingToJson(this);
}

// Feedback Model
@HiveType(typeId: 18)
@JsonSerializable()
class Feedback {
  @HiveField(0)
  final int id;
  
  @HiveField(1)
  final Map<String, dynamic>? client;
  
  @HiveField(2)
  final Map<String, dynamic>? ride;
  
  @HiveField(3)
  final String message;
  
  @HiveField(4)
  final Rating? rating;
  
  @HiveField(5)
  final String created;
  
  Feedback({
    required this.id,
    this.client,
    this.ride,
    required this.message,
    this.rating,
    required this.created,
  });
  
  factory Feedback.fromJson(Map<String, dynamic> json) => 
      _$FeedbackFromJson(json);
  
  Map<String, dynamic> toJson() => _$FeedbackToJson(this);
}