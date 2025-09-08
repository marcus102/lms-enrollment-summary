# enrollment_summary/apps.py - Fixed Django App Configuration
from django.apps import AppConfig


class EnrollmentSummaryConfig(AppConfig):
    """
    Django app configuration for the Enrollment Summary API plugin.
    Compatible with all Open edX versions.
    """
    name = "enrollment_summary"
    verbose_name = "LMS Enrollment Summary API"
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """
        Initialize the plugin when Django starts.
        """
        pass


# For Open edX plugin discovery (if supported)
try:
    from openedx.core.djangoapps.plugins.constants import PluginSettings, PluginURLs, ProjectType
    
    # Only add plugin configuration if the Open edX plugin system is available
    EnrollmentSummaryConfig.plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: "enrollment_summary",
                PluginURLs.REGEX: r"^api/enrollments/",
                PluginURLs.RELATIVE_PATH: "urls",
            }
        },
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                PluginSettings.COMMON: {
                    "ENROLLMENT_SUMMARY_PAGE_SIZE": 20,
                    "ENROLLMENT_SUMMARY_MAX_PAGE_SIZE": 100,
                }
            }
        },
    }
except ImportError:
    # Fallback for older Open edX versions or when plugin system is not available
    pass