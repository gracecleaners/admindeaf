import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile_app/core/routes/app_routes.dart';
import 'package:mobile_app/views/auth/login_screen.dart';
import 'package:mobile_app/views/auth/register.dart';
import 'package:mobile_app/views/auth/verify.dart';
import 'package:mobile_app/views/screens/book_ride.dart';
import 'package:mobile_app/views/screens/dashboard.dart';
import 'package:mobile_app/views/screens/google_map.dart';
import 'package:mobile_app/views/screens/my_rides.dart';
import 'package:mobile_app/views/layout/main_layout.dart';
import 'package:mobile_app/views/screens/profile.dart';
import 'package:mobile_app/views/screens/splash_screen.dart';

class AppPages {
  static const initial = Routes.splash;
  static final routes = [
    GetPage(name: Routes.splash, page: () => const SplashScreen()),
    GetPage(name: Routes.nav, page:()=> const MainLayout()),
    GetPage(name: Routes.home, page:()=> const MainLayout()), // Redirect home to main layout
    GetPage(name: Routes.myRide, page: () => const MyRidesScreen()),
    GetPage(name: Routes.profile, page: () => const ProfileScreen()),
    GetPage(name: Routes.register, page: ()=> RegistrationScreen()),
    GetPage(name: Routes.bookRide, page: ()=> const BookRideScreen()),
    // Placeholders for missing screens
    GetPage(name: Routes.rideDetail, page: () => Scaffold(appBar: AppBar(title: Text('Ride Detail')), body: Center(child: Text('Ride Detail')))),
    GetPage(name: Routes.support, page: () => Scaffold(appBar: AppBar(title: Text('Support')), body: Center(child: Text('Support')))),
    GetPage(name: Routes.payments, page: () => Scaffold(appBar: AppBar(title: Text('Payments')), body: Center(child: Text('Payments')))),
    GetPage(name: Routes.notifications, page: () => Scaffold(appBar: AppBar(title: Text('Notifications')), body: Center(child: Text('Notifications')))),
    GetPage(name: Routes.settings, page: () => Scaffold(appBar: AppBar(title: Text('Settings')), body: Center(child: Text('Settings')))),
    GetPage(name: Routes.favorites, page: () => Scaffold(appBar: AppBar(title: Text('Favorites')), body: Center(child: Text('Favorites')))),
    GetPage(name: Routes.vehiclePreferences, page: () => Scaffold(appBar: AppBar(title: Text('Vehicle Preferences')), body: Center(child: Text('Vehicle Preferences')))),
    GetPage(name: Routes.help, page: () => Scaffold(appBar: AppBar(title: Text('Help')), body: Center(child: Text('Help')))),
    GetPage(name: Routes.contactSupport, page: () => Scaffold(appBar: AppBar(title: Text('Contact Support')), body: Center(child: Text('Contact Support')))),
    GetPage(name: Routes.privacy, page: () => Scaffold(appBar: AppBar(title: Text('Privacy Policy')), body: Center(child: Text('Privacy Policy')))),
    GetPage(name: Routes.terms, page: () => Scaffold(appBar: AppBar(title: Text('Terms of Service')), body: Center(child: Text('Terms of Service')))),
    GetPage(name: Routes.deleteAccount, page: () => Scaffold(appBar: AppBar(title: Text('Delete Account')), body: Center(child: Text('Delete Account')))),
    GetPage(name: Routes.security, page: () => Scaffold(appBar: AppBar(title: Text('Security')), body: Center(child: Text('Security')))),
    GetPage(name: Routes.language, page: () => Scaffold(appBar: AppBar(title: Text('Language')), body: Center(child: Text('Language')))),
    GetPage(
      name: Routes.googleMap,
      page: () => GoogleMapFlutter(
        onLocationSelected: (location) {
          // Handle location selection
          // You can use Get.back() with result or update a controller
          print('Location selected: ${location.displayName}');
        },
        onCurrentLocationObtained: (position) {
          // Handle current location
          print('Current location: ${position.latitude}, ${position.longitude}');
        },
      ),
    ),
    GetPage(name: Routes.verify, page: ()=> EmailVerificationScreen(email: Get.arguments['email'] ?? '',)),
    GetPage(name: Routes.login, page: () => LoginScreen()),
  ];
}
