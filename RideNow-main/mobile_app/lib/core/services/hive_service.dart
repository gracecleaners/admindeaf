import 'package:hive_flutter/hive_flutter.dart';
import 'package:path_provider/path_provider.dart';

class HiveService {
  static final HiveService _instance = HiveService._internal();
  factory HiveService() => _instance;
  HiveService._internal();
  
  // Box names
  static const String userBox = 'user_data';
  static const String rideHistoryBox = 'ride_history';
  static const String nearbyDriversBox = 'nearby_drivers';
  static const String appSettingsBox = 'app_settings';
  static const String cachedLocationsBox = 'cached_locations';
  static const String paymentMethodsBox = 'payment_methods';
  
  Future<void> init() async {
    try {
      // Initialize Hive with path
      final appDocumentDir = await getApplicationDocumentsDirectory();
      Hive.init(appDocumentDir.path);
      
      // Register adapters (call this after generating adapters)
      // Hive.registerAdapter(UserModelAdapter());
      // Hive.registerAdapter(RideModelAdapter());
      // Hive.registerAdapter(PaymentMethodAdapter());
      
      // Open all boxes
      await Future.wait([
        Hive.openBox(userBox),
        Hive.openBox(rideHistoryBox),
        Hive.openBox(nearbyDriversBox),
        Hive.openBox(appSettingsBox),
        Hive.openBox(cachedLocationsBox),
        Hive.openBox(paymentMethodsBox),
      ]);
      
      print('Hive initialized successfully');
    } catch (e) {
      print('Error initializing Hive: $e');
    }
  }
  
  // Generic methods
  Future<void> saveToBox<T>(String boxName, String key, T value) async {
    final box = Hive.box(boxName);
    await box.put(key, value);
  }
  
  T? getFromBox<T>(String boxName, String key) {
    final box = Hive.box(boxName);
    return box.get(key) as T?;
  }
  
  Future<void> deleteFromBox(String boxName, String key) async {
    final box = Hive.box(boxName);
    await box.delete(key);
  }
  
  Future<void> clearBox(String boxName) async {
    final box = Hive.box(boxName);
    await box.clear();
  }
  
  bool containsKey(String boxName, String key) {
    final box = Hive.box(boxName);
    return box.containsKey(key);
  }
  
  // User data specific methods
  Future<void> saveUserData(Map<String, dynamic> userData) async {
    await saveToBox(userBox, 'current_user', userData);
  }
  
  Map<String, dynamic>? getUserData() {
    return getFromBox<Map<String, dynamic>>(userBox, 'current_user');
  }
  
  // Ride history specific methods
  Future<void> saveRideHistory(List<Map<String, dynamic>> rides) async {
    await saveToBox(rideHistoryBox, 'history', rides);
  }
  
  List<Map<String, dynamic>>? getRideHistory() {
    return getFromBox<List<Map<String, dynamic>>>(rideHistoryBox, 'history');
  }
  
  // Nearby drivers cache
  Future<void> cacheNearbyDrivers(List<Map<String, dynamic>> drivers) async {
    await saveToBox(nearbyDriversBox, 'drivers', {
      'data': drivers,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }
  
  Map<String, dynamic>? getCachedNearbyDrivers() {
    return getFromBox<Map<String, dynamic>>(nearbyDriversBox, 'drivers');
  }
  
  // Check if cache is valid (e.g., less than 5 minutes old)
  bool isCacheValid(String boxName, String key, Duration maxAge) {
    final cacheData = getFromBox<Map<String, dynamic>>(boxName, key);
    if (cacheData == null || cacheData['timestamp'] == null) return false;
    
    final cachedTime = DateTime.parse(cacheData['timestamp']);
    final now = DateTime.now();
    
    return now.difference(cachedTime) < maxAge;
  }
  
  // App settings
  Future<void> saveAppSetting(String key, dynamic value) async {
    await saveToBox(appSettingsBox, key, value);
  }
  
  dynamic getAppSetting(String key) {
    return getFromBox(appSettingsBox, key);
  }
  
  // Location cache
  Future<void> cacheLocation(String address, Map<String, dynamic> locationData) async {
    await saveToBox(cachedLocationsBox, address, locationData);
  }
  
  Map<String, dynamic>? getCachedLocation(String address) {
    return getFromBox<Map<String, dynamic>>(cachedLocationsBox, address);
  }
  
  // Clear all cached data (except secure data)
  Future<void> clearAllCache() async {
    await Future.wait([
      clearBox(userBox),
      clearBox(rideHistoryBox),
      clearBox(nearbyDriversBox),
      clearBox(cachedLocationsBox),
      clearBox(paymentMethodsBox),
    ]);
  }
}