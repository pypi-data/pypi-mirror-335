from django.core.management.base import BaseCommand, CommandError
from artd_siigo.models import SiigoDocumentType
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner
from artd_siigo.utils.siigo_api_util import to_bool

TYPES = (
    "RC",
    "NC",
    "FV",
    "CC",
)


class Command(BaseCommand):
    help = "Imports document types from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'partner_slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose document types need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Importing document types from Siigo..."))
        partner_slug = options["partner_slug"]
        # Validate partner existence
        try:
            partner = Partner.objects.get(
                partner_slug=partner_slug
            )  # Adjust this line if the slug field is named differently
        except Partner.DoesNotExist:
            raise CommandError(f"Partner with slug '{partner_slug}' does not exist")

        try:
            siigo_api = SiigoApiUtil(partner)
            document_types = []
            for type in TYPES:
                document_types.append(siigo_api.get_document_types(type=type))
            for document_type_list in document_types:
                for doc_type in document_type_list:
                    SiigoDocumentType.objects.update_or_create(
                        siigo_id=doc_type["id"],
                        partner=partner,
                        defaults={
                            "code": doc_type.get("code", ""),
                            "name": doc_type.get("name", ""),
                            "description": doc_type.get("description", ""),
                            "type": doc_type.get("type", ""),
                            "active": to_bool(doc_type.get("active", False)),
                            "seller_by_item": to_bool(
                                doc_type.get("seller_by_item", False)
                            ),
                            "cost_center": to_bool(doc_type.get("cost_center", False)),
                            "cost_center_mandatory": to_bool(
                                doc_type.get("cost_center_mandatory", False)
                            ),
                            "automatic_number": to_bool(
                                doc_type.get("automatic_number", False)
                            ),
                            "consecutive": doc_type.get("consecutive", 0),
                            "discount_type": doc_type.get("discount_type", ""),
                            "decimals": to_bool(doc_type.get("decimals", False)),
                            "advance_payment": to_bool(
                                doc_type.get("advance_payment", False)
                            ),
                            "reteiva": to_bool(doc_type.get("reteiva", False)),
                            "reteica": to_bool(doc_type.get("reteica", False)),
                            "self_withholding": to_bool(
                                doc_type.get("self_withholding", False)
                            ),
                            "self_withholding_limit": doc_type.get(
                                "self_withholding_limit", 0
                            ),
                            "electronic_type": doc_type.get("electronic_type", ""),
                            "cargo_transportation": to_bool(
                                doc_type.get("cargo_transportation", False)
                            ),
                            "healthcare_company": to_bool(
                                doc_type.get("healthcare_company", False)
                            ),
                            "customer_by_item": to_bool(
                                doc_type.get("customer_by_item", False)
                            ),
                            "json_data": doc_type,
                        },
                    )

            self.stdout.write(
                self.style.SUCCESS("Document types imported successfully")
            )

        except Exception as e:
            raise CommandError(f"Error importing document types: {e}")
