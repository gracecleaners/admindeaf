import 'package:get/get.dart';
import 'package:mobile_app/model/ride_model.dart';
import 'secure_storage_service.dart';
import 'hive_service.dart';

class CacheManager extends GetxController {
  static final CacheManager _instance = CacheManager._internal();
  factory CacheManager() => _instance;
  CacheManager._internal();
  
  final SecureStorageService _secureStorage = SecureStorageService();
  final HiveService _hiveService = HiveService();
  
  @override
  void onInit() {
    super.onInit();
    initCache();
  }
  
  Future<void> initCache() async {
    await _hiveService.init();
  }
  
  // Combined methods for common use cases
  
  Future<void> saveUserData({
    required Map<String, dynamic> userData,
    String? accessToken,
    String? refreshToken,
  }) async {
    // Save non-sensitive data to Hive
    await _hiveService.saveUserData(userData);
    
    // Save tokens to secure storage
    if (accessToken != null) {
      await _secureStorage.saveAccessToken(accessToken);
    }
    if (refreshToken != null) {
      await _secureStorage.saveRefreshToken(refreshToken);
    }
  }
  
  Future<Map<String, dynamic>?> getUserData() async {
    return _hiveService.getUserData();
  }
  
  Future<String?> getAccessToken() async {
    return await _secureStorage.getAccessToken();
  }
  
  Future<void> cacheRideData({
    required List<Map<String, dynamic>> rideHistory,
    required List<Map<String, dynamic>> nearbyDrivers,
  }) async {
    await Future.wait([
      _hiveService.saveRideHistory(rideHistory),
      _hiveService.cacheNearbyDrivers(nearbyDrivers),
    ]);
  }
  
  Future<void> logout() async {
    // Clearing secure storage
    await _secureStorage.clearAll();
    
    // Clearing non-sensitive cached data
    await _hiveService.clearAllCache();
    
    // Keeping app settings
    await _hiveService.clearBox(HiveService.appSettingsBox);
  }
  
  // Cache strategies
  Future<List<Map<String, dynamic>>?> getCachedRideHistory() async {
    final cachedHistory = _hiveService.getRideHistory();
    
    // Check if cache is older than 1 hour
    if (cachedHistory != null) {
      final cacheTime = _hiveService.getFromBox<Map<String, dynamic>>(
        HiveService.rideHistoryBox, 
        'timestamp'
      );
      
      if (cacheTime != null) {
        final cachedAt = DateTime.parse(cacheTime['timestamp']);
        if (DateTime.now().difference(cachedAt) < const Duration(hours: 1)) {
          return cachedHistory;
        }
      }
    }
    return null;
  }

   Future<void> cacheVehicleTypes(List<VehicleType> vehicleTypes) async {
    final serialized = vehicleTypes.map((vt) => vt.toJson()).toList();
    await _hiveService.saveToBox(
      HiveService.appSettingsBox,
      'vehicle_types',
      {
        'data': serialized,
        'timestamp': DateTime.now().toIso8601String(),
      },
    );
  }
  
  List<VehicleType>? getCachedVehicleTypes() {
    final cached = _hiveService.getFromBox<Map<String, dynamic>>(
      HiveService.appSettingsBox,
      'vehicle_types',
    );
    
    if (cached != null) {
      final timestamp = DateTime.parse(cached['timestamp']);
      if (DateTime.now().difference(timestamp) < const Duration(hours: 24)) {
        final List<dynamic> data = cached['data'];
        return data.map((json) => VehicleType.fromJson(json)).toList();
      }
    }
    return null;
  }
  
  // Ride history cache
  Future<void> cacheRideHistory(List<Ride> rides) async {
    final serialized = rides.map((ride) => ride.toJson()).toList();
    await _hiveService.saveToBox(
      HiveService.rideHistoryBox,
      'rides',
      {
        'data': serialized,
        'timestamp': DateTime.now().toIso8601String(),
      },
    );
  }
  
  List<Ride>? getCachedRides() {
    final cached = _hiveService.getFromBox<Map<String, dynamic>>(
      HiveService.rideHistoryBox,
      'rides',
    );
    
    if (cached != null) {
      final timestamp = DateTime.parse(cached['timestamp']);
      if (DateTime.now().difference(timestamp) < const Duration(hours: 1)) {
        final List<dynamic> data = cached['data'];
        return data.map((json) => Ride.fromJson(json)).toList();
      }
    }
    return null;
  }
  
  // Nearby drivers cache
  Future<void> cacheNearbyDrivers(List<DriverLocation> drivers) async {
    final serialized = drivers.map((driver) => driver.toJson()).toList();
    await _hiveService.saveToBox(
      HiveService.nearbyDriversBox,
      'drivers',
      {
        'data': serialized,
        'timestamp': DateTime.now().toIso8601String(),
      },
    );
  }
  
  List<DriverLocation>? getCachedNearbyDrivers() {
    final cached = _hiveService.getFromBox<Map<String, dynamic>>(
      HiveService.nearbyDriversBox,
      'drivers',
    );
    
    if (cached != null) {
      final timestamp = DateTime.parse(cached['timestamp']);
      if (DateTime.now().difference(timestamp) < const Duration(minutes: 5)) {
        final List<dynamic> data = cached['data'];
        return data.map((json) => DriverLocation.fromJson(json)).toList();
      }
    }
    return null;
  }
  
  // Payment methods cache
  Future<void> cachePaymentMethods(List<Map<String, dynamic>> methods) async {
    await _hiveService.saveToBox(
      HiveService.paymentMethodsBox, 
      'methods', 
      methods
    );
  }
  
  List<Map<String, dynamic>>? getCachedPaymentMethods() {
    return _hiveService.getFromBox<List<Map<String, dynamic>>>(
      HiveService.paymentMethodsBox, 
      'methods'
    );
  }
  
  // Check if user is logged in (has token)
  Future<bool> isLoggedIn() async {
    final token = await _secureStorage.getAccessToken();
    return token != null;
  }
  
  // Get user with fallback to cache
  Future<Map<String, dynamic>?> getUserWithFallback() async {
    final cachedUser = _hiveService.getUserData();
    if (cachedUser != null) {
      return cachedUser;
    }
    return null;
  }
}