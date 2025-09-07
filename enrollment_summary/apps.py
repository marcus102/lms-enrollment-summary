"""
Django app configuration for LMS Enrollment Summary
"""
from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import ProjectType, PluginSettings, PluginURLs


class LMSEnrollmentSummaryConfig(AppConfig):
    """
    App configuration for LMS Enrollment Summary plugin
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms_enrollment_summary'
    verbose_name = 'LMS Enrollment Summary API'

    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: 'lms_enrollment_summary',
                PluginURLs.REGEX: r'^api/enrollments/',
                PluginURLs.RELATIVE_PATH: 'urls',
            }
        },
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                PluginSettings.COMMON: {},
                PluginSettings.PRODUCTION: {},
                PluginSettings.DEVSTACK: {},
            }
        }
    }
