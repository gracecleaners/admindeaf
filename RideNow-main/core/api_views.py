from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import SystemUtility
from .utils import get_utility


@api_view(['GET'])
@permission_classes([AllowAny])
def get_terms_of_service(request):
    """Get Terms of Service from database"""
    try:
        utility = get_utility()
        
        if not utility or not utility.terms_of_use:
            return Response({
                'success': False,
                'error': 'Terms of Service not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'terms_of_service': utility.terms_of_use,
            'last_updated': utility.updated.isoformat() if utility.updated else None,
            'privacy_policy': utility.privacy_policy if utility.privacy_policy else None
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Failed to retrieve Terms of Service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_privacy_policy(request):
    """Get Privacy Policy from database"""
    try:
        utility = get_utility()
        
        if not utility or not utility.privacy_policy:
            return Response({
                'success': False,
                'error': 'Privacy Policy not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'privacy_policy': utility.privacy_policy,
            'last_updated': utility.updated.isoformat() if utility.updated else None
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Failed to retrieve Privacy Policy'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_system_info(request):
    """Get system information including terms and privacy policy"""
    try:
        utility = get_utility()
        
        if not utility:
            return Response({
                'success': False,
                'error': 'System information not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'system_info': {
                'terms_of_service': utility.terms_of_use,
                'privacy_policy': utility.privacy_policy,
                'info': utility.info,
                'support_email': utility.user_support_email,
                'support_phone': str(utility.user_support_phone) if utility.user_support_phone else None,
                'address': utility.address,
                'last_updated': utility.updated.isoformat() if utility.updated else None
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Failed to retrieve system information'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
