import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_app/core/services/cache_manager.dart';
import 'package:mobile_app/model/user_model.dart';
import 'package:mobile_app/core/routes/app_routes.dart';
import '../../core/services/auth_api_service.dart';

class AuthController extends GetxController {
  final AuthApiService _authApiService = Get.find<AuthApiService>();
  final CacheManager _cacheManager = Get.find<CacheManager>();
  final ImagePicker _picker = ImagePicker();
  final TextEditingController firstNameController = TextEditingController();
  final TextEditingController lastNameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController phoneNumberController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController confirmPasswordController =
      TextEditingController();

  // Observables
  var isLoading = false.obs;
  var isLoggedIn = false.obs;
  var user = Rxn<User>();
  var selectedUserType = 'client'.obs;

  // Form states
  var loginEmail = ''.obs;
  var loginPassword = ''.obs;

  @override
  void onInit() {
    super.onInit();

    // initiating reactive values from controllers
    firstNameController.addListener(() => update());
    lastNameController.addListener(() => update());
    emailController.addListener(() => update());
    phoneNumberController.addListener(() => update());
    passwordController.addListener(() => update());
    confirmPasswordController.addListener(() => update());
    checkLoginStatus();
  }

  @override
  void onClose() {
    firstNameController.dispose();
    lastNameController.dispose();
    emailController.dispose();
    phoneNumberController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    super.onClose();
  }

 // In AuthController class - update checkLoginStatus method:
Future<void> checkLoginStatus() async {
  try {
    final isLoggedInCache = await _cacheManager.isLoggedIn();
    print('=== CHECK LOGIN STATUS ===');
    print('Is logged in cache: $isLoggedInCache');
    
    if (isLoggedInCache) {
      // Try to fetch user profile to validate token
      try {
        await fetchUserProfile();
        isLoggedIn.value = true;
        
        // Navigate to home if not already there
        if (Get.currentRoute != Routes.home) {
          Get.offAllNamed(Routes.home);
        }
      } catch (e) {
        print('Token validation failed: $e');
        // Token might be expired, clear cache
        await _cacheManager.logout();
        isLoggedIn.value = false;
      }
    } else {
      isLoggedIn.value = false;
    }
  } catch (e) {
    print('Error checking login status: $e');
    isLoggedIn.value = false;
  }
}

  // Login with email
  // In AuthController class - UPDATE THE login method:
Future<void> login() async {
  try {
    isLoading.value = true;
    print('=== AUTH CONTROLLER LOGIN ===');
    print('Email: ${loginEmail.value}');
    print('Password: ${loginPassword.value.isNotEmpty ? "***" : "empty"}');

    final response = await _authApiService.login(
      loginEmail.value,
      loginPassword.value,
    );

    // Save tokens and user data
    print('Login successful, saving tokens...');
    await _cacheManager.saveUserData(
      userData: response.user.toJson(),
      accessToken: response.access,
      refreshToken: response.refresh,
    );

    user.value = response.user;
    isLoggedIn.value = true;

    // Clear form fields
    loginEmail.value = '';
    loginPassword.value = '';

    print('User isDriver: ${response.user.isDriver}');
    
    // Navigate based on user type
    if (response.user.isDriver) {
      Get.offAllNamed(Routes.home);
    } else {
      Get.offAllNamed(Routes.home);
    }

    Get.snackbar(
      'Success', 
      'Logged in successfully',
      backgroundColor: Colors.green,
      colorText: Colors.white,
    );
  } catch (e) {
    print('Login error in controller: $e');
    
    // Show more specific error messages
    String errorMessage = 'Login failed';
    if (e.toString().contains('401')) {
      errorMessage = 'Invalid email or password';
    } else if (e.toString().contains('400')) {
      errorMessage = 'Bad request. Please check your input.';
    } else if (e.toString().contains('403')) {
      errorMessage = 'Account not verified. Please verify your email first.';
    } else if (e.toString().contains('404')) {
      errorMessage = 'Account not found. Please sign up first.';
    } else if (e.toString().contains('500')) {
      errorMessage = 'Server error. Please try again later.';
    }
    
    Get.snackbar(
      'Error', 
      '$errorMessage: ${e.toString()}',
      backgroundColor: Colors.red,
      colorText: Colors.white,
      duration: Duration(seconds: 4),
    );
  } finally {
    isLoading.value = false;
  }
}

