// dashboard_controller.dart
import 'package:get/get.dart';

class DashboardController extends GetxController {
  int selectedIndex = 1;
  bool showAppBar = true;
  
  void updateIndex(int index) {
    selectedIndex = index;
    
    showAppBar = (index == 1);
    
    update(); 
  }
}