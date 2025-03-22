from django.core.management.base import BaseCommand, CommandError
from artd_siigo.utils.siigo_db_util import SiigoDbUtil
from artd_partner.models import Partner
from artd_siigo.data.product import PRODUCT_TYPES


class Command(BaseCommand):
    help = "Imports product types from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'partner_slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose product types lists need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Importing produc types from Siigo..."))
        partner_slug = options["partner_slug"]

        # Validate partner existence
        try:
            partner = Partner.objects.get(partner_slug=partner_slug)
        except Partner.DoesNotExist:
            raise CommandError(f"Partner with slug '{partner_slug}' does not exist")

        try:
            siigo_db = SiigoDbUtil(partner)
            for product_type in PRODUCT_TYPES:
                product_type_obj = siigo_db.create_or_get_product_type(
                    product_type,
                )
                if product_type_obj:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Product type '{product_type_obj.code}' imported successfully"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to import product type '{product_type['name']}'"
                        )
                    )
            self.stdout.write(self.style.NOTICE("Product types imported successfully"))

        except Exception as e:
            raise CommandError(f"Error importing products: {e}")
