import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mobile_app/views/screens/dashboard.dart';
import 'package:mobile_app/views/screens/my_rides.dart';
import 'package:mobile_app/views/screens/profile.dart';

class MainLayout extends StatefulWidget {
  const MainLayout({super.key});

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const ZyraDashboard(),
    const MyRidesScreen(),
    const ProfileScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: NavigationBar(
          height: 65,
          elevation: 0,
          backgroundColor: Colors.white,
          indicatorColor: Colors.green.withOpacity(0.1),
          selectedIndex: _selectedIndex,
          onDestinationSelected: _onItemTapped,
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          animationDuration: const Duration(milliseconds: 300),
          destinations: [
            NavigationDestination(
              icon: const Icon(Icons.home_outlined, color: Colors.grey),
              selectedIcon: const Icon(Icons.home_rounded, color: Colors.green),
              label: 'Home',
            ),
            NavigationDestination(
              icon: const Icon(Icons.directions_car_outlined, color: Colors.grey),
              selectedIcon: const Icon(Icons.directions_car_rounded, color: Colors.green),
              label: 'My Rides',
            ),
            NavigationDestination(
              icon: const Icon(Icons.person_outline, color: Colors.grey),
              selectedIcon: const Icon(Icons.person_rounded, color: Colors.green),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}
