"""
# LMS Enrollment Summary API Plugin for Open edX

A Django plugin for Open edX that provides a comprehensive REST API endpoint for retrieving enrollment summaries with filtering, pagination, and caching capabilities.

## Features

- **Read-only REST API**: GET endpoint for enrollment summaries
- **Flexible Filtering**: Filter by user_id and active status
- **Pagination**: Configurable page size with sensible defaults
- **Caching**: Built-in caching for performance optimization
- **Comprehensive Testing**: Full test suite with >90% coverage
- **Production Ready**: Follows Open edX conventions and best practices

## API Endpoint

### GET `/api/enrollments/summary/`

Returns paginated enrollment summaries with optional filtering.

#### Query Parameters

- `user_id` (optional): Filter by specific user ID
- `active` (optional): Filter by enrollment status (true/false)  
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

#### Response Format

```json
{
    "count": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "next": "http://localhost:8000/api/enrollments/summary/?page=2",
    "previous": null,
    "results": [
        {
            "user_id": 123,
            "username": "student1",
            "course_key": "course-v1:MITx+6.00x+2024",
            "course_title": "Introduction to Computer Science",
            "enrollment_status": "verified",
            "is_active": true,
            "created": "2024-01-15T10:30:00Z",
            "graded_subsections_count": 12
        }
    ]
}
```

## Installation

### Prerequisites

- Open edX running with Tutor
- Python 3.10+
- Admin/staff access to the LMS

### Installation Steps

1. **Clone the plugin code** (save the complete codebase to your local machine)

2. **Install via pip in your Tutor environment**:
```bash
# Enter the Tutor LMS container
tutor local exec lms bash

# Install the plugin
pip install -e /path/to/lms-enrollment-summary/

# Run migrations (if any)
python manage.py migrate

# Restart LMS
exit
tutor local restart lms
```

3. **Verify installation**:
```bash
# Check if the plugin is loaded
tutor local exec lms python manage.py shell -c "
from django.conf import settings
print('enrollment_summary' in settings.INSTALLED_APPS)
"
```

### Quick Test

```bash
# Create a superuser (if you don't have one)
tutor local exec lms python manage.py createsuperuser

# Test the API endpoint
curl -u "admin:password" \
  "http://localhost:8000/api/enrollments/summary/" \
  -H "Accept: application/json"
```

## API Usage Examples

### Basic Usage

```bash
# Get all enrollment summaries
curl -u "admin:password" \
  "http://localhost:8000/api/enrollments/summary/"

# Filter by user ID
curl -u "admin:password" \
  "http://localhost:8000/api/enrollments/summary/?user_id=123"

# Filter by active enrollments only
curl -u "admin:password" \
  "http://localhost:8000/api/enrollments/summary/?active=true"

# Pagination
curl -u "admin:password" \
  "http://localhost:8000/api/enrollments/summary/?page=2&page_size=10"

# Combined filters
curl -u "admin:password" \
  "http://localhost:8000/api/enrollments/summary/?user_id=123&active=true&page_size=5"
```

### Using with Python requests

```python
import requests
from requests.auth import HTTPBasicAuth

url = "http://localhost:8000/api/enrollments/summary/"
auth = HTTPBasicAuth('admin', 'password')

# Get all enrollments
response = requests.get(url, auth=auth)
data = response.json()

print(f"Total enrollments: {data['count']}")
for enrollment in data['results']:
    print(f"User: {enrollment['username']}, Course: {enrollment['course_title']}")
```

### Postman Collection

```json
{
    "info": {
        "name": "LMS Enrollment Summary API"
    },
    "item": [
        {
            "name": "Get All Enrollments",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/api/enrollments/summary/",
                "auth": {
                    "type": "basic",
                    "basic": {
                        "username": "{{admin_username}}",
                        "password": "{{admin_password}}"
                    }
                }
            }
        },
        {
            "name": "Filter by User ID",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/api/enrollments/summary/?user_id=123"
            }
        }
    ],
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:8000"
        },
        {
            "key": "admin_username",
            "value": "admin"
        },
        {
            "key": "admin_password",
            "value": "password"
        }
    ]
}
```

## Configuration

### Settings

Add these settings to your Open edX configuration:

```python
# Default page size for enrollment summary API
ENROLLMENT_SUMMARY_PAGE_SIZE = 20

# Maximum page size allowed
ENROLLMENT_SUMMARY_MAX_PAGE_SIZE = 100
```

### Caching

The plugin uses Django's cache framework:

- **Graded subsections count**: Cached for 1 hour per course
- **API responses**: HTTP cache headers set to 5 minutes
- **Cache keys**: Prefixed with `graded_subsections_count_`

## Testing

Run the test suite:

```bash
# Run all tests
tutor local exec lms python manage.py test enrollment_summary

# Run with coverage
tutor local exec lms python -m pytest enrollment_summary/tests/ --cov=enrollment_summary --cov-report=html

# Run specific test file
tutor local exec lms python manage.py test enrollment_summary.tests.test_views
```

## Architecture

### Data Flow

1. **Request**: API receives GET request with optional filters
2. **Authentication**: Verify user has admin/staff permissions
3. **Validation**: Validate query parameters
4. **Service Layer**: `EnrollmentSummaryService` handles business logic
5. **Data Retrieval**: Query CourseEnrollment and CourseOverview models
6. **Caching**: Check cache for graded subsections count
7. **Serialization**: Convert data using DRF serializers
8. **Response**: Return paginated JSON response

### Database Queries

- **Primary**: `student_courseenrollment` table (MySQL)
- **Secondary**: `course_overviews_courseoverview` table (MySQL)
- **Caching**: Course structure data via modulestore (MongoDB)

### Extension Points

The plugin integrates with Open edX through:

- **Django Apps**: Standard Django app with `AppConfig`
- **URL Routing**: Registered via `PluginURLs.CONFIG`
- **Settings**: Configurable via `PluginSettings.CONFIG`
- **Permissions**: Uses DRF permission classes

## Security

- **Authentication**: Requires authenticated users
- **Authorization**: Only staff/admin users can access
- **Input Validation**: All query parameters validated
- **SQL Injection**: Uses Django ORM (protected)
- **Rate Limiting**: HTTP cache headers prevent excessive requests

## Performance Considerations

- **Database Indexing**: Leverages existing Open edX indexes
- **Query Optimization**: Uses `select_related()` for foreign keys
- **Caching Strategy**: Caches expensive modulestore queries
- **Pagination**: Prevents large result sets
- **HTTP Caching**: Reduces server load with cache headers

## Troubleshooting

### Common Issues

1. **Plugin not loading**:
   ```bash
   # Check if plugin is in INSTALLED_APPS
   tutor local exec lms python manage.py shell -c "
   from django.conf import settings
   print([app for app in settings.INSTALLED_APPS if 'enrollment' in app])
   "
   ```

2. **Permission denied**:
   - Ensure user has `is_staff=True` or `is_superuser=True`
   - Check authentication credentials

3. **Empty results**:
   - Verify CourseEnrollment data exists
   - Check filters are not too restrictive

4. **Performance issues**:
   - Enable Django query logging to identify slow queries
   - Check cache hit rates
   - Consider database indexes

### Logs

Monitor these log locations:

```bash
# LMS logs
tutor local logs lms

# Plugin-specific logs
tutor local exec lms python manage.py shell -c "
import logging
logger = logging.getLogger('enrollment_summary.services')
logger.info('Testing plugin logging')
"
```

## Development

### Adding Features

1. **New endpoints**: Add to `urls.py` and create views
2. **New filters**: Extend `EnrollmentSummaryService.get_enrollment_summaries()`
3. **New fields**: Update `EnrollmentSummarySerializer`
4. **Tests**: Add corresponding test cases

### Code Quality

The plugin follows Open edX conventions:

- **Code Style**: Black, isort, flake8
- **Testing**: pytest with >90% coverage
- **Documentation**: Comprehensive docstrings
- **Type Hints**: Python 3.10+ typing support

## Future Enhancements

### Potential Features

1. **Export Functionality**: CSV/Excel export of enrollment data
2. **Real-time Updates**: WebSocket support for live enrollment changes
3. **Analytics Integration**: Integration with Open edX Analytics
4. **Bulk Operations**: Batch enrollment status updates
5. **Advanced Filtering**: Date ranges, course categories, enrollment modes
6. **Metrics Dashboard**: Built-in analytics and visualizations

### Performance Optimizations

1. **Database Views**: Create materialized views for complex queries
2. **Background Tasks**: Async processing for large datasets
3. **CDN Integration**: Cache API responses at CDN level
4. **Database Sharding**: Support for multiple database connections

## Support

For issues and questions:

1. **Check logs**: Review LMS and plugin logs for errors
2. **Test environment**: Verify setup in development environment
3. **Documentation**: Review Open edX and Django documentation
4. **Community**: Post questions on Open edX forums

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

---

**Plugin Version**: 1.0.0  
**Open edX Compatibility**: Olive, Palm, Quince releases  
**Python**: 3.10+  
**Django**: 3.2+
"""

# ============================================================================
# .gitignore
# ============================================================================
"""
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Testing
.coverage
.pytest_cache/
htmlcov/

# Virtual environments
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

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
"""

# ============================================================================
# requirements.txt - Dependencies
# ============================================================================
"""
Django>=3.2,<4.0
djangorestframework>=3.12
django-filter>=2.4
"""

# ============================================================================
# Makefile - Development Commands
# ============================================================================
"""
.PHONY: help install test lint format clean

help:
	@echo "Available commands:"
	@echo "  install    Install the plugin in development mode"
	@echo "  test       Run the test suite"
	@echo "  lint       Run code linting"
	@echo "  format     Format code with black and isort"
	@echo "  clean      Clean build artifacts"

install:
	pip install -e .
	
test:
	python -m pytest enrollment_summary/tests/ -v --cov=enrollment_summary

lint:
	flake8 enrollment_summary/
	black --check enrollment_summary/
	isort --check-only enrollment_summary/

format:
	black enrollment_summary/
	isort enrollment_summary/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
"""