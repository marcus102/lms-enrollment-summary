"""
Production settings for enrollment_summary plugin.
"""

def plugin_settings(settings):
    """
    Production-specific settings for the plugin.
    """
    # Import common settings first
    from .common import plugin_settings as common_plugin_settings
    common_plugin_settings(settings)
    
    # Production-specific overrides
    settings.ENROLLMENT_SUMMARY_PAGE_SIZE = 25
    settings.ENROLLMENT_SUMMARY_MAX_PAGE_SIZE = 200
    
    # Enable caching in production
    if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
        settings.CACHES['enrollment_summary'] = {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
            'KEY_PREFIX': 'enrollment_summary',
            'TIMEOUT': 3600,
        }
