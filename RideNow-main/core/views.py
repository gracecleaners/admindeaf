from django.db.models import Q
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import SystemUtility
from tracking_analyzer.models import Tracker
from accounts.models import ClientProfile, User
from accounts.forms import OTPSendForm, OTPVerifyForm
from .utils import (
    generate_otp, 
    send_otp_twilio, 
    save_otp, 
    verify_otp, 
    send_sms_alert, 
    send_email_alert, 
    send_html_email
)

channel_layer = get_channel_layer()

def home(request):
    return render(request, 'home.html')

def features(request):
    return render(request, 'features.html')

def about(request):
    return render(request, 'about.html', {})

def faq(request):
    return render(request, 'faq.html')

def contact(request):
    return render(request, 'contact.html')

def signup(request):
    if request.method == 'POST':
        # Handle signup logic here (e.g., save user data)
        return redirect('login')
    return render(request, 'registration/signup.html')


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('profile')

    # try:
    #     utility = SystemUtility.objects.get(id=1)
    #     try:
    #         Tracker.objects.create_from_request(request, utility)
    #     except Exception as e:
    #         # Log the error but don't break the page load
    #         ErrorLogs.objects.create(error_narration=f"Tracking error: {str(e)}")
    # except SystemUtility.DoesNotExist:
    #     utility = None  

    return render(request, 'landing_page.html')

@login_required
def user_settings(request):
    return render(request, 'settings.html', {})

def help_center(request):
    return render(request, 'core/help_center.html', {})

def cookie_policy(request):
    title = 'Cookie Policy'
    page_title = 'Cookie Policy'
    page_content = "When it comes to dating apps, you've got options out there no doubt..."  # Truncated for brevity
    return render(request, 'core/info.html', {
        'title': title,
        'page_title': page_title,
        'page_content': page_content
    })

@csrf_exempt
def send_otp_view(request):
    if request.method == 'POST':
        form = OTPSendForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']

            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                email = f"{phone_number}@ridenow.net"
                user = User.objects.create_user(email=email, phone_number=phone_number)

            otp_code = generate_otp()
            otp_instance = save_otp(phone_number, otp_code)
            
            try:
                response = send_otp_twilio(phone_number, otp_code)
                return JsonResponse({
                    'message': 'OTP sent successfully',
                    'details': response
                })
            except Exception as e:
                return JsonResponse({
                    'message': f'Error sending OTP: {str(e)}'
                }, status=500)
        else:
            return JsonResponse({
                'message': form.errors
            }, status=400)
    return JsonResponse({
        'message': 'Invalid request method'
    }, status=400)

@csrf_exempt
def verify_otp_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        otp_code = request.POST.get('otp')

        if verify_otp(phone_number, otp_code):
            return JsonResponse({
                'message': 'OTP verified successfully'
            })
        return JsonResponse({
            'message': 'Invalid OTP'
        }, status=400)
    return JsonResponse({
        'message': 'Invalid request method'
    }, status=400)