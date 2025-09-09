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
        "edx-django-utils>=3.0.0",
    ],
    entry_points={
        "lms.djangoapp": [
            "enrollment_summary = enrollment_summary.apps:EnrollmentSummaryConfig",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
    ],
)
