import 'package:hive/hive.dart';
import 'package:json_annotation/json_annotation.dart';

part 'user_model.g.dart';

// Base User Model
@HiveType(typeId: 1)
@JsonSerializable()
class User {
  @HiveField(0)
  final int id;

  @HiveField(1)
  final String? name;

  @HiveField(2)
  final String email;

  @HiveField(9)
  final String? username;

  @HiveField(3)
  @JsonKey(name: 'is_client')
  final bool isClient;

  @HiveField(4)
  @JsonKey(name: 'is_driver')
  final bool isDriver;

  @HiveField(5)
  @JsonKey(name: 'profile_image')
  final String? profileImage;

  @HiveField(6)
  final String? phone;

  @HiveField(7)
  final String? gender;

  @HiveField(8)
  final DateTime? dateOfBirth;

  @HiveField(10)
  final String? firstName;

  @HiveField(11)
  final String? lastName;

  User({
    required this.id,
    this.name,
    required this.email,
    required this.isClient,
    required this.isDriver,
    this.username,
    this.profileImage,
    this.phone,
    this.gender,
    this.dateOfBirth,
    this.firstName,
    this.lastName,
  });

  String get fullName {
    if (name != null && name!.isNotEmpty) return name!;
    if (firstName != null || lastName != null) {
      return "${firstName ?? ''} ${lastName ?? ''}".trim();
    }
    return username ?? 'User';
  }

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  Map<String, dynamic> toJson() => _$UserToJson(this);
}

// Login Request Model
@JsonSerializable()
class LoginRequest {
  final String email;
  final String password;

  LoginRequest({
    required this.email,
    required this.password,
  });

  Map<String, dynamic> toJson() => {
        'email': email,
        'password': password,
      };
}

// Login Response Model
@JsonSerializable()
class LoginResponse {
  final String access;
  final String refresh;
  final User user;

  LoginResponse({
    required this.access,
    required this.refresh,
    required this.user,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) =>
      _$LoginResponseFromJson(json);

  Map<String, dynamic> toJson() => _$LoginResponseToJson(this);
}

// Registration Request Models

// Client Registration
@JsonSerializable()
class ClientRegisterRequest {
  final String firstName;
  final String lastName;
  final String email;
  final String password;
  final String confirmPassword;
  final String? phone;

  ClientRegisterRequest({
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.password,
    required this.confirmPassword,
    this.phone,
  });

  Map<String, dynamic> toJson() => _$ClientRegisterRequestToJson(this);

  // Add this factory constructor
  factory ClientRegisterRequest.fromJson(Map<String, dynamic> json) =>
      _$ClientRegisterRequestFromJson(json);
}

// Driver Registration
@JsonSerializable()
class DriverRegisterRequest {
  final String name;
  final String email;
  final String password;
  final String confirmPassword;
  final String? phone;
  final String? gender;
  final String? dateOfBirth;
  final String? licenseNumber;
  final int? yearsOfExperience;
  final String? vehicleType;
  final String? vehicleRegistration;

  DriverRegisterRequest({
    required this.name,
    required this.email,
    required this.password,
    required this.confirmPassword,
    this.phone,
    this.gender,
    this.dateOfBirth,
    this.licenseNumber,
    this.yearsOfExperience,
    this.vehicleType,
    this.vehicleRegistration,
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'email': email,
        'password': password,
        'confirm_password': confirmPassword,
        'phone': phone,
        'gender': gender,
        'date_of_birth': dateOfBirth,
        'license_number': licenseNumber,
        'years_of_experience': yearsOfExperience,
        'vehicle_type': vehicleType,
        'vehicle_registration': vehicleRegistration,
      };
}

// Email Verification Request
@JsonSerializable()
class VerifyEmailRequest {
  final String email;
  final String otp;

  VerifyEmailRequest({
    required this.email,
    required this.otp,
  });

  Map<String, dynamic> toJson() => {
        'email': email,
        'otp': otp,
      };
}

// Password Reset Request
@JsonSerializable()
class ResetPasswordRequest {
  final String email;

  ResetPasswordRequest({
    required this.email,
  });

  Map<String, dynamic> toJson() => {
        'email': email,
      };
}

// Change Password Request
@JsonSerializable()
class ChangePasswordRequest {
  final String oldPassword;
  final String newPassword;
  final String confirmNewPassword;

  ChangePasswordRequest({
    required this.oldPassword,
    required this.newPassword,
    required this.confirmNewPassword,
  });

  Map<String, dynamic> toJson() => {
        'old_password': oldPassword,
        'new_password': newPassword,
        'confirm_new_password': confirmNewPassword,
      };
}

// Profile Update Request
@JsonSerializable()
class UpdateProfileRequest {
  final String? name;
  final String? phone;
  final String? gender;
  final String? dateOfBirth;
  final String? profileImage;

  UpdateProfileRequest({
    this.name,
    this.phone,
    this.gender,
    this.dateOfBirth,
    this.profileImage,
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'phone': phone,
        'gender': gender,
        'date_of_birth': dateOfBirth,
        'profile_image': profileImage,
      };
}

class UserAdapter extends TypeAdapter<User> {
  @override
  final int typeId = 1;

  @override
  User read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return User(
      id: fields[0] as int,
      name: fields[1] as String?,
      email: fields[2] as String,
      username: fields[9] as String?,
      isClient: fields[3] as bool,
      isDriver: fields[4] as bool,
      profileImage: fields[5] as String?,
      phone: fields[6] as String?,
      gender: fields[7] as String?,
      dateOfBirth: fields[8] as DateTime?,
      firstName: fields[10] as String?,
      lastName: fields[11] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, User obj) {
    writer
      ..writeByte(12)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.name)
      ..writeByte(2)
      ..write(obj.email)
      ..writeByte(9)
      ..write(obj.username)
      ..writeByte(3)
      ..write(obj.isClient)
      ..writeByte(4)
      ..write(obj.isDriver)
      ..writeByte(5)
      ..write(obj.profileImage)
      ..writeByte(6)
      ..write(obj.phone)
      ..writeByte(7)
      ..write(obj.gender)
      ..writeByte(8)
      ..write(obj.dateOfBirth)
      ..writeByte(10)
      ..write(obj.firstName)
      ..writeByte(11)
      ..write(obj.lastName);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UserAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
