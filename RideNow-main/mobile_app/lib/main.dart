import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:get/get.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';
import 'package:mobile_app/controllers/auth_controller.dart';
import 'package:mobile_app/core/routes/app_pages.dart';
import 'package:mobile_app/core/routes/app_routes.dart';
import 'package:mobile_app/core/services/cache_manager.dart';
import 'package:mobile_app/core/utils/app_bindings.dart';
import 'package:mobile_app/model/user_model.dart';
import 'package:mobile_app/views/screens/splash_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive
  await Hive.initFlutter();
  
  // Register Hive adapters
  Hive.registerAdapter(UserAdapter());

  await setup();
  
  runApp(MyApp());
}

Future<void> setup() async {
  await dotenv.load(fileName: ".env");
  MapboxOptions.setAccessToken(dotenv.env["MAPBOX_ACCESS_TOKEN"]!);
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Zyra Ride',
      theme: ThemeData(
        primarySwatch: Colors.green,
        useMaterial3: true,
      ),
      initialBinding: AppBinding(),
      initialRoute: Routes.splash,
      getPages: AppPages.routes,
    );
  }
}
