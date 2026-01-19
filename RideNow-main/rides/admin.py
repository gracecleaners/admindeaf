from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    VehicleType, Vehicle, VehiclePhoto, VehicleDocument,
    Route, Ride, Rating, FeedBack, RideRequest,
    DriverLocation, DriverLocationHistory, RideMatching
)


# Inline admin for VehiclePhoto
class VehiclePhotoInline(admin.TabularInline):
    model = VehiclePhoto
    extra = 1
    fields = ('photo', 'photo_preview', 'created')
    readonly_fields = ('photo_preview', 'created')

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.photo.url)
        return "No image"
    photo_preview.short_description = 'Preview'


# Inline admin for VehicleDocument
class VehicleDocumentInline(admin.TabularInline):
    model = VehicleDocument
    extra = 1
    fields = ('file', 'created')
    readonly_fields = ('created',)


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'engine_type', 'vehicle_capacity')
    list_filter = ('engine_type', 'vehicle_capacity')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'registration_number', 'is_air_conditioned', 'is_insured', 'age', 'created')
    list_filter = ('type', 'is_air_conditioned', 'is_insured', 'created')
    search_fields = ('name', 'registration_number')
    inlines = [VehiclePhotoInline, VehicleDocumentInline]
    readonly_fields = ('created', 'updated')
    fieldsets = (
        ('Basic Information', {
            'fields': ('type', 'name', 'registration_number', 'description')
        }),
        ('Vehicle Features', {
            'fields': ('is_air_conditioned', 'is_insured', 'age')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VehiclePhoto)
class VehiclePhotoAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'photo_preview', 'created')
    list_filter = ('created',)
    search_fields = ('vehicle__name', 'vehicle__registration_number')
    readonly_fields = ('photo_preview', 'created', 'updated')

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-width: 150px; max-height: 150px;" />', obj.photo.url)
        return "No image"
    photo_preview.short_description = 'Preview'


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'file', 'created')
    list_filter = ('created',)
    search_fields = ('vehicle__name', 'vehicle__registration_number')
    readonly_fields = ('created', 'updated')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickup_location', 'destination', 'eta', 'created')
    list_filter = ('created', 'eta')
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'created'


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'driver_link', 'client_link', 'vehicle_link', 'start_location', 'end_location', 'start_time', 'end_time', 'status_badge')
    list_filter = ('start_time', 'end_time', 'created')
    search_fields = ('driver__username', 'client__username', 'vehicle__name', 'start_location', 'end_location')
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'created'
    
    fieldsets = (
        ('Ride Participants', {
            'fields': ('driver', 'client', 'vehicle')
        }),
        ('Route Information', {
            'fields': ('route', 'start_location', 'end_location')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

    def driver_link(self, obj):
        if obj.driver:
            url = reverse('admin:accounts_driverprofile_change', args=[obj.driver.id])
            return format_html('<a href="{}">{}</a>', url, obj.driver.username)
        return '-'
    driver_link.short_description = 'Driver'

    def client_link(self, obj):
        if obj.client:
            url = reverse('admin:accounts_clientprofile_change', args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', url, obj.client.username)
        return '-'
    client_link.short_description = 'Client'

    def vehicle_link(self, obj):
        if obj.vehicle:
            url = reverse('admin:rides_vehicle_change', args=[obj.vehicle.id])
            return format_html('<a href="{}">{}</a>', url, obj.vehicle.name)
        return '-'
    vehicle_link.short_description = 'Vehicle'

    def status_badge(self, obj):
        if obj.end_time:
            return format_html('<span style="color: green;">●</span> Completed')
        return format_html('<span style="color: orange;">●</span> In Progress')
    status_badge.short_description = 'Status'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('ride_link', 'client_link', 'rating', 'star_display', 'created')
    list_filter = ('rating', 'created')
    search_fields = ('ride__id', 'client__username')
    readonly_fields = ('created', 'updated', 'star_display')
    date_hierarchy = 'created'

    def ride_link(self, obj):
        if obj.ride:
            url = reverse('admin:rides_ride_change', args=[obj.ride.id])
            return format_html('<a href="{}">Ride #{}</a>', url, obj.ride.id)
        return '-'
    ride_link.short_description = 'Ride'

    def client_link(self, obj):
        if obj.client:
            url = reverse('admin:accounts_clientprofile_change', args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', url, obj.client.username)
        return '-'
    client_link.short_description = 'Client'

    def star_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold; font-size: 16px;">{}</span>', stars)
    star_display.short_description = 'Stars'


@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_link', 'ride_link', 'rating_link', 'created')
    list_filter = ('created',)
    search_fields = ('client__username', 'ride__id', 'message')
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'created'

    def client_link(self, obj):
        if obj.client:
            url = reverse('admin:accounts_clientprofile_change', args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', url, obj.client.username)
        return '-'
    client_link.short_description = 'Client'

    def ride_link(self, obj):
        if obj.ride:
            url = reverse('admin:rides_ride_change', args=[obj.ride.id])
            return format_html('<a href="{}">Ride #{}</a>', url, obj.ride.id)
        return '-'
    ride_link.short_description = 'Ride'

    def rating_link(self, obj):
        if obj.rating:
            stars = '★' * obj.rating.rating + '☆' * (5 - obj.rating.rating)
            return format_html('<span style="color: gold;">{}</span>', stars)
        return '-'
    rating_link.short_description = 'Rating'


@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_link', 'driver_link', 'start_location', 'end_location', 'status_badge', 'requested_at', 'action_buttons')
    list_filter = ('status', 'requested_at', 'created')
    search_fields = ('client__username', 'driver__username', 'start_location', 'end_location')
    readonly_fields = ('requested_at', 'created', 'updated')
    date_hierarchy = 'requested_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('client', 'driver', 'vehicle', 'status')
        }),
        ('Location Details', {
            'fields': ('start_location', 'end_location')
        }),
        ('Ride Assignment', {
            'fields': ('ride',)
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'created', 'updated'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_accepted', 'mark_as_completed', 'mark_as_cancelled']

    def client_link(self, obj):
        if obj.client:
            url = reverse('admin:accounts_clientprofile_change', args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', url, obj.client.username)
        return '-'
    client_link.short_description = 'Client'

    def driver_link(self, obj):
        if obj.driver:
            url = reverse('admin:accounts_driverprofile_change', args=[obj.driver.id])
            return format_html('<a href="{}">{}</a>', url, obj.driver.username)
        return 'Not Assigned'
    driver_link.short_description = 'Driver'

    def status_badge(self, obj):
        colors = {
            'Pending': 'orange',
            'Accepted': 'blue',
            'Completed': 'green',
            'Cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">●</span> {}', color, obj.status)
    status_badge.short_description = 'Status'

    def action_buttons(self, obj):
        if obj.status == 'Pending':
            return format_html(
                '<a class="button" href="{}">Accept</a>&nbsp;'
                '<a class="button" href="{}">Cancel</a>',
                reverse('admin:rides_riderequest_change', args=[obj.id]),
                reverse('admin:rides_riderequest_change', args=[obj.id])
            )
        return '-'
    action_buttons.short_description = 'Actions'

    def mark_as_accepted(self, request, queryset):
        updated = queryset.update(status='Accepted')
        self.message_user(request, f'{updated} ride request(s) marked as accepted.')
    mark_as_accepted.short_description = 'Mark selected as Accepted'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='Completed')
        self.message_user(request, f'{updated} ride request(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected as Completed'

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='Cancelled')
        self.message_user(request, f'{updated} ride request(s) marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark selected as Cancelled'


@admin.register(DriverLocation)
class DriverLocationAdmin(admin.ModelAdmin):
    list_display = ('driver', 'location', 'address', 'is_online', 'is_available', 'last_updated', 'created')
    list_filter = ('is_online', 'is_available', 'last_updated', 'created')
    search_fields = ('driver__username', 'address', 'location')
    readonly_fields = ('created', 'last_updated')
    date_hierarchy = 'created'
    

@admin.register(DriverLocationHistory)
class DriverLocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('driver', 'location', 'address', 'on_active_ride', 'timestamp')
    list_filter = ('on_active_ride', 'timestamp')
    search_fields = ('driver__username', 'address')
    readonly_fields = ('timestamp', 'location', 'address')
    date_hierarchy = 'timestamp'
    

@admin.register(RideMatching)
class RideMatchingAdmin(admin.ModelAdmin):
    list_display = ('ride_request', 'driver', 'ride_request__client', 'ride_request', 'status', 'created')
    list_filter = ('status', 'created')
    search_fields = ('ride_request__id', 'driver__username', 'ride_request__client__username')
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'created'
    