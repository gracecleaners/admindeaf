// profile_controller.dart
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ProfileController extends GetxController {

  final scaffoldKey = GlobalKey<ScaffoldState>();

  // User Information
  var firstName = "Linc".obs;
  var lastName = "User".obs;
  var otherName = "".obs;
  var email = "linc@example.com".obs;
  var phone = "+256 700 000 000".obs;
  var country = "Uganda".obs;
  var gender = "Male".obs;
  var dateOfBirth = "01/01/1990".obs;
  var city = "Kampala".obs;
  var bio = "".obs;
  var interests = "".obs;

  // Menu Management
  var selectedMenuIndex = 0.obs;
  var isSidebarExpanded = true.obs;

  // Preferences
  var emailNotifications = true.obs;
  var smsNotifications = false.obs;
  var pushNotifications = true.obs;
  var marketingEmails = false.obs;
  var profileVisibility = 'Public'.obs;
  var language = 'English'.obs;
  var timezone = 'Africa/Kampala (EAT)'.obs;
  var preferredPaymentMethod = 'Cash'.obs;
  var minDriverRating = 4.0.obs;
  var preferredVehicleType = 'Any'.obs;

  // Security
  var twoFactorAuth = false.obs;
  var loginAlerts = true.obs;
  var sessionTimeout = 30.obs;
  var dataSharingConsent = true.obs;
  var analyticsTracking = true.obs;
  var locationTracking = true.obs;
  var apiAccess = false.obs;
  var connectGoogle = false.obs;
  var connectApple = false.obs;
  var maxConcurrentSessions = 3.obs;

  // Password Change
  var currentPassword = "".obs;
  var newPassword = "".obs;
  var confirmPassword = "".obs;

  // Account Deletion
  var deleteWarning = false.obs;
  var deleteReason = "".obs;
  var deleteFeedback = "".obs;
  var deleteConfirm = false.obs;

  void selectMenu(int index) {
    selectedMenuIndex.value = index;
  }

  void toggleSidebar() {
    isSidebarExpanded.value = !isSidebarExpanded.value;
  }

  void updateProfileInfo() {
    // Implementation for updating profile info
    Get.snackbar("Success", "Profile updated successfully");
  }

  void changePassword() {
    // Implementation for changing password
    if (newPassword.value != confirmPassword.value) {
      Get.snackbar("Error", "Passwords do not match");
      return;
    }
    Get.snackbar("Success", "Password changed successfully");
  }

  void deleteAccount() {
    if (!deleteWarning.value || !deleteConfirm.value) {
      Get.snackbar("Error", "Please confirm all warnings");
      return;
    }
    // Implementation for deleting account
    Get.snackbar("Success", "Account deletion requested");
  }
}