import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mobile_app/controllers/auth_controller.dart';
import 'package:mobile_app/controllers/ride_controller.dart';
import 'package:mobile_app/model/user_model.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final AuthController _authController = Get.find<AuthController>();
  final RideController _rideController = Get.find<RideController>();
  late TextEditingController _nameController;
  late TextEditingController _phoneController;
  late TextEditingController _emailController;

  @override
  void initState() {
    super.initState();
    _loadProfileData();
    
    // Initialize controllers with current user data
    final user = _authController.user.value;
    _nameController = TextEditingController(text: user?.name ?? '');
    _phoneController = TextEditingController(text: user?.phone ?? '');
    _emailController = TextEditingController(text: user?.email ?? '');
  }

  Future<void> _loadProfileData() async {
    try {
      await _authController.fetchUserProfile();
      await _rideController.getClientStatistics();
    } catch (e) {
      print('Error loading profile data: $e');
    }
  }

  Future<void> _updateProfile() async {
    final name = _nameController.text.trim();
    final phone = _phoneController.text.trim();

    if (name.isEmpty) {
      Get.snackbar('Error', 'Name is required');
      return;
    }

    try {
      await _authController.updateProfile(
        name: name,
        phone: phone.isNotEmpty ? phone : null,
      );
      
      // Refresh profile data
      await _authController.fetchUserProfile();
    } catch (e) {
      Get.snackbar('Error', 'Failed to update profile: $e');
    }
  }

  void _showEditDialog() {
    Get.dialog(
      AlertDialog(
        title: Text(
          'Edit Profile',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.w600,
          ),
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _nameController,
                decoration: InputDecoration(
                  labelText: 'Full Name',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _emailController,
                enabled: false, // Email cannot be changed
                decoration: InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _phoneController,
                decoration: InputDecoration(
                  labelText: 'Phone Number',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                keyboardType: TextInputType.phone,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: Text(
              'Cancel',
              style: GoogleFonts.poppins(color: Colors.grey),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Get.back();
              _updateProfile();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: Text(
              'Save',
              style: GoogleFonts.poppins(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      body: Obx(() {
        final user = _authController.user.value;
        final stats = _rideController.clientStatistics;
        
        return CustomScrollView(
          slivers: [
            // Profile Header
            SliverAppBar(
              expandedHeight: 250,
              floating: false,
              pinned: true,
              backgroundColor: Colors.transparent,
              flexibleSpace: FlexibleSpaceBar(
                background: Container(
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Color(0xFF16A34A), Color(0xFF22C55E)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.only(
                      top: 80,
                      left: 20,
                      right: 20,
                      bottom: 20,
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(40),
                                border: Border.all(
                                  color: Colors.white,
                                  width: 2,
                                ),
                              ),
                              child: user?.profileImage != null
                                  ? ClipRRect(
                                      borderRadius: BorderRadius.circular(40),
                                      child: Image.network(
                                        user!.profileImage!,
                                        width: 80,
                                        height: 80,
                                        fit: BoxFit.cover,
                                      ),
                                    )
                                  : Icon(
                                      Icons.person,
                                      size: 40,
                                      color: Colors.green.shade700,
                                    ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    user?.name ?? 'No Name',
                                    style: GoogleFonts.poppins(
                                      fontSize: 22,
                                      fontWeight: FontWeight.w700,
                                      color: Colors.white,
                                    ),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 8),
                                  Row(
                                    children: [
                                      Icon(
                                        Icons.email,
                                        size: 16,
                                        color: Colors.white.withOpacity(0.9),
                                      ),
                                      const SizedBox(width: 6),
                                      Expanded(
                                        child: Text(
                                          user?.email ?? 'No email',
                                          style: GoogleFonts.poppins(
                                            fontSize: 14,
                                            color: Colors.white.withOpacity(0.9),
                                          ),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ],
                                  ),
                                  if (user?.phone != null) ...[
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        Icon(
                                          Icons.phone,
                                          size: 16,
                                          color: Colors.white.withOpacity(0.9),
                                        ),
                                        const SizedBox(width: 6),
                                        Text(
                                          user!.phone!,
                                          style: GoogleFonts.poppins(
                                            fontSize: 14,
                                            color: Colors.white.withOpacity(0.9),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ],
                              ),
                            ),
                            IconButton(
                              onPressed: _showEditDialog,
                              icon: Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.edit,
                                  color: Colors.white,
                                  size: 20,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        // Stats Row
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            _ProfileStat(
                              title: 'Total Rides',
                              value: stats['total_rides']?.toString() ?? '0',
                              icon: Icons.directions_car,
                            ),
                            _ProfileStat(
                              title: 'Rating',
                              value: stats['average_rating']?.toStringAsFixed(1) ?? '0.0',
                              icon: Icons.star,
                            ),
                            _ProfileStat(
                              title: 'Wallet',
                              value: 'UGX ${stats['wallet_balance']?.toStringAsFixed(0) ?? '0'}',
                              icon: Icons.account_balance_wallet,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            // Profile Menu Options
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 24),
                child: Column(
                  children: [
                    // Account Section
                    _ProfileSection(
                      title: 'Account',
                      children: [
                        _ProfileMenuItem(
                          icon: Icons.person_outline,
                          title: 'Personal Information',
                          subtitle: 'Update your personal details',
                          onTap: _showEditDialog,
                        ),
                        _ProfileMenuItem(
                          icon: Icons.security,
                          title: 'Security',
                          subtitle: 'Password, 2FA, and security settings',
                          onTap: () => Get.toNamed('/security'),
                        ),
                        _ProfileMenuItem(
                          icon: Icons.notifications_outlined,
                          title: 'Notifications',
                          subtitle: 'Manage your notification preferences',
                          onTap: () => Get.toNamed('/notifications'),
                        ),
                        _ProfileMenuItem(
                          icon: Icons.language,
                          title: 'Language & Region',
                          subtitle: 'App language and regional settings',
                          onTap: () => Get.toNamed('/language'),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // Ride Preferences
                    _ProfileSection(
                      title: 'Ride Preferences',
                      children: [
                        _ProfileMenuItem(
                          icon: Icons.favorite_border,
                          title: 'Favorite Locations',
                          subtitle: 'Save your frequently visited places',
                          onTap: () => Get.toNamed('/favorites'),
                        ),
                        _ProfileMenuItem(
                          icon: Icons.payment,
                          title: 'Payment Methods',
                          subtitle: 'Add or manage payment options',
                          onTap: () => Get.toNamed('/payments'),
                        ),
                        _ProfileMenuItem(
                          icon: Icons.car_rental,
                          title: 'Vehicle Preferences',
                          subtitle: 'Preferred vehicle types and options',
                          onTap: () => Get.toNamed('/vehicle-preferences'),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // Support
                    _ProfileSection(
                      title: 'Support & Information',
                      children: [
                        _ProfileMenuItem(
                          icon: Icons.help_outline,
                          title: 'Help Center',
                          subtitle: 'FAQs and support articles',
                          onTap: () => Get.toNamed('/help'),
                        ),
                        _ProfileMenuItem(
                          icon: Icons.contact_support_outlined,
                          title: 'Contact Support',
                          subtitle: 'Get in touch with our support team',
                          onTap: () => Get.toNamed('/contact-support'),
                        ),
                        _ProfileMenuItem(
                          icon: Icons.privacy_tip_outlined,
                          title: 'Privacy Policy',
                          subtitle: 'Learn about our privacy practices',
                          onTap: () => Get.toNamed('/privacy'),
                        ),
                        _ProfileMenuItem(
                          icon: Icons.description_outlined,
                          title: 'Terms of Service',
                          subtitle: 'Read our terms and conditions',
                          onTap: () => Get.toNamed('/terms'),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // Account Actions
                    _ProfileSection(
                      title: 'Account Actions',
                      children: [
                        _ProfileMenuItem(
                          icon: Icons.logout,
                          title: 'Logout',
                          subtitle: 'Sign out of your account',
                          color: Colors.red,
                          onTap: () async {
                            final confirmed = await Get.dialog(
                              AlertDialog(
                                title: Text(
                                  'Logout',
                                  style: GoogleFonts.poppins(),
                                ),
                                content: Text(
                                  'Are you sure you want to logout?',
                                  style: GoogleFonts.poppins(),
                                ),
                                actions: [
                                  TextButton(
                                    onPressed: () => Get.back(result: false),
                                    child: Text(
                                      'Cancel',
                                      style: GoogleFonts.poppins(
                                        color: Colors.grey,
                                      ),
                                    ),
                                  ),
                                  TextButton(
                                    onPressed: () => Get.back(result: true),
                                    style: TextButton.styleFrom(
                                      backgroundColor: Colors.red,
                                      foregroundColor: Colors.white,
                                    ),
                                    child: Text(
                                      'Logout',
                                      style: GoogleFonts.poppins(),
                                    ),
                                  ),
                                ],
                              ),
                            );
                            
                            if (confirmed == true) {
                              await _authController.logout();
                            }
                          },
                        ),
                        _ProfileMenuItem(
                          icon: Icons.delete_outline,
                          title: 'Delete Account',
                          subtitle: 'Permanently delete your account',
                          color: Colors.red,
                          onTap: () => Get.toNamed('/delete-account'),
                        ),
                      ],
                    ),

                    const SizedBox(height: 40),
                    
                    // App Version
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Text(
                        'Zyra Ride v1.0.0',
                        style: GoogleFonts.poppins(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      }),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    super.dispose();
  }
}

// Profile Stat Widget
class _ProfileStat extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;

  const _ProfileStat({
    required this.title,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Icon(
            icon,
            color: Colors.white,
            size: 24,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: GoogleFonts.poppins(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          title,
          style: GoogleFonts.poppins(
            fontSize: 12,
            color: Colors.white.withOpacity(0.9),
          ),
        ),
      ],
    );
  }
}

// Profile Section Widget
class _ProfileSection extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _ProfileSection({
    required this.title,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: GoogleFonts.poppins(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.grey[800],
              ),
            ),
            const SizedBox(height: 8),
            ...children,
          ],
        ),
      ),
    );
  }
}

// Profile Menu Item Widget
class _ProfileMenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color? color;
  final VoidCallback onTap;

  const _ProfileMenuItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: (color ?? Colors.green).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  color: color ?? Colors.green,
                  size: 22,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: GoogleFonts.poppins(
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                        color: color ?? Colors.grey[800],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: GoogleFonts.poppins(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right,
                color: Colors.grey[400],
              ),
            ],
          ),
        ),
      ),
    );
  }
}