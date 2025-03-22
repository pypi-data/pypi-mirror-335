from django.core.management.base import BaseCommand, CommandError
from artd_siigo.models import SiigoUser
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner


class Command(BaseCommand):
    help = "Imports users from Siigo for a specified partner"

    def add_arguments(self, parser):
        # Define 'partner_slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose users need to be imported",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Importing users from Siigo..."))
        partner_slug = options["partner_slug"]
        # Validate partner existence
        try:
            partner = Partner.objects.get(
                partner_slug=partner_slug
            )  # Assuming the slug field is 'slug'
        except Partner.DoesNotExist:
            raise CommandError(f"Partner with slug '{partner_slug}' does not exist")

        try:
            siigo_api = SiigoApiUtil(partner)
            users = (
                siigo_api.get_users()
            )  # Make sure this method exists in your SiigoApiUtil

            for user in users:
                SiigoUser.objects.update_or_create(
                    identification=user[
                        "identification"
                    ],  # You may need to adjust the field name if it differs
                    partner=partner,
                    defaults={
                        "username": user["username"],
                        "first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "email": user["email"],
                        "active": user["active"],
                        "json_data": user,  # Assuming you want to store the entire user data as json
                    },
                )

            self.stdout.write(self.style.SUCCESS("Users imported successfully"))

        except Exception as e:
            raise CommandError(f"Error importing users: {e}")
