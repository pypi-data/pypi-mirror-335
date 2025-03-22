from django.core.management.base import BaseCommand, CommandError
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_siigo.utils.siigo_db_util import SiigoDbUtil
from artd_partner.models import Partner
import time


class Command(BaseCommand):
    help = "Imports products from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'partner_slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose products lists need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Importing producs from Siigo..."))
        partner_slug = options["partner_slug"]

        # Validate partner existence
        try:
            partner = Partner.objects.get(partner_slug=partner_slug)
        except Partner.DoesNotExist:
            raise CommandError(f"Partner with slug '{partner_slug}' does not exist")

        try:
            siigo_api = SiigoApiUtil(partner)
            siigo_db = SiigoDbUtil(partner)
            products = siigo_api.get_all_products(partner=partner)
            total_products = len(products)
            self.stdout.write(
                self.style.SUCCESS(
                    f"### Products imported successfully ### {total_products} products"
                )
            )
            processed_products = 0
            time.sleep(5)
            for product in products:
                siigo_id = product.get("id", "")
                code = product.get("code", "")
                name = product.get("name", "")
                account_group = product.get("account_group", "")
                account_group_id = account_group.get("id", "")
                siigo_account_group = siigo_db.get_account_group(account_group_id)
                type = product.get("type", "")
                stock_control = product.get("stock_control", "")
                active = product.get("active", "")
                tax_classification = product.get("tax_classification", "")
                tax_included = product.get("tax_included", "")
                tax_consumption_value = product.get("tax_consumption_value", 0)
                taxes = product.get("taxes", [])
                siigo_taxes = []
                for tax in taxes:
                    tax_id = tax.get("id", "")
                    siigo_tax = siigo_db.get_siigo_tax(tax_id)
                    siigo_taxes.append(siigo_tax)
                unit_label = product.get("unit_label", "")
                unit = product.get("unit", "")
                unit_obj, created = siigo_db.update_or_create_unit(unit)
                reference = product.get("reference", "")
                description = product.get("description", "")
                additional_fields = product.get("additional_fields", "")
                available_quantity = product.get("available_quantity", "")
                metadata = product.get("metadata", dict)
                product_data_dict = {
                    "siigo_id": siigo_id,
                    "code": code,
                    "name": name,
                    "account_group": siigo_account_group,
                    "type": type,
                    "stock_control": stock_control,
                    "active": active,
                    "tax_classification": tax_classification,
                    "tax_included": tax_included,
                    "tax_consumption_value": tax_consumption_value,
                    "unit_label": unit_label,
                    "unit": unit_obj,
                    "reference": reference,
                    "description": description,
                    "additional_fields": additional_fields,
                    "available_quantity": available_quantity,
                    "metadata": metadata,
                    "json_data": product,
                }

                product_obj, created = siigo_db.create_or_update_product(
                    product_data_dict
                )

                warehouses = product.get("warehouses", [])
                siigo_warehouses = []
                for warehouse in warehouses:
                    siigo_warehouse = siigo_db.get_warehouse(warehouse.get("id", ""))
                    siigo_warehouses.append(siigo_warehouse)
                if len(siigo_warehouses) > 0:
                    product_obj.warehouses.set(siigo_warehouses)
                siigo_taxes = []
                for tax in taxes:
                    siigo_tax = siigo_db.get_siigo_tax(tax.get("id", ""))
                    siigo_taxes.append(siigo_tax)
                if len(siigo_taxes) > 0:
                    product_obj.taxes.set(siigo_taxes)
                    product_obj.save()
                prices = product.get("prices", "")
                siigo_db.get_or_update_prices(product_obj, prices)
                processed_products += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Product {processed_products} of {total_products} '{name}' processed successfully"
                    )
                )

        except Exception as e:
            raise CommandError(f"Error importing products: {e}")
