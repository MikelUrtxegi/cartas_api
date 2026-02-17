from django.core.management.base import BaseCommand
from auth_template.models import CustomUser
from django.conf import settings


class Command(BaseCommand):
    help = "Creates default users for skootik"

    def create_user(self, username, email, first_name, last_name, password=None):
        # User data
        if not password:
            password = settings.DEFAULT_ADMIN_PASSWORD
        verified = True
        phone = "1234567890"

        # Check if the user already exists
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "verified": verified,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "is_staff": True,
            },
        )

        # Set the password if the user is created
        if created:
            user.set_password(password)
            user.save()

        if created:
            msg = f"User {username} has been created and added to Admin group."
        else:
            msg = f"User {username} already exists."

        self.stdout.write(self.style.SUCCESS(msg))

    def handle(self, *args, **kwargs):
        # Create Admin users
        self.create_user("skootik", "admin@skootik.com", "Skootik", "admin")
