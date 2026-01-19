import logging
from django.contrib.auth.models import User
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.db import models
from django.http import HttpRequest
# from geoip2.errors import GeoIP2Error, AddressNotFoundError
from geoip2.errors import GeoIP2Error
from ipware.ip import get_client_ip

logger = logging.getLogger('tracking_analyzer')

class TrackerManager(models.Manager):
    """
    Custom ``Tracker`` model manager that implements a method to create a new
    object instance from an HTTP request.
    """
    def get_device_type(self, request):
        """Determine device type from user agent"""
        if request.user_agent.is_mobile:
            return self.model.MOBILE
        elif request.user_agent.is_tablet:
            return self.model.TABLET
        elif request.user_agent.is_pc:
            return self.model.PC
        elif request.user_agent.is_bot:
            return self.model.BOT
        return self.model.UNKNOWN

    def get_geolocation(self, ip_address):
        """Get geolocation data with proper error handling"""
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            return {
                'country_code': '',
                'region': '',
                'city': 'Local Development'
            }

        try:
            geo = GeoIP2()
            return geo.city(ip_address)
        except (GeoIP2Error, GeoIP2Exception, AddressNotFoundError) as e:
            logger.warning(
                'Unable to determine geolocation for address %s: %s',
                ip_address, str(e)
            )
            return {
                'country_code': '',
                'region': '',
                'city': ''
            }

    def create_from_request(self, request, content_object):
        """
        Create a Tracker instance from an HTTP request.
        
        :param request: A Django ``HTTPRequest`` object.
        :param content_object: A Django model instance.
        :return: A newly created ``Tracker`` instance.
        """
        # Sanity checks
        assert isinstance(request, HttpRequest), \
            '`request` object is not an `HTTPRequest`'
        assert issubclass(content_object.__class__, models.Model), \
            '`content_object` is not a Django model'

        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None

        # Get device type
        device_type = self.get_device_type(request)

        # Get IP and geolocation
        ip_address, _ = get_client_ip(request) or ('', None)
        city_data = self.get_geolocation(ip_address)

        try:
            tracker = self.model.objects.create(
                content_object=content_object,
                ip_address=ip_address or '',
                ip_country=city_data.get('country_code', ''),
                ip_region=city_data.get('region', ''),
                ip_city=city_data.get('city', ''),
                referrer=request.META.get('HTTP_REFERER', ''),
                device_type=device_type,
                device=request.user_agent.device.family,
                browser=request.user_agent.browser.family[:30],
                browser_version=request.user_agent.browser.version_string,
                system=request.user_agent.os.family,
                system_version=request.user_agent.os.version_string,
                user=user
            )
            
            logger.info(
                'Tracked click in %s %s.',
                content_object._meta.object_name,
                content_object.pk
            )
            
            return tracker
            
        except Exception as e:
            logger.error(
                'Failed to create tracker for %s %s: %s',
                content_object._meta.object_name,
                content_object.pk,
                str(e)
            )
            raise