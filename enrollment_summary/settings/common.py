"""
Common settings for the Enrollment Summary API plugin
"""

def plugin_settings(settings):
    """
    Settings to be applied to the Open edX Django application.
    """
    # Add the plugin to installed apps
    settings.INSTALLED_APPS.extend([
        'enrollment_summary_api',
    ])
    
    # Configure logging
    settings.LOGGING['loggers']['enrollment_summary_api'] = {
        'handlers': ['local'],
        'level': 'INFO',
        'propagate': True,
    }
    
    # Configure caching for the plugin (using default cache)
    if 'enrollment_summary' not in settings.CACHES:
        settings.CACHES['enrollment_summary'] = settings.CACHES['default']