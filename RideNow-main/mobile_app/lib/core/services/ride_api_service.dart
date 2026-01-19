import 'dart:convert';
import 'package:get/get.dart';
import 'package:mobile_app/core/constants/api_endpoints.dart';
import 'package:mobile_app/core/services/cache_manager.dart';
import 'package:mobile_app/model/ride_model.dart';
import 'api_service.dart';

class RideApiService extends GetxService {
  final ApiService _apiService = Get.find<ApiService>();
  final CacheManager _cacheManager = Get.find<CacheManager>();
  
  // Ride Requests
  Future<List<RideRequest>> getRideRequests() async {
    try {
      final response = await _apiService.get(ApiEndpoints.rideRequests);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('Ride requests response: $data');
        
        if (data is List) {
          return data.map((item) => RideRequest.fromJson(item)).toList();
        } else if (data is Map && data.containsKey('results')) {
          final results = data['results'] as List;
          return results.map((item) => RideRequest.fromJson(item)).toList();
        } else {
          print('Unexpected ride requests response format');
          return [];
        }
      }
      throw Exception('Failed to get ride requests');
    } catch (e) {
      print('Get ride requests error: $e');
      rethrow;
    }
  }
  
  Future<RideRequest> createRideRequest({
    required String startLocation,
    required String endLocation,
    double? startLat,
    double? startLng,
    double? endLat,
    double? endLng,
    int? vehicleTypeId,
  }) async {
    try {
      final Map<String, dynamic> body = {
        'start_location': startLocation,
        'end_location': endLocation,
        'status': 'Pending',
      };
      
      if (startLat != null && startLng != null) {
        body['pickup_location'] = {
          'type': 'Point',
          'coordinates': [startLng, startLat]
        };
      }
      
      if (endLat != null && endLng != null) {
        body['destination'] = {
          'type': 'Point',
          'coordinates': [endLng, endLat]
        };
      }
      
      if (vehicleTypeId != null) {
        body['vehicle_type_id'] = vehicleTypeId;
      }
      
      final response = await _apiService.post(
        ApiEndpoints.rideRequests,
        body: body,
      );
      
      if (response.statusCode == 201) {
        return RideRequest.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to create ride request');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<RideRequest> getRideRequest(int id) async {
    try {
      final response = await _apiService.get(ApiEndpoints.rideRequestDetail(id));
      if (response.statusCode == 200) {
        return RideRequest.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to load ride request');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<RideRequest> updateRideRequest(int id, Map<String, dynamic> data) async {
    try {
      final response = await _apiService.patch(
        ApiEndpoints.rideRequestDetail(id),
        body: data,
      );
      
      if (response.statusCode == 200) {
        return RideRequest.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to update ride request');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> deleteRideRequest(int id) async {
    try {
      final response = await _apiService.delete(ApiEndpoints.rideRequestDetail(id));
      if (response.statusCode != 204) {
        throw Exception('Failed to delete ride request');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  Future<RideRequest> acceptRideRequest(int id) async {
    try {
      final response = await _apiService.post(ApiEndpoints.acceptRideRequest(id));
      if (response.statusCode == 200) {
        return RideRequest.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to accept ride request');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<RideRequest> cancelRideRequest(int id) async {
    try {
      final response = await _apiService.post(ApiEndpoints.cancelRideRequest(id));
      if (response.statusCode == 200) {
        return RideRequest.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to cancel ride request');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<List<RideRequest>> getPendingRideRequests() async {
    try {
      final response = await _apiService.get(ApiEndpoints.pendingRideRequests);
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => RideRequest.fromJson(json)).toList();
      }
      throw Exception('Failed to load pending ride requests');
    } catch (e) {
      rethrow;
    }
  }
  
  // Quick Ride Request
  Future<RideRequest> quickRideRequest({
    required double pickupLat,
    required double pickupLng,
    required double destLat,
    required double destLng,
    required String pickupAddress,
    required String destAddress,
  }) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.quickRideRequest,
        body: {
          'pickup_location': {
            'type': 'Point',
            'coordinates': [pickupLng, pickupLat]
          },
          'destination': {
            'type': 'Point',
            'coordinates': [destLng, destLat]
          },
          'pickup_address': pickupAddress,
          'destination_address': destAddress,
        },
      );
      
      if (response.statusCode == 201) {
        return RideRequest.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to create quick ride request');
    } catch (e) {
      rethrow;
    }
  }
  
  // Ride Matching
  Future<void> startDriverMatching(int rideRequestId, {double? lat, double? lng}) async {
    try {
      final Map<String, dynamic> body = {'ride_request_id': rideRequestId};
      if (lat != null) body['latitude'] = lat;
      if (lng != null) body['longitude'] = lng;

      final response = await _apiService.post(
        ApiEndpoints.startDriverMatching,
        body: body,
      );
      
      print('Start driver matching response: ${response.statusCode} ${response.body}');
      if (response.statusCode != 200) {
        String message = 'Failed to start driver matching';
        try {
          final errorData = json.decode(response.body);
          if (errorData['error'] != null) {
            message = errorData['error'];
          }
        } catch (_) {}
        throw Exception(message);
      }
    } catch (e) {
      print('Start driver matching error: $e');
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> checkMatchingStatus(int rideRequestId) async {
    try {
      final response = await _apiService.get(
        ApiEndpoints.checkMatchingStatus,
        queryParams: {'ride_request_id': rideRequestId.toString()},
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      throw Exception('Failed to check matching status');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> acceptRideMatch(int matchingId) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.acceptRideMatch,
        body: {'matching_id': matchingId},
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to accept ride match');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> declineRideMatch(int matchingId) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.declineRideMatch,
        body: {'matching_id': matchingId},
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to decline ride match');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> tryNextDriver(int rideRequestId) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.tryNextDriver,
        body: {'ride_request_id': rideRequestId},
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to try next driver');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> selectDriver(int rideRequestId, int driverId) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.selectDriver,
        body: {
          'ride_request_id': rideRequestId,
          'driver_id': driverId,
        },
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to select driver');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  // Find Nearby Drivers
  Future<List<DriverLocation>> findNearbyDrivers({
    required double lat,
    required double lng,
    double radius = 5.0, // in kilometers
    bool? availableOnly = true,
  }) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.findNearbyDrivers,
        body: {
          'latitude': lat,
          'longitude': lng,
          'radius_km': radius,
          'available_only': availableOnly,
        },
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body)['drivers'];
        return data.map((json) => DriverLocation.fromJson(json)).toList();
      }
      throw Exception('Failed to find nearby drivers');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<List<DriverLocation>> getAvailableDrivers() async {
    try {
      final response = await _apiService.get(ApiEndpoints.availableDrivers);
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => DriverLocation.fromJson(json)).toList();
      }
      throw Exception('Failed to get available drivers');
    } catch (e) {
      rethrow;
    }
  }
  
  // Get Driver Location for a specific ride
  Future<DriverLocation?> getDriverLocation(int rideRequestId) async {
    try {
      final response = await _apiService.get(
        '${ApiEndpoints.getDriverLocation}/$rideRequestId/',
      );
      
      if (response.statusCode == 200) {
        return DriverLocation.fromJson(json.decode(response.body));
      }
      return null;
    } catch (e) {
      return null;
    }
  }
  
  // Ride Actions
  Future<void> arriveAtPickup(int rideId) async {
    try {
      final response = await _apiService.post(ApiEndpoints.arriveAtPickup(rideId));
      if (response.statusCode != 200) {
        throw Exception('Failed to mark arrival at pickup');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> startRide(int rideId) async {
    try {
      final response = await _apiService.post(ApiEndpoints.startRide(rideId));
      if (response.statusCode != 200) {
        throw Exception('Failed to start ride');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Ride> completeRide(int rideId, {double? cost}) async {
    try {
      final Map<String, dynamic> body = {};
      if (cost != null) body['cost'] = cost;
      
      final response = await _apiService.post(
        ApiEndpoints.completeRide(rideId),
        body: body,
      );
      
      if (response.statusCode == 200) {
        return Ride.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to complete ride');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<void> cancelRide(int rideId) async {
    try {
      final response = await _apiService.post(ApiEndpoints.cancelRide(rideId));
      if (response.statusCode != 200) {
        throw Exception('Failed to cancel ride');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  // Ratings
  Future<Rating> submitRating({
    required int rideId,
    required int rating,
    String? review,
  }) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.submitRating,
        body: {
          'ride_id': rideId,
          'rating': rating,
          'review': review,
        },
      );
      
      if (response.statusCode == 201) {
        return Rating.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to submit rating');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<List<Rating>> getRatings() async {
    try {
      final response = await _apiService.get(ApiEndpoints.ratings);
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Rating.fromJson(json)).toList();
      }
      throw Exception('Failed to get ratings');
    } catch (e) {
      rethrow;
    }
  }
  
  // Feedback
  Future<Feedback> submitFeedback({
    required int rideId,
    required String message,
    int? ratingId,
  }) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.feedback,
        body: {
          'ride_id': rideId,
          'message': message,
          'rating': ratingId,
        },
      );
      
      if (response.statusCode == 201) {
        return Feedback.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to submit feedback');
    } catch (e) {
      rethrow;
    }
  }
  
  // Vehicle Types
  Future<List<VehicleType>> getVehicleTypes() async {
    try {
      final response = await _apiService.get(ApiEndpoints.vehicleTypes);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('Vehicle types response: $data');
        
        List<dynamic> results = [];
        if (data is List) {
          results = data;
        } else if (data is Map && data.containsKey('results')) {
          results = data['results'] as List;
        }
        
        return results.map((item) {
          // Manually cast string prices to double to avoid CheckedFromJsonException
          final Map<String, dynamic> cleanItem = Map<String, dynamic>.from(item);
          if (cleanItem['base_price'] is String) {
            cleanItem['base_price'] = double.tryParse(cleanItem['base_price']) ?? 0.0;
          }
          if (cleanItem['price_per_km'] is String) {
            cleanItem['price_per_km'] = double.tryParse(cleanItem['price_per_km']) ?? 0.0;
          }
          return VehicleType.fromJson(cleanItem);
        }).toList();
      }
      throw Exception('Failed to get vehicle types');
    } catch (e) {
      print('Get vehicle types error: $e');
      rethrow;
    }
  }
  
  // Vehicles
  Future<List<Vehicle>> getAvailableVehicles() async {
    try {
      final response = await _apiService.get(ApiEndpoints.availableVehicles);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('Available vehicles response: $data');
        
        if (data is List) {
          return data.map((item) => Vehicle.fromJson(item)).toList();
        } else if (data is Map && data.containsKey('results')) {
          final results = data['results'] as List;
          return results.map((item) => Vehicle.fromJson(item)).toList();
        } else {
          print('Unexpected vehicles response format');
          return [];
        }
      }
      throw Exception('Failed to get available vehicles');
    } catch (e) {
      print('Get available vehicles error: $e');
      rethrow;
    }
  }
  
  // Statistics
  Future<Map<String, dynamic>> getDriverStatistics() async {
    try {
      final response = await _apiService.get(ApiEndpoints.driverStatistics);
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      throw Exception('Failed to get driver statistics');
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> getClientStatistics() async {
    try {
      final response = await _apiService.get(ApiEndpoints.clientStatistics);
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      throw Exception('Failed to get client statistics');
    } catch (e) {
      rethrow;
    }
  }
  
  // Get all rides
Future<List<Ride>> getRides() async {
    try {
      final response = await _apiService.get(ApiEndpoints.rides);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('Rides response: $data');
        
        if (data is List) {
          return data.map((item) => Ride.fromJson(item)).toList();
        } else if (data is Map && data.containsKey('results')) {
          final results = data['results'] as List;
          return results.map((item) => Ride.fromJson(item)).toList();
        } else {
          print('Unexpected rides response format');
          return [];
        }
      }
      throw Exception('Failed to get rides');
    } catch (e) {
      print('Get rides error: $e');
      rethrow;
    }
  }
  
  Future<Ride> getRide(int id) async {
    try {
      final response = await _apiService.get(ApiEndpoints.rideDetail(id));
      if (response.statusCode == 200) {
        return Ride.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to get ride');
    } catch (e) {
      rethrow;
    }
  }
}