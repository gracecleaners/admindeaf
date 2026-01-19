import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart' as gl;
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart' as mp;
import 'package:mobile_app/core/services/location_serach_service.dart';
import 'package:mobile_app/model/location_suggestion.dart';

class GoogleMapFlutter extends StatefulWidget {
  final Function(LocationSuggestion) onLocationSelected;
  final Function(gl.Position) onCurrentLocationObtained;
  
  const GoogleMapFlutter({
    super.key,
    required this.onLocationSelected,
    required this.onCurrentLocationObtained,
  });

  @override
  State<GoogleMapFlutter> createState() => _GoogleMapFlutterState();
}

class _GoogleMapFlutterState extends State<GoogleMapFlutter> {
  mp.MapboxMap? mapBoxMapController;
  StreamSubscription? userPositionStream;
  final LocationService _locationService = LocationService();
  gl.Position? _currentPosition;
  
  // Use CircleAnnotationManager instead of generic AnnotationManager
  mp.CircleAnnotationManager? _circleAnnotationManager;
  mp.PolylineAnnotationManager? _polylineAnnotationManager;
  
  mp.CircleAnnotation? _pickupMarker;
  mp.CircleAnnotation? _destinationMarker;
  mp.PolylineAnnotation? _routeLine;

  @override
  void initState() {
    super.initState();
    _setupPositionTracking();
  }

