from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User, ClientProfile, ReportUser, ReportEvidence, LoginAttempt, DriverProfile, VerificationToken, TermsAcceptance, UserPreferences, UserSecuritySettings, UserActivityLog, UserSession


from import_export.admin import ExportActionMixin


class CustomUserAdmin(ExportActionMixin, UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = (
        'email', 'phone_number', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_client', 'is_driver', 'is_banned')
    list_filter = ('is_staff', 'is_active', 'is_client', 'is_driver', 'is_banned', 'date_joined', 'last_login',)
    filter_horizontal = ('groups', 'user_permissions',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active', 'is_client', 'is_driver', 'is_banned')
        }),
    )
    list_per_page = 50
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'first_name', 'last_name', 'password', 'date_joined', 'last_login')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups')}),
        ('User Type', {'fields': ('is_client', 'is_driver', 'is_banned')}),
    )
    search_fields = ('email', 'phone_number', 'first_name', 'last_name',)
    ordering = ('email',)


class ClientProfileAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'email', 'username', 'first_name', 'last_name', 'is_online')
    list_per_page = 50
    search_fields = ('email', 'first_name', 'last_name',)
    list_filter = ('is_verified',)


class ReportEvidenceInline(admin.TabularInline):
    model = ReportEvidence
    raw_id_fields = ['report']

class ReportUserAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('reported_user', 'reporter', 'timestamp')
    list_per_page = 50
    search_fields = ('complaints',)
    list_filter = ('is_attended_to',)
    inlines = [ReportEvidenceInline]


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'ip_address', 'timestamp', 'success')
    list_filter = ('success', 'timestamp')
    search_fields = ('username', 'ip_address')


class DriverProfileAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'email', 'username', 'first_name', 'last_name', 'is_online')
    list_per_page = 50
    search_fields = ('email', 'first_name', 'last_name',)
    list_filter = ('is_verified',)

class VerificationTokenAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'token', 'token_type', 'created_at', 'expires_at', 'is_used')
    list_per_page = 50
    search_fields = ('user', 'token', 'token_type')
    list_filter = ('created_at', 'expires_at', 'is_used')

class TermsAcceptanceAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'accepted_at', 'ip_address', 'user_agent', 'terms_version')
    list_per_page = 50
    search_fields = ('user', 'ip_address', 'user_agent', 'terms_version')
    list_filter = ('accepted_at',) 


@admin.register(UserPreferences)
class UserPreferencesAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'sms_notifications', 'language', 'timezone', 'created_at')
    list_filter = ('email_notifications', 'sms_notifications', 'push_notifications', 'language', 'timezone')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserSecuritySettings)
class UserSecuritySettingsAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'two_factor_enabled', 'login_alerts', 'account_locked', 'failed_login_attempts', 'created_at')
    list_filter = ('two_factor_enabled', 'login_alerts', 'account_locked', 'api_access_enabled')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'password_changed_at', 'last_failed_login')

@admin.register(UserActivityLog)
class UserActivityLogAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'user__username', 'description', 'ip_address')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(UserSession)
class UserSessionAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'is_active', 'created_at', 'last_activity', 'expires_at')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('user__email', 'user__username', 'session_key', 'ip_address')
    readonly_fields = ('created_at', 'last_activity')

admin.site.register(User, CustomUserAdmin)
admin.site.register(ClientProfile, ClientProfileAdmin)
admin.site.register(ReportUser, ReportUserAdmin)
admin.site.register(DriverProfile, DriverProfileAdmin)
admin.site.register(VerificationToken, VerificationTokenAdmin)
admin.site.register(TermsAcceptance, TermsAcceptanceAdmin)
