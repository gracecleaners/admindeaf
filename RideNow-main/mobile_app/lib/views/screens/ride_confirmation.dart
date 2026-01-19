import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile_app/controllers/ride_controller.dart';
import 'package:mobile_app/model/location_suggestion.dart';
import 'package:mobile_app/model/ride_model.dart';

class RideConfirmationScreen extends StatefulWidget {
  final LocationSuggestion pickup;
  final LocationSuggestion destination;

  const RideConfirmationScreen({
    Key? key,
    required this.pickup,
    required this.destination,
  }) : super(key: key);

  @override
  State<RideConfirmationScreen> createState() => _RideConfirmationScreenState();
}

class _RideConfirmationScreenState extends State<RideConfirmationScreen> {
  final RideController _rideController = Get.find<RideController>();
  int? _selectedVehicleTypeId;

  @override
  void initState() {
    super.initState();
    // Load vehicle types if not already loaded
    if (_rideController.vehicleTypes.isEmpty) {
      _rideController.getVehicleTypes();
    }
  }

  void _onBookRide() async {
    if (_selectedVehicleTypeId == null) {
      Get.snackbar('Error', 'Please select a vehicle type');
      return;
    }

    final rideRequest = await _rideController.requestRide(
      pickupAddress: widget.pickup.displayName,
      destinationAddress: widget.destination.displayName,
      pickupLat: widget.pickup.lat,
      pickupLng: widget.pickup.lon,
      destLat: widget.destination.lat,
      destLng: widget.destination.lon,
      vehicleTypeId: _selectedVehicleTypeId,
    );

    if (rideRequest != null) {
      // Logic for what happens after successful request
      // RideController already handles polling and showing snacks
      // Maybe show a "Searching for Driver" modal or screen
      _showMatchingModal(rideRequest.id);
    }
  }

  void _showMatchingModal(int requestId) {
    Get.bottomSheet(
      Container(
        padding: const EdgeInsets.all(20),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20),
            topRight: Radius.circular(20),
          ),
        ),
        child: Obx(() {
          final status = _rideController.matchingStatus.value;
          return Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                status == 'searching' || status == 'matching'
                    ? 'Searching for Driver...'
                    : status == 'matched'
                        ? 'Driver Found!'
                        : 'Matching Failed',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 20),
              if (status == 'searching' || status == 'matching')
                const CircularProgressIndicator(),
              if (status == 'matched')
                const Icon(Icons.check_circle, color: Colors.green, size: 60),
              if (status == 'failed')
                const Icon(Icons.error, color: Colors.red, size: 60),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  _rideController.cancelRideRequest(requestId);
                  Get.back();
                },
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                child: const Text('Cancel Request', style: TextStyle(color: Colors.white)),
              ),
            ],
          );
        }),
      ),
      isDismissible: false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Confirm Ride'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Trip Details',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            _buildLocationRow(Icons.location_on, Colors.green, widget.pickup.displayName),
            const Divider(),
            _buildLocationRow(Icons.location_on, Colors.red, widget.destination.displayName),
            const SizedBox(height: 30),
            const Text(
              'Select Vehicle Type',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: Obx(() {
                if (_rideController.isLoading.value && _rideController.vehicleTypes.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }
                return ListView.builder(
                  itemCount: _rideController.vehicleTypes.length,
                  itemBuilder: (context, index) {
                    final type = _rideController.vehicleTypes[index];
                    return ListTile(
                      leading: const Icon(Icons.directions_car),
                      title: Text(type.name),
                      subtitle: Text(type.description ?? ''),
                      trailing: Radio<int>(
                        value: type.id,
                        groupValue: _selectedVehicleTypeId,
                        onChanged: (value) {
                          setState(() {
                            _selectedVehicleTypeId = value;
                          });
                        },
                      ),
                      onTap: () {
                        setState(() {
                          _selectedVehicleTypeId = type.id;
                        });
                      },
                    );
                  },
                );
              }),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: Obx(() => ElevatedButton(
                    onPressed: _rideController.isLoading.value ? null : _onBookRide,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: _rideController.isLoading.value
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text(
                            'Confirm Booking',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                            ),
                          ),
                  )),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationRow(IconData icon, Color color, String address) {
    return Row(
      children: [
        Icon(icon, color: color),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            address,
            style: const TextStyle(fontSize: 16),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}