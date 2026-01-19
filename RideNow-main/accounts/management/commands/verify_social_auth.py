"""
Management command to verify social authentication setup
Usage: python manage.py verify_social_auth
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = 'Verify social authentication configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to create missing SocialApp entries',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🔍 Verifying Social Authentication Setup\n'))
        self.stdout.write('=' * 60)
        
        issues = []
        warnings = []
        success = []
        
        # 1. Check installed apps
        self.stdout.write('\n1️⃣  Checking installed apps...')
        required_apps = [
            'allauth',
            'allauth.account',
            'allauth.socialaccount',
            'allauth.socialaccount.providers.google',
            'allauth.socialaccount.providers.apple',
        ]
        
        for app in required_apps:
            if app in settings.INSTALLED_APPS:
                success.append(f'  ✅ {app}')
            else:
                issues.append(f'  ❌ Missing: {app}')
        
        for msg in success:
            self.stdout.write(self.style.SUCCESS(msg))
        for msg in issues:
            self.stdout.write(self.style.ERROR(msg))
        
        # 2. Check middleware
        self.stdout.write('\n2️⃣  Checking middleware...')
        if 'allauth.account.middleware.AccountMiddleware' in settings.MIDDLEWARE:
            self.stdout.write(self.style.SUCCESS('  ✅ AccountMiddleware configured'))
        else:
            issues.append('  ❌ Missing AccountMiddleware in MIDDLEWARE')
            self.stdout.write(self.style.ERROR('  ❌ Missing AccountMiddleware'))
        
        # 3. Check adapters
        self.stdout.write('\n3️⃣  Checking adapters...')
        if hasattr(settings, 'SOCIALACCOUNT_ADAPTER'):
            if settings.SOCIALACCOUNT_ADAPTER == 'accounts.adapters.SocialAccountAdapter':
                self.stdout.write(self.style.SUCCESS('  ✅ SocialAccountAdapter configured'))
            else:
                warnings.append(f'  ⚠️  Custom adapter: {settings.SOCIALACCOUNT_ADAPTER}')
                self.stdout.write(self.style.WARNING(f'  ⚠️  Using: {settings.SOCIALACCOUNT_ADAPTER}'))
        else:
            warnings.append('  ⚠️  Using default SocialAccountAdapter')
            self.stdout.write(self.style.WARNING('  ⚠️  Using default adapter'))
        
        if hasattr(settings, 'ACCOUNT_ADAPTER'):
            if settings.ACCOUNT_ADAPTER == 'accounts.adapters.AccountAdapter':
                self.stdout.write(self.style.SUCCESS('  ✅ AccountAdapter configured'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Using: {settings.ACCOUNT_ADAPTER}'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  Using default AccountAdapter'))
        
        # 4. Check environment variables
        self.stdout.write('\n4️⃣  Checking environment variables...')
        
        # Google
        google_client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
        google_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')
        
        if google_client_id and google_secret:
            self.stdout.write(self.style.SUCCESS('  ✅ Google OAuth credentials configured'))
        else:
            warnings.append('  ⚠️  Google OAuth credentials missing in .env')
            self.stdout.write(self.style.WARNING('  ⚠️  Google OAuth credentials missing'))
            self.stdout.write('      Add GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET to .env')
        
        # Apple
        apple_client_id = os.getenv('APPLE_OAUTH_CLIENT_ID', '')
        apple_secret = os.getenv('APPLE_OAUTH_CLIENT_SECRET', '')
        
        if apple_client_id and apple_secret:
            self.stdout.write(self.style.SUCCESS('  ✅ Apple OAuth credentials configured'))
        else:
            warnings.append('  ⚠️  Apple OAuth credentials missing in .env')
            self.stdout.write(self.style.WARNING('  ⚠️  Apple OAuth credentials missing'))
            self.stdout.write('      Add APPLE_OAUTH_CLIENT_ID and APPLE_OAUTH_CLIENT_SECRET to .env')
        
        # 5. Check SocialApp entries in database
        self.stdout.write('\n5️⃣  Checking database SocialApp entries...')
        try:
            google_app = SocialApp.objects.filter(provider='google').first()
            apple_app = SocialApp.objects.filter(provider='apple').first()
            
            if google_app:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Google SocialApp exists (ID: {google_app.id})'))
            else:
                warnings.append('  ⚠️  Google SocialApp not in database')
                self.stdout.write(self.style.WARNING('  ⚠️  Google SocialApp not found'))
                
                if options['fix'] and google_client_id and google_secret:
                    from django.contrib.sites.models import Site
                    site = Site.objects.get_current()
                    app = SocialApp.objects.create(
                        provider='google',
                        name='Google',
                        client_id=google_client_id,
                        secret=google_secret,
                    )
                    app.sites.add(site)
                    self.stdout.write(self.style.SUCCESS('  ✅ Created Google SocialApp'))
            
            if apple_app:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Apple SocialApp exists (ID: {apple_app.id})'))
            else:
                warnings.append('  ⚠️  Apple SocialApp not in database')
                self.stdout.write(self.style.WARNING('  ⚠️  Apple SocialApp not found'))
                
                if options['fix'] and apple_client_id and apple_secret:
                    from django.contrib.sites.models import Site
                    site = Site.objects.get_current()
                    app = SocialApp.objects.create(
                        provider='apple',
                        name='Apple',
                        client_id=apple_client_id,
                        secret=apple_secret,
                    )
                    app.sites.add(site)
                    self.stdout.write(self.style.SUCCESS('  ✅ Created Apple SocialApp'))
        except Exception as e:
            issues.append(f'  ❌ Database error: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ❌ Error: {str(e)}'))
        
        # 6. Check templates
        self.stdout.write('\n6️⃣  Checking templates...')
        template_files = [
            'templates/account/login.html',
            'templates/account/signup.html',
            'templates/socialaccount/login.html',
            'templates/socialaccount/signup.html',
            'templates/socialaccount/connections.html',
            'templates/socialaccount/authentication_error.html',
        ]
        
        for template in template_files:
            if os.path.exists(template):
                self.stdout.write(self.style.SUCCESS(f'  ✅ {template}'))
            else:
                warnings.append(f'  ⚠️  Missing: {template}')
                self.stdout.write(self.style.WARNING(f'  ⚠️  {template} not found'))
        
        # 7. Check settings configuration
        self.stdout.write('\n7️⃣  Checking settings...')
        
        config_checks = [
            ('SOCIALACCOUNT_AUTO_SIGNUP', True, 'Auto signup enabled'),
            ('SOCIALACCOUNT_EMAIL_REQUIRED', True, 'Email required'),
            ('SOCIALACCOUNT_STORE_TOKENS', True, 'Token storage enabled'),
        ]
        
        for key, expected, description in config_checks:
            value = getattr(settings, key, None)
            if value == expected:
                self.stdout.write(self.style.SUCCESS(f'  ✅ {description}'))
            else:
                warnings.append(f'  ⚠️  {key} = {value} (expected: {expected})')
                self.stdout.write(self.style.WARNING(f'  ⚠️  {key} = {value}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('\n📊 Summary:\n')
        
        if not issues and not warnings:
            self.stdout.write(self.style.SUCCESS('✅ All checks passed! Social auth is properly configured.'))
        else:
            if issues:
                self.stdout.write(self.style.ERROR(f'\n❌ Critical Issues: {len(issues)}'))
                for issue in issues:
                    self.stdout.write(self.style.ERROR(issue))
            
            if warnings:
                self.stdout.write(self.style.WARNING(f'\n⚠️  Warnings: {len(warnings)}'))
                for warning in warnings:
                    self.stdout.write(self.style.WARNING(warning))
        
        # Next steps
        self.stdout.write('\n📝 Next Steps:\n')
        
        if not google_client_id or not google_secret:
            self.stdout.write('  1. Add Google OAuth credentials to .env file')
        
        if not apple_client_id or not apple_secret:
            self.stdout.write('  2. Add Apple OAuth credentials to .env file')
        
        if options['fix']:
            self.stdout.write('  3. SocialApp entries created automatically (if credentials available)')
        else:
            if not SocialApp.objects.filter(provider='google').exists() or not SocialApp.objects.filter(provider='apple').exists():
                self.stdout.write('  3. Run with --fix flag to auto-create SocialApp entries')
                self.stdout.write('     OR manually add them in Django Admin at /admin/socialaccount/socialapp/')
        
        self.stdout.write('  4. Test social login at: http://127.0.0.1:8001/accounts/login/')
        self.stdout.write('  5. Monitor ErrorLogs for any authentication issues')
        
        self.stdout.write('\n' + '=' * 60 + '\n')

