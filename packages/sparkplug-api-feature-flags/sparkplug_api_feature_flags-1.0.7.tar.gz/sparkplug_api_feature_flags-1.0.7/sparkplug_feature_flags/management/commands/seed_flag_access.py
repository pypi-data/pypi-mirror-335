# django
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

# contrib
from decouple import config

# app
from ...models import FeatureFlag


User = get_user_model()


class Command(BaseCommand):
    help = "Seed flag access"

    def handle(self, *args, **options: str) -> None:  # noqa: ARG002
        email = config("USER_EMAIL")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        flags = (
            FeatureFlag.objects
            .filter(enabled=True)
            .order_by("-created")
        )

        user.feature_flags.add(*flags)
