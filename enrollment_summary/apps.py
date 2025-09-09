from openedx.core.djangoapps.plugins.constants import (
    PluginURLs,
    PluginSettings,
    ProjectType,
)
from openedx.core.djangoapps.plugins.plugin_app import PluginApp


class EnrollmentSummaryConfig(PluginApp):
    """
    PluginApp-based AppConfig so Open edX plugin manager can detect and register
    this app automatically when the package is installed.
    """

    name = "enrollment_summary"
    verbose_name = "LMS Enrollment Summary API"
    default_auto_field = "django.db.models.BigAutoField"

    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                "namespace": "enrollment_summary",
                "app_name": "enrollment_summary",
                "regex": r"^api/enrollments/",
                "relative_path": "urls",
            },
            ProjectType.CMS: {
                "namespace": "enrollment_summary",
                "app_name": "enrollment_summary",
                "regex": r"^api/enrollments/",
                "relative_path": "urls",
            },
        },
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                "common": {
                    "REST_FRAMEWORK": {
                        "DEFAULT_FILTER_BACKENDS": [
                            "django_filters.rest_framework.DjangoFilterBackend"
                        ],
                    },
                },
                "production": {
                    "FEATURES": {"ENABLE_ENROLLMENT_SUMMARY_API": True},
                    "ENROLLMENT_SUMMARY": {
                        "DEFAULT_PAGE_SIZE": 20,
                        "MAX_PAGE_SIZE": 100,
                        "CACHE_TTL_SECONDS": 3,
                    },
                },
            }
        },
    }
