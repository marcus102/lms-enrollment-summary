from setuptools import setup, find_packages

setup(
    name="lms-enrollment-summary-plugin",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
        "djangorestframework",
        "django-filter",
    ],
    entry_points={
        "lms.djangoapp": [
            "enrollment_summary = tutor_enrollment_summary.hooks",
        ],
    },
)
