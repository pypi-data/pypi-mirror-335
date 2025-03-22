from django.core.management.base import BaseCommand, CommandError
from artd_siigo.models import SiigoCostCenter
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner


class Command(BaseCommand):
    help = "Imports cost centers from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose cost centers need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Importing cost centers from Siigo..."))
        partner_slug = options["partner_slug"]
        # Validate partner existence
        try:
            partner = Partner.objects.get(
                partner_slug=partner_slug,
            )
        except Partner.DoesNotExist:
            raise CommandError(f"Partner with slug '{partner_slug}' does not exist")

        try:
            siigo_api = SiigoApiUtil(partner)
            cost_centers = siigo_api.get_cost_centers()

            for center in cost_centers:
                SiigoCostCenter.objects.update_or_create(
                    siigo_id=center["id"],
                    partner=partner,
                    defaults={
                        "code": center["code"],
                        "name": center["name"],
                        "active": center["active"],
                        "json_data": center,
                    },
                )
            self.stdout.write(self.style.SUCCESS("Cost centers imported successfully"))

        except Exception as e:
            raise CommandError(f"Error importing cost centers: {e}")
