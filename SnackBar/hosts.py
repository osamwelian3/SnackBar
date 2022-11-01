from django_hosts import patterns, host
from django.conf import settings

host_patterns = patterns('',
    host(r'api', settings.ROOT_URLCONF, name='api'),
    host(r'www', 'SnackBar.newUrls', name='www'),
    # host(r'maps', 'maps.urls', name='api'),
)
