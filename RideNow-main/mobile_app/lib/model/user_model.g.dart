// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

User _$UserFromJson(Map json) => $checkedCreate(
      'User',
      json,
      ($checkedConvert) {
        final val = User(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          name: $checkedConvert('name', (v) => v as String?),
          email: $checkedConvert('email', (v) => v as String),
          isClient: $checkedConvert('is_client', (v) => v as bool),
          isDriver: $checkedConvert('is_driver', (v) => v as bool),
          username: $checkedConvert('username', (v) => v as String?),
          profileImage: $checkedConvert('profile_image', (v) => v as String?),
          phone: $checkedConvert('phone', (v) => v as String?),
          gender: $checkedConvert('gender', (v) => v as String?),
          dateOfBirth: $checkedConvert('dateOfBirth',
              (v) => v == null ? null : DateTime.parse(v as String)),
          firstName: $checkedConvert('first_name', (v) => v as String?),
          lastName: $checkedConvert('last_name', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'isClient': 'is_client',
        'isDriver': 'is_driver',
        'profileImage': 'profile_image',
        'firstName': 'first_name',
        'lastName': 'last_name',
      },
    );

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'email': instance.email,
      'username': instance.username,
      'is_client': instance.isClient,
      'is_driver': instance.isDriver,
      'profile_image': instance.profileImage,
      'phone': instance.phone,
      'gender': instance.gender,
      'dateOfBirth': instance.dateOfBirth?.toIso8601String(),
      'first_name': instance.firstName,
      'last_name': instance.lastName,
    };

LoginRequest _$LoginRequestFromJson(Map json) => $checkedCreate(
      'LoginRequest',
      json,
      ($checkedConvert) {
        final val = LoginRequest(
          email: $checkedConvert('email', (v) => v as String),
          password: $checkedConvert('password', (v) => v as String),
        );
        return val;
      },
    );

Map<String, dynamic> _$LoginRequestToJson(LoginRequest instance) =>
    <String, dynamic>{
      'email': instance.email,
      'password': instance.password,
    };

LoginResponse _$LoginResponseFromJson(Map json) => $checkedCreate(
      'LoginResponse',
      json,
      ($checkedConvert) {
        final val = LoginResponse(
          access: $checkedConvert('access', (v) => v as String),
          refresh: $checkedConvert('refresh', (v) => v as String),
          user: $checkedConvert('user',
              (v) => User.fromJson(Map<String, dynamic>.from(v as Map))),
        );
        return val;
      },
    );

Map<String, dynamic> _$LoginResponseToJson(LoginResponse instance) =>
    <String, dynamic>{
      'access': instance.access,
      'refresh': instance.refresh,
      'user': instance.user.toJson(),
    };

ClientRegisterRequest _$ClientRegisterRequestFromJson(Map json) =>
    $checkedCreate(
      'ClientRegisterRequest',
      json,
      ($checkedConvert) {
        final val = ClientRegisterRequest(
          firstName: $checkedConvert('firstName', (v) => v as String),
          lastName: $checkedConvert('lastName', (v) => v as String),
          email: $checkedConvert('email', (v) => v as String),
          password: $checkedConvert('password', (v) => v as String),
          confirmPassword:
              $checkedConvert('confirmPassword', (v) => v as String),
          phone: $checkedConvert('phone', (v) => v as String?),
        );
        return val;
      },
    );

Map<String, dynamic> _$ClientRegisterRequestToJson(
        ClientRegisterRequest instance) =>
    <String, dynamic>{
      'firstName': instance.firstName,
      'lastName': instance.lastName,
      'email': instance.email,
      'password': instance.password,
      'confirmPassword': instance.confirmPassword,
      'phone': instance.phone,
    };

DriverRegisterRequest _$DriverRegisterRequestFromJson(Map json) =>
    $checkedCreate(
      'DriverRegisterRequest',
      json,
      ($checkedConvert) {
        final val = DriverRegisterRequest(
          name: $checkedConvert('name', (v) => v as String),
          email: $checkedConvert('email', (v) => v as String),
          password: $checkedConvert('password', (v) => v as String),
          confirmPassword:
              $checkedConvert('confirmPassword', (v) => v as String),
          phone: $checkedConvert('phone', (v) => v as String?),
          gender: $checkedConvert('gender', (v) => v as String?),
          dateOfBirth: $checkedConvert('dateOfBirth', (v) => v as String?),
          licenseNumber: $checkedConvert('licenseNumber', (v) => v as String?),
          yearsOfExperience:
              $checkedConvert('yearsOfExperience', (v) => (v as num?)?.toInt()),
          vehicleType: $checkedConvert('vehicleType', (v) => v as String?),
          vehicleRegistration:
              $checkedConvert('vehicleRegistration', (v) => v as String?),
        );
        return val;
      },
    );

Map<String, dynamic> _$DriverRegisterRequestToJson(
        DriverRegisterRequest instance) =>
    <String, dynamic>{
      'name': instance.name,
      'email': instance.email,
      'password': instance.password,
      'confirmPassword': instance.confirmPassword,
      'phone': instance.phone,
      'gender': instance.gender,
      'dateOfBirth': instance.dateOfBirth,
      'licenseNumber': instance.licenseNumber,
      'yearsOfExperience': instance.yearsOfExperience,
      'vehicleType': instance.vehicleType,
      'vehicleRegistration': instance.vehicleRegistration,
    };

VerifyEmailRequest _$VerifyEmailRequestFromJson(Map json) => $checkedCreate(
      'VerifyEmailRequest',
      json,
      ($checkedConvert) {
        final val = VerifyEmailRequest(
          email: $checkedConvert('email', (v) => v as String),
          otp: $checkedConvert('otp', (v) => v as String),
        );
        return val;
      },
    );

Map<String, dynamic> _$VerifyEmailRequestToJson(VerifyEmailRequest instance) =>
    <String, dynamic>{
      'email': instance.email,
      'otp': instance.otp,
    };

ResetPasswordRequest _$ResetPasswordRequestFromJson(Map json) => $checkedCreate(
      'ResetPasswordRequest',
      json,
      ($checkedConvert) {
        final val = ResetPasswordRequest(
          email: $checkedConvert('email', (v) => v as String),
        );
        return val;
      },
    );

Map<String, dynamic> _$ResetPasswordRequestToJson(
        ResetPasswordRequest instance) =>
    <String, dynamic>{
      'email': instance.email,
    };

ChangePasswordRequest _$ChangePasswordRequestFromJson(Map json) =>
    $checkedCreate(
      'ChangePasswordRequest',
      json,
      ($checkedConvert) {
        final val = ChangePasswordRequest(
          oldPassword: $checkedConvert('oldPassword', (v) => v as String),
          newPassword: $checkedConvert('newPassword', (v) => v as String),
          confirmNewPassword:
              $checkedConvert('confirmNewPassword', (v) => v as String),
        );
        return val;
      },
    );

Map<String, dynamic> _$ChangePasswordRequestToJson(
        ChangePasswordRequest instance) =>
    <String, dynamic>{
      'oldPassword': instance.oldPassword,
      'newPassword': instance.newPassword,
      'confirmNewPassword': instance.confirmNewPassword,
    };

UpdateProfileRequest _$UpdateProfileRequestFromJson(Map json) => $checkedCreate(
      'UpdateProfileRequest',
      json,
      ($checkedConvert) {
        final val = UpdateProfileRequest(
          name: $checkedConvert('name', (v) => v as String?),
          phone: $checkedConvert('phone', (v) => v as String?),
          gender: $checkedConvert('gender', (v) => v as String?),
          dateOfBirth: $checkedConvert('dateOfBirth', (v) => v as String?),
          profileImage: $checkedConvert('profileImage', (v) => v as String?),
        );
        return val;
      },
    );

Map<String, dynamic> _$UpdateProfileRequestToJson(
        UpdateProfileRequest instance) =>
    <String, dynamic>{
      'name': instance.name,
      'phone': instance.phone,
      'gender': instance.gender,
      'dateOfBirth': instance.dateOfBirth,
      'profileImage': instance.profileImage,
    };
