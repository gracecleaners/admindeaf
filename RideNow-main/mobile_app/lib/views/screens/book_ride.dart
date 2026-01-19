import 'package:debounce_throttle/debounce_throttle.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart' as gl;
import 'package:get/get.dart';
import 'package:mobile_app/controllers/ride_controller.dart';
import 'package:mobile_app/core/services/location_serach_service.dart';
import 'package:mobile_app/model/location_suggestion.dart';
import 'package:mobile_app/views/screens/google_map.dart';
import 'package:mobile_app/views/screens/ride_confirmation.dart';

class BookRideScreen extends StatefulWidget {
  const BookRideScreen({Key? key}) : super(key: key);

  @override
  State<BookRideScreen> createState() => _BookRideScreenState();
}

class _BookRideScreenState extends State<BookRideScreen> {
  final LocationService _locationService = LocationService();
  final RideController _rideController = Get.find<RideController>();
  
  // Separate debouncers for each field
  late final Debouncer<String> _pickupDebouncer;
  late final Debouncer<String> _destinationDebouncer;
  
  // Controllers for text fields
  final TextEditingController _pickupController = TextEditingController();
  final TextEditingController _destinationController = TextEditingController();
  
  // Focus nodes
  final FocusNode _pickupFocusNode = FocusNode();
  final FocusNode _destinationFocusNode = FocusNode();
  
  // State variables
  List<LocationSuggestion> _pickupSuggestions = [];
  List<LocationSuggestion> _destinationSuggestions = [];
  LocationSuggestion? _selectedPickup;
  LocationSuggestion? _selectedDestination;
  gl.Position? _currentPosition;
  
  bool _isLoadingPickup = false;
  bool _isLoadingDestination = false;
  
  @override
  void initState() {
    super.initState();
    
    // Initialize debouncers with faster response (300ms like SafeBoda)
    _pickupDebouncer = Debouncer<String>(
      const Duration(milliseconds: 300),
      initialValue: '',
    );
    _destinationDebouncer = Debouncer<String>(
      const Duration(milliseconds: 300),
      initialValue: '',
    );
    
    _getCurrentLocation();
    _setupSearchListeners();
  }
  
  @override
  void dispose() {
    _pickupDebouncer.cancel();
    _destinationDebouncer.cancel();
    _pickupController.dispose();
    _destinationController.dispose();
    _pickupFocusNode.dispose();
    _destinationFocusNode.dispose();
    super.dispose();
  }
  
  void _setupSearchListeners() {
    // Pickup search listener
    _pickupDebouncer.values.listen((query) {
      if (query.isNotEmpty && query.length > 2) {
        _performSearch(query, true);
      }
    });
    
    // Destination search listener
    _destinationDebouncer.values.listen((query) {
      if (query.isNotEmpty && query.length > 2) {
        _performSearch(query, false);
      }
    });
    
    // Focus listeners
    _pickupFocusNode.addListener(() {
      if (!_pickupFocusNode.hasFocus) {
        // Delay clearing to allow tap on suggestion
        Future.delayed(const Duration(milliseconds: 200), () {
          if (mounted && !_pickupFocusNode.hasFocus) {
            setState(() {
              _pickupSuggestions.clear();
            });
          }
        });
      }
    });
    
    _destinationFocusNode.addListener(() {
      if (!_destinationFocusNode.hasFocus) {
        Future.delayed(const Duration(milliseconds: 200), () {
          if (mounted && !_destinationFocusNode.hasFocus) {
            setState(() {
              _destinationSuggestions.clear();
            });
          }
        });
      }
    });
  }
  
  Future<void> _getCurrentLocation() async {
    try {
      final position = await gl.Geolocator.getCurrentPosition(
        desiredAccuracy: gl.LocationAccuracy.high,
      );
      setState(() {
        _currentPosition = position;
      });
      
      // Get address for current location
      final address = await _locationService.reverseGeocode(
        position.latitude,
        position.longitude,
      );
      
      if (address != null && mounted) {
        _pickupController.text = address;
        _selectedPickup = LocationSuggestion(
          displayName: address,
          lat: position.latitude,
          lon: position.longitude,
        );
      }
    } catch (e) {
      print('Error getting location: $e');
    }
  }
  
