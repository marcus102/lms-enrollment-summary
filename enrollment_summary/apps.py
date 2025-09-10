from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginURLs, PluginSettings


class EnrollmentSummaryConfig(AppConfig):
    """
    Django AppConfig for the LMS Enrollment Summary plugin.
    """

    name = "enrollment_summary"
    verbose_name = "LMS Enrollment Summary API"
    default_auto_field = "django.db.models.BigAutoField"

    plugin_app = {
        PluginURLs.CONFIG: {
            "lms.djangoapp": {
                "namespace": "enrollment_summary",
                "app_name": "enrollment_summary",
                "regex": r"^api/enrollments/",
                "relative_path": "urls",
            },
        },
        PluginSettings.CONFIG: {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "production": {"relative_path": "settings.production"},
            }
        },
    }
