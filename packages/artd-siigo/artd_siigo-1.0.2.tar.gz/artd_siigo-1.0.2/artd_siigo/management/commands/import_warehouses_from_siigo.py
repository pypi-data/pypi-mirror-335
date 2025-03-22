from django.core.management.base import BaseCommand, CommandError
from artd_siigo.models import SiigoWarehouse  # Importa el modelo SiigoWarehouse
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner


class Command(BaseCommand):
    help = "Imports warehouses from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose warehouses need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Importing warehouses from Siigo..."))
        partner_slug = options["partner_slug"]

        # Validate partner existence
        try:
            partner = Partner.objects.get(
                partner_slug=partner_slug
            )  # Asegúrate de que este sea el campo correcto
        except Partner.DoesNotExist:
            raise CommandError(f"Partner with slug '{partner_slug}' does not exist")

        try:
            siigo_api = SiigoApiUtil(partner)
            warehouses = (
                siigo_api.get_warehouses()
            )  # Supón que este método obtiene los datos de las bodegas

            for warehouse in warehouses:
                obj, created = SiigoWarehouse.objects.update_or_create(
                    siigo_id=warehouse["id"],
                    partner=partner,
                    defaults={
                        "name": warehouse["name"],
                        "active": warehouse["active"],
                        "has_movements": warehouse["has_movements"],
                        "json_data": warehouse,  # Almacena toda la respuesta JSON
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created warehouse: {warehouse['name']}")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated warehouse: {warehouse['name']}")
                    )
            self.stdout.write(self.style.SUCCESS("Countries imported successfully"))

        except Exception as e:
            raise CommandError(f"Error importing warehouses: {e}")
