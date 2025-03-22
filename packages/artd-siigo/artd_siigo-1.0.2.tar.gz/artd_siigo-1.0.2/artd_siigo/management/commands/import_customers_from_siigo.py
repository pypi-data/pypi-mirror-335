from django.core.management.base import BaseCommand, CommandError
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_siigo.utils.create_customer_util import (
    create_customer_from_siigo_integration,
    SiigoDbUtil,
)
from artd_partner.models import Partner
import time


class Command(BaseCommand):
    help = "Imports customers from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'partner_slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose customers lists need to be imported",
        )

    def handle(self, *args, **options):
        partner_slug = options["partner_slug"]

        # Validate partner existence
        try:
            partner = Partner.objects.get(partner_slug=partner_slug)
        except Partner.DoesNotExist:
            raise CommandError(f"Partner with slug '{partner_slug}' does not exist")

        try:
            siigo_api = SiigoApiUtil(partner)
            siigo_db = SiigoDbUtil(partner)
            self.stdout.write(self.style.SUCCESS("### Partner found ###"))
            self.stdout.write(
                self.style.WARNING(
                    "### Importing... Importing... please wait while we get the data ###"
                )
            )
            self.stdout.write(
                self.style.WARNING(f"### Partner: {partner.partner_slug} ###")
            )
            customer = siigo_api.get_all_customers(partner=partner)
            self.stdout.write(
                self.style.WARNING("### Customers imported successfully ###")
            )
            self.stdout.write(self.style.WARNING(f"### {len(customer)} customers ###"))
            time.sleep(5)
            total_customers = len(customer)
            processed_customers = 0

            for customer in customer:
                customer_identification = customer.get("identification", "")
                customer_obj, created = create_customer_from_siigo_integration(
                    customer, siigo_db
                )
                processed_customers += 1
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Customer {processed_customers} of {total_customers} '{customer_identification}' created successfully ID: {customer_obj.id}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Customer {processed_customers} of {total_customers} '{customer_identification}' updated successfully ID: {customer_obj.id}"
                        )
                    )
            self.stdout.write(self.style.WARNING("Customer imported successfully"))

        except Exception as e:
            raise CommandError(f"Error importing customer: {e}")
