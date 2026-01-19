from django.urls import path
from . import api_views

api_urlpatterns = [
    path('terms-of-service/', api_views.get_terms_of_service, name='get_terms_of_service'),
    path('privacy-policy/', api_views.get_privacy_policy, name='get_privacy_policy'),
    path('system-info/', api_views.get_system_info, name='get_system_info'),
]

urlpatterns = api_urlpatterns
