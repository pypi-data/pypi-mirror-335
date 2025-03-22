from celery import shared_task
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_siigo.utils.siigo_db_util import SiigoDbUtil
from artd_siigo.models import PartnerSiigoConfiguration
from artd_partner.models import Partner


@shared_task(bind=True)
def sync_siigo_products(partner_slug):
    """
    Celery task to import products from Siigo for a specified partner.

    Args:
        partner_slug (str): The slug of the partner whose products need to be imported.

    Returns:
        dict: A summary containing the number of products processed and any errors encountered.
    """
    # Validate partner existence
    try:
        partner = Partner.objects.get(partner_slug=partner_slug)
    except Partner.DoesNotExist:
        return {"error": f"Partner with slug '{partner_slug}' does not exist"}

    partner_siigo_configuration = PartnerSiigoConfiguration.objects.filter(
        partner
    ).last()

    if not partner_siigo_configuration:
        error_message = (
            f"PartnerSiigoConfiguration for partner '{partner_slug}' does not exist"
        )
        return {"status": "error", "message": error_message}

    if not partner_siigo_configuration.import_products_from_siigo:
        error_message = f"Products import is not enabled for partner '{partner_slug}'"
        return {"status": "error", "message": error_message}
    try:
        siigo_api = SiigoApiUtil(partner)
        siigo_db = SiigoDbUtil(partner)
        products = siigo_api.get_all_products(partner=partner)
        total_products = len(products)
        processed_products = 0
        errors = []

        # Process each product
        for product in products:
            try:
                siigo_id = product.get("id", "")
                account_group = product.get("account_group", {}).get("id", "")

                product_data = {
                    "siigo_id": siigo_id,
                    "code": product.get("code", ""),
                    "name": product.get("name", ""),
                    "account_group": siigo_db.get_account_group(account_group),
                    "type": product.get("type", ""),
                    "stock_control": product.get("stock_control", ""),
                    "active": product.get("active", ""),
                    "tax_classification": product.get("tax_classification", ""),
                    "tax_included": product.get("tax_included", ""),
                    "tax_consumption_value": product.get("tax_consumption_value", 0),
                    "unit_label": product.get("unit_label", ""),
                    "unit": siigo_db.update_or_create_unit(product.get("unit", ""))[0],
                    "reference": product.get("reference", ""),
                    "description": product.get("description", ""),
                    "additional_fields": product.get("additional_fields", ""),
                    "available_quantity": product.get("available_quantity", ""),
                    "metadata": product.get("metadata", {}),
                    "json_data": product,
                }

                # Create or update the product
                product_obj, created = siigo_db.create_or_update_product(product_data)

                # Set related warehouses
                warehouses = [
                    siigo_db.get_warehouse(w.get("id", ""))
                    for w in product.get("warehouses", [])
                ]
                if warehouses:
                    product_obj.warehouses.set(warehouses)

                # Set related taxes
                taxes = [
                    siigo_db.get_siigo_tax(t.get("id", ""))
                    for t in product.get("taxes", [])
                ]
                if taxes:
                    product_obj.taxes.set(taxes)

                # Update product prices
                siigo_db.get_or_update_prices(product_obj, product.get("prices", ""))
                processed_products += 1

            except Exception as product_error:
                errors.append(
                    f"Error processing product '{product.get('name', 'Unknown')}': {product_error}"
                )

        # Return a summary of the results
        return {
            "total_products": total_products,
            "processed_products": processed_products,
            "errors": errors,
        }

    except Exception as e:
        return {"error": f"Error importing products: {e}"}
