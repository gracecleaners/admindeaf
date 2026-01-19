import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile_app/controllers/auth_controller.dart';
import 'package:mobile_app/core/routes/app_routes.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initializeApp();
  }
  
  Future<void> _initializeApp() async {
    final AuthController authController = Get.find<AuthController>();
    
    // Check if user is logged in
    await authController.checkLoginStatus();
    
    // Add delay for smooth transition
    await Future.delayed(const Duration(milliseconds: 1500));
    
    if (authController.isLoggedIn.value) {
      Get.offAllNamed(Routes.nav); // Go to main layout
    } else {
      Get.offAllNamed(Routes.login); // Go to login screen
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Your app logo
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: Colors.green,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Icon(
                Icons.local_taxi,
                size: 60,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Zyra Ride',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.green,
              ),
            ),
            const SizedBox(height: 10),
            const CircularProgressIndicator(
              color: Colors.green,
            ),
          ],
        ),
      ),
    );
  }
}
