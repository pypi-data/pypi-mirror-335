from artd_siigo.utils.siigo_db_util import SiigoDbUtil


def create_customer_from_siigo_integration(
    customer: dict,
    siigo_db: SiigoDbUtil,
):
    siigo_customer_document_type = ""
    if "id_type" in customer:
        id_type = customer["id_type"]
        if "code" in id_type:
            siigo_customer_document_type = id_type.get("code", "")
    customer_data = {
        "siigo_id": customer.get("id", ""),
        "siigo_customer_type": siigo_db.get_customer_type(customer.get("type", "")),
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
        "fiscal_responsibilities": customer.get("fiscal_responsibilities", dict),
        "address": customer.get("address", dict),
        "phones": customer.get("phones", dict),
        "contacts": customer.get("contacts", dict),
        "comments": customer.get("comments", ""),
        "related_users": customer.get("related_users", dict),
        "metadata": customer.get("metadata", dict),
    }

    customer_obj, created = siigo_db.create_or_update_customer(customer_data)
    return customer_obj, created
