#!/usr/bin/env python3
"""
Test script for RideNow API
This script demonstrates how to use the RideNow API endpoints
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000/accounts/api"

class RideNowAPIClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()
    
    def _get_headers(self, include_auth=True):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if include_auth and self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        return headers
    
    def client_signup(self, email, phone, password, first_name, last_name, date_of_birth, gender, country='UG', city='Kampala'):
        """Register a new client"""
        url = f"{self.base_url}/auth/client/signup/"
        data = {
            'email': email,
            'phone': phone,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'country': country,
            'city': city
        }
        response = self.session.post(url, json=data, headers=self._get_headers(include_auth=False))
        return response.json(), response.status_code
    
    def driver_signup(self, email, phone, password, first_name, last_name, date_of_birth, gender, vehicle_registration, drivers_license_no='', country='UG', city='Kampala'):
        """Register a new driver"""
        url = f"{self.base_url}/auth/driver/signup/"
        data = {
            'email': email,
            'phone': phone,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'country': country,
            'city': city,
            'vehicle_registration': vehicle_registration,
            'drivers_license_no': drivers_license_no
        }
        response = self.session.post(url, json=data, headers=self._get_headers(include_auth=False))
        return response.json(), response.status_code
    
    def login(self, username_or_email_or_phone, password):
        """Login user and get tokens"""
        url = f"{self.base_url}/auth/login/"
        data = {
            'username_or_email_or_phone': username_or_email_or_phone,
            'password': password
        }
        response = self.session.post(url, json=data, headers=self._get_headers(include_auth=False))
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            self.refresh_token = data.get('refresh')
        return response.json(), response.status_code
    
    def verify_account(self, verification_code):
        """Verify user account"""
        url = f"{self.base_url}/auth/verify/"
        data = {'verification_code': verification_code}
        response = self.session.post(url, json=data, headers=self._get_headers(include_auth=False))
        return response.json(), response.status_code
    
    def get_profile(self):
        """Get user profile"""
        url = f"{self.base_url}/profile/"
        response = self.session.get(url, headers=self._get_headers())
        return response.json(), response.status_code
    
    def update_client_profile(self, **kwargs):
        """Update client profile"""
        url = f"{self.base_url}/profile/client/"
        response = self.session.put(url, json=kwargs, headers=self._get_headers())
        return response.json(), response.status_code
    
    def update_driver_profile(self, **kwargs):
        """Update driver profile"""
        url = f"{self.base_url}/profile/driver/"
        response = self.session.put(url, json=kwargs, headers=self._get_headers())
        return response.json(), response.status_code
    
    def change_password(self, old_password, new_password, confirm_password):
        """Change user password"""
        url = f"{self.base_url}/account/change-password/"
        data = {
            'old_password': old_password,
            'new_password': new_password,
            'confirm_password': confirm_password
        }
        response = self.session.post(url, json=data, headers=self._get_headers())
        return response.json(), response.status_code
    
    def report_user(self, reported_user_id, complaint):
        """Report a user"""
        url = f"{self.base_url}/report/user/"
        data = {
            'reported_user': reported_user_id,
            'complaint': complaint
        }
        response = self.session.post(url, json=data, headers=self._get_headers())
        return response.json(), response.status_code
    
    def delete_account(self, password, reason='', feedback=''):
        """Delete user account"""
        url = f"{self.base_url}/account/delete/"
        data = {
            'password': password,
            'reason': reason,
            'feedback': feedback
        }
        response = self.session.post(url, json=data, headers=self._get_headers())
        return response.json(), response.status_code
    
    def logout(self):
        """Logout user"""
        url = f"{self.base_url}/auth/logout/"
        data = {'refresh_token': self.refresh_token}
        response = self.session.post(url, json=data, headers=self._get_headers())
        return response.json(), response.status_code


def main():
    """Test the API endpoints"""
    print("🚗 RideNow API Test Script")
    print("=" * 50)
    
    # Initialize API client
    api = RideNowAPIClient()
    
    # Test data
    client_email = f"client_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
    driver_email = f"driver_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
    password = "SecurePassword123"
    
    print("\n1. Testing Client Registration...")
    try:
        response, status = api.client_signup(
            email=client_email,
            phone="+256700000000",
            password=password,
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            gender="M"
        )
        print(f"Status: {status}")
        print(f"Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Testing Driver Registration...")
    try:
        response, status = api.driver_signup(
            email=driver_email,
            phone="+256700000001",
            password=password,
            first_name="Jane",
            last_name="Smith",
            date_of_birth="1985-05-15",
            gender="F",
            vehicle_registration="UAB123A",
            drivers_license_no="DL123456"
        )
        print(f"Status: {status}")
        print(f"Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Testing Login...")
    try:
        response, status = api.login(client_email, password)
        print(f"Status: {status}")
        print(f"Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n4. Testing Get Profile...")
    try:
        response, status = api.get_profile()
        print(f"Status: {status}")
        print(f"Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n5. Testing Update Client Profile...")
    try:
        response, status = api.update_client_profile(
            bio="I love traveling and meeting new people",
            interests="Travel, Music, Sports"
        )
        print(f"Status: {status}")
        print(f"Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n6. Testing Change Password...")
    try:
        response, status = api.change_password(
            old_password=password,
            new_password="NewSecurePassword123",
            confirm_password="NewSecurePassword123"
        )
        print(f"Status: {status}")
        print(f"Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n7. Testing Logout...")
    try:
        response, status = api.logout()
        print(f"Status: {status}")
        print(f"Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ API Test Complete!")


if __name__ == "__main__":
    main()
