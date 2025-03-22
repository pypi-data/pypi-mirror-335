from django.core.management.base import BaseCommand, CommandError
from artd_siigo.models import SiigoCustomer
from artd_partner.models import Partner
import json


class Command(BaseCommand):
    help = "Extract unique fiscal responsibility codes from SiigoCustomer model and save to JSON file"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose account groups need to be imported",  # noqa
        )

    def handle(self, *args, **options):
        unique_fiscal_responsibilities = {}
        partner_slug = options["partner_slug"]
        # Validate partner existence
        try:
            partner = Partner.objects.get(partner_slug=partner_slug)
        except Partner.DoesNotExist:
            raise CommandError(
                f"Partner with slug '{partner_slug}' does not exist",
            )

        # Filter SiigoCustomer by partner
        for customer in SiigoCustomer.objects.filter(partner=partner):
            fiscal_responsibilities = customer.fiscal_responsibilities
            if isinstance(fiscal_responsibilities, list):
                for responsibility in fiscal_responsibilities:
                    code = responsibility.get("code")
                    name = responsibility.get("name")
                    if code and code not in unique_fiscal_responsibilities:
                        unique_fiscal_responsibilities[code] = name

        # Save to JSON file
        with open(
            "unique_fiscal_responsibilities.json", "w", encoding="utf-8"
        ) as json_file:
            json.dump(
                unique_fiscal_responsibilities, json_file, ensure_ascii=False, indent=4
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Unique Fiscal Responsibilities saved to unique_fiscal_responsibilities.json"
            )
        )
        for code, name in unique_fiscal_responsibilities.items():
            self.stdout.write(f"{code}: {name}")
