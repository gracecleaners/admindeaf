# RideNow/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('tracking/', include('tracking_analyzer.urls')),  # Ensure this path is correct
    # Other URL patterns...
]
