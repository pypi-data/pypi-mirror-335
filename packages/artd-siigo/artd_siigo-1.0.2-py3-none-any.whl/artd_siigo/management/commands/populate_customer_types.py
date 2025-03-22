from artd_partner.models import Partner
from django.core.management.base import BaseCommand, CommandError

from artd_siigo.models import SiigoCustomerType
from artd_siigo.data.customer import TYPES


class Command(BaseCommand):
    help = "Imports customer types from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose customer types need to be imported",  # noqa
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Importing customer types...",
            )
        )
        partner_slug = options["partner_slug"]
        # Validate partner existence
        try:
            partner = Partner.objects.get(partner_slug=partner_slug)
        except Partner.DoesNotExist:
            raise CommandError(
                f"Partner with slug '{partner_slug}' does not exist",
            )

        try:
            for type in TYPES:
                SiigoCustomerType.objects.update_or_create(
                    id=type["id"],
                    partner=partner,
                    defaults={
                        "name": type["name"],
                    },
                )
            self.stdout.write(
                self.style.SUCCESS("Customer types imported successfully")
            )

        except Exception as e:
            raise CommandError(f"Error importing customer types: {e}")