  // Register Client
  Future<void> registerClient() async {
    try {
      isLoading.value = true;

      // Validate passwords match
      if (passwordController.text != confirmPasswordController.text) {
        Get.snackbar('Error', 'Passwords do not match');
        return;
      }

      final request = ClientRegisterRequest(
        firstName: firstNameController.text,
        lastName: lastNameController.text,
        email: emailController.text,
        password: passwordController.text,
        confirmPassword: confirmPasswordController.text,
        phone: phoneNumberController.text.isEmpty
            ? null
            : phoneNumberController.text,
      );

      final response = await _authApiService.registerClient(request);

      // Navigate to email verification screen
      Get.offAllNamed(
        '/verify-email',
        arguments: {
          'email': emailController.text,
          'userType': 'client',
        },
      );

      Get.snackbar(
        'Success',
        'Registration successful! Please verify your email.',
      );
    } catch (e) {
      Get.snackbar('Error', 'Registration failed: ${e.toString()}');
      print('Registration failed: ${e.toString()}');
    } finally {
      isLoading.value = false;
    }
  }

  // // Register Driver
  // Future<void> registerDriver() async {
  //   try {
  //     isLoading.value = true;

  //     // Validate passwords match
  //     if (regPassword.value != regConfirmPassword.value) {
  //       Get.snackbar('Error', 'Passwords do not match');
  //       return;
  //     }

  //     // Validate driver specific fields
  //     if (driverLicenseNumber.value.isEmpty) {
  //       Get.snackbar('Error', 'License number is required');
  //       return;
  //     }

  //     final request = DriverRegisterRequest(
  //       name: regName.value,
  //       email: regEmail.value,
  //       password: regPassword.value,
  //       confirmPassword: regConfirmPassword.value,
  //       phone: regPhone.value.isEmpty ? null : regPhone.value,
  //       gender: regGender.value.isEmpty ? null : regGender.value,
  //       dateOfBirth: regDateOfBirth.value.isEmpty ? null : regDateOfBirth.value,
  //       licenseNumber: driverLicenseNumber.value,
  //       yearsOfExperience: int.tryParse(driverYearsOfExperience.value),
  //       vehicleType:
  //           driverVehicleType.value.isEmpty ? null : driverVehicleType.value,
  //       vehicleRegistration: driverVehicleRegistration.value.isEmpty
  //           ? null
  //           : driverVehicleRegistration.value,
  //     );

  //     final response = await _authApiService.registerDriver(request);

  //     // Navigate to email verification screen
  //     Get.offAllNamed(
  //       '/verify-email',
  //       arguments: {
  //         'email': regEmail.value,
  //         'userType': 'driver',
  //       },
  //     );

  //     Get.snackbar(
  //       'Success',
  //       'Registration successful! Please verify your email.',
  //     );
  //   } catch (e) {
  //     Get.snackbar('Error', 'Registration failed: ${e.toString()}');
  //   } finally {
  //     isLoading.value = false;
  //   }
  // }

  // Verify Email
  // In AuthController class - UPDATE THIS METHOD:
Future<void> verifyEmail(String email, String otp) async {
  try {
    isLoading.value = true;
    print('Verifying email: $email with OTP: $otp');

    await _authApiService.verifyEmail(email, otp);

    Get.offAllNamed('/login');
    Get.snackbar(
      'Success', 
      'Email verified successfully! You can now login.',
      duration: Duration(seconds: 4),
    );
  } catch (e) {
    print('Email verification error: $e');
    Get.snackbar(
      'Error', 
      'Email verification failed: ${e.toString()}',
      duration: Duration(seconds: 4),
    );
  } finally {
    isLoading.value = false;
  }
}

  // Resend OTP
  Future<void> resendOtp(String email) async {
    try {
      isLoading.value = true;

      await _authApiService.resendOtp(email);

      Get.snackbar('Success', 'OTP sent to your email');
    } catch (e) {
      Get.snackbar('Error', 'Failed to resend OTP: ${e.toString()}');
    } finally {
      isLoading.value = false;
    }
  }

