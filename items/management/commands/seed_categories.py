from django.core.management.base import BaseCommand

from catalog.models import ItemCategory


class Command(BaseCommand):
    help = "Seed default e-waste categories"

    DEFAULT_CATEGORIES = {
        "Motherboards": 5500,
        "RAM": 7500,
        "Phone Boards": 7500,
    }

    def handle(self, *args, **options):
        for name, price in self.DEFAULT_CATEGORIES.items():
            category, created = ItemCategory.objects.get_or_create(
                name=name,
                defaults={"base_price_per_kg": price},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category {name}"))
            else:
                self.stdout.write(f"Category {name} already exists")
