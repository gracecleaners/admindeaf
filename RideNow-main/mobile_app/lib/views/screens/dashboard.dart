import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mobile_app/controllers/auth_controller.dart';
import 'package:mobile_app/controllers/ride_controller.dart';
import 'package:mobile_app/core/routes/app_routes.dart';

class ZyraDashboard extends StatefulWidget {
  const ZyraDashboard({super.key});

  @override
  State<ZyraDashboard> createState() => _ZyraDashboardState();
}

class _ZyraDashboardState extends State<ZyraDashboard> {
  final AuthController _authController = Get.find<AuthController>();
  final RideController _rideController = Get.find<RideController>();


  @override
  void initState() {
    super.initState();
    // Load data when dashboard opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadDashboardData();
    });
  }

  Future<void> _loadDashboardData() async {
    try {
      await _rideController.getVehicleTypes();
      await _rideController.getAvailableVehicles();
      await _rideController.getRideHistory();
      await _rideController.getClientStatistics();
    } catch (e) {
      print('Error loading dashboard data: $e');
    }
  }



  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isSmallScreen = screenWidth < 360;

    return Scaffold(
      backgroundColor: const Color(0xFFF9FAFB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 2,
        shadowColor: Colors.green.withOpacity(0.1),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child:
                  const Icon(Icons.local_taxi, color: Colors.green, size: 24),
            ),
            const SizedBox(width: 12),
            Text("Zyra",
                style: GoogleFonts.poppins(
                  color: Colors.black,
                  fontWeight: FontWeight.w700,
                  fontSize: isSmallScreen ? 18 : 20,
                )),
          ],
        ),
        actions: [
          // Wallet balance
          Obx(() {
            final stats = _rideController.clientStatistics;
            final balance = stats['wallet_balance'] ?? 0.0;
            return Container(
              margin: const EdgeInsets.only(right: 16),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.green.shade50, Colors.green.shade100],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.green.withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.account_balance_wallet,
                      size: 16, color: Colors.green),
                  const SizedBox(width: 6),
                  Text("UGX ${balance.toStringAsFixed(0)}",
                      style: GoogleFonts.poppins(
                        color: Colors.green[800],
                        fontWeight: FontWeight.w600,
                        fontSize: isSmallScreen ? 12 : 14,
                      )),
                ],
              ),
            );
          }),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.symmetric(
            horizontal: isSmallScreen ? 12 : 16,
            vertical: 16,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Section with User Info
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.white, Colors.green.shade50],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.1),
                      blurRadius: 15,
                      offset: const Offset(0, 4),
                    )
                  ],
                ),
                child: Obx(() {
                  final user = _authController.user.value;
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Welcome, ${user?.fullName ?? 'User'}! 👋",
                        style: GoogleFonts.poppins(
                          fontSize: isSmallScreen ? 18 : 22,
                          fontWeight: FontWeight.w700,
                          color: Colors.green[900],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        user?.email ?? 'Client Dashboard',
                        style: GoogleFonts.poppins(
                          fontSize: isSmallScreen ? 13 : 15,
                          color: Colors.grey[700],
                        ),
                      ),
                      if (user?.phone != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          "📱 ${user!.phone!}",
                          style: GoogleFonts.poppins(
                            fontSize: isSmallScreen ? 12 : 14,
                            color: Colors.grey[700],
                          ),
                        ),
                      ],
                    ],
                  );
                }),
              ),

              const SizedBox(height: 20),

              // Book a Ride Card
              Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.green.shade50, Colors.green.shade100],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.green.withOpacity(0.2),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    )
                  ],
                ),
                padding: EdgeInsets.all(isSmallScreen ? 16 : 20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text("Book a Ride 🚗",
                              style: GoogleFonts.poppins(
                                  fontWeight: FontWeight.w700,
                                  fontSize: isSmallScreen ? 16 : 18,
                                  color: Colors.green[900])),
                          const SizedBox(height: 6),
                          Text(
                            "Start a new ride request with our interactive booking system.",
                            style: GoogleFonts.poppins(
                                fontSize: isSmallScreen ? 12 : 14,
                                color: Colors.green[800]),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.green.withOpacity(0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 3),
                          )
                        ],
                      ),
                      child: ElevatedButton.icon(
                        onPressed: () => Get.toNamed(Routes.bookRide),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12)),
                          padding: EdgeInsets.symmetric(
                            horizontal: isSmallScreen ? 12 : 16,
                            vertical: isSmallScreen ? 10 : 12,
                          ),
                        ),
                        icon: const Icon(Icons.add, size: 18),
                        label: Text(isSmallScreen ? "Book" : "Book Ride",
                            style: GoogleFonts.poppins(
                              fontWeight: FontWeight.w600,
                              fontSize: isSmallScreen ? 12 : 14,
                            )),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Active Ride Status
              Obx(() {
                final currentRide = _rideController.currentRide.value;
                if (currentRide != null) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.blue.shade100),
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: Colors.blue,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(Icons.directions_car,
                              color: Colors.white, size: 24),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Active Ride',
                                style: GoogleFonts.poppins(
                                  fontWeight: FontWeight.w700,
                                  color: Colors.blue.shade800,
                                  fontSize: 16,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Status: ${currentRide.status}',
                                style: GoogleFonts.poppins(
                                  color: Colors.blue.shade600,
                                  fontSize: 12,
                                ),
                              ),
                              if (currentRide.driver != null) ...[
                                const SizedBox(height: 2),
                                Text(
                                  'Driver: ${currentRide.driver!['name'] ?? 'Assigned'}',
                                  style: GoogleFonts.poppins(
                                    color: Colors.blue.shade600,
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.arrow_forward,
                              color: Colors.blue),
                          onPressed: () {
                            Get.toNamed(Routes.rideDetail,
                                arguments: currentRide.id);
                          },
                        ),
                      ],
                    ),
                  );
                }
                return const SizedBox.shrink();
              }),





              const SizedBox(height: 24),

              // Quick Actions
              Text(
                "Quick Actions",
                style: GoogleFonts.poppins(
                  fontWeight: FontWeight.w700,
                  fontSize: isSmallScreen ? 17 : 19,
                  color: Colors.green[900],
                ),
              ),

              const SizedBox(height: 16),

              // Responsive Grid for Quick Actions
              LayoutBuilder(
                builder: (context, constraints) {
                  final crossAxisCount = constraints.maxWidth > 600 ? 4 : 2;
                  final childAspectRatio =
                      constraints.maxWidth > 600 ? 1.0 : 1.2;

                  return GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: crossAxisCount,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    childAspectRatio: childAspectRatio,
                    children: [
                      _buildActionCard(
                        Icons.directions_car,
                        "Book a Ride",
                        "Request a new ride",
                        Colors.blue.shade50,
                        Colors.blue,
                        isSmallScreen,
                        onTap: () => Get.toNamed(Routes.bookRide),
                      ),
                      _buildActionCard(
                        Icons.history,
                        "Ride History",
                        "View past rides",
                        Colors.green.shade50,
                        Colors.green,
                        isSmallScreen,
                        onTap: () => Get.toNamed(Routes.myRide),
                      ),
                      _buildActionCard(
                        Icons.map,
                        "Map View",
                        "View map and drivers",
                        Colors.purple.shade50,
                        Colors.purple,
                        isSmallScreen,
                        onTap: () => Get.toNamed(Routes.googleMap),
                      ),
                      _buildActionCard(
                        Icons.person,
                        "My Profile",
                        "Manage your profile",
                        Colors.orange.shade50,
                        Colors.orange,
                        isSmallScreen,
                        onTap: () => Get.toNamed(Routes.profile),
                      ),
                      if (constraints.maxWidth > 600) ...[
                        _buildActionCard(
                          Icons.support_agent,
                          "Support",
                          "Get help & support",
                          Colors.red.shade50,
                          Colors.red,
                          isSmallScreen,
                          onTap: () => Get.toNamed(Routes.support),
                        ),
                        _buildActionCard(
                          Icons.payment,
                          "Payments",
                          "Manage payments",
                          Colors.teal.shade50,
                          Colors.teal,
                          isSmallScreen,
                          onTap: () => Get.toNamed(Routes.payments),
                        ),
                        _buildActionCard(
                          Icons.notifications,
                          "Notifications",
                          "View notifications",
                          Colors.pink.shade50,
                          Colors.pink,
                          isSmallScreen,
                          onTap: () => Get.toNamed(Routes.notifications),
                        ),
                        _buildActionCard(
                          Icons.settings,
                          "Settings",
                          "App settings",
                          Colors.grey.shade50,
                          Colors.grey,
                          isSmallScreen,
                          onTap: () => Get.toNamed(Routes.settings),
                        ),
                      ],
                    ],
                  );
                },
              ),

              // Recent Rides Section
              Obx(() {
                final recentRides = _rideController.rideHistory.take(3).toList();
                if (recentRides.isEmpty) return const SizedBox.shrink();

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 24),
                    Text(
                      "Recent Rides",
                      style: GoogleFonts.poppins(
                        fontWeight: FontWeight.w700,
                        fontSize: isSmallScreen ? 17 : 19,
                        color: Colors.green[900],
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...recentRides.map((ride) {
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.grey.withOpacity(0.1),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: ride.isActive
                                    ? Colors.blue.shade50
                                    : Colors.green.shade50,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Icon(
                                ride.isActive
                                    ? Icons.directions_car
                                    : Icons.check_circle,
                                color: ride.isActive
                                    ? Colors.blue
                                    : Colors.green,
                                size: 24,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    '${ride.startLocation} → ${ride.endLocation}',
                                    style: GoogleFonts.poppins(
                                      fontWeight: FontWeight.w600,
                                      fontSize: 14,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '${ride.startTime} • ${ride.status}',
                                    style: GoogleFonts.poppins(
                                      fontSize: 12,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                    if (_rideController.rideHistory.length > 3)
                      Align(
                        alignment: Alignment.centerRight,
                        child: TextButton(
                          onPressed: () => Get.toNamed(Routes.myRide),
                          child: Text(
                            'View All Rides →',
                            style: GoogleFonts.poppins(
                              color: Colors.green,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                  ],
                );
              }),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),

    );
  }



  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
    bool isSmallScreen,
  ) {
    return Container(
      width: isSmallScreen ? 100 : 110,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: isSmallScreen ? 20 : 24),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: GoogleFonts.poppins(
              fontSize: isSmallScreen ? 16 : 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: GoogleFonts.poppins(
              fontSize: isSmallScreen ? 11 : 12,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard(
    IconData icon,
    String title,
    String subtitle,
    Color bgColor,
    Color iconColor,
    bool isSmallScreen, {
    VoidCallback? onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(20),
          onTap: onTap,
          child: Padding(
            padding: EdgeInsets.all(isSmallScreen ? 12 : 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: bgColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: iconColor,
                    size: isSmallScreen ? 20 : 24,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  title,
                  style: GoogleFonts.poppins(
                    fontWeight: FontWeight.w600,
                    fontSize: isSmallScreen ? 13 : 15,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: GoogleFonts.poppins(
                    fontSize: isSmallScreen ? 11 : 12,
                    color: Colors.grey[600],
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}