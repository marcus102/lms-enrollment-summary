from setuptools import setup, find_packages

setup(
    name="lms-enrollment-summary",
    version="1.0.0",
    description="Open edX LMS Enrollment Summary API Plugin",
    author="Open edX Developer",
    author_email="developer@example.com",
    packages=find_packages(),
    install_requires=[
        "Django>=3.2,<4.0",
        "djangorestframework>=3.12",
        "django-filter>=2.4",
    ],
    entry_points={
        "lms.djangoapp": [
            "enrollment_summary = enrollment_summary.apps:EnrollmentSummaryConfig",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
)