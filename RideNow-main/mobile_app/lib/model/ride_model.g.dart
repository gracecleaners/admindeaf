// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ride_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

VehicleType _$VehicleTypeFromJson(Map json) => $checkedCreate(
      'VehicleType',
      json,
      ($checkedConvert) {
        final val = VehicleType(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          name: $checkedConvert('name', (v) => v as String),
          vehicleType: $checkedConvert('vehicle_type', (v) => v as String?),
          description: $checkedConvert('description', (v) => v as String),
          engineType: $checkedConvert('engine_type', (v) => v as String?),
          vehicleCapacity:
              $checkedConvert('vehicle_capacity', (v) => v as String?),
          basePrice:
              $checkedConvert('base_price', (v) => (v as num).toDouble()),
          pricePerKm:
              $checkedConvert('price_per_km', (v) => (v as num).toDouble()),
        );
        return val;
      },
      fieldKeyMap: const {
        'vehicleType': 'vehicle_type',
        'engineType': 'engine_type',
        'vehicleCapacity': 'vehicle_capacity',
        'basePrice': 'base_price',
        'pricePerKm': 'price_per_km'
      },
    );

Map<String, dynamic> _$VehicleTypeToJson(VehicleType instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'vehicle_type': instance.vehicleType,
      'description': instance.description,
      'engine_type': instance.engineType,
      'vehicle_capacity': instance.vehicleCapacity,
      'base_price': instance.basePrice,
      'price_per_km': instance.pricePerKm,
    };

