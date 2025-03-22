from django.db.models.signals import post_save
from django.dispatch import receiver
from artd_product.models import Product
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner
from artd_siigo.models import (
    ProductTypeMapping,
    SiigoProductType,
    TaxMapping,
    SiigoProductProxy,
    SiigoTax,
    SiigoProduct,
)
from artd_siigo.models import PartnerSiigoConfiguration


@receiver(post_save, sender=Product)
def create_artd_product(
    sender: Product,
    instance: Product,
    created: bool,
    **kwargs,
) -> None:
    partner_siigo_configuration = PartnerSiigoConfiguration.objects.filter(
        partner=instance.partner
    ).last()
    if not partner_siigo_configuration:
        return

    if not partner_siigo_configuration.import_products_from_siigo:
        return

    product: Product = instance
    source_dict = product.source
    if source_dict:
        if len(source_dict) > 0:
            if "name" in source_dict:
                source = source_dict["name"]
                if source == "SIIGO":
                    return
    partner: Partner = product.partner
    siigo_api_util = SiigoApiUtil(partner=partner)
    try:
        product_type_mapping = ProductTypeMapping.objects.get(
            product_type=product.type,
            partner=partner,
        )
        siigo_product_type: SiigoProductType = product_type_mapping.siigo_product_type
        siigo_product_proxy = SiigoProductProxy.objects.filter(product=product).last()
        siigo_account_group = None
        if siigo_product_proxy:
            siigo_account_group = siigo_product_proxy.siigo_account_group
        tax = product.tax
        tax_mapping = TaxMapping.objects.get(
            tax=tax,
            partner=partner,
        )
        siigo_tax: SiigoTax = tax_mapping.siigo_tax
        taxes = []
        tax_dict = {
            "id": siigo_tax.siigo_id,
            "name": siigo_tax.name,
            "type": siigo_tax.type,
            "percentage": siigo_tax.percentage,
        }
        taxes.append(tax_dict)
        product_data = {
            "code": product.sku,
            "name": product.name,
            "type": siigo_product_type.code,
            "active": product.status,
            "taxes": taxes,
        }
        if siigo_account_group:
            product_data["account_group"] = siigo_account_group.siigo_id
        if not SiigoProduct.objects.filter(product=product).exists():
            response = siigo_api_util.create_product(product_data)
            print
            if response:
                if isinstance(response, dict):
                    if "status_code" in response:
                        if response["status_code"] == "400":
                            print(f"Response error: {response}")
                        else:
                            print(f"Response: {response}")
                            status_code = int(response["status_code"])
                            if status_code >= 200 and status_code < 300:
                                create_siigo_product(
                                    product, response["response"]["id"]
                                )
    except Exception as e:
        print(f"error:{str(e)}")


def create_siigo_product(
    product: Product,
    siigo_id: str,
):
    """
    Creates a new Siigo product record.

    Args:
        product (Product): The product instance.
    """
    SiigoProduct.objects.create(
        partner=product.partner,
        siigo_id=siigo_id,
        synchronized=True,
        product=product,
    )
