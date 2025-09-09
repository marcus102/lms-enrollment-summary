from tutor import hooks

# Add the app to LMS and CMS
hooks.Filters.ENV_PATCHES.add_item(
    ("openedx-lms-common-settings", "INSTALLED_APPS.append('enrollment_summary')")
)
hooks.Filters.ENV_PATCHES.add_item(
    ("openedx-cms-common-settings", "INSTALLED_APPS.append('enrollment_summary')")
)

# Add URLs
hooks.Filters.ENV_PATCHES.add_item(
    ("openedx-lms-common-settings", "ROOT_URLCONF = 'enrollment_summary.urls'")
)
