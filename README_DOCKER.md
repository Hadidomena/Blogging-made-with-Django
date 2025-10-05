# Django Blog - Docker Setup

This Django blog application has been configured to run with Docker Compose and PostgreSQL.

## Prerequisites

- Docker Desktop (with WSL2 backend on Windows)
- Git

## Quick Start

### Option 1: Automated Setup (Recommended)

For Windows:
```bash
./setup.bat
```

For Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Build and start services:**
   ```bash
   docker-compose up --build -d
   ```

3. **Run database migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create a superuser (optional):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Access the Application

- **Blog:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **PostgreSQL:** localhost:5432

## Environment Variables

Edit the `.env` file to customize your setup:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Settings
DB_NAME=blogdb
DB_USER=bloguser
DB_PASSWORD=blogpassword
DB_HOST=db
DB_PORT=5432

# Django Configuration
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

## Docker Commands

### Development Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Access Django shell
docker-compose exec web python manage.py shell

# Access database shell
docker-compose exec db psql -U bloguser -d blogdb

# Run tests
docker-compose exec web python manage.py test

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### Database Management

```bash
# Create new migration
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

## Volumes

- `postgres_data`: PostgreSQL database files
- `static_volume`: Django static files
- `media_volume`: User uploaded media files

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Ensure PostgreSQL container is healthy:
   ```bash
   docker-compose ps
   ```

2. Check database logs:
   ```bash
   docker-compose logs db
   ```

3. Restart services:
   ```bash
   docker-compose restart
   ```

### Port Conflicts

If port 8000 or 5432 is already in use, modify the ports in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Rebuilding Images

After changing dependencies in `requirements.txt`:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Production Considerations

For production deployment:

1. **Change secret key** in `.env`
2. **Set DEBUG=False** in `.env`
3. **Configure proper ALLOWED_HOSTS** in `.env`
4. **Use environment-specific compose files**
5. **Set up proper SSL/TLS termination**
6. **Configure backup strategy for PostgreSQL**

## File Structure

```
├── Blog/                 # Django project settings
├── webBlog/             # Main Django app
├── Dockerfile           # Django container configuration
├── docker-compose.yml   # Multi-container setup
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── .env.example         # Environment template
├── setup.sh            # Linux/Mac setup script
├── setup.bat           # Windows setup script
└── README_DOCKER.md    # This file
```