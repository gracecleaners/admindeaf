import 'package:get/get.dart';
import 'package:mobile_app/core/services/cache_manager.dart';
import 'package:mobile_app/model/ride_model.dart';
import '../../core/services/ride_api_service.dart';

class RideController extends GetxController {
  final RideApiService _rideApiService = Get.find<RideApiService>();
  final CacheManager _cacheManager = Get.find<CacheManager>();
  
  // Observables
  var isLoading = false.obs;
  var currentRide = Rxn<RideRequest>();
  var rideHistory = <Ride>[].obs;
  var rideRequests = <RideRequest>[].obs;
  var nearbyDrivers = <DriverLocation>[].obs;
  var vehicleTypes = <VehicleType>[].obs;
  var availableVehicles = <Vehicle>[].obs;
  
  // Statistics
  var driverStatistics = <String, dynamic>{}.obs;
  var clientStatistics = <String, dynamic>{}.obs;
  
  // Ride matching status
  var matchingStatus = 'idle'.obs; // idle, searching, matching, matched, failed
  var currentMatching = Rxn<RideMatching>();
  
  @override
  void onInit() {
    super.onInit();
    loadInitialData();
  }
  
  Future<void> loadInitialData() async {
    await getVehicleTypes();
    await getAvailableVehicles();
    await getRideHistory();
    await getRideRequests();
  }
  
  // Create Ride Request
  Future<RideRequest?> requestRide({
    required String pickupAddress,
    required String destinationAddress,
    double? pickupLat,
    double? pickupLng,
    double? destLat,
    double? destLng,
    int? vehicleTypeId,
  }) async {
    try {
      isLoading.value = true;
      
      final rideRequest = await _rideApiService.createRideRequest(
        startLocation: pickupAddress,
        endLocation: destinationAddress,
        startLat: pickupLat,
        startLng: pickupLng,
        endLat: destLat,
        endLng: destLng,
        vehicleTypeId: vehicleTypeId,
      );
      
      currentRide.value = rideRequest;
      rideRequests.insert(0, rideRequest);
      
      // Start driver matching
      await startDriverMatching(rideRequest.id, lat: pickupLat, lng: pickupLng);
      
      return rideRequest;
    } catch (e) {
      Get.snackbar('Error', 'Failed to request ride: ${e.toString()}');
      return null;
    } finally {
      isLoading.value = false;
    }
  }
  
  // Quick Ride Request
  Future<RideRequest?> quickRideRequest({
    required double pickupLat,
    required double pickupLng,
    required double destLat,
    required double destLng,
    required String pickupAddress,
    required String destAddress,
  }) async {
    try {
      isLoading.value = true;
      
      final rideRequest = await _rideApiService.quickRideRequest(
        pickupLat: pickupLat,
        pickupLng: pickupLng,
        destLat: destLat,
        destLng: destLng,
        pickupAddress: pickupAddress,
        destAddress: destAddress,
      );
      
      currentRide.value = rideRequest;
      rideRequests.insert(0, rideRequest);
      
      // Start driver matching
      await startDriverMatching(rideRequest.id, lat: pickupLat, lng: pickupLng);
      
      return rideRequest;
    } catch (e) {
      Get.snackbar('Error', 'Failed to request ride: ${e.toString()}');
      return null;
    } finally {
      isLoading.value = false;
    }
  }
  
  // Driver Matching
  Future<void> startDriverMatching(int rideRequestId, {double? lat, double? lng}) async {
    try {
      matchingStatus.value = 'searching';
      await _rideApiService.startDriverMatching(rideRequestId, lat: lat, lng: lng);
      
      // Start polling for matching status
      startMatchingStatusPolling(rideRequestId);
    } catch (e) {
      matchingStatus.value = 'failed';
      print('Start driver matching error: $e');
      final message = e.toString().replaceAll('Exception: ', '');
      Get.snackbar('Driver Matching', message);
    }
  }
  
  void startMatchingStatusPolling(int rideRequestId) {
    const interval = Duration(seconds: 3);
    
    Future.doWhile(() async {
      if (matchingStatus.value == 'matched' || matchingStatus.value == 'failed') {
        return false;
      }
      
      try {
        final status = await _rideApiService.checkMatchingStatus(rideRequestId);
        matchingStatus.value = status['status'];
        
        if (status['matching'] != null) {
          currentMatching.value = RideMatching.fromJson(status['matching']);
        }
        
        if (status['status'] == 'matched') {
          // Get updated ride request
          final updatedRide = await _rideApiService.getRideRequest(rideRequestId);
          currentRide.value = updatedRide;
          Get.snackbar('Success', 'Driver found!');
        } else if (status['status'] == 'failed') {
          Get.snackbar('Error', 'No drivers available. Please try again.');
        }
      } catch (e) {
        print('Error polling matching status: $e');
      }
      
      await Future.delayed(interval);
      return matchingStatus.value == 'searching' || matchingStatus.value == 'matching';
    });
  }
  
  Future<void> acceptRideMatch(int matchingId) async {
    try {
      await _rideApiService.acceptRideMatch(matchingId);
      matchingStatus.value = 'matched';
      Get.snackbar('Success', 'Ride match accepted');
    } catch (e) {
      Get.snackbar('Error', 'Failed to accept ride match');
    }
  }
  
  Future<void> declineRideMatch(int matchingId) async {
    try {
      await _rideApiService.declineRideMatch(matchingId);
      matchingStatus.value = 'searching';
      Get.snackbar('Info', 'Ride match declined');
    } catch (e) {
      Get.snackbar('Error', 'Failed to decline ride match');
    }
  }
  
