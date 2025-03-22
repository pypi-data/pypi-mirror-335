from artd_product.data.taxes import TAXES
from artd_product.models import Tax
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create taxes"

    def handle(self, *args, **options):
        for tax in TAXES:
            Tax.objects.get_or_create(
                name=tax[0],
                percentage=tax[1],
            )
        self.stdout.write(self.style.SUCCESS("Taxes created successfully"))
