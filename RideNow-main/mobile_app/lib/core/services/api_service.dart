import 'dart:convert';

import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:mobile_app/core/constants/api_endpoints.dart';
import 'package:mobile_app/core/services/secure_storage_service.dart';

class ApiService extends GetxService {
  final SecureStorageService _secureStorageService = SecureStorageService();

  // request headers
  final Map<String, String> _defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // getting headers with the access token
 Future<Map<String, String>> _getHeaders({bool requireAuth = true}) async {
  final headers = Map<String, String>.from(_defaultHeaders);
  
  if (requireAuth) {
    final accessToken = await _secureStorageService.getAccessToken();
    if (accessToken != null && accessToken.isNotEmpty) {
      headers['Authorization'] = 'Bearer $accessToken';
    }
  }
  
  return headers;
}
  // handling errors
  String _handleError(http.Response response) {
    try {
      final errorData = json.decode(response.body);
      return errorData['message'] ??
          errorData['detail'] ??
          'Error: ${response.statusCode}';
    } catch (e) {
      return 'Error: ${response.statusCode} ${response.reasonPhrase}';
    }
  }

  // HANDLING REFRESH TOKEN
  Future<bool> _refreshToken() async {
    try {
      final refreshToken =await _secureStorageService.getRefreshToken();

      final response = await http.post(
          Uri.parse('${ApiEndpoints.authentication}/refresh'),
          headers: _defaultHeaders,
          body: json.encode({'refresh': refreshToken}));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final newToken = data['access'];
        final newRefreshToken = data['refresh'];

        await _secureStorageService.saveAccessToken(newToken);
        if (newRefreshToken != null) {
          await _secureStorageService.saveRefreshToken(newRefreshToken);
        }
        return true;
      }
    } catch (err) {
      print('refresh token failed $err');
    }
    return false;
  }

  // HANDLING UNAUTHORIZED RESPONSE
  Future<http.Response> _handleUnauthorized(
    Future<http.Response> Function() requestFunction,
  ) async {
    final response = await requestFunction();

    if (response.statusCode == 401) {
      // Try to refresh token
      final refreshed = await _refreshToken();
      if (refreshed) {
        // Retry the original request
        return await requestFunction();
      } else {
        // Logout user
        // await _cacheManager.logout();
        Get.offAllNamed('/login');
        throw Exception('Session expired. Please login again.');
      }
    }

    return response;
  }

// GET request
  Future<http.Response> get(
    String endpoint, {
    Map<String, dynamic>? queryParams,
    bool useCache = true,
    Duration cacheDuration = const Duration(minutes: 5),
  }) async {
    // Build URL with query parameters
    Uri uri = Uri.parse('$endpoint');
    if (queryParams != null) {
      uri = uri.replace(queryParameters: queryParams);
    }

    Future<http.Response> requestFunction() async {
      final headers = await _getHeaders();
      return await http.get(uri, headers: headers);
    }

    try {
      final response = await _handleUnauthorized(requestFunction);
      return response;
    } catch (e) {
      rethrow;
    }
  }

  // POST request
  Future<http.Response> post(
    String endpoint, {
    dynamic body,
    Map<String, String>? headers,
    bool requireAuth = true,
  }) async {
    Future<http.Response> requestFunction() async {
      final defaultHeaders = await _getHeaders();
      final mergedHeaders = {...defaultHeaders, ...?headers};

      return await http.post(
        Uri.parse('$endpoint'),
        headers: mergedHeaders,
        body: body is String ? body : json.encode(body),
      );
    }

    if (!requireAuth) {
    return await requestFunction();
  }

    return await _handleUnauthorized(requestFunction);
  }

  // PUT request
  Future<http.Response> put(
    String endpoint, {
    dynamic body,
    Map<String, String>? headers,
  }) async {
    Future<http.Response> requestFunction() async {
      final defaultHeaders = await _getHeaders();
      final mergedHeaders = {...defaultHeaders, ...?headers};

      return await http.put(
        Uri.parse('$endpoint'),
        headers: mergedHeaders,
        body: body is String ? body : json.encode(body),
      );
    }

    return await _handleUnauthorized(requestFunction);
  }

  // PATCH request
  Future<http.Response> patch(
    String endpoint, {
    dynamic body,
    Map<String, String>? headers,
  }) async {
    Future<http.Response> requestFunction() async {
      final defaultHeaders = await _getHeaders();
      final mergedHeaders = {...defaultHeaders, ...?headers};

      return await http.patch(
        Uri.parse('$endpoint'),
        headers: mergedHeaders,
        body: body is String ? body : json.encode(body),
      );
    }

    return await _handleUnauthorized(requestFunction);
  }

  // DELETE request
  Future<http.Response> delete(
    String endpoint, {
    Map<String, String>? headers,
  }) async {
    Future<http.Response> requestFunction() async {
      final defaultHeaders = await _getHeaders();
      final mergedHeaders = {...defaultHeaders, ...?headers};

      return await http.delete(
        Uri.parse('$endpoint'),
        headers: mergedHeaders,
      );
    }

    return await _handleUnauthorized(requestFunction);
  }
}
