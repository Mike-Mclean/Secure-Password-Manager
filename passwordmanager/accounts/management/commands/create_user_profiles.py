from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = "Ensure all users have a UserProfile"

    def handle(self, *args, **kwargs):
        count = 0
        for user in User.objects.all():
            _, created = UserProfile.objects.get_or_create(user=user)
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {count} missing UserProfiles."))
