from artd_partner.models import Partner
from django.core.management.base import BaseCommand, CommandError

from artd_siigo.models import SiigoCustomerPersonType
from artd_siigo.data.customer import PERSON_TYPES


class Command(BaseCommand):
    help = "Imports customer person types from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose person types need to be imported",  # noqa
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Importing customer person types...",
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
            for type in PERSON_TYPES:
                SiigoCustomerPersonType.objects.update_or_create(
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
