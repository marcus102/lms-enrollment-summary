

# ------------------------------
# README.md
# ------------------------------

# LMS Enrollment Summary API Plugin

A Django plugin for Open edX that provides a read-only REST API endpoint for retrieving enrollment summaries with filtering and pagination capabilities.

## Features

- **Read-only API**: Secure endpoint for retrieving enrollment data
- **Filtering**: Support for filtering by user ID, enrollment status, and course key
- **Pagination**: Efficient pagination with configurable page sizes
- **Caching**: Built-in caching for improved performance
- **Permissions**: Staff/admin-only access with proper authentication
- **Comprehensive Testing**: Full test coverage for views, services, and serializers

## API Endpoints

### GET /api/enrollments/summary

Retrieve enrollment summaries with optional filtering.

**Query Parameters:**
- `user_id` (optional): Filter by specific user ID
- `active` (optional): Filter by enrollment status (`true`/`false`)
- `course_key` (optional): Filter by specific course key
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (max 100, default 20)

**Example Requests:**

```bash
# Get all enrollments (paginated)
curl -X GET "https://your-lms.com/api/enrollments/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get active enrollments for a specific user
curl -X GET "https://your-lms.com/api/enrollments/summary?user_id=123&active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get enrollments for a specific course
curl -X GET "https://your-lms.com/api/enrollments/summary?course_key=course-v1:TestX+CS101+2023" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get enrollments with custom pagination
curl -X GET "https://your-lms.com/api/enrollments/summary?page=2&page_size=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Format:**

```json
{
  "count": 150,
  "next": "https://your-lms.com/api/enrollments/summary?page=2",
  "previous": null,
  "results": [
    {
      "user_id": 123,
      "username": "student123",
      "course_key": "course-v1:TestX+CS101+2023",
      "course_title": "Introduction to Computer Science",
      "enrollment_status": "active",
      "is_active": true,
      "enrollment_date": "2023-09-01T10:00:00Z",
      "graded_subsections_count": 8,
      "course_start": "2023-09-15T00:00:00Z",
      "course_end": "2023-12-15T23:59:59Z"
    }
  ]
}
```

## Installation

### 1. Install the Package

```bash
# From source
pip install -e .

# Or from a repository
pip install git+https://github.com/your-org/lms-enrollment-summary-api.git
```

### 2. Configure Open edX

Add the plugin to your Open edX configuration:

**In your `lms/envs/common.py` or tutor configuration:**

```python
# Add to INSTALLED_APPS
INSTALLED_APPS += [
    'enrollment_summary_api',
]

# Optional: Configure plugin settings
ENROLLMENT_SUMMARY_API_SETTINGS = {
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'CACHE_TIMEOUT': 300,  # 5 minutes
}
```

### 3. Run Migrations

```bash
# In your Open edX environment
python manage.py lms migrate
```

### 4. Restart Services

```bash
# For Tutor
tutor local restart lms

# For native installations
sudo systemctl restart edxapp
```

## Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/your-org/lms-enrollment-summary-api.git
cd lms-enrollment-summary-api
pip install -e .
```

### 2. Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=enrollment_summary_api --cov-report=html

# Run specific test file
python -m pytest tests/test_views.py -v
```

### 3. Code Quality

```bash
# Format code
black enrollment_summary_api/ tests/

# Sort imports  
isort enrollment_summary_api/ tests/

# Lint code
flake8 enrollment_summary_api/ tests/

