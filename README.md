# Django Blog Application

A full-featured blog application built with Django, featuring markdown support, user authentication, and commenting system.

## Features

- 📝 **Rich Text Posts**: Create posts with full markdown support including images, links, code blocks, and formatting
- 💬 **Comment System**: Users can comment on posts with safe markdown formatting (images and links stripped for security)
- 🔐 **User Authentication**: Login/logout functionality with proper user management
- 👨‍💼 **Admin Interface**: Full Django admin integration for content management
- 📱 **Responsive Design**: Clean, mobile-friendly interface
- 🎨 **Syntax Highlighting**: Code blocks with proper formatting
- 🔒 **Security**: XSS protection, CSRF tokens, and safe HTML rendering

## Project Structure

```
Django/
├── Blog/                   # Main project directory
│   ├── __init__.py
│   ├── settings.py        # Project settings
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── webBlog/              # Blog application
│   ├── __init__.py
│   ├── admin.py          # Admin interface configuration
│   ├── apps.py           # App configuration
│   ├── models.py         # Database models (Post, Comment)
│   ├── views.py          # View functions
│   ├── urls.py           # App URL patterns
│   ├── forms.py          # Form definitions
│   ├── migrations/       # Database migrations
│   ├── management/       # Custom management commands
│   │   └── commands/
│   │       └── createbloguser.py
│   ├── templates/        # HTML templates
│   │   └── webBlog/
│   │       ├── post_list.html
│   │       ├── post_detail.html
│   │       ├── login.html
│   │       └── markdown_guide.html
│   └── templatetags/     # Custom template filters
│       └── markdown_extras.py
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── db.sqlite3           # SQLite database (created after setup)
└── README.md            # This file
```

## Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd Django
```

### 2. Create virtual environment
```bash
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create a superuser
```bash
python manage.py createsuperuser
```

### 6. Start the development server
```bash
python manage.py runserver
```

### 7. Access the application
- **Blog**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Markdown Guide**: http://127.0.0.1:8000/markdown-guide/

## Usage

### Creating Blog Posts
1. Log in to the admin panel at `/admin/`
2. Go to "Posts" and click "Add Post"
3. Write your content using markdown syntax
4. Save and publish

### User Management
Create regular users using the management command:
```bash
python manage.py createbloguser username email@example.com password123
```

### Markdown Support
Posts support full markdown including:
- **Bold** and *italic* text
- Headers (H1, H2, H3)
- Links and images
- Code blocks with syntax highlighting
- Lists and tables
- Blockquotes

Comments support safe markdown (no images/links):
- **Bold** and *italic* text
- `Inline code`
- Block quotes
- Lists

## Development

### Project follows Django best practices:
- ✅ Proper app structure with `apps.py` configuration
- ✅ Namespaced URLs with `app_name`
- ✅ Static files configuration
- ✅ Media files support
- ✅ Custom template tags and filters
- ✅ Management commands
- ✅ Proper settings organization
- ✅ Requirements file for dependencies

### Key Models
- **Post**: Blog posts with title, content, author, timestamps
- **Comment**: User comments linked to posts with markdown support

### Security Features
- CSRF protection on all forms
- XSS prevention with safe HTML rendering
- Image/link stripping in comments
- User authentication required for commenting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.