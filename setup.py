from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="lms-enrollment-summary",
    version="1.0.0",
    description="Open edX LMS Enrollment Summary API Plugin",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Open edX Developer",
    author_email="developer@example.com",
    url="https://github.com/your-org/lms-enrollment-summary",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2,<4.0",
        "djangorestframework>=3.12",
        "django-filter>=2.4",
    ],
    entry_points={
        # Open edX plugin entry points
        "lms.djangoapp": [
            "enrollment_summary = enrollment_summary.apps:EnrollmentSummaryConfig",
        ],
        "openedx.django_app": [
            "enrollment_summary = enrollment_summary.apps:EnrollmentSummaryConfig",
        ],
        # Settings entry points
        "lms.django_setting": [
            "common = enrollment_summary.settings.common:plugin_settings",
            "production = enrollment_summary.settings.production:plugin_settings",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)