  Future<void> tryNextDriver(int rideRequestId) async {
    try {
      await _rideApiService.tryNextDriver(rideRequestId);
      matchingStatus.value = 'searching';
      Get.snackbar('Info', 'Trying next driver...');
    } catch (e) {
      Get.snackbar('Error', 'Failed to try next driver');
    }
  }
  
  // Find Nearby Drivers
  Future<void> findNearbyDrivers(double lat, double lng, {double radius = 5.0}) async {
    try {
      // Check cache first
      final cached = _cacheManager.getCachedNearbyDrivers();
      if (cached != null) {
        nearbyDrivers.value = cached;
      }
      
      final drivers = await _rideApiService.findNearbyDrivers(
        lat: lat,
        lng: lng,
        radius: radius,
      );
      
      nearbyDrivers.value = drivers;
    } catch (e) {
      print('Error finding nearby drivers: $e');
    }
  }
  
  // Ride Actions
  Future<void> arriveAtPickup(int rideId) async {
    try {
      await _rideApiService.arriveAtPickup(rideId);
      Get.snackbar('Success', 'Arrived at pickup location');
    } catch (e) {
      Get.snackbar('Error', 'Failed to mark arrival');
    }
  }
  
  Future<void> startRide(int rideId) async {
    try {
      await _rideApiService.startRide(rideId);
      Get.snackbar('Success', 'Ride started');
    } catch (e) {
      Get.snackbar('Error', 'Failed to start ride');
    }
  }
  
  Future<void> completeRide(int rideId, {double? cost}) async {
    try {
      final ride = await _rideApiService.completeRide(rideId, cost: cost);
      
      // Update ride history
      rideHistory.insert(0, ride);
      
      // Clear current ride
      currentRide.value = null;
      matchingStatus.value = 'idle';
      
      Get.offAllNamed('/ride-completion', arguments: ride);
      Get.snackbar('Success', 'Ride completed');
    } catch (e) {
      Get.snackbar('Error', 'Failed to complete ride');
    }
  }
  
  Future<void> cancelRide(int rideId) async {
    try {
      await _rideApiService.cancelRide(rideId);
      
      // Clear current ride
      currentRide.value = null;
      matchingStatus.value = 'idle';
      
      Get.back();
      Get.snackbar('Success', 'Ride cancelled');
    } catch (e) {
      Get.snackbar('Error', 'Failed to cancel ride');
    }
  }

  Future<void> cancelRideRequest(int requestId) async {
    try {
      await _rideApiService.cancelRideRequest(requestId);
      
      // Clear current ride if it matches this request
      if (currentRide.value?.id == requestId) {
        currentRide.value = null;
      }
      matchingStatus.value = 'idle';
      
      Get.snackbar('Success', 'Ride request cancelled');
    } catch (e) {
      Get.snackbar('Error', 'Failed to cancel ride request');
    }
  }
  
  // Ratings & Feedback
  Future<void> submitRating({
    required int rideId,
    required int rating,
    String? review,
  }) async {
    try {
      await _rideApiService.submitRating(
        rideId: rideId,
        rating: rating,
        review: review,
      );
      
      Get.back();
      Get.snackbar('Success', 'Thank you for your rating!');
    } catch (e) {
      Get.snackbar('Error', 'Failed to submit rating');
    }
  }
  
  Future<void> submitFeedback({
    required int rideId,
    required String message,
    int? ratingId,
  }) async {
    try {
      await _rideApiService.submitFeedback(
        rideId: rideId,
        message: message,
        ratingId: ratingId,
      );
      
      Get.back();
      Get.snackbar('Success', 'Feedback submitted');
    } catch (e) {
      Get.snackbar('Error', 'Failed to submit feedback');
    }
  }
  
  // Get Data
  // Get Data
  Future<void> getVehicleTypes() async {
    try {
      final response = await _rideApiService.getVehicleTypes();
      vehicleTypes.value = response;
    } catch (e) {
      print('Error getting vehicle types: $e');
    }
  }
  
  Future<void> getAvailableVehicles() async {
    try {
      final response = await _rideApiService.getAvailableVehicles();
      availableVehicles.value = response;
    } catch (e) {
      print('Error getting available vehicles: $e');
    }
  }
  
  Future<void> getRideHistory() async {
    try {
      isLoading.value = true;
      final response = await _rideApiService.getRides();
      rideHistory.value = response;
    } catch (e) {
      print('Error getting ride history: $e');
    } finally {
      isLoading.value = false;
    }
  }
  
  Future<void> getRideRequests() async {
    try {
      final response = await _rideApiService.getRideRequests();
      rideRequests.value = response;
    } catch (e) {
      print('Error getting ride requests: $e');
    }
  }
  
  Future<void> getPendingRideRequests() async {
    try {
      final requests = await _rideApiService.getPendingRideRequests();
      rideRequests.value = requests;
    } catch (e) {
      print('Error getting pending ride requests: $e');
    }
  }
  
  Future<void> getDriverStatistics() async {
    try {
      final stats = await _rideApiService.getDriverStatistics();
      driverStatistics.value = stats;
    } catch (e) {
      print('Error getting driver statistics: $e');
    }
  }
  
  Future<void> getClientStatistics() async {
    try {
      final stats = await _rideApiService.getClientStatistics();
      clientStatistics.value = stats;
    } catch (e) {
      print('Error getting client statistics: $e');
    }
  }
  
  // Helper methods
  VehicleType? getVehicleTypeById(int id) {
    return vehicleTypes.firstWhereOrNull((type) => type.id == id);
  }
  
  bool isRideInProgress() {
    return currentRide.value != null && 
           currentRide.value!.status == 'Accepted';
  }
  
  void clearCurrentRide() {
    currentRide.value = null;
    matchingStatus.value = 'idle';
    currentMatching.value = null;
  }
}