# REST API Tests

## Test Coverage

### Authentication Tests
- API status endpoint
- User registration (valid/invalid)
- User login (valid/invalid)
- User logout
- Authentication status

### Posts Tests
- Posts list with pagination/sorting
- Post detail
- Create post (auth required)
- Error handling (404, validation)

### Comments Tests
- Comments list with sorting
- Create comment (auth required)
- Error handling (validation, 404)

### Integration Tests
- Complete user workflow
- Pagination workflow

## Running Tests

```bash
# Run all API tests
python manage.py test webBlog.test_api

# Run with verbose output
python manage.py test webBlog.test_api -v 2

# Using test runner
python test_api_runner.py -v
```

## Statistics
- Total Tests: 26
- Test Classes: 2
- Endpoints Covered: 10