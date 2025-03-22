from artd_partner.models import Partner
from django.core.management.base import BaseCommand, CommandError

from artd_siigo.models import SiigoAccountGroup
from artd_siigo.utils.siigo_api_util import SiigoApiUtil


class Command(BaseCommand):
    help = "Imports account groups from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose account groups need to be imported",  # noqa
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Importing account groups from Siigo...",
            )
        )
        partner_slug = options["partner_slug"]
        # Validate partner existence
        try:
            partner = Partner.objects.get(partner_slug=partner_slug)
        except Partner.DoesNotExist:
            raise CommandError(
                f"Partner with slug '{partner_slug}' does not exist",
            )

        try:
            siigo_api = SiigoApiUtil(partner)
            groups = siigo_api.get_account_groups()

            for group in groups:
                SiigoAccountGroup.objects.update_or_create(
                    siigo_id=group["id"],
                    partner=partner,
                    defaults={
                        "name": group["name"],
                        "active": group["active"],
                        "json_data": group,
                    },
                )
            self.stdout.write(
                self.style.SUCCESS("Account groups imported successfully")
            )

        except Exception as e:
            raise CommandError(f"Error importing account groups: {e}")
