from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from artd_siigo.models import SiigoCustomer, CountryMapping, CityMapping
from artd_customer.models import Customer
from artd_location.models import Country, City
from artd_siigo.data.source import SOURCE
import traceback
from artd_siigo.models import PartnerSiigoConfiguration


@receiver(post_save, sender=SiigoCustomer)
def create_siigo_customer(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a Customer when a SiigoCustomer is saved.

    This function listens to the post_save signal of the SiigoCustomer model,
    and creates or updates a corresponding Customer in the system based on
    SiigoCustomer's data, including contacts and address mappings.

    Args:
        sender (Model): The model class that sent the signal (SiigoCustomer).
        instance (SiigoCustomer): The actual instance being saved.
        created (bool): Boolean; True if the object was created, False if updated.
        **kwargs: Additional keyword arguments.
    """
    try:
        partner_siigo_configuration = PartnerSiigoConfiguration.objects.filter(
            partner=instance.partner
        ).last()
        if not partner_siigo_configuration:
            return

        if not partner_siigo_configuration.import_customers_from_siigo:
            return

        siigo_customer: SiigoCustomer = instance
        if not siigo_customer.synchronized:
            partner = siigo_customer.partner
            # Default values for first_name, last_name, email, phone_number, country, and city
            first_name, last_name, email, phone_number = "", "", "", ""
            default_country_id, default_city_id = 45, 169
            artd_country = Country.objects.get(id=default_country_id)
            artd_city = City.objects.get(id=default_city_id)
            other_data = model_to_dict(siigo_customer)
            # Extract first contact information if available
            if siigo_customer.contacts:
                contact = siigo_customer.contacts[0]
                first_name = contact.get("first_name", "")
                last_name = contact.get("last_name", "")
                email = contact.get("email", "")
                phone_number = contact.get("phone", {}).get("number", "")

            if first_name == "":
                if len(other_data["name"]) > 0:
                    first_name = other_data["name"][0]

            # Handle address and city-country mappings
            if siigo_customer.address and siigo_customer.address.get("city"):
                city = siigo_customer.address["city"]

                # Get country mapping based on partner and country_code if available
                country_code = city.get("country_code")
                if country_code:
                    artd_country_mapping = CountryMapping.objects.filter(
                        partner=partner, country_code=country_code
                    ).last()
                    if artd_country_mapping:
                        artd_country = artd_country_mapping.country

                # Get city mapping based on partner and city_code if available
                city_code = city.get("city_code")
                if city_code:
                    artd_city_mapping = CityMapping.objects.filter(
                        partner=partner, city_code=city_code
                    ).last()
                    if artd_city_mapping:
                        artd_city = artd_city_mapping.city

            # Prepare customer data
            customer_data = {
                "name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": f"+{artd_country.phone_code}{phone_number}",
                "city": artd_city,
                "other_data": other_data,
            }
            customer_count = Customer.objects.filter(
                document=siigo_customer.identification, partner=siigo_customer.partner
            ).count()
            if customer_count > 0:
                customer_obj = Customer.objects.filter(
                    document=siigo_customer.identification,
                    partner=siigo_customer.partner,
                ).last()
                customer_data["source"] = customer_obj.source
            else:
                customer_data["source"] = SOURCE
            # Create or update the Customer instance
            customer, created = Customer.objects.update_or_create(
                document=siigo_customer.identification,
                partner=siigo_customer.partner,
                defaults=customer_data,
            )
            siigo_customer.synchronized = True
            siigo_customer.customer = customer
            siigo_customer.save()
        else:
            print("SIIGO customer signal: Customer already synchronized.")
    except Exception as e:
        print(f"Error: {e}")
        print("Tipo de error:", type(e).__name__)
        print("Linea del error:", traceback.extract_tb(e.__traceback__)[-1].lineno)
        print("Traceback completo:")
        print(traceback.format_exc())
        siigo_customer.synchronized = True
        siigo_customer.save()
