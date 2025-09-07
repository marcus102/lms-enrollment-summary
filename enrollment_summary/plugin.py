"""
Plugin configuration for Open edX.
"""

from django.conf import settings


def ready():
    """
    Called when the plugin is ready.
    """
    pass


# Plugin metadata
__version__ = "1.0.0"
__description__ = "LMS Enrollment Summary API Plugin"