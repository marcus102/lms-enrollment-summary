"""
Production settings for enrollment_summary plugin.
"""


def plugin_settings(settings):
    """
    Production plugin settings.
    """
    # Enable the feature in production
    settings.FEATURES.update(
        {
            "ENABLE_ENROLLMENT_SUMMARY_API": True,
        }
    )

    # Plugin-specific settings
    settings.ENROLLMENT_SUMMARY = {
        "DEFAULT_PAGE_SIZE": 20,
        "MAX_PAGE_SIZE": 100,
        "CACHE_TTL_SECONDS": 3,
    }
