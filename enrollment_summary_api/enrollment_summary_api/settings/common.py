"""
Common settings for the Enrollment Summary API plugin.
"""

# API Configuration
ENROLLMENT_SUMMARY_API_SETTINGS = {
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'CACHE_TIMEOUT': 300,  # 5 minutes
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'enrollment_summary_api': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'enrollment_summary_api': {
            'handlers': ['enrollment_summary_api'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}