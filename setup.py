"""
Setup configuration for the lms-enrollment-summary plugin
"""
from setuptools import setup, find_packages

setup(
    name="lms-enrollment-summary",
    version="1.0.0",
    description="A Django plugin for Open edX that provides enrollment summary API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Open edX Developer",
    author_email="developer@example.com",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "Django>=3.2,<4.0",
        "djangorestframework>=3.12.0",
        "opaque-keys",
        "edx-django-utils",
    ],
    entry_points={
        "lms.djangoapp": [
            "lms_enrollment_summary = lms_enrollment_summary.apps:LMSEnrollmentSummaryConfig",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
)