from openedx.core.djangoapps.plugins.constants import (
    PluginURLs,
    PluginSettings,
    ProjectType,
)
from openedx.core.djangoapps.plugins.plugin_app import PluginApp


class EnrollmentSummaryConfig(PluginApp):
    name = "enrollment_summary"
    verbose_name = "LMS Enrollment Summary API"
    default_auto_field = "django.db.models.BigAutoField"

    plugin_app = {
        # URLs (mounted under /api/enrollments/)
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                "namespace": "enrollment_summary",
                "app_name": "enrollment_summary",
                "regex": r"^api/enrollments/",
                "relative_path": "urls",
            },
        },
        # Settings that Open edX will merge automatically
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                "common": {
                    "INSTALLED_APPS": ["enrollment_summary"],
                    "REST_FRAMEWORK": {
                        "DEFAULT_FILTER_BACKENDS": [
                            "django_filters.rest_framework.DjangoFilterBackend"
                        ],
                    },
                },
                "production": {
                    "FEATURES": {"ENABLE_ENROLLMENT_SUMMARY_API": True},
                    # Example: If you want to restrict page size or cache differently in prod
                    "ENROLLMENT_SUMMARY": {
                        "DEFAULT_PAGE_SIZE": 20,
                        "MAX_PAGE_SIZE": 100,
                        "CACHE_TTL_SECONDS": 300,
                    },
                },
            },
        },
    }
