from django.utils.timezone import now
from django.contrib.auth import get_user_model
from .models import VerificationToken, ClientProfile, DriverProfile, ReportUser, ReportEvidence

from rest_framework import serializers

User = get_user_model()


class ClientSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True, write_only=True)  # Add write_only to prevent mapping to model field
    first_name = serializers.CharField(required=True, max_length=75)
    last_name = serializers.CharField(required=False, max_length=75, allow_blank=True)
    # date_of_birth = serializers.DateField(required=False)
    # gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], required=False)
    country = serializers.CharField(max_length=2, default='UG')
    city = serializers.CharField(required=False, max_length=75, default='Kampala')

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'first_name', 'last_name', 'country', 'city']

    def validate_email(self, value):
        """Ensure the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        """Ensure the phone number is unique."""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def generate_username(self, email):
        """Generate a unique username with a max length of 15 characters."""
        if email:
            base_username = email.split('@')[0]  # Extract part before '@'
        else:
            base_username = "user"  # Default if no email

        date_suffix = now().strftime("%d%m%y")  # Shortened format: DDMMYY

        # Ensure base + date suffix leaves space for counter (max 2 digits)
        max_base_length = 15 - len(date_suffix) - 2  # Reserve 2 chars for counter
        base_username = base_username[:max_base_length]  # Truncate if needed

        # Find a unique counter
        count = 1
        while User.objects.filter(username=f"{base_username}{date_suffix}{count:02d}").exists():
            count += 1
            if count > 99:  # Fallback in case of extreme collisions
                base_username = "usr"  # Force a short base name
                break

        return f"{base_username}{date_suffix}{count:02d}"

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        phone = validated_data.pop('phone')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name', '')
        # date_of_birth = validated_data.pop('date_of_birth')
        # gender = validated_data.pop('gender')
        country = validated_data.pop('country', 'UG')
        city = validated_data.pop('city', 'Kampala')
        
        # Create user
        user = User.objects.create(
            username=self.generate_username(email),
            email=email,
            phone_number=str(phone),  # Convert PhoneNumber to string for JSON serialization
            first_name=first_name,
            last_name=last_name,
            is_client=True,
            is_active=False
        )
        user.set_password(password)
        user.save()

        # Create client profile
        client_profile = ClientProfile.objects.create(
            user=user,
            username=user.username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=str(phone),  # Convert PhoneNumber to string for JSON serialization
            # date_of_birth=date_of_birth,
            # gender=gender,
            country=country,
            city=city
        )

        return user

    def to_representation(self, instance):
        """Override to prevent PhoneNumber serialization issues."""
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'is_client': instance.is_client,
            'is_active': instance.is_active,
            'message': 'Account created successfully'
        }


class DriverSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True, write_only=True)  # Add write_only to prevent mapping to model field
    first_name = serializers.CharField(required=True, max_length=75)
    last_name = serializers.CharField(required=False, max_length=75, allow_blank=True)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], required=True)
    country = serializers.CharField(max_length=2, default='UG')
    city = serializers.CharField(required=False, max_length=75, default='Kampala')
    vehicle_registration = serializers.CharField(required=True, max_length=15)
    drivers_license_no = serializers.CharField(required=False, max_length=15, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'first_name', 'last_name', 'date_of_birth', 'gender', 'country', 'city', 'vehicle_registration', 'drivers_license_no']

    def validate_email(self, value):
        """Ensure the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        """Ensure the phone number is unique."""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def generate_username(self, email):
        """Generate a unique username with a max length of 15 characters."""
        if email:
            base_username = email.split('@')[0]  # Extract part before '@'
        else:
            base_username = "user"  # Default if no email

        date_suffix = now().strftime("%d%m%y")  # Shortened format: DDMMYY

        # Ensure base + date suffix leaves space for counter (max 2 digits)
        max_base_length = 15 - len(date_suffix) - 2  # Reserve 2 chars for counter
        base_username = base_username[:max_base_length]  # Truncate if needed

        # Find a unique counter
        count = 1
        while User.objects.filter(username=f"{base_username}{date_suffix}{count:02d}").exists():
            count += 1
            if count > 99:  # Fallback in case of extreme collisions
                base_username = "usr"  # Force a short base name
                break

        return f"{base_username}{date_suffix}{count:02d}"

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        phone = validated_data.pop('phone')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name', '')
        date_of_birth = validated_data.pop('date_of_birth')
        gender = validated_data.pop('gender')
        country = validated_data.pop('country', 'UG')
        city = validated_data.pop('city', 'Kampala')
        vehicle_registration = validated_data.pop('vehicle_registration')
        drivers_license_no = validated_data.pop('drivers_license_no', '')
        
        # Create user
        user = User.objects.create(
            username=self.generate_username(email),
            email=email,
            phone_number=str(phone),  # Convert PhoneNumber to string for JSON serialization
            first_name=first_name,
            last_name=last_name,
            is_driver=True,
            is_active=False
        )
        user.set_password(password)
        user.save()

        # Create driver profile
        driver_profile = DriverProfile.objects.create(
            user=user,
            username=user.username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=str(phone),  # Convert PhoneNumber to string for JSON serialization
            date_of_birth=date_of_birth,
            gender=gender,
            country=country,
            city=city,
            vehicle_registration=vehicle_registration,
            drivers_license_no=drivers_license_no
        )

        return user

    def to_representation(self, instance):
        """Override to prevent PhoneNumber serialization issues."""
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'is_driver': instance.is_driver,
            'is_active': instance.is_active,
            'message': 'Account created successfully'
        }
    