Vehicle _$VehicleFromJson(Map json) => $checkedCreate(
      'Vehicle',
      json,
      ($checkedConvert) {
        final val = Vehicle(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          type: $checkedConvert(
              'type',
              (v) => v == null
                  ? null
                  : VehicleType.fromJson(Map<String, dynamic>.from(v as Map))),
          name: $checkedConvert('name', (v) => v as String),
          registrationNumber:
              $checkedConvert('registration_number', (v) => v as String),
          description: $checkedConvert('description', (v) => v as String),
          isAirConditioned:
              $checkedConvert('is_air_conditioned', (v) => v as bool),
          isInsured: $checkedConvert('is_insured', (v) => v as bool),
          age: $checkedConvert('age', (v) => v as String),
          manufacturingYear:
              $checkedConvert('manufacturing_year', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'registrationNumber': 'registration_number',
        'isAirConditioned': 'is_air_conditioned',
        'isInsured': 'is_insured',
        'manufacturingYear': 'manufacturing_year'
      },
    );

Map<String, dynamic> _$VehicleToJson(Vehicle instance) => <String, dynamic>{
      'id': instance.id,
      'type': instance.type?.toJson(),
      'name': instance.name,
      'registration_number': instance.registrationNumber,
      'description': instance.description,
      'is_air_conditioned': instance.isAirConditioned,
      'is_insured': instance.isInsured,
      'age': instance.age,
      'manufacturing_year': instance.manufacturingYear,
    };

Route _$RouteFromJson(Map json) => $checkedCreate(
      'Route',
      json,
      ($checkedConvert) {
        final val = Route(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          pickupLocation: $checkedConvert(
              'pickup_location', (v) => Map<String, dynamic>.from(v as Map)),
          destination: $checkedConvert(
              'destination', (v) => Map<String, dynamic>.from(v as Map)),
          eta: $checkedConvert('eta', (v) => v as String),
          isActive: $checkedConvert('is_active', (v) => v as bool),
        );
        return val;
      },
      fieldKeyMap: const {
        'pickupLocation': 'pickup_location',
        'isActive': 'is_active'
      },
    );

Map<String, dynamic> _$RouteToJson(Route instance) => <String, dynamic>{
      'id': instance.id,
      'pickup_location': instance.pickupLocation,
      'destination': instance.destination,
      'eta': instance.eta,
      'is_active': instance.isActive,
    };

Ride _$RideFromJson(Map json) => $checkedCreate(
      'Ride',
      json,
      ($checkedConvert) {
        final val = Ride(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          driver: $checkedConvert(
              'driver',
              (v) => (v as Map?)?.map(
                    (k, e) => MapEntry(k as String, e),
                  )),
          client: $checkedConvert(
              'client',
              (v) => (v as Map?)?.map(
                    (k, e) => MapEntry(k as String, e),
                  )),
          vehicle: $checkedConvert(
              'vehicle',
              (v) => v == null
                  ? null
                  : Vehicle.fromJson(Map<String, dynamic>.from(v as Map))),
          route: $checkedConvert(
              'route',
              (v) => v == null
                  ? null
                  : Route.fromJson(Map<String, dynamic>.from(v as Map))),
          startLocation: $checkedConvert('start_location', (v) => v as String),
          endLocation: $checkedConvert('end_location', (v) => v as String),
          startTime: $checkedConvert('start_time', (v) => v as String),
          endTime: $checkedConvert('end_time', (v) => v as String),
          isActive: $checkedConvert('is_active', (v) => v as bool),
          status: $checkedConvert('status', (v) => v as String),
        );
        return val;
      },
      fieldKeyMap: const {
        'startLocation': 'start_location',
        'endLocation': 'end_location',
        'startTime': 'start_time',
        'endTime': 'end_time',
        'isActive': 'is_active'
      },
    );

Map<String, dynamic> _$RideToJson(Ride instance) => <String, dynamic>{
      'id': instance.id,
      'driver': instance.driver,
      'client': instance.client,
      'vehicle': instance.vehicle?.toJson(),
      'route': instance.route?.toJson(),
      'start_location': instance.startLocation,
      'end_location': instance.endLocation,
      'start_time': instance.startTime,
      'end_time': instance.endTime,
      'is_active': instance.isActive,
      'status': instance.status,
    };

RideRequest _$RideRequestFromJson(Map json) => $checkedCreate(
      'RideRequest',
      json,
      ($checkedConvert) {
        final val = RideRequest(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          client: $checkedConvert(
              'client',
              (v) {
                if (v is int && json['client_details'] is Map) {
                   return (json['client_details'] as Map).map((k, e) => MapEntry(k as String, e));
                }
                return (v as Map?)?.map((k, e) => MapEntry(k as String, e));
              }),
          driver: $checkedConvert(
              'driver',
              (v) {
                if (v is int && json['driver_details'] is Map) {
                   return (json['driver_details'] as Map).map((k, e) => MapEntry(k as String, e));
                }
                return (v as Map?)?.map((k, e) => MapEntry(k as String, e));
              }),
          vehicle: $checkedConvert(
              'vehicle',
              (v) {
                if (v is int && json['vehicle_details'] is Map) {
                  return Vehicle.fromJson(Map<String, dynamic>.from(json['vehicle_details'] as Map));
                }
                return v == null
                  ? null
                  : Vehicle.fromJson(Map<String, dynamic>.from(v as Map));
              }),
          route: $checkedConvert(
              'route',
              (v) => v == null
                  ? null
                  : Route.fromJson(Map<String, dynamic>.from(v as Map))),
          startLocation: $checkedConvert('start_location', (v) => v as String),
          endLocation: $checkedConvert('end_location', (v) => v as String),
          requestedAt: $checkedConvert('requested_at', (v) => v as String?),
          status: $checkedConvert('status', (v) => v as String?),
          ride: $checkedConvert(
              'ride',
              (v) {
                if (v is int && json['ride_details'] is Map) {
                  return Ride.fromJson(Map<String, dynamic>.from(json['ride_details'] as Map));
                }
                return v == null
                  ? null
                  : Ride.fromJson(Map<String, dynamic>.from(v as Map));
              }),
          cost: $checkedConvert('cost', (v) => (v as num?)?.toDouble()),
          expiresAt: $checkedConvert('expires_at', (v) => v as String?),
          matchingStartedAt:
              $checkedConvert('matching_started_at', (v) => v as String?),
          driverConfirmedAt:
              $checkedConvert('driver_confirmed_at', (v) => v as String?),
          pickupEta: $checkedConvert('pickup_eta', (v) => v as String?),
          potentialDrivers:
              $checkedConvert('potential_drivers', (v) => v as List<dynamic>?),
          currentDriverIndex: $checkedConvert(
              'current_driver_index', (v) => (v as num?)?.toInt() ?? 0),
        );
        return val;
      },
      fieldKeyMap: const {
        'startLocation': 'start_location',
        'endLocation': 'end_location',
        'requestedAt': 'requested_at',
        'expiresAt': 'expires_at',
        'matchingStartedAt': 'matching_started_at',
        'driverConfirmedAt': 'driver_confirmed_at',
        'pickupEta': 'pickup_eta',
        'potentialDrivers': 'potential_drivers',
        'currentDriverIndex': 'current_driver_index'
      },
    );

Map<String, dynamic> _$RideRequestToJson(RideRequest instance) =>
    <String, dynamic>{
      'id': instance.id,
      'client': instance.client,
      'driver': instance.driver,
      'vehicle': instance.vehicle?.toJson(),
      'route': instance.route?.toJson(),
      'start_location': instance.startLocation,
      'end_location': instance.endLocation,
      'requested_at': instance.requestedAt,
      'status': instance.status,
      'ride': instance.ride?.toJson(),
      'cost': instance.cost,
      'expires_at': instance.expiresAt,
      'matching_started_at': instance.matchingStartedAt,
      'driver_confirmed_at': instance.driverConfirmedAt,
      'pickup_eta': instance.pickupEta,
      'potential_drivers': instance.potentialDrivers,
      'current_driver_index': instance.currentDriverIndex,
    };

RideMatching _$RideMatchingFromJson(Map json) => $checkedCreate(
      'RideMatching',
      json,
      ($checkedConvert) {
        final val = RideMatching(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          rideRequest: $checkedConvert('ride_request',
              (v) => RideRequest.fromJson(Map<String, dynamic>.from(v as Map))),
          driver: $checkedConvert(
              'driver', (v) => Map<String, dynamic>.from(v as Map)),
          distanceKm:
              $checkedConvert('distance_km', (v) => (v as num).toDouble()),
          estimatedEtaMinutes: $checkedConvert(
              'estimated_eta_minutes', (v) => (v as num).toInt()),
          matchingScore:
              $checkedConvert('matching_score', (v) => (v as num).toDouble()),
          status: $checkedConvert('status', (v) => v as String),
          expiresAt: $checkedConvert('expires_at', (v) => v as String),
          respondedAt: $checkedConvert('responded_at', (v) => v as String?),
          responseTimeSeconds: $checkedConvert(
              'response_time_seconds', (v) => (v as num?)?.toInt()),
        );
        return val;
      },
      fieldKeyMap: const {
        'rideRequest': 'ride_request',
        'distanceKm': 'distance_km',
        'estimatedEtaMinutes': 'estimated_eta_minutes',
        'matchingScore': 'matching_score',
        'expiresAt': 'expires_at',
        'respondedAt': 'responded_at',
        'responseTimeSeconds': 'response_time_seconds'
      },
    );

Map<String, dynamic> _$RideMatchingToJson(RideMatching instance) =>
    <String, dynamic>{
      'id': instance.id,
      'ride_request': instance.rideRequest.toJson(),
      'driver': instance.driver,
      'distance_km': instance.distanceKm,
      'estimated_eta_minutes': instance.estimatedEtaMinutes,
      'matching_score': instance.matchingScore,
      'status': instance.status,
      'expires_at': instance.expiresAt,
      'responded_at': instance.respondedAt,
      'response_time_seconds': instance.responseTimeSeconds,
    };

DriverLocation _$DriverLocationFromJson(Map json) => $checkedCreate(
      'DriverLocation',
      json,
      ($checkedConvert) {
        final val = DriverLocation(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          driver: $checkedConvert(
              'driver', (v) => Map<String, dynamic>.from(v as Map)),
          location: $checkedConvert(
              'location', (v) => Map<String, dynamic>.from(v as Map)),
          address: $checkedConvert('address', (v) => v as String?),
          isOnline: $checkedConvert('is_online', (v) => v as bool),
          onActiveRide: $checkedConvert('on_active_ride', (v) => v as bool),
          isAvailable: $checkedConvert('is_available', (v) => v as bool),
          lastUpdated: $checkedConvert('last_updated', (v) => v as String),
        );
        return val;
      },
      fieldKeyMap: const {
        'isOnline': 'is_online',
        'onActiveRide': 'on_active_ride',
        'isAvailable': 'is_available',
        'lastUpdated': 'last_updated'
      },
    );

Map<String, dynamic> _$DriverLocationToJson(DriverLocation instance) =>
    <String, dynamic>{
      'id': instance.id,
      'driver': instance.driver,
      'location': instance.location,
      'address': instance.address,
      'is_online': instance.isOnline,
      'on_active_ride': instance.onActiveRide,
      'is_available': instance.isAvailable,
      'last_updated': instance.lastUpdated,
    };

Rating _$RatingFromJson(Map json) => $checkedCreate(
      'Rating',
      json,
      ($checkedConvert) {
        final val = Rating(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          ride: $checkedConvert(
              'ride',
              (v) => (v as Map?)?.map(
                    (k, e) => MapEntry(k as String, e),
                  )),
          client: $checkedConvert(
              'client',
              (v) => (v as Map?)?.map(
                    (k, e) => MapEntry(k as String, e),
                  )),
          rating: $checkedConvert('rating', (v) => (v as num).toInt()),
          created: $checkedConvert('created', (v) => v as String),
        );
        return val;
      },
    );

Map<String, dynamic> _$RatingToJson(Rating instance) => <String, dynamic>{
      'id': instance.id,
      'ride': instance.ride,
      'client': instance.client,
      'rating': instance.rating,
      'created': instance.created,
    };

Feedback _$FeedbackFromJson(Map json) => $checkedCreate(
      'Feedback',
      json,
      ($checkedConvert) {
        final val = Feedback(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          client: $checkedConvert(
              'client',
              (v) => (v as Map?)?.map(
                    (k, e) => MapEntry(k as String, e),
                  )),
          ride: $checkedConvert(
              'ride',
              (v) => (v as Map?)?.map(
                    (k, e) => MapEntry(k as String, e),
                  )),
          message: $checkedConvert('message', (v) => v as String),
          rating: $checkedConvert(
              'rating',
              (v) => v == null
                  ? null
                  : Rating.fromJson(Map<String, dynamic>.from(v as Map))),
          created: $checkedConvert('created', (v) => v as String),
        );
        return val;
      },
    );

Map<String, dynamic> _$FeedbackToJson(Feedback instance) => <String, dynamic>{
      'id': instance.id,
      'client': instance.client,
      'ride': instance.ride,
      'message': instance.message,
      'rating': instance.rating?.toJson(),
      'created': instance.created,
    };
