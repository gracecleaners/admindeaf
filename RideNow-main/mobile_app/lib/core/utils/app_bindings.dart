import 'package:get/get.dart';
import 'package:mobile_app/controllers/auth_controller.dart';
import 'package:mobile_app/controllers/ride_controller.dart';
import 'package:mobile_app/core/services/api_service.dart';
import 'package:mobile_app/core/services/auth_api_service.dart';
import 'package:mobile_app/core/services/cache_manager.dart';
import 'package:mobile_app/core/services/ride_api_service.dart';

class AppBinding extends Bindings {
  @override
  void dependencies() {
    // Core services
    Get.put(CacheManager(), permanent: true);
    Get.put(ApiService(), permanent: true);
    Get.put(RideApiService(), permanent: true);
    Get.put(AuthApiService(), permanent: true);

    // Controllers
    Get.lazyPut(() => AuthController(), fenix: true);
    Get.lazyPut(() => RideController(), fenix: true);
  }
}
