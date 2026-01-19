class Validator {
  // Email validation
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return "Email is required";
    }

    // regex for email
    final emailRegex = RegExp(r'^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-zA-Z]+');
    if (!emailRegex.hasMatch(value)) {
      return "Enter valid Email";
    }
    return null;
  }

  // phone validation
  static String? validatePhone(String? value) {
    if (value == null || value.isEmpty) {
      return 'Phone number is required';
    }
    // phone number regex
    final phoneRegex = RegExp(r'^\\+?256\\s?\\d{9}$|^0\\s?\\d{9}$');
    if (!phoneRegex.hasMatch(value)) {
      return "Enter a valid phone number";
    }
    if (value.length < 10) {
      return "Phone number must be atleast 10 digits";
    }
    return null;
  }

//  password validation
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return "Password is required";
    }
    // password regex
    final passwordRegex = RegExp(
        r'/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/');
    if (!passwordRegex.hasMatch(value)) {
      return "Password must contain at least eight characters, at least one number and both lower and uppercase letters and special characters";
    }
    return null;
  }
}
