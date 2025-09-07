"""
Production settings for the Enrollment Summary API plugin
"""

def plugin_settings(settings):
    """
    Production-specific settings.
    """
    # Set more conservative cache timeout in production
    settings.ENROLLMENT_SUMMARY_CACHE_TIMEOUT = 600  # 10 minutes
    
    # Configure logging for production
    settings.LOGGING['loggers']['enrollment_summary_api'] = {
        'handlers': ['local'],
        'level': 'WARNING',  # Less verbose in production
        'propagate': True,
    }