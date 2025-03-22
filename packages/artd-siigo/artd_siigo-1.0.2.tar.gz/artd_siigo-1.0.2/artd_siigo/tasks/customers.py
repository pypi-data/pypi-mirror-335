from celery import shared_task
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_siigo.utils.siigo_db_util import SiigoDbUtil
from artd_siigo.models import PartnerSiigoConfiguration
from artd_partner.models import Partner


@shared_task(bind=True)
def sync_siigo_customers(partner_slug):
    """
    Celery task to synchronize customers from Siigo API to local database.

    Args:
        partner_slug (str): The slug identifier for the partner.

    Returns:
        dict: A summary of the task's result or error details.
    """

    try:
        # Validate partner existence
        partner = Partner.objects.get(partner_slug=partner_slug)
    except Partner.DoesNotExist:
        error_message = f"Partner with slug '{partner_slug}' does not exist"
        return {"status": "error", "message": error_message}
    partner_siigo_configuration = PartnerSiigoConfiguration.objects.filter(
        partner
    ).last()
    if not partner_siigo_configuration:
        error_message = (
            f"PartnerSiigoConfiguration for partner '{partner_slug}' does not exist"
        )
        return {"status": "error", "message": error_message}

    if not partner_siigo_configuration.import_customers_from_siigo:
        error_message = f"Customers import is not enabled for partner '{partner_slug}'"
        return {"status": "error", "message": error_message}
    try:
        # Initialize Siigo API and DB utilities
        siigo_api = SiigoApiUtil(partner)
        siigo_db = SiigoDbUtil(partner)

        # Fetch customers from Siigo API
        customers = siigo_api.get_all_customers(partner=partner)

        processed_customers = 0

        # Process each customer
        for customer in customers:
            try:
                siigo_customer_document_type = customer.get("id_type", {}).get(
                    "code", ""
                )

                customer_data = {
                    "siigo_id": customer.get("id", ""),
                    "siigo_customer_type": siigo_db.get_customer_type(
                        customer.get("type", "")
                    ),
                    "siigo_customer_person_type": siigo_db.get_customer_person_type(
                        customer.get("person_type", "")
                    ),
                    "siigo_customer_document_type": siigo_db.get_customer_document_type(
                        siigo_customer_document_type
                    ),
                    "identification": customer.get("identification", ""),
                    "check_digit": customer.get("check_digit", ""),
                    "name": customer.get("name", ""),
                    "commercial_name": customer.get("commercial_name", ""),
                    "branch_office": customer.get("branch_office", ""),
                    "active": customer.get("active", ""),
                    "vat_responsible": customer.get("vat_responsible", ""),
                    "fiscal_responsibilities": customer.get(
                        "fiscal_responsibilities", {}
                    ),
                    "address": customer.get("address", {}),
                    "phones": customer.get("phones", {}),
                    "contacts": customer.get("contacts", {}),
                    "comments": customer.get("comments", ""),
                    "related_users": customer.get("related_users", {}),
                    "metadata": customer.get("metadata", {}),
                }

                # Create or update customer in the database
                siigo_db.create_or_update_customer(customer_data)
                processed_customers += 1

            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {
            "status": "success",
            "processed": processed_customers,
            "total": len(customers),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