class LoginSerializer(serializers.Serializer):
    username_or_email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if user with this email exists"""
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError("Account is not active.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email address.")


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate token and password confirmation"""
        token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check if passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        # Validate token
        try:
            reset_token = VerificationToken.objects.get(token=token, token_type='PASSWORD_RESET')
            if not reset_token.is_valid():
                raise serializers.ValidationError("Invalid or expired token.")
            data['reset_token'] = reset_token
        except VerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")

        return data


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = [
            'id', 'username', 'unique_id', 'first_name', 'last_name', 'other_name',
            'photo', 'cover_photo', 'email', 'email_confirmed', 'phone', 'country',
            'gender', 'date_of_birth', 'city', 'bio', 'interests', 'is_verified',
            'is_active', 'is_banned', 'is_online', 'created', 'updated_on'
        ]
        read_only_fields = ['id', 'unique_id', 'created', 'updated_on', 'is_online']

    def update(self, instance, validated_data):
        # Update user fields if they exist
        user = instance.user
        if 'first_name' in validated_data:
            user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user.last_name = validated_data.pop('last_name')
        if 'email' in validated_data:
            user.email = validated_data.pop('email')
        if 'phone' in validated_data:
            user.phone_number = validated_data.pop('phone')
        user.save()
        
        return super().update(instance, validated_data)


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = [
            'id', 'username', 'unique_id', 'first_name', 'last_name', 'other_name',
            'photo', 'cover_photo', 'email', 'email_confirmed', 'phone', 'country',
            'gender', 'date_of_birth', 'city', 'bio', 'vehicle_registration',
            'drivers_license_no', 'is_verified', 'is_active', 'is_banned', 'is_online',
            'created', 'updated_on'
        ]
        read_only_fields = ['id', 'unique_id', 'created', 'updated_on', 'is_online']

    def update(self, instance, validated_data):
        # Update user fields if they exist
        user = instance.user
        if 'first_name' in validated_data:
            user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user.last_name = validated_data.pop('last_name')
        if 'email' in validated_data:
            user.email = validated_data.pop('email')
        if 'phone' in validated_data:
            user.phone_number = validated_data.pop('phone')
        user.save()
        
        return super().update(instance, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    client_profile = ClientProfileSerializer(read_only=True)
    driver_profile = DriverProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 'first_name', 'last_name',
            'is_client', 'is_driver', 'is_banned', 'date_joined', 'last_login',
            'client_profile', 'driver_profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords don't match.")
        return data


class ReportUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportUser
        fields = ['reported_user', 'complaint']
        read_only_fields = ['reporter', 'timestamp', 'updated']


class ReportEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportEvidence
        fields = ['file']
        read_only_fields = ['report', 'timestamp', 'updated']


class AccountDeletionSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    feedback = serializers.CharField(required=False, allow_blank=True)
