"""
Common settings for enrollment_summary plugin.
"""

def plugin_settings(settings):
    """
    Common plugin settings.
    """
    # Add REST framework configuration
    if hasattr(settings, 'REST_FRAMEWORK'):
        default_filters = settings.REST_FRAMEWORK.get('DEFAULT_FILTER_BACKENDS', [])
        if 'django_filters.rest_framework.DjangoFilterBackend' not in default_filters:
            default_filters.append('django_filters.rest_framework.DjangoFilterBackend')
            settings.REST_FRAMEWORK['DEFAULT_FILTER_BACKENDS'] = default_filters
    else:
        settings.REST_FRAMEWORK = {
            'DEFAULT_FILTER_BACKENDS': [
                'django_filters.rest_framework.DjangoFilterBackend'
            ],
        }