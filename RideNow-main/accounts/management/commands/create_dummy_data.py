from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
import uuid

from accounts.models import ClientProfile, DriverProfile, TermsAcceptance
from rides.models import VehicleType, Vehicle, RideRequest, DriverLocation
from core.models import SystemUtility
from finance.models import UserWallet

User = get_user_model()


class Command(BaseCommand):
    help = 'Create dummy data for testing ride booking experience'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing dummy data before creating new data (always enabled)',
        )

    def handle(self, *args, **options):
        # Always clear existing dummy data to avoid conflicts
        self.clear_dummy_data()
        
        self.stdout.write(self.style.SUCCESS('Creating dummy data...'))
        
        # Create Terms of Service
        self.create_terms_of_service()
        
        # Create Vehicle Types
        self.create_vehicle_types()
        
        # Create Vehicles
        self.create_vehicles()
        
        # Create Test Users and Profiles
        self.create_test_users()
        
        # Create Drivers
        self.create_drivers()
        
        # Create Driver Locations
        self.create_driver_locations()
        
        self.stdout.write(self.style.SUCCESS('Successfully created dummy data!'))

    def clear_dummy_data(self):
        """Clear existing dummy data"""
        self.stdout.write(self.style.WARNING('Clearing existing dummy data...'))
        
        # Delete test users (those with @ridenow.test domain)
        User.objects.filter(email__endswith='@ridenow.test').delete()
        
        # Clear dummy driver locations (only for test drivers)
        DriverLocation.objects.filter(driver__user__email__endswith='@ridenow.test').delete()
        
        # Clear dummy vehicles (only those with UAB registration pattern)
        Vehicle.objects.filter(registration_number__startswith='UAB').delete()
        
        # Clear dummy vehicle types (only those created by this command)
        VehicleType.objects.filter(name__in=[
            'Boda Boda', 'Standard Car', 'Comfort Car', 'Executive Car', 'XL Vehicle',
            'Premium SUV', 'Minivan', 'Bus', 'Tuk Tuk', 'Pickup Truck'
        ]).delete()
        
        self.stdout.write(self.style.SUCCESS('Existing dummy data cleared!'))

    def create_terms_of_service(self):
        """Create Terms of Service in SystemUtility"""
        self.stdout.write('Creating Terms of Service...')
        
        terms_content = """
        <h2>Terms of Service - RideNow</h2>
        
        <h3>1. Acceptance of Terms</h3>
        <p>By using RideNow services, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our services.</p>
        
        <h3>2. Service Description</h3>
        <p>RideNow provides a platform connecting riders with drivers for transportation services. We facilitate the connection but are not responsible for the actual transportation service.</p>
        
        <h3>3. User Responsibilities</h3>
        <ul>
            <li>Provide accurate personal information</li>
            <li>Behave respectfully during rides</li>
            <li>Pay for services as agreed</li>
            <li>Follow local traffic laws and regulations</li>
        </ul>
        
        <h3>4. Driver Responsibilities</h3>
        <ul>
            <li>Maintain valid licenses and insurance</li>
            <li>Provide safe and reliable transportation</li>
            <li>Treat all passengers with respect</li>
            <li>Follow platform guidelines and policies</li>
        </ul>
        
        <h3>5. Payment Terms</h3>
        <p>All payments are processed through our secure payment system. Riders agree to pay the quoted fare for services rendered.</p>
        
        <h3>6. Cancellation Policy</h3>
        <p>Rides can be cancelled up to 5 minutes before scheduled pickup time without penalty. Late cancellations may incur fees.</p>
        
        <h3>7. Safety and Security</h3>
        <p>We prioritize safety for all users. Any violations of safety protocols may result in account suspension or termination.</p>
        
        <h3>8. Limitation of Liability</h3>
        <p>RideNow's liability is limited to the amount paid for the specific service. We are not liable for indirect damages or losses.</p>
        
        <h3>9. Privacy Policy</h3>
        <p>Your privacy is important to us. Please review our Privacy Policy for information on how we collect, use, and protect your data.</p>
        
        <h3>10. Changes to Terms</h3>
        <p>We reserve the right to modify these terms at any time. Users will be notified of significant changes via email or app notification.</p>
        
        <h3>11. Contact Information</h3>
        <p>For questions about these terms, please contact us at:</p>
        <ul>
            <li>Email: support@ridenow.com</li>
            <li>Phone: +256 700 123 456</li>
            <li>Address: Kampala, Uganda</li>
        </ul>
        
        <p><strong>Last Updated:</strong> {}</p>
        """.format(timezone.now().strftime('%B %d, %Y'))
        
        privacy_content = """
        <h2>Privacy Policy - RideNow</h2>
        
        <h3>Information We Collect</h3>
        <p>We collect information you provide directly to us, such as when you create an account, request a ride, or contact us for support.</p>
        
        <h3>How We Use Your Information</h3>
        <p>We use the information we collect to provide, maintain, and improve our services, process transactions, and communicate with you.</p>
        
        <h3>Information Sharing</h3>
        <p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.</p>
        
        <h3>Data Security</h3>
        <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
        
        <h3>Your Rights</h3>
        <p>You have the right to access, update, or delete your personal information. You can do this through your account settings or by contacting us.</p>
        
        <p><strong>Last Updated:</strong> {}</p>
        """.format(timezone.now().strftime('%B %d, %Y'))
        
        utility, created = SystemUtility.objects.get_or_create(
            id=1,
            defaults={
                'root_email': 'admin@ridenow.com',
                'user_support_email': 'support@ridenow.com',
                'sales_commission': 10,
                'terms_of_use': terms_content,
                'privacy_policy': privacy_content,
                'info': 'Welcome to RideNow - Your reliable ride-hailing service in Uganda',
                'address': 'Kampala, Uganda',
                'send_emails_alert': True,
                'send_sms_alert': True,
            }
        )
        
        if not created:
            utility.terms_of_use = terms_content
            utility.privacy_policy = privacy_content
            utility.save()
        
        self.stdout.write(self.style.SUCCESS('✓ Terms of Service created'))

    def create_vehicle_types(self):
        """Create vehicle types"""
        self.stdout.write('Creating vehicle types...')
        
        vehicle_types_data = [
            {
                'name': 'Boda Boda',
                'vehicle_type': 'motorcycle',
                'description': 'Quick and affordable motorcycle taxi popular in Uganda',
                'engine_type': '125cc',
                'vehicle_capacity': '2 seater',
                'base_price': 2000.00,
                'price_per_km': 500.00
            },
            {
                'name': 'Standard Car',
                'vehicle_type': 'sedan',
                'description': 'Comfortable 4-seater sedan perfect for everyday rides',
                'engine_type': '1500cc',
                'vehicle_capacity': '4 seater',
                'base_price': 5000.00,
                'price_per_km': 1000.00
            },
            {
                'name': 'Comfort Car',
                'vehicle_type': 'sedan',
                'description': 'Premium sedan with extra comfort features',
                'engine_type': '2000cc',
                'vehicle_capacity': '4 seater',
                'base_price': 7000.00,
                'price_per_km': 1500.00
            },
            {
                'name': 'Executive Car',
                'vehicle_type': 'sedan',
                'description': 'Luxury sedan for business and special occasions',
                'engine_type': '2500cc',
                'vehicle_capacity': '4 seater',
                'base_price': 12000.00,
                'price_per_km': 2500.00
            },
            {
                'name': 'XL Vehicle',
                'vehicle_type': 'SUV',
                'description': 'Large SUV perfect for groups and luggage',
                'engine_type': '2500cc',
                'vehicle_capacity': '6 seater',
                'base_price': 10000.00,
                'price_per_km': 2000.00
            },
            {
                'name': 'Premium SUV',
                'vehicle_type': 'SUV',
                'description': 'Luxury SUV with premium features',
                'engine_type': '3000cc',
                'vehicle_capacity': '7 seater',
                'base_price': 15000.00,
                'price_per_km': 3000.00
            },
            {
                'name': 'Minivan',
                'vehicle_type': 'van',
                'description': 'Spacious minivan for large groups',
                'engine_type': '2500cc',
                'vehicle_capacity': '8 seater',
                'base_price': 8000.00,
                'price_per_km': 1800.00
            },
            {
                'name': 'Bus',
                'vehicle_type': 'van',
                'description': 'Large bus for group transportation',
                'engine_type': '4000cc',
                'vehicle_capacity': '14 seater',
                'base_price': 20000.00,
                'price_per_km': 4000.00
            },
            {
                'name': 'Tuk Tuk',
                'vehicle_type': 'auto_rickshaw',
                'description': 'Three-wheeled auto rickshaw for short distances',
                'engine_type': '200cc',
                'vehicle_capacity': '3 seater',
                'base_price': 3000.00,
                'price_per_km': 700.00
            },
            {
                'name': 'Pickup Truck',
                'vehicle_type': 'truck',
                'description': 'Pickup truck for cargo and passenger transport',
                'engine_type': '3000cc',
                'vehicle_capacity': '5 seater',
                'base_price': 9000.00,
                'price_per_km': 2200.00
            }
        ]
        
        for vehicle_data in vehicle_types_data:
            VehicleType.objects.get_or_create(
                name=vehicle_data['name'],
                defaults=vehicle_data
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Vehicle types created'))

    def create_vehicles(self):
        """Create vehicles"""
        self.stdout.write('Creating vehicles...')
        
        vehicle_types = VehicleType.objects.all()
        if not vehicle_types.exists():
            self.stdout.write(self.style.WARNING('No vehicle types found. Creating vehicle types first...'))
            self.create_vehicle_types()
            vehicle_types = VehicleType.objects.all()
        
        vehicles_data = [
            # Boda Boda Motorcycles
            {'name': 'Bajaj Boxer', 'registration_number': 'UAB 101A', 'vehicle_type': 'Boda Boda', 'is_air_conditioned': False, 'is_insured': True, 'age': '2021'},
            {'name': 'TVS Star', 'registration_number': 'UAB 102B', 'vehicle_type': 'Boda Boda', 'is_air_conditioned': False, 'is_insured': True, 'age': '2022'},
            {'name': 'Honda CG', 'registration_number': 'UAB 103C', 'vehicle_type': 'Boda Boda', 'is_air_conditioned': False, 'is_insured': True, 'age': '2020'},
            {'name': 'Yamaha FZ', 'registration_number': 'UAB 104D', 'vehicle_type': 'Boda Boda', 'is_air_conditioned': False, 'is_insured': True, 'age': '2021'},
            {'name': 'Suzuki GSX-R', 'registration_number': 'UAB 105E', 'vehicle_type': 'Boda Boda', 'is_air_conditioned': False, 'is_insured': True, 'age': '2022'},
            
            # Standard Cars
            {'name': 'Toyota Corolla', 'registration_number': 'UAB 201A', 'vehicle_type': 'Standard Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2020'},
            {'name': 'Honda Civic', 'registration_number': 'UAB 202B', 'vehicle_type': 'Standard Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            {'name': 'Nissan Almera', 'registration_number': 'UAB 203C', 'vehicle_type': 'Standard Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2019'},
            {'name': 'Mazda 3', 'registration_number': 'UAB 204D', 'vehicle_type': 'Standard Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2022'},
            {'name': 'Hyundai Elantra', 'registration_number': 'UAB 205E', 'vehicle_type': 'Standard Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            
            # Comfort Cars
            {'name': 'Toyota Camry', 'registration_number': 'UAB 301A', 'vehicle_type': 'Comfort Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2020'},
            {'name': 'Honda Accord', 'registration_number': 'UAB 302B', 'vehicle_type': 'Comfort Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            {'name': 'Nissan Altima', 'registration_number': 'UAB 303C', 'vehicle_type': 'Comfort Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2019'},
            {'name': 'BMW 3 Series', 'registration_number': 'UAB 304D', 'vehicle_type': 'Comfort Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2022'},
            {'name': 'Mercedes C-Class', 'registration_number': 'UAB 305E', 'vehicle_type': 'Comfort Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            
            # Executive Cars
            {'name': 'BMW 5 Series', 'registration_number': 'UAB 401A', 'vehicle_type': 'Executive Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2020'},
            {'name': 'Mercedes E-Class', 'registration_number': 'UAB 402B', 'vehicle_type': 'Executive Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            {'name': 'Audi A6', 'registration_number': 'UAB 403C', 'vehicle_type': 'Executive Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2019'},
            {'name': 'Lexus ES', 'registration_number': 'UAB 404D', 'vehicle_type': 'Executive Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2022'},
            {'name': 'Jaguar XF', 'registration_number': 'UAB 405E', 'vehicle_type': 'Executive Car', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            
            # SUVs
            {'name': 'Toyota RAV4', 'registration_number': 'UAB 501A', 'vehicle_type': 'XL Vehicle', 'is_air_conditioned': True, 'is_insured': True, 'age': '2020'},
            {'name': 'Honda CR-V', 'registration_number': 'UAB 502B', 'vehicle_type': 'XL Vehicle', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            {'name': 'Nissan X-Trail', 'registration_number': 'UAB 503C', 'vehicle_type': 'XL Vehicle', 'is_air_conditioned': True, 'is_insured': True, 'age': '2019'},
            {'name': 'Mazda CX-5', 'registration_number': 'UAB 504D', 'vehicle_type': 'XL Vehicle', 'is_air_conditioned': True, 'is_insured': True, 'age': '2022'},
            {'name': 'Hyundai Tucson', 'registration_number': 'UAB 505E', 'vehicle_type': 'XL Vehicle', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            
            # Premium SUVs
            {'name': 'Toyota Land Cruiser', 'registration_number': 'UAB 601A', 'vehicle_type': 'Premium SUV', 'is_air_conditioned': True, 'is_insured': True, 'age': '2020'},
            {'name': 'BMW X5', 'registration_number': 'UAB 602B', 'vehicle_type': 'Premium SUV', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            {'name': 'Mercedes GLE', 'registration_number': 'UAB 603C', 'vehicle_type': 'Premium SUV', 'is_air_conditioned': True, 'is_insured': True, 'age': '2019'},
            {'name': 'Audi Q7', 'registration_number': 'UAB 604D', 'vehicle_type': 'Premium SUV', 'is_air_conditioned': True, 'is_insured': True, 'age': '2022'},
            {'name': 'Range Rover', 'registration_number': 'UAB 605E', 'vehicle_type': 'Premium SUV', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            
            # Vans
            {'name': 'Toyota Hiace', 'registration_number': 'UAB 701A', 'vehicle_type': 'Minivan', 'is_air_conditioned': False, 'is_insured': True, 'age': '2020'},
            {'name': 'Nissan Urvan', 'registration_number': 'UAB 702B', 'vehicle_type': 'Minivan', 'is_air_conditioned': False, 'is_insured': True, 'age': '2021'},
            {'name': 'Ford Transit', 'registration_number': 'UAB 703C', 'vehicle_type': 'Minivan', 'is_air_conditioned': False, 'is_insured': True, 'age': '2019'},
            {'name': 'Mercedes Sprinter', 'registration_number': 'UAB 704D', 'vehicle_type': 'Minivan', 'is_air_conditioned': True, 'is_insured': True, 'age': '2022'},
            {'name': 'Iveco Daily', 'registration_number': 'UAB 705E', 'vehicle_type': 'Minivan', 'is_air_conditioned': False, 'is_insured': True, 'age': '2021'},
            
            # Buses
            {'name': 'Toyota Coaster', 'registration_number': 'UAB 801A', 'vehicle_type': 'Bus', 'is_air_conditioned': True, 'is_insured': True, 'age': '2020'},
            {'name': 'Isuzu NPR', 'registration_number': 'UAB 802B', 'vehicle_type': 'Bus', 'is_air_conditioned': False, 'is_insured': True, 'age': '2021'},
            {'name': 'Mitsubishi Rosa', 'registration_number': 'UAB 803C', 'vehicle_type': 'Bus', 'is_air_conditioned': True, 'is_insured': True, 'age': '2019'},
            {'name': 'Ford Transit Bus', 'registration_number': 'UAB 804D', 'vehicle_type': 'Bus', 'is_air_conditioned': True, 'is_insured': True, 'age': '2022'},
            {'name': 'Mercedes Sprinter Bus', 'registration_number': 'UAB 805E', 'vehicle_type': 'Bus', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            
            # Tuk Tuks
            {'name': 'Bajaj RE', 'registration_number': 'UAB 901A', 'vehicle_type': 'Tuk Tuk', 'is_air_conditioned': False, 'is_insured': True, 'age': '2021'},
            {'name': 'TVS King', 'registration_number': 'UAB 902B', 'vehicle_type': 'Tuk Tuk', 'is_air_conditioned': False, 'is_insured': True, 'age': '2022'},
            {'name': 'Piaggio Ape', 'registration_number': 'UAB 903C', 'vehicle_type': 'Tuk Tuk', 'is_air_conditioned': False, 'is_insured': True, 'age': '2020'},
            
            # Pickup Trucks
            {'name': 'Toyota Hilux', 'registration_number': 'UAB 951A', 'vehicle_type': 'Pickup Truck', 'is_air_conditioned': True, 'is_insured': True, 'age': '2020'},
            {'name': 'Ford Ranger', 'registration_number': 'UAB 952B', 'vehicle_type': 'Pickup Truck', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
            {'name': 'Nissan Navara', 'registration_number': 'UAB 953C', 'vehicle_type': 'Pickup Truck', 'is_air_conditioned': True, 'is_insured': True, 'age': '2019'},
            {'name': 'Mitsubishi L200', 'registration_number': 'UAB 954D', 'vehicle_type': 'Pickup Truck', 'is_air_conditioned': True, 'is_insured': True, 'age': '2022'},
            {'name': 'Isuzu D-Max', 'registration_number': 'UAB 955E', 'vehicle_type': 'Pickup Truck', 'is_air_conditioned': True, 'is_insured': True, 'age': '2021'},
        ]
        
        # Create a mapping of vehicle type names to vehicle type objects
        vehicle_type_map = {vt.name: vt for vt in vehicle_types}
        
        for vehicle_data in vehicles_data:
            vehicle_type = vehicle_type_map.get(vehicle_data['vehicle_type'])
            if vehicle_type:
                Vehicle.objects.get_or_create(
                    registration_number=vehicle_data['registration_number'],
                    defaults={
                        'type': vehicle_type,
                        'name': vehicle_data['name'],
                        'description': f'Well-maintained {vehicle_data["name"]} with excellent service record',
                        'is_air_conditioned': vehicle_data['is_air_conditioned'],
                        'is_insured': vehicle_data['is_insured'],
                        'age': vehicle_data['age']
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('✓ Vehicles created'))

    def create_test_users(self):
        """Create test users"""
        self.stdout.write('Creating test users...')
        
        test_users = [
            {
                'email': 'test.client@ridenow.test',
                'phone_number': '+256700123456',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_client': True
            },
            {
                'email': 'test.client2@ridenow.test',
                'phone_number': '+256700123457',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'is_client': True
            },
            {
                'email': 'test.client3@ridenow.test',
                'phone_number': '+256700123458',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'is_client': True
            }
        ]
        
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'phone_number': user_data['phone_number'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_client': user_data['is_client'],
                    'is_active': True,
                    'username': user_data['email'].split('@')[0]
                }
            )
            
            if created and user.is_client:
                # Create client profile
                ClientProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'phone': user.phone_number,
                        'date_of_birth': timezone.now().date() - timedelta(days=random.randint(6570, 10950)),  # 18-30 years old
                        'gender': random.choice(['M', 'F']),
                        'city': 'Kampala',
                        'is_active': True
                    }
                )
                
                # Create wallet
                UserWallet.objects.get_or_create(
                    owner=user,
                    defaults={
                        'amount': random.randint(10000, 100000),  # Random amount between 10,000-100,000 UGX
                        'points': random.randint(0, 1000),
                        'is_active': True
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('✓ Test users created'))

    def create_drivers(self):
        """Create driver profiles"""
        self.stdout.write('Creating drivers...')
        
        vehicles = Vehicle.objects.all()
        if not vehicles.exists():
            self.stdout.write(self.style.WARNING('No vehicles found. Creating vehicles first...'))
            self.create_vehicles()
            vehicles = Vehicle.objects.all()
        
        driver_data = [
            # Kampala Drivers
            {'email': 'driver1@ridenow.test', 'phone_number': '+256700200001', 'first_name': 'Peter', 'last_name': 'Ochieng', 'vehicle_registration': 'UAB 101A', 'city': 'Kampala'},
            {'email': 'driver2@ridenow.test', 'phone_number': '+256700200002', 'first_name': 'Sarah', 'last_name': 'Nakato', 'vehicle_registration': 'UAB 201A', 'city': 'Kampala'},
            {'email': 'driver3@ridenow.test', 'phone_number': '+256700200003', 'first_name': 'David', 'last_name': 'Mukasa', 'vehicle_registration': 'UAB 301A', 'city': 'Kampala'},
            {'email': 'driver4@ridenow.test', 'phone_number': '+256700200004', 'first_name': 'Grace', 'last_name': 'Akello', 'vehicle_registration': 'UAB 401A', 'city': 'Kampala'},
            {'email': 'driver5@ridenow.test', 'phone_number': '+256700200005', 'first_name': 'Robert', 'last_name': 'Kato', 'vehicle_registration': 'UAB 501A', 'city': 'Kampala'},
            {'email': 'driver6@ridenow.test', 'phone_number': '+256700200006', 'first_name': 'Mary', 'last_name': 'Namukasa', 'vehicle_registration': 'UAB 601A', 'city': 'Kampala'},
            {'email': 'driver7@ridenow.test', 'phone_number': '+256700200007', 'first_name': 'Joseph', 'last_name': 'Ssemwogerere', 'vehicle_registration': 'UAB 701A', 'city': 'Kampala'},
            {'email': 'driver8@ridenow.test', 'phone_number': '+256700200008', 'first_name': 'Florence', 'last_name': 'Nabukenya', 'vehicle_registration': 'UAB 801A', 'city': 'Kampala'},
            {'email': 'driver9@ridenow.test', 'phone_number': '+256700200009', 'first_name': 'Paul', 'last_name': 'Kiggundu', 'vehicle_registration': 'UAB 901A', 'city': 'Kampala'},
            {'email': 'driver10@ridenow.test', 'phone_number': '+256700200010', 'first_name': 'Esther', 'last_name': 'Mugabi', 'vehicle_registration': 'UAB 951A', 'city': 'Kampala'},
            
            # Jinja Drivers
            {'email': 'driver11@ridenow.test', 'phone_number': '+256700200011', 'first_name': 'Samuel', 'last_name': 'Waiswa', 'vehicle_registration': 'UAB 102B', 'city': 'Jinja'},
            {'email': 'driver12@ridenow.test', 'phone_number': '+256700200012', 'first_name': 'Rebecca', 'last_name': 'Nalubega', 'vehicle_registration': 'UAB 202B', 'city': 'Jinja'},
            {'email': 'driver13@ridenow.test', 'phone_number': '+256700200013', 'first_name': 'Moses', 'last_name': 'Kakooza', 'vehicle_registration': 'UAB 302B', 'city': 'Jinja'},
            {'email': 'driver14@ridenow.test', 'phone_number': '+256700200014', 'first_name': 'Dorothy', 'last_name': 'Nakamya', 'vehicle_registration': 'UAB 402B', 'city': 'Jinja'},
            {'email': 'driver15@ridenow.test', 'phone_number': '+256700200015', 'first_name': 'Andrew', 'last_name': 'Mutebi', 'vehicle_registration': 'UAB 502B', 'city': 'Jinja'},
            
            # Entebbe Drivers
            {'email': 'driver16@ridenow.test', 'phone_number': '+256700200016', 'first_name': 'John', 'last_name': 'Kigozi', 'vehicle_registration': 'UAB 103C', 'city': 'Entebbe'},
            {'email': 'driver17@ridenow.test', 'phone_number': '+256700200017', 'first_name': 'Agnes', 'last_name': 'Nabukeera', 'vehicle_registration': 'UAB 203C', 'city': 'Entebbe'},
            {'email': 'driver18@ridenow.test', 'phone_number': '+256700200018', 'first_name': 'Francis', 'last_name': 'Lubwama', 'vehicle_registration': 'UAB 303C', 'city': 'Entebbe'},
            {'email': 'driver19@ridenow.test', 'phone_number': '+256700200019', 'first_name': 'Peace', 'last_name': 'Nakirijja', 'vehicle_registration': 'UAB 403C', 'city': 'Entebbe'},
            {'email': 'driver20@ridenow.test', 'phone_number': '+256700200020', 'first_name': 'Patrick', 'last_name': 'Kiggundu', 'vehicle_registration': 'UAB 503C', 'city': 'Entebbe'},
            
            # Mbarara Drivers
            {'email': 'driver21@ridenow.test', 'phone_number': '+256700200021', 'first_name': 'Richard', 'last_name': 'Tumwesigye', 'vehicle_registration': 'UAB 104D', 'city': 'Mbarara'},
            {'email': 'driver22@ridenow.test', 'phone_number': '+256700200022', 'first_name': 'Immaculate', 'last_name': 'Kyomugisha', 'vehicle_registration': 'UAB 204D', 'city': 'Mbarara'},
            {'email': 'driver23@ridenow.test', 'phone_number': '+256700200023', 'first_name': 'Geoffrey', 'last_name': 'Mugisha', 'vehicle_registration': 'UAB 304D', 'city': 'Mbarara'},
            {'email': 'driver24@ridenow.test', 'phone_number': '+256700200024', 'first_name': 'Grace', 'last_name': 'Muhwezi', 'vehicle_registration': 'UAB 404D', 'city': 'Mbarara'},
            {'email': 'driver25@ridenow.test', 'phone_number': '+256700200025', 'first_name': 'Solomon', 'last_name': 'Baryamujura', 'vehicle_registration': 'UAB 504D', 'city': 'Mbarara'},
            
            # Gulu Drivers
            {'email': 'driver26@ridenow.test', 'phone_number': '+256700200026', 'first_name': 'James', 'last_name': 'Ocaya', 'vehicle_registration': 'UAB 105E', 'city': 'Gulu'},
            {'email': 'driver27@ridenow.test', 'phone_number': '+256700200027', 'first_name': 'Alice', 'last_name': 'Acan', 'vehicle_registration': 'UAB 205E', 'city': 'Gulu'},
            {'email': 'driver28@ridenow.test', 'phone_number': '+256700200028', 'first_name': 'Charles', 'last_name': 'Lakor', 'vehicle_registration': 'UAB 305E', 'city': 'Gulu'},
            {'email': 'driver29@ridenow.test', 'phone_number': '+256700200029', 'first_name': 'Mary', 'last_name': 'Akello', 'vehicle_registration': 'UAB 405E', 'city': 'Gulu'},
            {'email': 'driver30@ridenow.test', 'phone_number': '+256700200030', 'first_name': 'Peter', 'last_name': 'Ochola', 'vehicle_registration': 'UAB 505E', 'city': 'Gulu'},
            
            # Mbale Drivers
            {'email': 'driver31@ridenow.test', 'phone_number': '+256700200031', 'first_name': 'Wilson', 'last_name': 'Wandera', 'vehicle_registration': 'UAB 601A', 'city': 'Mbale'},
            {'email': 'driver32@ridenow.test', 'phone_number': '+256700200032', 'first_name': 'Rose', 'last_name': 'Namono', 'vehicle_registration': 'UAB 701A', 'city': 'Mbale'},
            {'email': 'driver33@ridenow.test', 'phone_number': '+256700200033', 'first_name': 'Stephen', 'last_name': 'Mugoya', 'vehicle_registration': 'UAB 801A', 'city': 'Mbale'},
            {'email': 'driver34@ridenow.test', 'phone_number': '+256700200034', 'first_name': 'Joy', 'last_name': 'Nabirye', 'vehicle_registration': 'UAB 901A', 'city': 'Mbale'},
            {'email': 'driver35@ridenow.test', 'phone_number': '+256700200035', 'first_name': 'Daniel', 'last_name': 'Mukisa', 'vehicle_registration': 'UAB 951A', 'city': 'Mbale'},
            
            # Masaka Drivers
            {'email': 'driver36@ridenow.test', 'phone_number': '+256700200036', 'first_name': 'Alex', 'last_name': 'Ssekitoleko', 'vehicle_registration': 'UAB 602B', 'city': 'Masaka'},
            {'email': 'driver37@ridenow.test', 'phone_number': '+256700200037', 'first_name': 'Catherine', 'last_name': 'Nakamya', 'vehicle_registration': 'UAB 702B', 'city': 'Masaka'},
            {'email': 'driver38@ridenow.test', 'phone_number': '+256700200038', 'first_name': 'Simon', 'last_name': 'Ssemakula', 'vehicle_registration': 'UAB 802B', 'city': 'Masaka'},
            {'email': 'driver39@ridenow.test', 'phone_number': '+256700200039', 'first_name': 'Ruth', 'last_name': 'Nabatanzi', 'vehicle_registration': 'UAB 902B', 'city': 'Masaka'},
            {'email': 'driver40@ridenow.test', 'phone_number': '+256700200040', 'first_name': 'Michael', 'last_name': 'Kavuma', 'vehicle_registration': 'UAB 952B', 'city': 'Masaka'},
            
            # Fort Portal Drivers
            {'email': 'driver41@ridenow.test', 'phone_number': '+256700200041', 'first_name': 'Edwin', 'last_name': 'Mugisa', 'vehicle_registration': 'UAB 603C', 'city': 'Fort Portal'},
            {'email': 'driver42@ridenow.test', 'phone_number': '+256700200042', 'first_name': 'Priscilla', 'last_name': 'Katusiime', 'vehicle_registration': 'UAB 703C', 'city': 'Fort Portal'},
            {'email': 'driver43@ridenow.test', 'phone_number': '+256700200043', 'first_name': 'Ben', 'last_name': 'Mugume', 'vehicle_registration': 'UAB 803C', 'city': 'Fort Portal'},
            {'email': 'driver44@ridenow.test', 'phone_number': '+256700200044', 'first_name': 'Sarah', 'last_name': 'Kyomuhendo', 'vehicle_registration': 'UAB 903C', 'city': 'Fort Portal'},
            {'email': 'driver45@ridenow.test', 'phone_number': '+256700200045', 'first_name': 'Tom', 'last_name': 'Businge', 'vehicle_registration': 'UAB 953C', 'city': 'Fort Portal'},
            
            # Lira Drivers
            {'email': 'driver46@ridenow.test', 'phone_number': '+256700200046', 'first_name': 'Kenneth', 'last_name': 'Otema', 'vehicle_registration': 'UAB 604D', 'city': 'Lira'},
            {'email': 'driver47@ridenow.test', 'phone_number': '+256700200047', 'first_name': 'Patricia', 'last_name': 'Aciro', 'vehicle_registration': 'UAB 704D', 'city': 'Lira'},
            {'email': 'driver48@ridenow.test', 'phone_number': '+256700200048', 'first_name': 'Vincent', 'last_name': 'Okello', 'vehicle_registration': 'UAB 804D', 'city': 'Lira'},
            {'email': 'driver49@ridenow.test', 'phone_number': '+256700200049', 'first_name': 'Nancy', 'last_name': 'Akello', 'vehicle_registration': 'UAB 904D', 'city': 'Lira'},
            {'email': 'driver50@ridenow.test', 'phone_number': '+256700200050', 'first_name': 'Martin', 'last_name': 'Ocen', 'vehicle_registration': 'UAB 954D', 'city': 'Lira'},
            
            # Arua Drivers
            {'email': 'driver51@ridenow.test', 'phone_number': '+256700200051', 'first_name': 'Peter', 'last_name': 'Dramani', 'vehicle_registration': 'UAB 101A', 'city': 'Arua'},
            {'email': 'driver52@ridenow.test', 'phone_number': '+256700200052', 'first_name': 'Sarah', 'last_name': 'Adraa', 'vehicle_registration': 'UAB 201A', 'city': 'Arua'},
            {'email': 'driver53@ridenow.test', 'phone_number': '+256700200053', 'first_name': 'John', 'last_name': 'Oyuku', 'vehicle_registration': 'UAB 301A', 'city': 'Arua'},
            {'email': 'driver54@ridenow.test', 'phone_number': '+256700200054', 'first_name': 'Grace', 'last_name': 'Akello', 'vehicle_registration': 'UAB 401A', 'city': 'Arua'},
            {'email': 'driver55@ridenow.test', 'phone_number': '+256700200055', 'first_name': 'Moses', 'last_name': 'Amaku', 'vehicle_registration': 'UAB 501A', 'city': 'Arua'},
            
            # Additional Kampala Drivers for better coverage
            {'email': 'driver56@ridenow.test', 'phone_number': '+256700200056', 'first_name': 'Ivan', 'last_name': 'Ssali', 'vehicle_registration': 'UAB 601A', 'city': 'Kampala'},
            {'email': 'driver57@ridenow.test', 'phone_number': '+256700200057', 'first_name': 'Naomi', 'last_name': 'Nakazibwe', 'vehicle_registration': 'UAB 701A', 'city': 'Kampala'},
            {'email': 'driver58@ridenow.test', 'phone_number': '+256700200058', 'first_name': 'Mark', 'last_name': 'Lukwago', 'vehicle_registration': 'UAB 801A', 'city': 'Kampala'},
            {'email': 'driver59@ridenow.test', 'phone_number': '+256700200059', 'first_name': 'Juliet', 'last_name': 'Nakimbugwe', 'vehicle_registration': 'UAB 901A', 'city': 'Kampala'},
            {'email': 'driver60@ridenow.test', 'phone_number': '+256700200060', 'first_name': 'Brian', 'last_name': 'Kizito', 'vehicle_registration': 'UAB 951A', 'city': 'Kampala'},
        ]
        
        for driver_info in driver_data:
            user, created = User.objects.get_or_create(
                email=driver_info['email'],
                defaults={
                    'phone_number': driver_info['phone_number'],
                    'first_name': driver_info['first_name'],
                    'last_name': driver_info['last_name'],
                    'is_driver': True,
                    'is_active': True,
                    'username': driver_info['email'].split('@')[0]
                }
            )
            
            if created:
                # Find the vehicle by registration number
                try:
                    vehicle = vehicles.get(registration_number=driver_info['vehicle_registration'])
                except Vehicle.DoesNotExist:
                    vehicle = vehicles.first()  # Fallback to first vehicle
                
                # Create driver profile
                DriverProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'phone': user.phone_number,
                        'vehicle_registration': driver_info['vehicle_registration'],
                        'drivers_license_no': f'DL{random.randint(100000, 999999)}',
                        'date_of_birth': timezone.now().date() - timedelta(days=random.randint(9125, 14600)),  # 25-40 years old
                        'gender': random.choice(['M', 'F']),
                        'city': driver_info['city'],
                        'is_active': True,
                        'is_verified': True
                    }
                )
                
                # Create wallet
                UserWallet.objects.get_or_create(
                    owner=user,
                    defaults={
                        'amount': random.randint(50000, 200000),  # Drivers have higher amounts
                        'points': random.randint(0, 2000),
                        'is_active': True
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('✓ Drivers created'))


    def create_driver_locations(self):
        """Create driver locations for testing"""
        self.stdout.write('Creating driver locations...')
        
        from django.contrib.gis.geos import Point
        
        drivers = DriverProfile.objects.all()
        if not drivers.exists():
            self.stdout.write(self.style.WARNING('No drivers found. Skipping driver locations.'))
            return
        
        # Uganda cities coordinates and locations
        uganda_cities = {
            'Kampala': [
                {'lat': 0.3476, 'lng': 32.5825, 'address': 'Kampala City Centre'},
                {'lat': 0.3136, 'lng': 32.5811, 'address': 'Makerere University'},
                {'lat': 0.3163, 'lng': 32.5822, 'address': 'Nakawa Industrial Area'},
                {'lat': 0.3371, 'lng': 32.5825, 'address': 'Ntinda Shopping Centre'},
                {'lat': 0.3267, 'lng': 32.5781, 'address': 'Kawempe'},
                {'lat': 0.3628, 'lng': 32.5825, 'address': 'Bweyogerere'},
                {'lat': 0.2944, 'lng': 32.5528, 'address': 'Kajjansi'},
                {'lat': 0.3594, 'lng': 32.6251, 'address': 'Lubowa'},
                {'lat': 0.3192, 'lng': 32.5821, 'address': 'Kololo'},
                {'lat': 0.3319, 'lng': 32.5625, 'address': 'Muyenga'},
                {'lat': 0.3342, 'lng': 32.5825, 'address': 'Nansana'},
                {'lat': 0.3292, 'lng': 32.5825, 'address': 'Ggaba'},
            ],
            'Entebbe': [
                {'lat': 0.0644, 'lng': 32.4465, 'address': 'Entebbe Airport'},
                {'lat': 0.0644, 'lng': 32.4465, 'address': 'Entebbe Town Centre'},
                {'lat': 0.0600, 'lng': 32.4500, 'address': 'Entebbe Road'},
                {'lat': 0.0680, 'lng': 32.4400, 'address': 'Entebbe Port'},
            ],
            'Jinja': [
                {'lat': 0.4244, 'lng': 33.2042, 'address': 'Jinja City Centre'},
                {'lat': 0.4244, 'lng': 33.2042, 'address': 'Source of the Nile'},
                {'lat': 0.4300, 'lng': 33.2000, 'address': 'Jinja Industrial Area'},
                {'lat': 0.4200, 'lng': 33.2100, 'address': 'Jinja Market'},
            ],
            'Mbarara': [
                {'lat': -0.6072, 'lng': 30.6515, 'address': 'Mbarara City Centre'},
                {'lat': -0.6100, 'lng': 30.6500, 'address': 'Mbarara University'},
                {'lat': -0.6050, 'lng': 30.6550, 'address': 'Mbarara Market'},
                {'lat': -0.6080, 'lng': 30.6480, 'address': 'Mbarara Hospital'},
            ],
            'Gulu': [
                {'lat': 2.7806, 'lng': 32.2991, 'address': 'Gulu City Centre'},
                {'lat': 2.7800, 'lng': 32.3000, 'address': 'Gulu University'},
                {'lat': 2.7850, 'lng': 32.2950, 'address': 'Gulu Market'},
                {'lat': 2.7750, 'lng': 32.3050, 'address': 'Gulu Hospital'},
            ],
            'Mbale': [
                {'lat': 1.0827, 'lng': 34.1750, 'address': 'Mbale City Centre'},
                {'lat': 1.0800, 'lng': 34.1700, 'address': 'Islamic University'},
                {'lat': 1.0850, 'lng': 34.1800, 'address': 'Mbale Market'},
                {'lat': 1.0750, 'lng': 34.1650, 'address': 'Mbale Hospital'},
            ],
            'Masaka': [
                {'lat': -0.3400, 'lng': 31.7300, 'address': 'Masaka City Centre'},
                {'lat': -0.3350, 'lng': 31.7250, 'address': 'Masaka Market'},
                {'lat': -0.3450, 'lng': 31.7350, 'address': 'Masaka Hospital'},
                {'lat': -0.3300, 'lng': 31.7200, 'address': 'Masaka Industrial Area'},
            ],
            'Fort Portal': [
                {'lat': 0.6710, 'lng': 30.2750, 'address': 'Fort Portal City Centre'},
                {'lat': 0.6700, 'lng': 30.2700, 'address': 'Fort Portal Market'},
                {'lat': 0.6750, 'lng': 30.2800, 'address': 'Fort Portal Hospital'},
                {'lat': 0.6650, 'lng': 30.2650, 'address': 'Fort Portal University'},
            ],
            'Lira': [
                {'lat': 2.2489, 'lng': 32.8997, 'address': 'Lira City Centre'},
                {'lat': 2.2500, 'lng': 32.9000, 'address': 'Lira University'},
                {'lat': 2.2450, 'lng': 32.8950, 'address': 'Lira Market'},
                {'lat': 2.2550, 'lng': 32.9050, 'address': 'Lira Hospital'},
            ],
            'Mukono': [
                {'lat': 0.3533, 'lng': 32.7553, 'address': 'Mukono Town Centre'},
                {'lat': 0.3550, 'lng': 32.7500, 'address': 'Mukono University'},
                {'lat': 0.3500, 'lng': 32.7600, 'address': 'Mukono Market'},
                {'lat': 0.3580, 'lng': 32.7450, 'address': 'Mukono Industrial Area'},
            ],
            'Arua': [
                {'lat': 3.0201, 'lng': 30.9111, 'address': 'Arua City Centre'},
                {'lat': 3.0150, 'lng': 30.9100, 'address': 'Arua Market'},
                {'lat': 3.0250, 'lng': 30.9150, 'address': 'Arua Hospital'},
                {'lat': 3.0100, 'lng': 30.9050, 'address': 'Arua Airport'},
            ],
        }
        
        for driver in drivers:
            city = driver.city
            if city in uganda_cities:
                # Get random location from the driver's city
                location_data = random.choice(uganda_cities[city])
            else:
                # Fallback to Kampala if city not found
                location_data = random.choice(uganda_cities['Kampala'])
            
            # Add some random variation to make locations more realistic
            lat_variation = random.uniform(-0.005, 0.005)
            lng_variation = random.uniform(-0.005, 0.005)
            
            latitude = location_data['lat'] + lat_variation
            longitude = location_data['lng'] + lng_variation
            address = f"{location_data['address']}, {city}"
            
            # Create driver location
            DriverLocation.objects.get_or_create(
                driver=driver,
                defaults={
                    'location': Point(longitude, latitude, srid=4326),
                    'address': address,
                    'is_online': random.choice([True, True, True, False]),  # 75% online
                    'is_available': random.choice([True, True, False])  # 67% available
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Driver locations created'))
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('DUMMY DATA SUMMARY'))
        self.stdout.write('='*50)
        self.stdout.write(f'Vehicle Types: {VehicleType.objects.count()}')
        self.stdout.write(f'Vehicles: {Vehicle.objects.count()}')
        self.stdout.write(f'Test Users: {User.objects.filter(email__endswith="@ridenow.test").count()}')
        self.stdout.write(f'Clients: {ClientProfile.objects.count()}')
        self.stdout.write(f'Drivers: {DriverProfile.objects.count()}')
        self.stdout.write(f'Driver Locations: {DriverLocation.objects.count()}')
        self.stdout.write('='*50)
        
        # Display test credentials
        self.stdout.write('\n' + self.style.SUCCESS('TEST CREDENTIALS:'))
        test_users = User.objects.filter(email__endswith="@ridenow.test")
        for user in test_users:
            if user.is_client:
                self.stdout.write(f'Client: {user.email} | Phone: {user.phone_number}')
            elif user.is_driver:
                self.stdout.write(f'Driver: {user.email} | Phone: {user.phone_number}')
        
        self.stdout.write('\n' + self.style.SUCCESS('All dummy data created successfully!'))
