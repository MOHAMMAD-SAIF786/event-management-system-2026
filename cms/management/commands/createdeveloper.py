from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from cms.models import AdminProfile


class Command(BaseCommand):
    help = "Promote or create a user as a CMS Developer role"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username of the developer account")
        parser.add_argument("--password", type=str, help="Password if creating new user", default="Developer123!")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        user = User.objects.filter(username=username).first()
        if not user:
            user = User.objects.create_superuser(
                username=username,
                email=f"{username}@admin.local",
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f"Created new superuser '{username}'"))
        else:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        profile, created = AdminProfile.objects.get_or_create(
            user=user,
            defaults={"role": "developer"},
        )
        if not created:
            profile.role = "developer"
            profile.save()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully promoted user '{username}' to CMS Developer role!")
        )
