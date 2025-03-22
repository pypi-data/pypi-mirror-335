from django.core.management.base import BaseCommand, CommandError
from artd_siigo.models import SiigoPriceList
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner


class Command(BaseCommand):
    help = "Imports price lists from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'partner_slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose price lists need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Importing price lists from Siigo..."))
        partner_slug = options["partner_slug"]
        # Validate partner existence
        try:
            partner = Partner.objects.get(partner_slug=partner_slug)
        except Partner.DoesNotExist:
            raise CommandError(f"Partner with slug '{partner_slug}' does not exist")

        try:
            siigo_api = SiigoApiUtil(partner)
            price_lists = (
                siigo_api.get_price_lists()
            )  # Assumes you have this method implemented

            for price_list in price_lists:
                SiigoPriceList.objects.update_or_create(
                    siigo_id=price_list["id"],
                    partner=partner,
                    defaults={
                        "name": price_list["name"],
                        "active": price_list["active"],
                        "position": price_list["position"],
                        "json_data": price_list,  # Assuming this field exists in SiigoPriceList
                    },
                )
            self.stdout.write(self.style.SUCCESS("Price lists imported successfully"))

        except Exception as e:
            raise CommandError(f"Error importing price lists: {e}")
