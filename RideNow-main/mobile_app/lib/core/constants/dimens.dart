import 'package:get/get.dart';

class Dimens {
  static double get horizontalPadding {
    final width = Get.width;
    if (width < 360) return 16;
    if (width < 600) return 20;
    return 24;
  }

  static double get verticalPadding {
    final height = Get.height;
    if (height < 600) return 12;
    if (height < 800) return 16;
    return 20;
  }

  static const double smallSpacing = 8;
  static const double mediumSpacing = 16;
  static const double largeSpacing = 24;
}