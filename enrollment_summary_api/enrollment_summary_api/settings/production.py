"""
Production settings for the Enrollment Summary API plugin.
"""

from .common import *

# In production, we might want longer cache times
ENROLLMENT_SUMMARY_API_SETTINGS.update({
    'CACHE_TIMEOUT': 900,  # 15 minutes in production
})

# More restrictive logging in production
LOGGING_CONFIG['loggers']['enrollment_summary_api']['level'] = 'WARNING'