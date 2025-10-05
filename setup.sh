#!/bin/bash

echo "Building and starting Django Blog with Docker Compose..."

if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

docker-compose up --build -d

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
docker-compose exec web python manage.py migrate

echo "Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose exec web python manage.py createsuperuser
fi

echo "Django Blog is now running!"
echo "Access the application at: http://localhost:8000"
echo "Admin panel at: http://localhost:8000/admin"