from django.urls import path, include
from django.urls import path
from .views import send_otp_view, verify_otp,home


from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('about/', views.about, name='about'),
    path('cookie_policy/', views.cookie_policy, name='cookie_policy'),
    path('features/', views.features, name='features'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path("send-otp/", send_otp_view, name="send_otp"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path('home/', views.home, name='home'),
]

