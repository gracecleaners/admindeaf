import 'dart:convert';
import 'package:get/get.dart';
import 'package:mobile_app/core/constants/api_endpoints.dart';
import 'package:mobile_app/core/services/cache_manager.dart';
import 'package:mobile_app/model/user_model.dart';
import 'api_service.dart';

class AuthApiService extends GetxService {
  final ApiService _apiService = Get.find<ApiService>();
  final CacheManager _cacheManager = Get.find<CacheManager>();
  
  // Initialize service
  Future<AuthApiService> init() async {
    return this;
  }
  
  // Login with email and password
  // In AuthApiService class - UPDATE THE login method:
Future<LoginResponse> login(String email, String password) async {
  try {
    print('=== LOGIN DEBUG ===');
    print('Email: $email');
    print('Password: ${password.isNotEmpty ? "***" : "empty"}');
    print('Endpoint: ${ApiEndpoints.login}');
    
    final response = await _apiService.post(
      ApiEndpoints.login,
      body: {
        'username_or_email_or_phone': email,
        'password': password,
      },
      requireAuth: false, // Login doesn't need auth token
    );
    
    print('Response status: ${response.statusCode}');
    print('Response headers: ${response.headers}');
    print('Response body: ${response.body}');
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return LoginResponse.fromJson(data);
    }
    
    // Parse error response for better error messages
    String errorMessage = 'Login failed with status ${response.statusCode}';
    try {
      final errorData = json.decode(response.body);
      print('Error data: $errorData');
      
      if (errorData is Map) {
        errorMessage = errorData['message'] ?? 
                      errorData['detail'] ?? 
                      errorData['error'] ??
                      errorData['non_field_errors']?.toString() ??
                      json.encode(errorData);
      }
    } catch (e) {
      errorMessage = 'Server error: ${response.body}';
    }
    
    throw Exception(errorMessage);
  } catch (e) {
    print('Login exception: $e');
    rethrow;
  }
}
  
  // Client Registration
 Future<Map<String, dynamic>> registerClient(ClientRegisterRequest request) async {
  try {
    print('=== REGISTRATION DEBUG ===');
    print('Endpoint: ${ApiEndpoints.clientRegister}');
    print('Request body: ${json.encode(request.toJson())}');
    
    final response = await _apiService.post(
      ApiEndpoints.clientRegister,
      body: request.toJson(),
      requireAuth: false,
    );
    
    print('Response status: ${response.statusCode}');
    print('Response body: ${response.body}');
    print('Response headers: ${response.headers}');
    
    if (response.statusCode == 201 || response.statusCode == 200) {
      return json.decode(response.body) as Map<String, dynamic>;
    }
    
    // Parse error message from 400 response
    String errorMessage = 'Registration failed';
    try {
      final errorData = json.decode(response.body);
      print('Error data: $errorData');
      
      // Handle different error formats
      if (errorData is Map) {
        // Try common error field names
        errorMessage = errorData['message'] ?? 
                      errorData['detail'] ?? 
                      errorData['error'] ??
                      errorData['non_field_errors']?.toString() ??
                      json.encode(errorData); // Show full error object
      }
    } catch (e) {
      errorMessage = 'Server error: ${response.body}';
    }
    
    throw Exception(errorMessage);
  } catch (e) {
    print('Registration exception: $e');
    rethrow;
  }
}
  
  // Driver Registration
  Future<Map<String, dynamic>> registerDriver(DriverRegisterRequest request) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.driverRegister,
        body: request.toJson(),
      );
      
      if (response.statusCode == 201) {
        return json.decode(response.body);
      }
      
      throw Exception('Driver registration failed: ${response.statusCode}');
    } catch (e) {
      rethrow;
    }
  }
  
  // Verify Email with OTP
 // In AuthApiService class - UPDATE THIS METHOD:
Future<void> verifyEmail(String email, String otp) async {
  try {
    print('=== VERIFY EMAIL DEBUG ===');
    print('Email: $email');
    print('OTP: $otp');
    print('Endpoint: ${ApiEndpoints.verifyEmail}');
    
    print('Request body: ${json.encode({'email': email, 'verification_code': otp})}');
    
    final response = await _apiService.post(
      ApiEndpoints.verifyEmail,
      body: {
        'email': email,
        'verification_code': otp,
      },
      requireAuth: false,
    );
    
    print('Response status: ${response.statusCode}');
    print('Response body: ${response.body}');
    
    if (response.statusCode == 200) {
      return;
    }
    
    // Parse error response
    String errorMessage = 'Verification failed';
    try {
      final errorData = json.decode(response.body);
      print('Error data: $errorData');
      
      if (errorData is Map) {
        errorMessage = errorData['message'] ?? 
                      errorData['detail'] ?? 
                      errorData['error'] ??
                      errorData['non_field_errors']?.toString() ??
                      'Status: ${response.statusCode}';
      }
    } catch (e) {
      errorMessage = 'Server error: ${response.body}';
    }
    
    throw Exception(errorMessage);
  } catch (e) {
    print('Verify email exception: $e');
    rethrow;
  }
}
  // Resend OTP
  Future<void> resendOtp(String email) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.resendOtp,
        body: {'email': email},
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to resend OTP: ${response.statusCode}');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  // Get User Profile
  Future<User> getProfile() async {
    try {
      final response = await _apiService.get(ApiEndpoints.profileMgt);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return User.fromJson(data);
      }
      
      throw Exception('Failed to get profile: ${response.statusCode}');
    } catch (e) {
      rethrow;
    }
  }
  
  // Update Profile
  Future<User> updateProfile(UpdateProfileRequest request) async {
    try {
      final response = await _apiService.put(
        ApiEndpoints.updateProfile,
        body: request.toJson(),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return User.fromJson(data);
      }
      
      throw Exception('Failed to update profile: ${response.statusCode}');
    } catch (e) {
      rethrow;
    }
  }
  
  // Upload Profile Image
  // Future<String> uploadProfileImage(String imagePath) async {
  //   try {
  //     final response = await _apiService.multipartRequest(
  //       ApiConstants.uploadProfileImage,
  //       method: 'POST',
  //       files: {'profile_image': imagePath},
  //     );
      
  //     if (response.statusCode == 200) {
  //       final data = json.decode(response.body);
  //       return data['profile_image'];
  //     }
      
  //     throw Exception('Failed to upload image: ${response.statusCode}');
  //   } catch (e) {
  //     rethrow;
  //   }
  // }
  
  // Change Password
  Future<void> changePassword(
    String oldPassword,
    String newPassword,
    String confirmNewPassword,
  ) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.changePassword,
        body: {
          'old_password': oldPassword,
          'new_password': newPassword,
          'confirm_new_password': confirmNewPassword,
        },
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to change password: ${response.statusCode}');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  // Reset Password Request
  Future<void> requestPasswordReset(String email) async {
    try {
      final response = await _apiService.post(
        ApiEndpoints.resetPassword,
        body: {'email': email},
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to request password reset: ${response.statusCode}');
      }
    } catch (e) {
      rethrow;
    }
  }
  
  // Logout
  Future<void> logout() async {
    try {
      await _apiService.post(ApiEndpoints.logout);
    } catch (e) {
      print('Logout API error: $e');
    }
  }
  
}