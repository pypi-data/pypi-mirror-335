from typing import Dict, List, Union
from artd_customer.models import Customer, CustomerAddress
from artd_siigo.models import (
    CustomerTypeMapping,
    CustomerDocumentTypeMapping,
    CustomerPersonTypeMapping,
    SiigoTaxResponsibilitiesBySegment,
    CountryMapping,
    RegionMapping,
    CityMapping,
    SiigoConfig,
    SiigoCustomer,
)
from artd_location.models import City, Region
from django.db.models.signals import post_save
from django.dispatch import receiver
from artd_siigo.utils.siigo_api_util import SiigoApiUtil
from artd_partner.models import Partner
from artd_siigo.utils.siigo_config_util import update_tax_segment
from artd_siigo.models import PartnerSiigoConfiguration


def get_customer_type(customer: Customer) -> str:
    """
    Retrieves the customer type name mapped to the given customer.

    Args:
        customer (Customer): The customer instance.

    Returns:
        str: The mapped customer type name, or 'Customer' as the default.
    """
    if customer.customer_type:
        customer_type_mapping = CustomerTypeMapping.objects.filter(
            customer_type=customer.customer_type,
            partner=customer.partner,
        ).last()
        if customer_type_mapping:
            return customer_type_mapping.customer_type.name
    return "Customer"


def get_customer_document_type(customer: Customer) -> str:
    """
    Retrieves the customer document type code mapped to the given customer.

    Args:
        customer (Customer): The customer instance.

    Returns:
        str: The mapped document type code, or '13' as the default.
    """
    if customer.document_type:
        customer_document_type_mapping = CustomerDocumentTypeMapping.objects.filter(
            customer_document_type=customer.document_type,
            partner=customer.partner,
        ).last()
        if customer_document_type_mapping:
            return customer_document_type_mapping.code
    return "13"


def get_customer_person_type(customer: Customer) -> str:
    """
    Retrieves the customer person type code mapped to the given customer.

    Args:
        customer (Customer): The customer instance.

    Returns:
        str: The mapped person type code, or 'Person' as the default.
    """
    if customer.customer_person_type:
        customer_person_type_mapping = CustomerPersonTypeMapping.objects.filter(
            customer_person_type=customer.customer_person_type,
            partner=customer.partner,
        ).last()
        if customer_person_type_mapping:
            return customer_person_type_mapping.customer_person_type.code
    return "Person"


def get_name_list(customer: Customer) -> List[str]:
    """
    Builds a list containing the first and last name of the customer,
    excluding any empty values.

    Args:
        customer (Customer): The customer instance.

    Returns:
        List[str]: A list containing the customer's first and last name.
    """
    name_list = [name for name in [customer.name, customer.last_name] if name]
    if len(name_list) == 0:
        name_list.append("--")
        name_list.append("--")
    elif len(name_list) == 1:
        name_list.append("--")
    return name_list


def get_fiscal_responsibilities(customer: Customer) -> List[str]:
    """
    Retrieves the fiscal responsibilities based on the customer's tax segment.

    Args:
        customer (Customer): The customer instance.

    Returns:
        List[str]: A list of fiscal responsibility codes or a default value.
    """
    tax_responsibilities_list = []
    if customer.tax_segment:
        tax_responsibilities = SiigoTaxResponsibilitiesBySegment.objects.filter(
            tax_segment=customer.tax_segment,
            partner=customer.partner,
        )
        for tax_responsibility in tax_responsibilities:
            if tax_responsibility.code:
                tax_responsibilities_list.append(
                    {
                        "code": tax_responsibility.code,
                    }
                )
        return tax_responsibilities_list
    return [
        {
            "code": "R-99-PN",
        },
    ]


