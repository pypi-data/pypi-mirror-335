import traceback
from django.db.models.signals import post_save
from django.dispatch import receiver
from artd_siigo.models import SiigoProduct
from artd_product.models import Product, Tax
from artd_partner.models import Partner
from artd_siigo.models import ProductTypeMapping, SiigoProductType, TaxMapping
from artd_siigo.data.source import SOURCE
from artd_siigo.models import PartnerSiigoConfiguration


@receiver(post_save, sender=SiigoProduct)
def create_siigo_product(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a Product when a SiigoProduct is saved.

    This function listens to the post_save signal of the SiigoProduct model,
    and creates or updates a corresponding Product in the system based on
    SiigoProduct's data.

    Args:
        sender (Model): The model class that sent the signal (SiigoProduct).
        instance (SiigoProduct): The actual instance being saved.
        created (bool): Boolean; True if the object was created, False if updated.
        **kwargs: Additional keyword arguments.
    """

    partner_siigo_configuration = PartnerSiigoConfiguration.objects.filter(
        partner=instance.partner
    ).last()
    if not partner_siigo_configuration:
        return

    if not partner_siigo_configuration.import_products_from_siigo:
        return

    siigo_product: SiigoProduct = instance
    if siigo_product.synchronized:
        return
    siigo_product = SiigoProduct.objects.get(id=siigo_product.id)
    partner: Partner = siigo_product.partner
    code = siigo_product.code
    name = siigo_product.name
    product_type = siigo_product.type
    taxes = siigo_product.taxes.all()
    description = siigo_product.description
    try:
        siigo_product_type = SiigoProductType.objects.filter(
            partner=partner,
            code=product_type,
        ).last()
        product_type_mapping = ProductTypeMapping.objects.filter(
            partner=partner,
            siigo_product_type=siigo_product_type,
        ).last()

        artd_tax = Tax.objects.first()
        if taxes.count() > 0:
            siigo_tax = taxes.last()
            if (
                TaxMapping.objects.filter(
                    partner=partner,
                    siigo_tax=siigo_tax,
                ).count()
                > 0
            ):
                tax_mapping = TaxMapping.objects.filter(
                    partner=partner,
                    siigo_tax=siigo_tax,
                ).last()
                artd_tax = tax_mapping.tax
        defaults = {
            "type": product_type_mapping.product_type,
            "name": name,
            "sku": code,
            "description": description,
            "short_description": description,
            "tax": artd_tax,
            "json_data": siigo_product.json_data,
            "source": SOURCE,
        }

        product_obj, created = Product.objects.update_or_create(
            partner=partner,
            sku=code,
            defaults=defaults,
        )
        siigo_product.synchronized = True
        siigo_product.product = product_obj
        siigo_product.save()

    except Exception as e:
        tb = traceback.format_exc()
        print(
            "-------------------------",
            "Error: ",
            str(e),
            tb,
            "-------------------------",
            "\n",
        )
        siigo_product.synchronized = True
        siigo_product.save()
