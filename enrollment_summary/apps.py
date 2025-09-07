from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import (
    PluginSettings,
    PluginURLs,
    ProjectType,
    SettingsType,
)


class EnrollmentSummaryConfig(AppConfig):
    """
    Django app configuration for the Enrollment Summary API plugin.
    """
    name = "enrollment_summary"
    verbose_name = "LMS Enrollment Summary API"
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Open edX plugin configuration
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: "enrollment_summary",
                PluginURLs.REGEX: r"^api/enrollments/",
                PluginURLs.RELATIVE_PATH: "urls",
            }
        },
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.COMMON: {
                    "ENROLLMENT_SUMMARY_PAGE_SIZE": 20,
                    "ENROLLMENT_SUMMARY_MAX_PAGE_SIZE": 100,
                }
            }
        },
    }

    def ready(self):
        """
        Method called when Django starts up.
        """
        # Import signal handlers if any
        pass