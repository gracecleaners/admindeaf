import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile_app/controllers/auth_controller.dart';

class EmailVerificationScreen extends StatefulWidget {
  final String email;
  
  const EmailVerificationScreen({
    Key? key,
    required this.email,
  }) : super(key: key);

  @override
  _EmailVerificationScreenState createState() => _EmailVerificationScreenState();
}

class _EmailVerificationScreenState extends State<EmailVerificationScreen> {
  final AuthController authController = Get.find<AuthController>();
  final TextEditingController otpController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  final List<FocusNode> _focusNodes = List.generate(6, (index) => FocusNode());
  final List<TextEditingController> _digitControllers = List.generate(6, (index) => TextEditingController());
  
  @override
  void initState() {
    super.initState();
    // Set up focus node listeners
    for (int i = 0; i < _focusNodes.length; i++) {
      _focusNodes[i].addListener(() {
        if (!_focusNodes[i].hasFocus && _digitControllers[i].text.isEmpty && i > 0) {
          FocusScope.of(context).requestFocus(_focusNodes[i - 1]);
        }
      });
    }
  }
  
  @override
  void dispose() {
    for (var controller in _digitControllers) {
      controller.dispose();
    }
    for (var focusNode in _focusNodes) {
      focusNode.dispose();
    }
    otpController.dispose();
    super.dispose();
  }
  
  void _verifyEmail() {
    if (_formKey.currentState?.validate() ?? false) {
      String otp = _digitControllers.map((c) => c.text).join();
      authController.verifyEmail(widget.email, otp);
    }
  }
  
  void _resendOtp() {
    authController.resendOtp(widget.email);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 60),
              
              // Back button
              IconButton(
                onPressed: () => Get.back(),
                icon: const Icon(Icons.arrow_back_rounded, color: Colors.black87),
              ),
              
              const SizedBox(height: 20),
              
              // Title
              Text(
                'Verify Your Email',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[900],
                ),
              ),
              
              const SizedBox(height: 8),
              
              // Subtitle
              Text(
                'We\'ve sent a 6-digit code to',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
              ),
              
              const SizedBox(height: 4),
              
              // Email address
              Text(
                widget.email,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.grey[900],
                ),
              ),
              
              const SizedBox(height: 40),
              
              // Illustration/Icon
              Center(
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    color: const Color(0xFF4F46E5).withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.mark_email_read_outlined,
                    size: 60,
                    color: Color(0xFF4F46E5),
                  ),
                ),
              ),
              
              const SizedBox(height: 40),
              
              // OTP Input Form
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    // OTP Input Fields
                    Text(
                      'Enter 6-digit code',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: Colors.grey[800],
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // OTP Digits
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: List.generate(6, (index) {
                        return SizedBox(
                          width: 50,
                          height: 60,
                          child: TextFormField(
                            controller: _digitControllers[index],
                            focusNode: _focusNodes[index],
                            keyboardType: TextInputType.number,
                            textAlign: TextAlign.center,
                            maxLength: 1,
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                            decoration: InputDecoration(
                              counterText: '',
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide(color: Colors.grey[300]!),
                              ),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide(color: Colors.grey[300]!),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: const BorderSide(color: Color(0xFF4F46E5), width: 2),
                              ),
                              filled: true,
                              fillColor: Colors.grey[50],
                            ),
                            onChanged: (value) {
                              if (value.isNotEmpty && index < 5) {
                                FocusScope.of(context).requestFocus(_focusNodes[index + 1]);
                              }
                              if (value.isEmpty && index > 0) {
                                FocusScope.of(context).requestFocus(_focusNodes[index - 1]);
                              }
                              // Auto verify when all digits are filled
                              if (index == 5 && value.isNotEmpty) {
                                bool allFilled = true;
                                for (var controller in _digitControllers) {
                                  if (controller.text.isEmpty) {
                                    allFilled = false;
                                    break;
                                  }
                                }
                                if (allFilled) {
                                  Future.delayed(const Duration(milliseconds: 300), _verifyEmail);
                                }
                              }
                            },
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return '';
                              }
                              return null;
                            },
                          ),
                        );
                      }),
                    ),
                    
                    const SizedBox(height: 32),
                    
                    // Verify Button
                    Obx(() => SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: authController.isLoading.value ? null : _verifyEmail,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF4F46E5),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 0,
                          disabledBackgroundColor: Colors.grey[300],
                        ),
                        child: authController.isLoading.value
                            ? const SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 3,
                                  valueColor: AlwaysStoppedAnimation(Colors.white),
                                ),
                              )
                            : const Text(
                                'Verify Email',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                      ),
                    )),
                    
                    const SizedBox(height: 24),
                    
                    // Alternative OTP Input
                    Text(
                      'Or enter code manually',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14,
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    TextFormField(
                      controller: otpController,
                      keyboardType: TextInputType.number,
                      textAlign: TextAlign.center,
                      maxLength: 6,
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.black87,
                      ),
                      decoration: InputDecoration(
                        hintText: 'Enter 6-digit code',
                        hintStyle: TextStyle(color: Colors.grey[500]),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey[300]!),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey[300]!),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFF4F46E5), width: 2),
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 18,
                        ),
                        filled: true,
                        fillColor: Colors.grey[50],
                      ),
                      onChanged: (value) {
                        // Update individual digit controllers
                        for (int i = 0; i < _digitControllers.length; i++) {
                          if (i < value.length) {
                            _digitControllers[i].text = value[i];
                          } else {
                            _digitControllers[i].text = '';
                          }
                        }
                      },
                    ),
                    
                    const SizedBox(height: 40),
                    
                    // Resend OTP Section
                    Column(
                      children: [
                        Text(
                          'Didn\'t receive the code?',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                        
                        const SizedBox(height: 8),
                        
                        Obx(() => TextButton(
                          onPressed: authController.isLoading.value ? null : _resendOtp,
                          child: Text(
                            'Resend OTP',
                            style: TextStyle(
                              color: const Color(0xFF4F46E5),
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        )),
                        
                        const SizedBox(height: 8),
                        
                        Text(
                          'Resend available in 60s',
                          style: TextStyle(
                            color: Colors.grey[500],
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 32),
                    
                    // Wrong email?
                    Center(
                      child: GestureDetector(
                        onTap: () {
                          Get.back(); // Go back to registration screen
                        },
                        child: Text(
                          'Wrong email address?',
                          style: TextStyle(
                            color: Colors.grey[700],
                            fontSize: 14,
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 40),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}