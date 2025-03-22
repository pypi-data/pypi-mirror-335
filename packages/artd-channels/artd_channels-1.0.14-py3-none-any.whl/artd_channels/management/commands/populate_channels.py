from django.core.management.base import BaseCommand
from artd_channels.models import Channel
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Populate the Channel model with WhatsApp, SMS, and Email"

    def handle(self, *args, **kwargs):
        channels = [
            {"name": "WhatsApp", "id": 1},
            {"name": "SMS", "id": 2},
            {"name": "Email", "id": 3},
        ]

        for channel_data in channels:
            name = channel_data["name"]
            slug = slugify(name)
            id = channel_data["id"]

            # Verificar si ya existe un canal con el mismo slug o nombre
            channel, created = Channel.objects.update_or_create(
                id=id,
                defaults={
                    "name": name,
                    "slug": slug,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Channel {name} created successfully.")
                )
            else:
                self.stdout.write(self.style.WARNING(f"Channel {name} already exists."))
