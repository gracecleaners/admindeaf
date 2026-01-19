"""
Custom API Documentation Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings


def api_docs_home(request):
    """
    API Documentation home page with Zyra branding
    """
    context = {
        'title': 'Zyra API Documentation',
        'version': settings.SPECTACULAR_SETTINGS.get('VERSION', '1.0.0'),
        'user': request.user,
    }
    return render(request, 'api_docs/home.html', context)


class CustomSwaggerView(SpectacularSwaggerView):
    """
    Custom Swagger UI view with Zyra branding
    """
    template_name = 'drf_spectacular/swagger_ui.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = settings.SPECTACULAR_SETTINGS.get('TITLE', 'API Documentation')
        context['version'] = settings.SPECTACULAR_SETTINGS.get('VERSION', '1.0.0')
        return context


class CustomRedocView(SpectacularRedocView):
    """
    Custom ReDoc view with Zyra branding
    """
    template_name = 'drf_spectacular/redoc.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = settings.SPECTACULAR_SETTINGS.get('TITLE', 'API Documentation')
        context['version'] = settings.SPECTACULAR_SETTINGS.get('VERSION', '1.0.0')
        return context

