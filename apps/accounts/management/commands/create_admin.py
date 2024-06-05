import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser if one does not exist"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, default="admin@admin.com")
        parser.add_argument("--password", type=str, default="admin")

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        role = User.Role.MANAGER

        if User.objects.filter(email=email, is_superuser=True).exists():
            self.stdout.write(self.style.WARNING("Development superuser already exists."))
            # logger.info(f"Admin User created with email: {ADMIN_EMAIL}")
        else:
            User.objects.create_superuser(
                email=email,
                password=password,
                role=role,
            )
            self.stdout.write(self.style.SUCCESS("Development Superuser created successfully"))
        self.stdout.write(self.style.WARNING(f"\temail: {email} \n\tpassword: {password} \n\trole: {role}"))
