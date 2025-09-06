from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a regular user for the blog'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the new user')
        parser.add_argument('email', type=str, help='Email for the new user')
        parser.add_argument('password', type=str, help='Password for the new user')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User "{username}" already exists!')
            )
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created user "{username}" with email "{email}"'
            )
        )
