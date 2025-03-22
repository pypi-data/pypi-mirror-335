from artd_partner.models import Partner
from artd_siigo.models import (
    SiigoAccountGroup,
    SiigoTax,
    SiigoWarehouse,
    SiigoProduct,
    SiigoProductUnit,
    SiigoProductPriceList,
    SiigoProductPrice,
    SiigoCustomerDocumentType,
    SiigoCustomerPersonType,
    SiigoCustomerType,
    SiigoCustomer,
    SiigoProductType,
)


class SiigoDbUtil:
    """
    Utility class for interacting with Siigo-related models in the database.
    """

    def __init__(self, partner: Partner) -> None:
        """
        Initialize the SiigoDbUtil with a Partner instance.

        Args:
            partner (Partner): The partner associated with the Siigo data.
        """
        self.__partner = partner

    def get_account_group(self, siigo_id: int) -> SiigoAccountGroup | None:
        """
        Retrieve the account group by its Siigo ID and partner.

        Args:
            siigo_id (int): The Siigo ID of the account group.

        Returns:
            SiigoAccountGroup | None: The account group instance if found, otherwise None.
        """
        try:
            account_group = SiigoAccountGroup.objects.get(
                siigo_id=siigo_id, partner=self.__partner
            )
            return account_group
        except SiigoAccountGroup.DoesNotExist:
            return None

    def get_tax(self, siigo_id: int) -> SiigoTax | None:
        """
        Retrieve the tax by its Siigo ID and partner.

        Args:
            siigo_id (int): The Siigo ID of the tax.

        Returns:
            SiigoTax | None: The tax instance if found, otherwise None.
        """
        try:
            tax = SiigoTax.objects.get(
                siigo_id=siigo_id,
                partner=self.__partner,
            )
            return tax
        except SiigoTax.DoesNotExist:
            return None

    def get_warehouse(self, siigo_id: int) -> SiigoWarehouse | None:
        """
        Retrieve the warehouse by its Siigo ID and partner.

        Args:
            siigo_id (int): The Siigo ID of the warehouse.

        Returns:
            SiigoWarehouse | None: The warehouse instance if found, otherwise None.
        """
        try:
            tax = SiigoWarehouse.objects.get(
                siigo_id=siigo_id,
                partner=self.__partner,
            )
            return tax
        except SiigoWarehouse.DoesNotExist:
            return None

    def get_siigo_tax(self, siigo_id: int) -> SiigoTax | None:
        """
        Retrieve the tax by its Siigo ID and partner.

        Args:
            siigo_id (int): The Siigo ID of the tax.

        Returns:
            SiigoTax | None: The tax instance if found, otherwise None.
        """
        try:
            tax = SiigoTax.objects.get(
                siigo_id=siigo_id,
                partner=self.__partner,
            )
            return tax
        except SiigoTax.DoesNotExist:
            return None

    def update_or_create_unit(
        self, unit_data: dict
    ) -> tuple[SiigoProductUnit | None, bool]:
        """
        Update or create a product unit based on the given unit data.

        Args:
            unit_data (dict): Dictionary containing the unit data.

        Returns:
            tuple[SiigoProductUnit | None, bool]: The unit instance and a boolean indicating if it was created.
        """
        try:
            defaults = unit_data.copy()
            del defaults["code"]
            unit, created = SiigoProductUnit.objects.update_or_create(
                code=unit_data.get("code"),
                partner=self.__partner,
                defaults=defaults,
            )
            return unit, created
        except Exception:
            return None, False

    def create_or_update_product(
        self, product_data: dict
    ) -> tuple[SiigoProduct | None, bool]:
        """
        Create or update a product based on the provided product data.

        Args:
            product_data (dict): Dictionary containing the product data.

        Returns:
            tuple[SiigoProduct | None, bool]: The product instance and a boolean indicating if it was created.
        """
        try:
            defaults = product_data.copy()
            del defaults["siigo_id"]
            product, created = SiigoProduct.objects.update_or_create(
                siigo_id=product_data.get("siigo_id"),
                partner=self.__partner,
                defaults=defaults,
            )
            return product, created
        except Exception as e:
            print(e)
            return None, False

    def get_or_update_prices(self, product: SiigoProduct, prices: dict) -> None:
        """
        Get or update the prices for a given product.

        Args:
            product (SiigoProduct): The product instance to update prices for.
            prices (dict): Dictionary containing price data.
        """
        for price in prices:
            currency_code = price["currency_code"]
            price_lists = price["price_list"]
            price, created = SiigoProductPrice.objects.get_or_create(
                partner=self.__partner,
                product=product,
                currency_code=currency_code,
            )
            price.price_lists.clear()
            for price_list in price_lists:
                price_list_position = price_list["position"]
                price_list_name = price_list["name"]
                price_list_value = price_list["value"]
                price_list_obj, _ = SiigoProductPriceList.objects.get_or_create(
                    partner=self.__partner,
                    position=price_list_position,
                    name=price_list_name,
                    value=price_list_value,
                )
                price.price_lists.add(price_list_obj)

    def get_customer_document_type(self, code: str) -> SiigoCustomerDocumentType | None:
        """
        Retrieve the customer document type by code.

        Args:
            code (str): The code of the customer document type.

        Returns:
            SiigoCustomerDocumentType | None: The document type instance if found, otherwise None.
        """
        try:
            document_type = SiigoCustomerDocumentType.objects.get(
                code=code,
                partner=self.__partner,
            )
            return document_type
        except SiigoCustomerDocumentType.DoesNotExist:
            return None

    def get_customer_person_type(self, name: str) -> SiigoCustomerPersonType | None:
        """
        Retrieve the customer person type by name.

        Args:
            name (str): The name of the customer person type.

        Returns:
            SiigoCustomerPersonType | None: The person type instance if found, otherwise None.
        """
        try:
            person_type = SiigoCustomerPersonType.objects.get(
                name__icontains=name,
                partner=self.__partner,
            )
            return person_type
        except SiigoCustomerPersonType.DoesNotExist:
            return None

    def get_customer_type(self, name: str) -> SiigoCustomerType | None:
        """
        Retrieve the customer type by name.

        Args:
            name (str): The name of the customer type.

        Returns:
            SiigoCustomerType | None: The customer type instance if found, otherwise None.
        """
        try:
            customer_type = SiigoCustomerType.objects.get(
                name=name,
                partner=self.__partner,
            )
            return customer_type
        except SiigoCustomerType.DoesNotExist:
            return None

    def create_or_update_customer(
        self, customer_data: dict
    ) -> tuple[SiigoCustomer | None, bool]:
        """
        Create or update a customer based on the provided customer data.

        Args:
            customer_data (dict): Dictionary containing the customer data.

        Returns:
            tuple[SiigoCustomer | None, bool]: The customer instance and a boolean indicating if it was created.
        """
        try:
            defaults = customer_data.copy()
            del defaults["siigo_id"]

            customer, created = SiigoCustomer.objects.update_or_create(
                siigo_id=customer_data.get("siigo_id"),
                partner=self.__partner,
                defaults=defaults,
            )
            return customer, created
        except Exception as e:
            print(f"SIIGO DB util 265: Error creating or updating customer: {e}")
            return None, False

    def get_siigo_customer_from_db(self, identification: str) -> SiigoCustomer | None:
        """
        Retrieve the Siigo customer from the database based on the customer's identification.

        Args:
            identification (str): The DNI of the customer.

        Returns:
            SiigoCustomer | None: The Siigo customer instance if found, otherwise None.
        """
        try:
            customer = SiigoCustomer.objects.get(
                partner=self.__partner,
                identification=identification,
            )
            return customer
        except SiigoCustomer.DoesNotExist:
            return None

    def create_or_get_product_type(self, code: str) -> SiigoProductType | None:
        """
        Create or update a product type based on the provided product type data.

        Args:
            product_type_data (dict): Dictionary containing the product type data.

        Returns:
            SiigoProductType | None: The product type instance, otherwise None.
        """
        try:
            if SiigoProductType.objects.filter(
                code=code,
                partner=self.__partner,
            ).exists():
                return SiigoProductType.objects.filter(
                    code=code,
                    partner=self.__partner,
                ).last()
            else:
                product_type = SiigoProductType.objects.create(
                    code=code,
                    partner=self.__partner,
                )
                return product_type
        except Exception:
            return None
