import 'package:geolocator/geolocator.dart';
import 'package:mobile_app/model/location_suggestion.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class LocationService {
  static const String _baseUrl = 'https://nominatim.openstreetmap.org/search';

  Future<List<LocationSuggestion>> searchLocation({
    required String query,
    double? lat,
    double? lng,
    int limit = 5,
  }) async {
    try {
      final params = {
        'q': query,
        'format': 'json',
        'limit': limit.toString(),
        'addressdetails': '1',
      };

      // Add viewbox to bias results towards current location
      if (lat != null && lng != null) {
        // Create a bounding box around the current location
        // 0.1 degrees is roughly 11km at the equator
        params['viewbox'] =
            '${lng - 0.1},${lat + 0.1},${lng + 0.1},${lat - 0.1}';
        params['bounded'] = '1';
      }

      final uri = Uri.parse(_baseUrl).replace(queryParameters: params);
      final response = await http.get(
        uri,
        headers: {'User-Agent': 'Mobile_app/1.0'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        final suggestions = data
            .map((item) => LocationSuggestion.fromJson(item))
            .toList();

        // Sort by importance if available (higher importance first)
        suggestions.sort((a, b) {
          final importanceA = a.importance ?? 0;
          final importanceB = b.importance ?? 0;
          return importanceB.compareTo(importanceA);
        });

        return suggestions;
      }
      return [];
    } catch (e) {
      print('Search error: $e');
      return [];
    }
  }

  Future<List<LocationSuggestion>> searchNearby({
    required double lat,
    required double lng,
    int radius = 1000,
  }) async {
    try {
      final params = {
        'format': 'json',
        'limit': '10',
        'addressdetails': '1',
        'lat': lat.toString(),
        'lon': lng.toString(),
      };

      final uri = Uri.parse(_baseUrl).replace(queryParameters: params);
      final response = await http.get(
        uri,
        headers: {'User-Agent': 'Mobile_app/1.0'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((item) => LocationSuggestion.fromJson(item)).toList();
      }
      return [];
    } catch (e) {
      print('Nearby search error: $e');
      return [];
    }
  }

  Future<String?> reverseGeocode(double lat, double lng) async {
    try {
      final url = 'https://nominatim.openstreetmap.org/reverse?'
          'format=json&lat=$lat&lon=$lng&addressdetails=1';

      final response = await http.get(
        Uri.parse(url),
        headers: {'User-Agent': 'Mobile_app/1.0'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final address = data['display_name'] as String?;
        return address;
      }
      return null;
    } catch (e) {
      print('Reverse geocode error: $e');
      return null;
    }
  }
}