def get_address(customer: Customer) -> Dict[str, Union[str, Dict[str, str]]]:
    """
    Retrieves the address details for the customer, either from the customer's
    address or from the Siigo configuration if no customer address is found.

    Args:
        customer (Customer): The customer instance.

    Returns:
        Dict[str, Union[str, Dict[str, str]]]: A dictionary containing the address and city codes.
    """
    if customer.customeraddress_set.exists():
        address_obj: CustomerAddress = customer.customeraddress_set.last()
        city: City = address_obj.city
        region: Region = city.region
        country = region.country

        country_code = "Co"
        state_code = "19"
        city_code = "19001"

        country_mapping = CountryMapping.objects.filter(
            country=country,
            partner=customer.partner,
        ).last()
        if country_mapping:
            country_code = country_mapping.country_code

        region_mapping = RegionMapping.objects.filter(
            region=region,
            partner=customer.partner,
        ).last()
        if region_mapping:
            state_code = region_mapping.state_code

        city_mapping = CityMapping.objects.filter(
            city=city,
            partner=customer.partner,
        ).last()
        if city_mapping:
            city_code = city_mapping.city_code

        return {
            "address": address_obj.address,
            "city": {
                "country_code": country_code,
                "state_code": state_code,
                "city_code": city_code,
            },
            "postal_code": city.code,
        }

    siigo_config = SiigoConfig.objects.filter(partner=customer.partner).last()
    if siigo_config and siigo_config.address:
        return siigo_config.address

    return {
        "address": "Cra. 18 #79A - 42",
        "city": {
            "country_code": "Co",
            "state_code": "19",
            "city_code": "19001",
        },
        "postal_code": "110911",
    }


def get_phones(customer: Customer) -> List[Dict[str, str]]:
    """
    Retrieves the customer's phone number(s) in a structured format.

    Args:
        customer (Customer): The customer instance.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing phone details.
    """
    phones = []
    if customer.phone:
        country_code = customer.city.region.country.phone_code
        phone_number = customer.phone.replace(f"+{country_code}", "")
        phones.append(
            {
                "indicative": country_code,
                "number": phone_number,
                "extension": "",
            }
        )
    return phones


@receiver(post_save, sender=Customer)
def create_customer(
    sender: Customer, instance: Customer, created: bool, **kwargs
) -> None:
    """
    Signal handler for creating or updating a customer in the external Siigo system.

    Args:
        sender (Customer): The model class that triggered the signal.
        instance (Customer): The actual instance being saved.
        created (bool): A boolean indicating if a new instance was created.
        **kwargs: Additional keyword arguments.
    """
    partner_siigo_configuration = PartnerSiigoConfiguration.objects.filter(
        partner=instance.partner
    ).last()
    if not partner_siigo_configuration:
        return

    if not partner_siigo_configuration.import_customers_from_siigo:
        return

    customer: Customer = instance
    source_dict = customer.source
    if source_dict:
        if len(source_dict) > 0:
            if "name" in source_dict:
                source = source_dict["name"]
                if source == "SIIGO":
                    return

    partner: Partner = customer.partner

    # Update tax segment for the customer
    update_tax_segment(partner=partner, customer=customer)

    # Initialize Siigo API utility
    siigo_api_util = SiigoApiUtil(partner=partner)
    # Prepare customer data for the API request
    address = get_address(customer)
    phones = get_phones(customer)
    customer_data = {
        "person_type": get_customer_person_type(customer),
        "id_type": get_customer_document_type(customer),
        "identification": customer.document,
        "name": get_name_list(customer),
        "active": True,
        "vat_responsible": customer.vat_responsible,
        "fiscal_responsibilities": get_fiscal_responsibilities(customer),
        "comments": "Created from integration",
    }
    if len(address) > 0:
        customer_data["address"] = address
    if len(phones) > 0:
        customer_data["phones"] = phones
    if customer.document_check_digit:
        customer_data["check_digit"] = str(customer.document_check_digit)

    if customer.trade_name:
        customer_data["commercial_name"] = customer.trade_name

    # Send data to the Siigo API to create the customer
    if not SiigoCustomer.objects.filter(customer=customer).exists():
        response = siigo_api_util.create_customer(customer_data)
        if response:
            if isinstance(response, dict):
                if "status_code" in response:
                    if response["status_code"] == "400":
                        print(f"Response error: {response}")
                    else:
                        status_code = int(response["status_code"])
                        if status_code >= 200 and status_code < 300:
                            create_siigo_customer(customer, response["response"]["id"])


def create_siigo_customer(
    customer: Customer,
    siigo_id: str,
):
    """
    Creates a new Siigo customer record.

    Args:
        customer (Customer): The customer instance.
    """
    SiigoCustomer.objects.create(
        partner=customer.partner,
        siigo_id=siigo_id,
        synchronized=True,
        customer=customer,
    )
