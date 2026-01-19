class ApiEndpoints {
  static const String baseUrl = 'https://zyra.daraza.net';
  static const String authentication = '$baseUrl/accounts/api/auth';
  static const String security = '$baseUrl/accounts/api/security';
  static const String accountMgt =
      '$baseUrl/accounts/api/account'; //change password & delete account
  static const String accounts = '$baseUrl/accounts/api';
  static const String userPref = '$baseUrl/accounts/api/preferences';
  static const String profileMgt = '$baseUrl/accounts/api/profile/';
  static const String userMgt =
      '$baseUrl/accounts/api/report'; //add report evidenc & report user
  static const String core = '$baseUrl/core/api';
  static const String finance = '$baseUrl/finance/api/wallet';
  static const String rideBase = '$baseUrl/rides/api';

  // Auth Endpoints
  static const String login = '$authentication/login/';
  static const String register = '$authentication/register/';
  static const String verifyEmail = '$authentication/verify/';
  static const String resendOtp = '$authentication/resend-verification/';
  static const String logout = '$authentication/logout/';
  static const String refreshToken = '$authentication/refresh/';
  static const String resetPassword = '$authentication/password-reset/request/';
  static const String changePassword = '$baseUrl/accounts/api/account/change-password/';
  static const String updateProfile = '$baseUrl/accounts/api/profile/update/';
  static const String uploadProfileImage =
      '$authentication/upload-profile-image/';

  // Client Registration
  static const String clientRegister = '$authentication/client/signup/';

  // Driver Registration
  static const String driverRegister = '$authentication/driver/signup/';

  // Rides Endpoints
  static const String rideRequests = '$rideBase/ride-requests/';
  static const String pendingRideRequests = '$rideRequests/pending/';
  static String rideRequestDetail(int id) => '$rideRequests$id/';
  static String acceptRideRequest(int id) => '$rideRequests$id/accept/';
  static String cancelRideRequest(int id) => '$rideRequests$id/cancel/';
  static String completeRideRequest(int id) => '$rideRequests$id/complete/';

  // Ride Matching
  static const String rideMatching = '$rideBase/ride-matching/';
  static String rideMatchingDetail(int id) => '$rideMatching$id/';
  static const String acceptRideMatch = '$rideBase/accept-ride-match/';
  static const String declineRideMatch = '$rideBase/decline-ride-match/';
  static const String startDriverMatching = '$rideBase/start-driver-matching/';
  static const String checkMatchingStatus = '$rideBase/check-matching-status/';
  static const String tryNextDriver = '$rideBase/try-next-driver/';
  static const String selectDriver = '$rideBase/select-driver/';

  // Driver Locations
  static const String driverLocations = '$rideBase/driver-locations/';
  static String driverLocationDetail(int id) => '$driverLocations$id/';
  static const String updateDriverLocation =
      '$driverLocations/update_location/';
  static const String goOnline = '$driverLocations/go_online/';
  static const String goOffline = '$driverLocations/go_offline/';
  static const String availableDrivers = '$rideBase/available-drivers/';
  static const String findNearbyDrivers = '$rideBase/find-nearby-drivers/';
  static const String getDriverLocation = '$rideBase/get-driver-location/';

  // Ride Actions
  static String arriveAtPickup(int rideId) =>
      '$rideBase/arrive-at-pickup/$rideId/';
  static String startRide(int rideId) => '$rideBase/start-ride/$rideId/';
  static String completeRide(int rideId) => '$rideBase/complete-ride/$rideId/';
  static String cancelRide(int rideId) => '$rideBase/cancel-ride/$rideId/';
  static const String quickRideRequest = '$rideBase/quick-ride-request/';

  // Ratings & Feedback
  static const String ratings = '$rideBase/ratings/';
  static String ratingDetail(int id) => '$ratings$id/';
  static const String submitRating = '$rideBase/submit-rating/';
  static const String feedback = '$rideBase/feedback/';
  static String feedbackDetail(int id) => '$feedback$id/';

  // Vehicle Types & Vehicles
  static const String vehicleTypes = '$rideBase/vehicle-types/';
  static String vehicleTypeDetail(int id) => '$vehicleTypes$id/';
  static const String vehicles = '$rideBase/vehicles/';
  static String vehicleDetail(int id) => '$vehicles$id/';
  static const String availableVehicles = '$vehicles/available/';

  // Statistics
  static const String driverStatistics = '$rideBase/driver-statistics/';
  static const String clientStatistics = '$rideBase/client-statistics/';

  static const String rides = '$rideBase/rides/';
  static String rideDetail(int id) => '$rides$id/';
}
