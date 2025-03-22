from django.core.management.base import BaseCommand, CommandError
from artd_siigo.models import SiigoFixedAsset
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner


class Command(BaseCommand):
    help = "Imports fixed assets from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose fixed assets need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Importing fixed assets from Siigo..."))
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
            assets = (
                siigo_api.get_fixed_assets()
            )  # Assuming `get_fixed_assets` retrieves the assets list

            for asset in assets:
                SiigoFixedAsset.objects.update_or_create(
                    siigo_id=asset["id"],
                    partner=partner,
                    defaults={
                        "name": asset["name"],
                        "group": asset["group"],
                        "active": asset["active"],
                        "json_data": asset,
                    },
                )
            self.stdout.write(self.style.SUCCESS("Fixed assets imported successfully"))

        except Exception as e:
            raise CommandError(f"Error importing fixed assets: {e}")
