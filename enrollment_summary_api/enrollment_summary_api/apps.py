"""
Django app configuration for the Enrollment Summary API plugin.
"""

from django.apps import AppConfig


class EnrollmentSummaryApiConfig(AppConfig):
    """
    Configuration for the Enrollment Summary API Django app.
    """
    name = "enrollment_summary_api"
    verbose_name = "LMS Enrollment Summary API"
    default_auto_field = "django.db.models.BigAutoField"
    
    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "enrollment_summary_api",
                "regex": "^api/enrollments/",
                "relative_path": "urls",
            }
        },
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "production": {"relative_path": "settings.production"},
            }
        }
    }