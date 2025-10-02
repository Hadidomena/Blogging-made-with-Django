# Blog REST API

## Base URL: `http://127.0.0.1:8000/api/`

## Endpoints

### Authentication
- **POST** `/api/auth/register/` - Register user
- **POST** `/api/auth/login/` - Login user  
- **POST** `/api/auth/logout/` - Logout user
- **GET** `/api/auth/status/` - Check auth status

### Posts
- **GET** `/api/posts/` - List posts
- **GET** `/api/posts/{id}/` - Get post details
- **POST** `/api/posts/create/` - Create post (auth required)

### Comments
- **GET** `/api/posts/{id}/comments/` - Get post comments
- **POST** `/api/posts/{id}/comments/create/` - Add comment (auth required)

## Query Parameters
- `?sort=newest|oldest|updated_newest|updated_oldest`
- `?comment_sort=newest|oldest`
- `?page=1&page_size=10` - Pagination

## Authentication
Uses Django session authentication with CSRF protection.