import json
from datetime import datetime
from decimal import Decimal
from typing import Union, List

from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_order.models import Order, OrderProduct
from artd_partner.models import Partner
from artd_siigo.models import BillConfig, SiigoDocumentType, SiigoInvoice
from artd_customer.models import Customer


def json_serial(obj: Union[Decimal, datetime]) -> Union[float, str]:
    """
    Helper function for JSON serialization of non-standard data types.

    Args:
        obj (Union[Decimal, datetime]): The object to serialize, typically a Decimal or datetime.

    Returns:
        Union[float, str]: The serialized form of `obj` as float or string.

    Raises:
        TypeError: If the object type is not supported for serialization.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d")
    raise TypeError(f"Type {type(obj)} not serializable in JSON")


def create_bill(order: Order, seller_id: int = 629) -> None:
    """
    Creates or updates a Siigo invoice (SiigoInvoice) based on the given order details.

    Retrieves billing configuration and related information to prepare an invoice dictionary
    which is then sent to Siigo's API. The response is used to create or update a
    `SiigoInvoice` instance.

    Args:
        order (Order): The order object for which the invoice is generated.
        seller_id (int, optional): The ID of the seller. Defaults to 629.

    Returns:
        None
    """
    partner: Partner = order.partner
    # Retrieve billing configuration for the partner
    bill_config = BillConfig.objects.filter(
        partner=partner, artd_document_type="order"
    ).first()
    siigo_document_type: SiigoDocumentType = bill_config.siigo_document_type
    now_date = datetime.now().strftime("%Y-%m-%d")
    customer: Customer = order.customer

    # Prepare line items for the invoice
    items: List[dict] = [
        {
            "code": order_product.product.sku,
            "quantity": order_product.quantity,
            "price": float(order_product.base_total),
            "discount": float(order_product.base_discount_amount),
        }
        for order_product in OrderProduct.objects.filter(order=order)
    ]

    # Prepare the invoice dictionary for the API request
    bill_dict = {
        "document": {"id": siigo_document_type.siigo_id},
        "date": now_date,
        "customer": {"identification": customer.document},
        "seller": seller_id,
        "stamp": {"send": bill_config.generate_electronic_document},
        "items": items,
    }

    # Serialize the dictionary to ensure all data types are JSON-compatible
    bill_dict = json.loads(json.dumps(bill_dict, default=json_serial))

    # Create or update the Siigo invoice using the API
    siigo_api_util = SiigoApiUtil(partner)
    response = siigo_api_util.create_invoice(bill_dict)

    # Store or update the invoice details in the database
    siigo_invoice, created = SiigoInvoice.objects.update_or_create(
        partner=partner,
        order=order,
        defaults={
            "siigo_id": response["id"],
            "number": response["number"],
            "name": response["name"],
            "date": response["date"],
            "customer": response["customer"],
            "cost_center": response["cost_center"],
            "currency": response["currency"],
            "total": response["total"],
            "balance": response["balance"],
            "seller": response["seller"],
            "stamp": response["stamp"],
            "mail": response["mail"],
            "observations": response["observations"],
            "items": response["items"],
            "payments": response["payments"],
            "public_url": response["public_url"],
            "global_discounts": response.get("global_discounts", []),
            "additional_fields": response["additional_fields"],
            "metadata": response["metadata"],
            "json_data": response,
        },
    )

    print("SiigoInvoice created" if created else "SiigoInvoice updated")
