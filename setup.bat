@echo off
echo Building and starting Django Blog with Docker Compose...

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
)

docker-compose up --build -d

echo Waiting for database to be ready...
timeout /t 10 /nobreak

echo Running database migrations...
docker-compose exec web python manage.py migrate

set /p response="Do you want to create a superuser? (y/n): "
if /i "%response%"=="y" (
    docker-compose exec web python manage.py createsuperuser
)

echo Django Blog is now running!
echo Access the application at: http://localhost:8000
echo Admin panel at: http://localhost:8000/admin
pause