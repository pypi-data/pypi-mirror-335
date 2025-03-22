from django.core.management.base import BaseCommand, CommandError
from artd_siigo.models import SiigoPaymentType
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner
from artd_siigo.utils.siigo_api_util import to_bool

TYPES = (
    "RC",
    "FV",
)


class Command(BaseCommand):
    help = "Imports payment types from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'partner_slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose payment types need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Importing payment types from Siigo..."))
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
            payment_types = []
            for type in TYPES:
                payment_types.append(siigo_api.get_document_types(type=type))

            for payment_type_list in payment_types:
                for payment_type in payment_type_list:
                    SiigoPaymentType.objects.update_or_create(
                        siigo_id=payment_type["id"],
                        partner=partner,
                        defaults={
                            "name": payment_type.get("name", ""),
                            "type": payment_type.get("type", ""),
                            "active": to_bool(payment_type.get("active", False)),
                            "due_date": to_bool(payment_type.get("due_date", "")),
                            "json_data": payment_type,
                        },
                    )
            self.stdout.write(self.style.SUCCESS("Payment types imported successfully"))

        except Exception as e:
            raise CommandError(f"Error importing payment types: {e}")
