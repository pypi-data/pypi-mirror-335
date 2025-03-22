from django.core.management.base import BaseCommand
from artd_channels.models import Provider
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Populate the Channel model with WhatsApp, SMS, and Email"

    def handle(self, *args, **kwargs):
        providers = [
            {"name": "Aws", "id": 1},
            {"name": "Messagebird", "id": 2},
        ]

        for providers_data in providers:
            name = providers_data["name"]
            slug = slugify(name)
            id = providers_data["id"]

            # Verificar si ya existe un canal con el mismo slug o nombre
            provider, created = Provider.objects.update_or_create(
                id=id,
                defaults={
                    "name": name,
                    "slug": slug,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Provider {name} created successfully.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Provider {name} already exists.")
                )
