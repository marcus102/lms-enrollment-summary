"""
Common settings for enrollment_summary plugin.
"""

def plugin_settings(settings):
    """
    Modify the provided settings object with settings specific to this plugin.
    """
    # Plugin specific settings
    settings.ENROLLMENT_SUMMARY_PAGE_SIZE = getattr(
        settings, 'ENROLLMENT_SUMMARY_PAGE_SIZE', 20
    )
    settings.ENROLLMENT_SUMMARY_MAX_PAGE_SIZE = getattr(
        settings, 'ENROLLMENT_SUMMARY_MAX_PAGE_SIZE', 100
    )
    
    # Add plugin to INSTALLED_APPS if not already there
    if 'enrollment_summary' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append('enrollment_summary')
    
    # REST Framework settings for this plugin
    if hasattr(settings, 'REST_FRAMEWORK'):
        settings.REST_FRAMEWORK.setdefault('DEFAULT_PAGINATION_CLASS', 
            'rest_framework.pagination.PageNumberPagination')