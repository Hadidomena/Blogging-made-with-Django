# Blog REST API Documentation

## API Base URL: `http://127.0.0.1:8000/api/`

## Endpoints

### Authentication
- **POST** `/api/auth/register/` - Register user
- **POST** `/api/auth/login/` - Login user  
- **POST** `/api/auth/logout/` - Logout user
- **GET** `/api/auth/status/` - Check auth status

### Posts
- **GET** `/api/posts/` - List posts (pagination, sorting)
- **GET** `/api/posts/{id}/` - Get post details
- **POST** `/api/posts/create/` - Create post (auth required)

### Comments
- **GET** `/api/posts/{id}/comments/` - Get post comments
- **POST** `/api/posts/{id}/comments/create/` - Add comment (auth required)

## Query Parameters

### Sorting
- `?sort=newest|oldest|updated_newest|updated_oldest`
- `?comment_sort=newest|oldest`

### Pagination
- `?page=1` - Page number
- `?page_size=10` - Items per page

## Usage Examples

### Register
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "pass123"}'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass123"}'
```

### Get Posts
```bash
curl http://127.0.0.1:8000/api/posts/
curl "http://127.0.0.1:8000/api/posts/?sort=oldest&page=1"
```

### Create Post (requires auth)
```bash
curl -X POST http://127.0.0.1:8000/api/posts/create/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: TOKEN" \
  --cookie "sessionid=SESSION" \
  -d '{"title": "Title", "content": "Content"}'
```

## Response Format

### Posts List
```json
{
  "posts": [{"id": 1, "title": "Post", "author": "user", ...}],
  "pagination": {"current_page": 1, "total_pages": 2, ...}
}
```

### Post Detail
```json
{
  "id": 1,
  "title": "Post Title",
  "content": "Content",
  "author": "username",
  "comments": [{"id": 1, "content": "Comment", ...}]
}
```

## Authentication
Uses Django session authentication. Include session cookie and CSRF token for protected endpoints.