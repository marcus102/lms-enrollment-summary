from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginSettings, PluginURLs, ProjectType


class EnrollmentSummaryConfig(AppConfig):
    """
    Django app configuration for the Enrollment Summary API plugin.
    """
    name = "enrollment_summary"
    verbose_name = "LMS Enrollment Summary API"
    
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
                PluginSettings.COMMON: {
                    "ENROLLMENT_SUMMARY_PAGE_SIZE": 20,
                    "ENROLLMENT_SUMMARY_MAX_PAGE_SIZE": 100,
                }
            }
        },
    }