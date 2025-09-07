"""
Setup configuration for the LMS Enrollment Summary API plugin.
"""

from setuptools import setup, find_packages

setup(
    name="lms-enrollment-summary-api",
    version="1.0.0",
    description="Open edX plugin providing enrollment summary API endpoint",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Backend Resident",
    author_email="developer@example.com",
    url="https://github.com/your-org/lms-enrollment-summary-api",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2,<4.0",
        "djangorestframework>=3.12.0",
        "edx-django-utils>=3.0.0",
        "edx-drf-extensions>=6.0.0",
    ],
    entry_points={
        "lms.djangoapp": [
            "enrollment_summary_api = enrollment_summary_api.apps:EnrollmentSummaryApiConfig",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)