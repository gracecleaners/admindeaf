#!/usr/bin/env python
"""
Script to create a superuser or reset admin credentials
Run this from the project root: python create_admin.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RideNow.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_superuser():
    """Create a new superuser"""
    print("Creating a new superuser...")
    
    email = input("Enter email address: ").strip()
    if not email:
        print("Email is required!")
        return
    
    username = input("Enter username (optional, will use email prefix if empty): ").strip()
    if not username:
        username = email.split('@')[0]
    
    password = input("Enter password: ").strip()
    if not password:
        print("Password is required!")
        return
    
    try:
        with transaction.atomic():
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                print(f"User with email {email} already exists!")
                choice = input("Do you want to make them a superuser? (y/n): ").strip().lower()
                if choice == 'y':
                    user = User.objects.get(email=email)
                    user.is_staff = True
                    user.is_superuser = True
                    user.set_password(password)
                    user.save()
                    print(f"✅ User {email} is now a superuser!")
                else:
                    print("Operation cancelled.")
                return
            
            # Create new superuser
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            print(f"✅ Superuser created successfully!")
            print(f"Email: {email}")
            print(f"Username: {username}")
            
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

def list_users():
    """List all users"""
    print("\n=== All Users ===")
    users = User.objects.all()
    if not users:
        print("No users found.")
        return
    
    for user in users:
        status = []
        if user.is_superuser:
            status.append("Superuser")
        if user.is_staff:
            status.append("Staff")
        if user.is_active:
            status.append("Active")
        else:
            status.append("Inactive")
        
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        print(f"Phone: {user.phone_number or 'Not set'}")
        print(f"Status: {', '.join(status)}")
        print("-" * 40)

def reset_user_password():
    """Reset password for existing user"""
    email = input("Enter email address of user to reset: ").strip()
    if not email:
        print("Email is required!")
        return
    
    try:
        user = User.objects.get(email=email)
        new_password = input("Enter new password: ").strip()
        if not new_password:
            print("Password is required!")
            return
        
        user.set_password(new_password)
        user.save()
        print(f"✅ Password reset successfully for {email}")
        
    except User.DoesNotExist:
        print(f"❌ User with email {email} not found!")

def main():
    print("=== RideNow Admin Management ===")
    print("1. Create new superuser")
    print("2. List all users")
    print("3. Reset user password")
    print("4. Exit")
    
    choice = input("\nSelect an option (1-4): ").strip()
    
    if choice == '1':
        create_superuser()
    elif choice == '2':
        list_users()
    elif choice == '3':
        reset_user_password()
    elif choice == '4':
        print("Goodbye!")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