  void _onSearchTextChanged(String query, bool isPickup) {
    if (query.length > 2) {
      // Update the appropriate debouncer
      if (isPickup) {
        _pickupDebouncer.value = query;
        setState(() {
          _isLoadingPickup = true;
        });
      } else {
        _destinationDebouncer.value = query;
        setState(() {
          _isLoadingDestination = true;
        });
      }
    } else {
      setState(() {
        if (isPickup) {
          _pickupSuggestions.clear();
          _isLoadingPickup = false;
        } else {
          _destinationSuggestions.clear();
          _isLoadingDestination = false;
        }
      });
    }
  }
  
  Future<void> _performSearch(String query, bool isPickup) async {
    try {
      final suggestions = await _locationService.searchLocation(
        query: query,
        lat: _currentPosition?.latitude,
        lng: _currentPosition?.longitude,
        limit: 8, // Increased for better results
      );
      
      if (mounted) {
        setState(() {
          if (isPickup) {
            _pickupSuggestions = suggestions;
            _isLoadingPickup = false;
          } else {
            _destinationSuggestions = suggestions;
            _isLoadingDestination = false;
          }
        });
      }
    } catch (e) {
      print('Search error: $e');
      if (mounted) {
        setState(() {
          if (isPickup) {
            _isLoadingPickup = false;
          } else {
            _isLoadingDestination = false;
          }
        });
      }
    }
  }
  
  void _selectLocation(LocationSuggestion location, bool isPickup) {
    setState(() {
      if (isPickup) {
        _selectedPickup = location;
        _pickupController.text = location.displayName;
        _pickupSuggestions.clear();
        _pickupFocusNode.unfocus();
        _isLoadingPickup = false;
      } else {
        _selectedDestination = location;
        _destinationController.text = location.displayName;
        _destinationSuggestions.clear();
        _destinationFocusNode.unfocus();
        _isLoadingDestination = false;
      }
    });
  }
  
  void _useCurrentLocation() async {
    if (_currentPosition != null) {
      setState(() {
        _isLoadingPickup = true;
      });
      
      final address = await _locationService.reverseGeocode(
        _currentPosition!.latitude,
        _currentPosition!.longitude,
      );
      
      if (address != null && mounted) {
        _selectLocation(
          LocationSuggestion(
            displayName: address,
            lat: _currentPosition!.latitude,
            lon: _currentPosition!.longitude,
          ),
          true,
        );
      }
      
      setState(() {
        _isLoadingPickup = false;
      });
    }
  }
  
  void _clearSelection(bool isPickup) {
    setState(() {
      if (isPickup) {
        _selectedPickup = null;
        _pickupController.clear();
        _pickupSuggestions.clear();
      } else {
        _selectedDestination = null;
        _destinationController.clear();
        _destinationSuggestions.clear();
      }
    });
  }
  
  bool get _canProceed {
    return _selectedPickup != null && _selectedDestination != null;
  }
  
  void _onProceed() {
    if (_canProceed) {
      Get.to(() => RideConfirmationScreen(
            pickup: _selectedPickup!,
            destination: _selectedDestination!,
          ));
    }
  }
  
