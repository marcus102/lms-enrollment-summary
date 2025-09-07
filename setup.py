"""
Setup configuration for the LMS Enrollment Summary API plugin
"""
from setuptools import setup, find_packages

setup(
    name="lms-enrollment-summary-api",
    version="1.0.0",
    description="Open edX plugin providing enrollment summary API endpoints",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Marcus",
    author_email="marcus@example.com",
    url="https://github.com/marcus102/lms-enrollment-summary-api.git",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "Django>=3.2,<4.0",
        "djangorestframework>=3.12.0",
        "edx-opaque-keys[django]",
    ],
    entry_points={
        "lms.djangoapp": [
            "enrollment_summary_api = enrollment_summary.apps:EnrollmentSummaryAPIConfig",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: AGPL License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django :: 3.2",
    ],
)