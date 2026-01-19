class LocationSuggestion {
  final String displayName;
  final double lat;
  final double lon;
  final Map<String, dynamic>? addressDetails;
  final double? importance; // Add this field
  
  LocationSuggestion({
    required this.displayName,
    required this.lat,
    required this.lon,
    this.addressDetails,
    this.importance,
  });
  
  factory LocationSuggestion.fromJson(Map<String, dynamic> json) {
    return LocationSuggestion(
      displayName: json['display_name'] ?? '',
      lat: double.parse(json['lat'].toString()),
      lon: double.parse(json['lon'].toString()),
      addressDetails: json['address'],
      importance: json['importance'] != null 
          ? double.tryParse(json['importance'].toString()) 
          : null,
    );
  }
  
  String get shortAddress {
    if (addressDetails != null) {
      // Try to get the most specific address component
      return addressDetails?['road'] ?? 
             addressDetails?['suburb'] ?? 
             addressDetails?['village'] ??
             addressDetails?['town'] ??
             addressDetails?['city'] ?? 
             addressDetails?['county'] ??
             displayName;
    }
    // Fallback to first two parts of display name
    final parts = displayName.split(',');
    return parts.take(2).join(',').trim();
  }
  
  Map<String, dynamic> toJson() {
    return {
      'display_name': displayName,
      'lat': lat.toString(),
      'lon': lon.toString(),
      'address': addressDetails,
      'importance': importance,
    };
  }
}