  Widget _buildLocationInput(
    String label,
    String hint,
    TextEditingController controller,
    FocusNode focusNode,
    bool isPickup,
    VoidCallback? onUseCurrentLocation,
  ) {
    final isSelected = isPickup ? _selectedPickup != null : _selectedDestination != null;
    final suggestions = isPickup ? _pickupSuggestions : _destinationSuggestions;
    final isLoading = isPickup ? _isLoadingPickup : _isLoadingDestination;
    final hasSuggestions = suggestions.isNotEmpty;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: isPickup ? Colors.green : Colors.red,
                shape: BoxShape.circle,
                border: isPickup ? Border.all(color: Colors.green, width: 2) : null,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                  TextField(
                    controller: controller,
                    focusNode: focusNode,
                    onChanged: (value) => _onSearchTextChanged(value, isPickup),
                    decoration: InputDecoration(
                      hintText: hint,
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.zero,
                      suffixIcon: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (isLoading)
                            const Padding(
                              padding: EdgeInsets.all(12.0),
                              child: SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(Colors.green),
                                ),
                              ),
                            )
                          else if (isSelected)
                            IconButton(
                              icon: const Icon(Icons.clear, size: 16),
                              onPressed: () => _clearSelection(isPickup),
                            ),
                        ],
                      ),
                    ),
                    style: const TextStyle(
                      color: Colors.black,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            if (isPickup && onUseCurrentLocation != null)
              IconButton(
                icon: const Icon(Icons.my_location, color: Colors.green),
                onPressed: onUseCurrentLocation,
                tooltip: 'Use current location',
              ),
          ],
        ),
        
        // Suggestions dropdown - now shows when focused and has suggestions
        if (hasSuggestions && focusNode.hasFocus)
          Container(
            margin: const EdgeInsets.only(left: 24, top: 8, right: 8),
            constraints: const BoxConstraints(maxHeight: 300),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 10,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: ListView.separated(
              shrinkWrap: true,
              padding: EdgeInsets.zero,
              itemCount: suggestions.length,
              separatorBuilder: (context, index) => Divider(
                height: 1,
                color: Colors.grey[200],
              ),
              itemBuilder: (context, index) {
                final suggestion = suggestions[index];
                return ListTile(
                  leading: Icon(
                    Icons.location_on,
                    color: Colors.grey[600],
                    size: 20,
                  ),
                  title: Text(
                    suggestion.shortAddress,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  subtitle: Text(
                    suggestion.displayName.length > 60
                        ? '${suggestion.displayName.substring(0, 60)}...'
                        : suggestion.displayName,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  onTap: () => _selectLocation(suggestion, isPickup),
                );
              },
            ),
          ),
      ],
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Map - Pass callback to handle location selection from map
          GoogleMapFlutter(
            onLocationSelected: (location) {
              // Handle location selected from map
              if (_pickupFocusNode.hasFocus) {
                _selectLocation(location, true);
              } else if (_destinationFocusNode.hasFocus) {
                _selectLocation(location, false);
              }
            },
            onCurrentLocationObtained: (position) {
              setState(() {
                _currentPosition = position;
              });
            },
          ),
          
          // Back button
          if (Navigator.canPop(context))
            Positioned(
              top: MediaQuery.of(context).padding.top,
              left: 20,
              child: Container(
                height: 35,
                width: 35,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Center(
                  child: IconButton(
                    icon: const Icon(Icons.arrow_back_ios, size: 16),
                    onPressed: () => Get.back(),
                  ),
                ),
              ),
            ),
          
          // Zoom controls
          Positioned(
            right: 16,
            bottom: 250,
            child: Column(
              children: [
                FloatingActionButton(
                  heroTag: 'zoom_in',
                  mini: true,
                  backgroundColor: Colors.white,
                  onPressed: () {},
                  child: const Icon(Icons.add, color: Colors.black87),
                ),
                const SizedBox(height: 8),
                FloatingActionButton(
                  heroTag: 'zoom_out',
                  mini: true,
                  backgroundColor: Colors.white,
                  onPressed: () {},
                  child: const Icon(Icons.remove, color: Colors.black87),
                ),
              ],
            ),
          ),
          
          // Location selection panel at bottom
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.all(20),
                    child: Text(
                      'Where to?',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  
                  // Pickup Location
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: _buildLocationInput(
                      'Pickup Location',
                      'Select on map or type address',
                      _pickupController,
                      _pickupFocusNode,
                      true,
                      _useCurrentLocation,
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Destination
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: _buildLocationInput(
                      'Destination',
                      'Where are you going?',
                      _destinationController,
                      _destinationFocusNode,
                      false,
                      null,
                    ),
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Proceed Button
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 0, 20, 30),
                    child: SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _canProceed ? _onProceed : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          disabledBackgroundColor: Colors.grey[300],
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: const Text(
                           'Select Vehicle',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
