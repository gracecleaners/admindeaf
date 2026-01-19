import 'dart:convert';

import 'package:http/http.dart' as http;

class HttpResponseHandler {
  static dynamic handleResponse(http.Response response) {
    switch (response.statusCode) {
      case 200:
      case 201:
        return _parseResponse(response);
      case 400:
        throw Exception('Bad request: ${response.body}');
      case 401:
        throw Exception('Unauthorized: Please login again');
      case 403:
        throw Exception('Forbidden: ${response.body}');
      case 404:
        throw Exception('Not found: ${response.body}');
      case 500:
        throw Exception('Server error: ${response.body}');
      default:
        throw Exception(
          'Error occurred while communicating with server: '
          'Status code ${response.statusCode}'
        );
    }
  }
  
  static dynamic _parseResponse(http.Response response) {
    final contentType = response.headers['content-type'];
    
    if (contentType?.contains('application/json') == true) {
      return response.body.isNotEmpty 
          ? json.decode(response.body)
          : null;
    } else if (contentType?.contains('text/') == true) {
      return response.body;
    } else {
      return response.bodyBytes;
    }
  }
  
  static bool isSuccess(int statusCode) {
    return statusCode >= 200 && statusCode < 300;
  }
  
  static Map<String, dynamic> parseError(http.Response response) {
    try {
      final errorData = json.decode(response.body);
      return {
        'statusCode': response.statusCode,
        'message': errorData['message'] ?? errorData['detail'] ?? 'Unknown error',
        'errors': errorData['errors'] ?? [],
      };
    } catch (e) {
      return {
        'statusCode': response.statusCode,
        'message': 'Error: ${response.statusCode}',
        'errors': [],
      };
    }
  }
}