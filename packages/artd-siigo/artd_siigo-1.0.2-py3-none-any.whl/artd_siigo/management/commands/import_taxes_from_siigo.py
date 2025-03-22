from artd_partner.models import Partner
from django.core.management.base import BaseCommand, CommandError

from artd_siigo.models import SiigoTax
from artd_siigo.utils.siigo_api_util import SiigoApiUtil


class Command(BaseCommand):
    help = "Imports tax information from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose tax information needs to be imported",  # noqa
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Importing tax information from Siigo...",
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
            siigo_api = SiigoApiUtil(partner)
            taxes = siigo_api.get_taxes()

            for tax in taxes:
                SiigoTax.objects.update_or_create(
                    siigo_id=tax["id"],
                    partner=partner,
                    defaults={
                        "name": tax["name"],
                        "type": tax["type"],
                        "percentage": tax["percentage"],
                        "active": tax["active"],
                        "json_data": tax,
                    },
                )
            self.stdout.write(
                self.style.SUCCESS("Tax information imported successfully")
            )

        except Exception as e:
            raise CommandError(f"Error importing tax information: {e}")
