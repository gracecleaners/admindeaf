# Create Admin Command Documentation

## Overview

The `create_admin.py` is a Django management command that provides a comprehensive interface for managing superuser accounts in the RideNow application. This command allows you to create new superusers, reset passwords for existing users, and list all users in the system.

## Location

```
accounts/management/commands/create_admin.py
```

## Command Syntax

```bash
python manage.py create_admin [options]
```

## Available Options

### 1. Create Superuser

**Basic Usage:**
```bash
python manage.py create_admin
```

**With Parameters:**
```bash
python manage.py create_admin --email admin@example.com --username admin --password mypassword
```

**Parameters:**
- `--email`: Email address for the superuser (required)
- `--username`: Username for the superuser (optional, defaults to email prefix)
- `--password`: Password for the superuser (optional, will prompt if not provided)

### 2. Reset Password

**Usage:**
```bash
python manage.py create_admin --reset-password admin@example.com
```

**Parameters:**
- `--reset-password`: Email address of the user whose password you want to reset

### 3. List Users

**Usage:**
```bash
python manage.py create_admin --list-users
```

**Parameters:**
- `--list-users`: Lists all users in the system with their details

## Features

### 1. Interactive Superuser Creation

When run without parameters, the command provides an interactive interface:

1. Prompts for email address
2. Generates username from email (if not provided)
3. Prompts for password
4. Creates the superuser with proper permissions

### 2. Duplicate User Handling

If a user with the same email already exists:
- Warns the user about the existing account
- Asks if they want to promote the existing user to superuser
- Updates the existing user's permissions and password if confirmed

### 3. Comprehensive User Listing

The `--list-users` option displays:
- User ID
- Email address
- Username
- Phone number (if available)
- Account status (Superuser, Staff, Active/Inactive)

### 4. Password Reset Functionality

Allows administrators to reset passwords for existing users:
- Verifies user existence
- Prompts for new password
- Updates the user's password securely

## Usage Examples

### Example 1: Create a New Superuser

```bash
# Interactive mode
python manage.py create_admin

# With all parameters
python manage.py create_admin --email admin@ridenow.com --username admin --password SecurePass123
```

**Expected Output:**
```
✅ Superuser created successfully!
Email: admin@ridenow.com
Username: admin
```

### Example 2: Promote Existing User to Superuser

```bash
python manage.py create_admin --email existing@ridenow.com --password NewPassword123
```

**Expected Output:**
```
User with email existing@ridenow.com already exists!
Do you want to make them a superuser? (y/n): y
✅ User existing@ridenow.com is now a superuser!
```

### Example 3: List All Users

```bash
python manage.py create_admin --list-users
```

**Expected Output:**
```
=== All Users ===
ID: 1
Email: admin@ridenow.com
Username: admin
Phone: +1234567890
Status: Superuser, Staff, Active
----------------------------------------
ID: 2
Email: driver@ridenow.com
Username: driver
Phone: +1234567891
Status: Active
----------------------------------------
```

### Example 4: Reset User Password

```bash
python manage.py create_admin --reset-password user@ridenow.com
```

**Expected Output:**
```
Enter new password: [password input]
✅ Password reset successfully for user@ridenow.com
```

## Error Handling

The command includes comprehensive error handling:

1. **Missing Required Fields**: Displays error messages for missing email or password
2. **User Not Found**: Shows appropriate error when trying to reset password for non-existent user
3. **Database Errors**: Uses transactions to ensure data consistency
4. **Validation**: Ensures email format and password requirements

## Security Features

1. **Password Security**: Uses Django's built-in password hashing
2. **Transaction Safety**: All database operations are wrapped in transactions
3. **Permission Validation**: Properly sets superuser and staff permissions
4. **Input Validation**: Validates required fields before processing

## Integration with Django

This command integrates seamlessly with Django's user management system:

- Uses `get_user_model()` for compatibility with custom user models
- Follows Django's management command conventions
- Uses Django's built-in user creation and password handling methods
- Supports Django's admin interface permissions

## Troubleshooting

### Common Issues

1. **"Email is required!" Error**
   - Solution: Provide an email address via `--email` parameter or when prompted

2. **"User with email X already exists!" Warning**
   - Solution: Choose 'y' to promote existing user or 'n' to cancel

3. **"User with email X not found!" Error**
   - Solution: Verify the email address exists using `--list-users`

4. **Permission Denied Errors**
   - Solution: Ensure you have proper database permissions and the Django project is properly configured

### Best Practices

1. **Use Strong Passwords**: Always use secure passwords for superuser accounts
2. **Regular User Audits**: Use `--list-users` periodically to review user accounts
3. **Backup Before Changes**: Always backup your database before making user changes
4. **Test in Development**: Test password resets and user creation in development environment first

## Related Commands

- `python manage.py createsuperuser` - Django's default superuser creation command
- `python manage.py changepassword` - Django's password change command
- `python manage.py shell` - For advanced user management operations

## Support

For issues or questions regarding this command, refer to:
- Django Management Commands Documentation
- RideNow Project Documentation
- Django User Model Documentation

---

*This documentation covers the `create_admin.py` management command version as of the current codebase. For updates or modifications, please refer to the source code and update this documentation accordingly.*