  // Fetch User Profile
  Future<void> fetchUserProfile() async {
    try {
      final profile = await _authApiService.getProfile();
      user.value = profile;

      // Update cache
      await _cacheManager.saveUserData(userData: profile.toJson());
    } catch (e) {
      print('Error fetching profile: $e');
    }
  }

  // Update Profile
  Future<void> updateProfile({
    String? name,
    String? phone,
    String? gender,
    String? dateOfBirth,
  }) async {
    try {
      isLoading.value = true;

      final request = UpdateProfileRequest(
        name: name,
        phone: phone,
        gender: gender,
        dateOfBirth: dateOfBirth,
      );

      final updatedUser = await _authApiService.updateProfile(request);
      user.value = updatedUser;

      // Update cache
      await _cacheManager.saveUserData(userData: updatedUser.toJson());

      Get.back();
      Get.snackbar('Success', 'Profile updated successfully');
    } catch (e) {
      Get.snackbar('Error', 'Failed to update profile: ${e.toString()}');
    } finally {
      isLoading.value = false;
    }
  }

  // Upload Profile Image
  Future<void> uploadProfileImage() async {
    try {
      final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
      if (pickedFile == null) return;

      isLoading.value = true;

      // Update user profile with new image
      final updatedUser = User(
        id: user.value!.id,
        name: user.value!.name,
        email: user.value!.email,
        isClient: user.value!.isClient,
        isDriver: user.value!.isDriver,
        username: user.value!.username,
        profileImage: user.value!.profileImage, // adding this just in case as well
        phone: user.value!.phone,
        gender: user.value!.gender,
        dateOfBirth: user.value!.dateOfBirth,
        firstName: user.value!.firstName,
        lastName: user.value!.lastName,
      );

      user.value = updatedUser;

      // Update cache
      await _cacheManager.saveUserData(userData: updatedUser.toJson());

      Get.snackbar('Success', 'Profile image updated');
    } catch (e) {
      Get.snackbar('Error', 'Failed to upload image: ${e.toString()}');
    } finally {
      isLoading.value = false;
    }
  }

  // Change Password
  Future<void> changePassword(
    String oldPassword,
    String newPassword,
    String confirmNewPassword,
  ) async {
    try {
      isLoading.value = true;

      await _authApiService.changePassword(
        oldPassword,
        newPassword,
        confirmNewPassword,
      );

      Get.back();
      Get.snackbar('Success', 'Password changed successfully');
    } catch (e) {
      Get.snackbar('Error', 'Failed to change password: ${e.toString()}');
    } finally {
      isLoading.value = false;
    }
  }

  // Request Password Reset
  Future<void> requestPasswordReset(String email) async {
    try {
      isLoading.value = true;

      await _authApiService.requestPasswordReset(email);

      Get.toNamed(
        '/reset-password-instructions',
        arguments: {'email': email},
      );

      Get.snackbar('Success', 'Password reset instructions sent to your email');
    } catch (e) {
      Get.snackbar(
          'Error', 'Failed to request password reset: ${e.toString()}');
    } finally {
      isLoading.value = false;
    }
  }

  // Logout
  Future<void> logout() async {
    try {
      isLoading.value = true;
      await _authApiService.logout();
    } catch (e) {
      print('Logout API error: $e');
    } finally {
      // Clear cache and local data
      await _cacheManager.logout();

      // Reset state
      isLoggedIn.value = false;
      user.value = null;

      // Navigate to login
      Get.offAllNamed('/welcome');

      isLoading.value = false;
    }
  }

  // Form validators
  String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }
    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
      return 'Please enter a valid email';
    }
    return null;
  }

  String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }
    if (value.length < 6) {
      return 'Password must be at least 6 characters';
    }
    return null;
  }

  String? validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please confirm your password';
    }
    if (value != passwordController.text) {
      return 'Passwords do not match';
    }
    return null;
  }

  String? validateName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Name is required';
    }
    if (value.length < 2) {
      return 'Name must be at least 2 characters';
    }
    return null;
  }

  // Select user type
  void selectUserType(String type) {
    selectedUserType.value = type;
  }
}
