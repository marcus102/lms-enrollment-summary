# ====================
# README.md
# ====================
"""
# LMS Enrollment Summary API Plugin

A comprehensive Open edX plugin that provides a REST API endpoint for retrieving enrollment summaries with course details and pagination support.

## Features

- **Read-only REST API** for enrollment summaries
- **Flexible filtering** by user ID and enrollment status
- **Comprehensive course data** including graded subsections count
- **Pagination support** with configurable page sizes
- **Caching** with ETag headers for performance
- **Staff-only access** with proper permission controls
- **Comprehensive test suite** with high coverage
- **Production-ready** with logging and error handling

## Quick Start

### Installation

1. **Clone or download** this plugin to your Open edX environment:
   ```bash
   cd /path/to/your/openedx
   git clone <your-repo-url> src/lms-enrollment-summary-api
   ```

2. **Install the plugin** in development mode:
   ```bash
   cd src/lms-enrollment-summary-api
   pip install -e .
   ```

3. **Restart your Open edX services**:
   ```bash
   # For Tutor development
   tutor dev restart lms
   
   # For Tutor local
   tutor local restart lms
   ```

### Verification

1. **Check plugin registration**:
   ```bash
   tutor dev run lms python manage.py lms shell
   ```
   ```python
   from django.apps import apps
   print('enrollment_summary_api' in [app.name for app in apps.get_app_configs()])
   # Should print: True
   ```

2. **Verify URL routing**:
   ```bash
   curl -H "Authorization: Bearer <your-token>" \
        http://localhost:8000/api/enrollments/summary/
   ```

## API Documentation

### Endpoint
```
GET /api/enrollments/summary/
```

### Authentication
- Requires authenticated user
- Requires staff permissions (`is_staff=True`)

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | No | Filter by specific user ID |
| `active` | boolean | No | Filter by enrollment status (`true`/`false`) |
| `page` | integer | No | Page number (default: 1) |
| `page_size` | integer | No | Results per page (default: 20, max: 100) |

### Response Format

```json
{
    "count": 150,
    "next": "http://localhost:8000/api/enrollments/summary/?page=2",
    "previous": null,
    "results": [
        {
            "user_id": 123,
            "username": "john_doe",
            "course_key": "course-v1:MITx+6.00x+2023",
            "course_title": "Introduction to Computer Science",
            "course_short_description": "Learn programming with Python",
            "enrollment_status": "active",
            "enrollment_mode": "verified",
            "is_active": true,
            "created_date": "2023-09-01T10:30:00Z",
            "graded_subsections_count": 12,
            "course_start": "2023-09-01T00:00:00Z",
            "course_end": "2023-12-15T23:59:59Z"
        }
    ]
}
```

### Example Requests

#### Get all enrollments (paginated)
```bash
curl -H "Authorization: Bearer <token>" \
     -H "Accept: application/json" \
     "http://localhost:8000/api/enrollments/summary/"
```

#### Filter by user ID
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/enrollments/summary/?user_id=123"
```

#### Filter by active status
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/enrollments/summary/?active=true"
```

#### Combined filters with pagination
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/enrollments/summary/?user_id=123&active=true&page_size=50"
```

## Development

### Running Tests

```bash
# Run all tests
python manage.py test enrollment_summary_api

# Run specific test files
python manage.py test enrollment_summary_api.tests.test_views
python manage.py test enrollment_summary_api.tests.test_services
python manage.py test enrollment_summary_api.tests.test_serializers

# Run with coverage
pip install coverage
coverage run --source='enrollment_summary_api' manage.py test enrollment_summary_api
coverage report -m
```

### Code Quality

The plugin follows Open edX coding standards:

```bash
# Format code
black enrollment_summary_api/
isort enrollment_summary_api/

# Lint code
flake8 enrollment_summary_api/

# Type checking (optional)
mypy enrollment_summary_api/
```

### Plugin Structure

```
enrollment_summary_api/
├── __init__.py              # Package initialization
├── apps.py                  # Django app configuration
├── urls.py                  # URL routing
├── views.py                 # API views
├── serializers.py           # DRF serializers
├── services.py              # Business logic layer
├── permissions.py           # Custom permissions
├── settings/                # Plugin settings
│   ├── common.py           # Common settings
│   └── production.py       # Production settings
└── tests/                   # Test suite
    ├── __init__.py
    ├── test_views.py       # View tests
    ├── test_serializers.py # Serializer tests
    └── test_services.py    # Service tests
```

## Production Considerations

### Performance
- **Caching**: 5-minute cache for API responses with ETag headers
- **Database optimization**: Uses `select_related()` for efficient queries
- **Pagination**: Prevents large result sets from impacting performance

### Security
- **Authentication required**: All requests must be authenticated
- **Staff-only access**: Only staff users can access enrollment data
- **Input validation**: All query parameters are validated
- **Error handling**: Comprehensive error handling without data leaks

### Monitoring
- **Structured logging**: All operations are logged with appropriate levels
- **Error tracking**: Failed operations are logged with context
- **Cache monitoring**: Cache hit/miss information in logs

### Scalability
- **Efficient queries**: Minimizes database round trips
- **Paginated responses**: Handles large datasets gracefully
- **Modular design**: Easy to extend with additional features

## Troubleshooting

### Common Issues

1. **Plugin not loading**
   - Verify the plugin is installed: `pip list | grep lms-enrollment`
   - Check Django settings: `tutor config printvalue LMS_EXTRA_PIP_REQUIREMENTS`
   - Restart services after installation

2. **Permission errors**
   - Ensure user has staff permissions: `user.is_staff = True`
   - Check authentication token is valid
   - Verify CORS settings if making cross-domain requests

3. **Empty results**
   - Check if there are enrollments in the database
   - Verify filter parameters are correct
   - Check course overviews are populated

4. **Performance issues**
   - Monitor database query patterns
   - Check cache configuration
   - Consider adjusting page sizes

### Debug Commands

```bash
# Check plugin installation
tutor dev run lms python manage.py lms shell -c "
from django.conf import settings
print('enrollment_summary_api' in settings.INSTALLED_APPS)
"

# Test database connectivity
tutor dev run lms python manage.py lms shell -c "
from common.djangoapps.student.models import CourseEnrollment
print(f'Total enrollments: {CourseEnrollment.objects.count()}')
"

# Check URL routing
tutor dev run lms python manage.py lms shell -c "
from django.urls import reverse
print(reverse('enrollment_summary_api:enrollment-summary'))
"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and add tests
4. Run the test suite: `python manage.py test enrollment_summary_api`
5. Ensure code quality: `black`, `isort`, `flake8`
6. Commit your changes: `git commit -m 'Add some feature'`
7. Push to the branch: `git push origin feature/your-feature-name`
8. Submit a pull request

## License

This project is licensed under the AGPL v3.0 License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review the [Open edX documentation](https://docs.openedx.org/)
3. Open an issue in this repository
4. Join the Open edX community forums
"""

# ====================
# MANIFEST.in
# ====================
include README.md
include LICENSE
recursive-include enrollment_summary_api *.py
recursive-include enrollment_summary_api *.html
recursive-include enrollment_summary_api *.js
recursive-include enrollment_summary_api *.css
recursive-exclude enrollment_summary_api/tests *
recursive-exclude enrollment_summary_api *.pyc
recursive-exclude enrollment_summary_api *.pyo

# ====================
# requirements.txt
# ====================
Django>=3.2,<4.0
djangorestframework>=3.12.0
edx-opaque-keys[django]

# Development dependencies
black>=22.0.0
isort>=5.10.0
flake8>=4.0.0
pytest>=7.0.0
pytest-django>=4.5.0
coverage>=6.0.0

# ====================
# pytest.ini
# ====================
[tool:pytest]
DJANGO_SETTINGS_MODULE = test_settings
python_files = tests.py test_*.py *_tests.py
addopts = --verbose --tb=short
testpaths = enrollment_summary_api/tests

# ====================
# .gitignore
# ====================
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db