  @override
  void dispose() {
    userPositionStream?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        heroTag: 'current_location',
        backgroundColor: Colors.white,
        onPressed: _centerOnCurrentLocation,
        child: const Icon(Icons.my_location, color: Colors.green),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      body: mp.MapWidget(
        styleUri: mp.MapboxStyles.MAPBOX_STREETS,
        onMapCreated: _onMapCreated,
        onTapListener: _onMapTap, // Use onTapListener instead of onMapClick
      ),
    );
  }

  void _onMapCreated(mp.MapboxMap controller) {
    setState(() {
      mapBoxMapController = controller;
    });

    // Enable location component
    mapBoxMapController?.location.updateSettings(
      mp.LocationComponentSettings(
        enabled: true,
        pulsingEnabled: true,
        pulsingColor: Colors.green.value,
      ),
    );

    // Create annotation managers
    controller.annotations.createCircleAnnotationManager().then((manager) {
      setState(() {
        _circleAnnotationManager = manager;
      });
    });

    controller.annotations.createPolylineAnnotationManager().then((manager) {
      setState(() {
        _polylineAnnotationManager = manager;
      });
    });
  }

  void _onMapTap(mp.MapContentGestureContext context) async {
    if (mapBoxMapController == null) return;

    // Get the coordinate from the tap
    final coordinate = context.point.coordinates;
    final lat = coordinate.lat.toDouble();
    final lng = coordinate.lng.toDouble();
    
    // Reverse geocode to get address
    final address = await _locationService.reverseGeocode(lat, lng);
    
    if (address != null) {
      final location = LocationSuggestion(
        displayName: address,
        lat: lat,
        lon: lng,
      );
      
      widget.onLocationSelected(location);
      
      // Add marker at tapped location
      _addMarker(lat, lng, isPickup: true);
    }
  }

  Future<void> _setupPositionTracking() async {
    bool serviceEnabled;
    gl.LocationPermission permission;

    // Check if geolocator service is enabled
    serviceEnabled = await gl.Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      return Future.error("Location Services Disabled");
    }

    // Request permission from user
    permission = await gl.Geolocator.checkPermission();
    if (permission == gl.LocationPermission.denied) {
      permission = await gl.Geolocator.requestPermission();
      if (permission == gl.LocationPermission.denied) {
        return Future.error("Location permissions are denied");
      }
    }
    if (permission == gl.LocationPermission.deniedForever) {
      return Future.error(
        "Location permissions are permanently denied, we cannot request permission",
      );
    }

    // Get initial position
    final position = await gl.Geolocator.getCurrentPosition(
      desiredAccuracy: gl.LocationAccuracy.high,
    );
    
    if (mounted) {
      setState(() {
        _currentPosition = position;
      });
      
      widget.onCurrentLocationObtained(position);
      _centerOnLocation(position.latitude, position.longitude);
    }

    // Set up location settings
    const locationSettings = gl.LocationSettings(
      accuracy: gl.LocationAccuracy.high,
      distanceFilter: 100,
    );

    // Listen to location changes
    userPositionStream?.cancel();
    userPositionStream = gl.Geolocator.getPositionStream(
      locationSettings: locationSettings,
    ).listen((gl.Position? position) {
      if (position != null && mapBoxMapController != null && mounted) {
        setState(() {
          _currentPosition = position;
        });
      }
    });
  }

  void _centerOnCurrentLocation() {
    if (_currentPosition != null && mapBoxMapController != null) {
      _centerOnLocation(
        _currentPosition!.latitude,
        _currentPosition!.longitude,
      );
    }
  }

  void _centerOnLocation(double lat, double lng) {
    mapBoxMapController?.setCamera(
      mp.CameraOptions(
        center: mp.Point(
          coordinates: mp.Position(lng, lat),
        ),
        zoom: 15,
        bearing: 0,
        pitch: 0,
      ),
    );
  }

  void _addMarker(double lat, double lng, {bool isPickup = true}) {
    if (_circleAnnotationManager == null) return;

    final color = isPickup ? Colors.green.value : Colors.red.value;

    // Remove existing marker
    if (isPickup && _pickupMarker != null) {
      _circleAnnotationManager!.delete(_pickupMarker!);
    } else if (!isPickup && _destinationMarker != null) {
      _circleAnnotationManager!.delete(_destinationMarker!);
    }

    // Create circle annotation options
    final circleOptions = mp.CircleAnnotationOptions(
      geometry: mp.Point(
        coordinates: mp.Position(lng, lat),
      ),
      circleColor: color,
      circleRadius: 8.0,
      circleStrokeColor: Colors.white.value,
      circleStrokeWidth: 2.0,
    );

    // Create the annotation
    _circleAnnotationManager!.create(circleOptions).then((circle) {
      if (isPickup) {
        _pickupMarker = circle;
      } else {
        _destinationMarker = circle;
      }
    });
  }

  void clearMarkers() {
    if (_circleAnnotationManager != null) {
      if (_pickupMarker != null) {
        _circleAnnotationManager!.delete(_pickupMarker!);
        _pickupMarker = null;
      }
      if (_destinationMarker != null) {
        _circleAnnotationManager!.delete(_destinationMarker!);
        _destinationMarker = null;
      }
    }
    
    if (_polylineAnnotationManager != null && _routeLine != null) {
      _polylineAnnotationManager!.delete(_routeLine!);
      _routeLine = null;
    }
  }

  void drawRoute(LocationSuggestion pickup, LocationSuggestion destination) {
    if (_polylineAnnotationManager == null) return;

    // Remove existing route
    if (_routeLine != null) {
      _polylineAnnotationManager!.delete(_routeLine!);
    }

    // Create polyline annotation options
    final polylineOptions = mp.PolylineAnnotationOptions(
      geometry: mp.LineString(
        coordinates: [
          mp.Position(pickup.lon, pickup.lat),
          mp.Position(destination.lon, destination.lat),
        ],
      ),
      lineColor: Colors.green.value,
      lineWidth: 3.0,
      lineOpacity: 0.7,
    );

    // Create the polyline
    _polylineAnnotationManager!.create(polylineOptions).then((line) {
      _routeLine = line;
    });

    // Fit bounds to show both points
    _fitBoundsToRoute(pickup, destination);
  }

  void _fitBoundsToRoute(LocationSuggestion pickup, LocationSuggestion destination) {
    if (mapBoxMapController == null) return;

    // Calculate bounds
    final minLat = pickup.lat < destination.lat ? pickup.lat : destination.lat;
    final maxLat = pickup.lat > destination.lat ? pickup.lat : destination.lat;
    final minLng = pickup.lon < destination.lon ? pickup.lon : destination.lon;
    final maxLng = pickup.lon > destination.lon ? pickup.lon : destination.lon;

    // Add padding
    const padding = 0.01;
    
    // Calculate center
    final centerLat = (minLat + maxLat) / 2;
    final centerLng = (minLng + maxLng) / 2;

    // Calculate appropriate zoom level
    final latDiff = maxLat - minLat;
    final lngDiff = maxLng - minLng;
    final maxDiff = latDiff > lngDiff ? latDiff : lngDiff;
    
    double zoom = 15;
    if (maxDiff > 0.1) {
      zoom = 11;
    } else if (maxDiff > 0.05) {
      zoom = 12;
    } else if (maxDiff > 0.01) {
      zoom = 13;
    } else if (maxDiff > 0.005) {
      zoom = 14;
    }

    mapBoxMapController?.setCamera(
      mp.CameraOptions(
        center: mp.Point(
          coordinates: mp.Position(centerLng, centerLat),
        ),
        zoom: zoom,
        bearing: 0,
        pitch: 0,
      ),
    );
  }
}