# Type checking (if using mypy)
mypy enrollment_summary_api/
```

## Configuration Options

The plugin supports the following configuration options in your Open edX settings:

```python
ENROLLMENT_SUMMARY_API_SETTINGS = {
    # Default number of items per page
    'DEFAULT_PAGE_SIZE': 20,
    
    # Maximum allowed page size
    'MAX_PAGE_SIZE': 100,
    
    # Cache timeout in seconds (5 minutes default)
    'CACHE_TIMEOUT': 300,
}
```

## Performance Considerations

- **Caching**: The API implements multi-level caching for course overviews and graded subsection counts
- **Database Optimization**: Uses `select_related()` to minimize database queries
- **Pagination**: Implements efficient pagination to handle large datasets
- **Query Optimization**: Bulk fetches course data to avoid N+1 query problems

## Security

- **Authentication Required**: All endpoints require user authentication
- **Staff/Admin Only**: Access restricted to staff users and administrators
- **Input Validation**: Comprehensive validation of all query parameters
- **SQL Injection Protection**: Uses Django ORM with parameterized queries

## Monitoring and Logging

The plugin includes comprehensive logging for:
- API access patterns
- Cache hit/miss ratios
- Performance metrics
- Error tracking

Logs are written to the `enrollment_summary_api` logger.

## Architecture Integration

### Open edX Integration Points

1. **Django App Plugin**: Integrates as a standard Django app using Open edX plugin architecture
2. **URL Configuration**: Registers URLs under `/api/enrollments/` namespace
3. **Database Models**: Leverages existing Open edX models (`CourseEnrollment`, `CourseOverview`, `User`)
4. **Modulestore Integration**: Accesses course structure data for graded subsection counts
5. **Permission System**: Uses Open edX's staff/admin permission framework

### Data Flow

```
Client Request → Authentication → Permission Check → Parameter Validation 
→ Service Layer → Database Query → Course Data Aggregation → Caching 
→ Serialization → Paginated Response
```

## Testing Strategy

The plugin includes comprehensive tests covering:

- **Unit Tests**: Individual component testing (services, serializers)
- **Integration Tests**: API endpoint testing with authentication
- **Edge Cases**: Invalid parameters, missing data, permission errors
- **Performance Tests**: Cache behavior and query optimization

## Production Deployment

### Tutor Deployment

1. **Add to requirements:**
```yaml
# In tutor config
OPENEDX_EXTRA_PIP_REQUIREMENTS:
  - git+https://github.com/your-org/lms-enrollment-summary-api.git
```

2. **Configure plugin:**
```python
# In tutor patches
ENROLLMENT_SUMMARY_API_SETTINGS = {
    'CACHE_TIMEOUT': 900,  # 15 minutes in production
}
```

3. **Deploy:**
```bash
tutor config save
tutor images build openedx
tutor local restart
```

### Native Deployment

1. **Install in virtual environment:**
```bash
source /edx/app/edxapp/edxapp_env
pip install git+https://github.com/your-org/lms-enrollment-summary-api.git
```

2. **Update settings:**
```python
# In /edx/app/edxapp/lms.env.json
{
    "ADDL_INSTALLED_APPS": ["enrollment_summary_api"]
}
```

3. **Restart services:**
```bash
sudo /edx/bin/supervisorctl restart edxapp:*
```

## Troubleshooting

### Common Issues

**1. Plugin not loading:**
- Verify the plugin is in `INSTALLED_APPS`
- Check for import errors in logs
- Ensure dependencies are installed

**2. Permission denied:**
- Verify user has staff or admin privileges
- Check authentication token validity
- Review permission configuration

**3. Cache issues:**
- Clear Django cache: `python manage.py lms shell -c "from django.core.cache import cache; cache.clear()"`
- Verify cache backend configuration
- Check cache key generation logic

**4. Performance problems:**
- Enable query debugging: `LOGGING['loggers']['django.db.backends'] = {'level': 'DEBUG'}`
- Monitor cache hit ratios
- Review database indexes

### Debug Commands

```bash
# Check plugin registration
python manage.py lms shell -c "
from django.apps import apps
print([app.name for app in apps.get_app_configs() if 'enrollment' in app.name])
"

# Test API endpoint
python manage.py lms shell -c "
from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()
client = Client()
user = User.objects.filter(is_staff=True).first()
client.force_login(user)
response = client.get('/api/enrollments/summary')
print(f'Status: {response.status_code}')
print(f'Content: {response.content[:200]}')
"

# Check database connections
python manage.py lms dbshell
```

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Make your changes** following the coding standards
4. **Add tests** for any new functionality
5. **Run the test suite:** `python -m pytest tests/`
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description

### Code Standards

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Maintain test coverage above 90%
- Use type hints where appropriate

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Future Enhancements

- **Advanced Filtering**: Date range filters, course status filters
- **Bulk Operations**: Batch enrollment status updates
- **Analytics Integration**: Integration with Open edX analytics pipeline  
- **Export Functionality**: CSV/Excel export capabilities
- **Real-time Updates**: WebSocket support for live enrollment tracking
- **Advanced Caching**: Redis-based distributed caching
- **API Versioning**: Support for multiple API versions
- **Rate Limiting**: Request throttling for high-traffic scenarios

---

For more information, please refer to the [Open edX Developer Documentation](https://docs.openedx.org/) and the [Django REST Framework documentation](https://www.django-rest-framework.org/).