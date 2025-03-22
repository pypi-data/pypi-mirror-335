from artd_partner.models import Partner
from django.db import models
from django.utils.translation import gettext_lazy as _

from artd_siigo.models.base_models import BaseModel
from artd_location.models import Country, Region, City
from artd_customer.models import TaxSegment
from artd_customer.models import CustomerType, CustomerDocumentType, CustomerPersonType
from artd_product.models import Tax, PRODUCT_TYPE
from artd_siigo.models import SiigoTax, SiigoProductType, SiigoUser


class CountryMapping(BaseModel):
    """Model definition for Country Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="country_mappings",
    )
    country = models.ForeignKey(
        Country,
        verbose_name=_("Country"),
        on_delete=models.CASCADE,
    )
    country_code = models.CharField(
        _("Country Code"),
        help_text=_("Country Code"),
        max_length=2,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Country Mapping."""

        verbose_name = _("Mapping Country")
        verbose_name_plural = _("Mapping Countries")
        unique_together = ("partner", "country")

    def __str__(self):
        """Unicode representation of Country Mapping."""
        return self.country_code


class RegionMapping(BaseModel):
    """Model definition for Region Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="region_mappings",
    )
    region = models.ForeignKey(
        Region,
        verbose_name=_("Region"),
        on_delete=models.CASCADE,
    )
    state_code = models.CharField(
        _("State Code"),
        help_text=_("State Code"),
        max_length=2,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Region Mapping."""

        verbose_name = _("Mappin Region")
        verbose_name_plural = _("Mapping Regions")
        unique_together = ("partner", "region")

    def __str__(self):
        """Unicode representation of Region Mapping."""
        return self.state_code


class CityMapping(BaseModel):
    """Model definition for City Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="city_mappings",
    )
    city = models.ForeignKey(
        City,
        verbose_name=_("City"),
        on_delete=models.CASCADE,
    )
    city_code = models.CharField(
        _("City Code"),
        help_text=_("City Code"),
        max_length=2,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for City Mapping."""

        verbose_name = _("Mapping City")
        verbose_name_plural = _("Mappings Cities")
        unique_together = ("partner", "city")

    def __str__(self):
        """Unicode representation of City Mapping."""
        return self.city_code


class FiscalResponsibilitiesMapping(BaseModel):
    """Model definition for Fiscal Responsibilities Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="fiscal_responsibilities_mappings",
    )
    tax_segment = models.ForeignKey(
        TaxSegment,
        verbose_name=_("Tax Segment"),
        on_delete=models.CASCADE,
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code"),
        max_length=100,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Fiscal Responsibilities Mapping."""

        verbose_name = _("Mapping Fiscal Responsibilities Mapping")
        verbose_name_plural = _("Mapping Fiscal Responsibilities Mappings")
        unique_together = ("partner", "tax_segment")

    def __str__(self):
        """Unicode representation of Fiscal Responsibilities Mapping."""
        return self.code


class CustomerTypeMapping(BaseModel):
    """Model definition for Customer Type Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="customer_type_mappings",
    )
    customer_type = models.ForeignKey(
        CustomerType,
        verbose_name=_("Customer Type"),
        on_delete=models.CASCADE,
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code"),
        max_length=100,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Customer Type Mapping."""

        verbose_name = _("Mapping Customer Typ")
        verbose_name_plural = _("Mapping Customer Types")
        unique_together = ("partner", "customer_type")

    def __str__(self):
        """Unicode representation of Customer Type Mapping."""
        return self.code


class CustomerDocumentTypeMapping(BaseModel):
    """Model definition for Customer Document Type Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="customer_document_type_mappings",
    )
    customer_document_type = models.ForeignKey(
        CustomerDocumentType,
        verbose_name=_("Customer Document Type"),
        on_delete=models.CASCADE,
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code"),
        max_length=100,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Customer Document Type Mapping."""

        verbose_name = _("Mapping Customer Document Type")
        verbose_name_plural = _("Mapping Customer Document Type")
        unique_together = ("partner", "customer_document_type")

    def __str__(self):
        """Unicode representation of Customer Document Type Mapping."""
        return self.code


class CustomerPersonTypeMapping(BaseModel):
    """Model definition for Customer Person Type Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="customer_person_type_mappings",
    )
    customer_person_type = models.ForeignKey(
        CustomerPersonType,
        verbose_name=_("Customer Person Type"),
        on_delete=models.CASCADE,
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code"),
        max_length=100,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Customer Person Type Mapping."""

        verbose_name = _("Mapping Customer Person Type")
        verbose_name_plural = _("Mapping Customer Person Types")
        unique_together = ("partner", "customer_person_type")

    def __str__(self):
        """Unicode representation of Customer Person Type Mapping."""
        return self.code


class TaxMapping(BaseModel):
    """Model definition for Tax Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="tax_mappings",
    )
    siigo_tax = models.ForeignKey(
        SiigoTax,
        verbose_name=_("Siigo Tax"),
        on_delete=models.CASCADE,
    )
    tax = models.ForeignKey(
        Tax,
        verbose_name=_("Tax"),
        on_delete=models.CASCADE,
    )

    class Meta:
        """Meta definition for Tax Mapping."""

        verbose_name = _("Mapping Tax")
        verbose_name_plural = _("Mapping Taxes")
        unique_together = ("partner", "siigo_tax", "tax")

    def __str__(self):
        """Unicode representation of Tax Mapping."""
        return f"{self.partner.name} - {self.siigo_tax.name} - {self.tax.name}"


class ProductTypeMapping(BaseModel):
    """Model definition for Product Type Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="product_type_mappings",
    )
    siigo_product_type = models.ForeignKey(
        SiigoProductType,
        verbose_name=_("Siigo Product Type"),
        on_delete=models.CASCADE,
    )
    product_type = models.CharField(
        _("Product Type"),
        help_text=_("Product Type"),
        max_length=100,
        choices=PRODUCT_TYPE,
    )

    class Meta:
        """Meta definition for Product Type Mapping."""

        verbose_name = _("Mapping Product Type")
        verbose_name_plural = _("Mapping Product Types")
        unique_together = ("partner", "siigo_product_type", "product_type")

    def __str__(self):
        """Unicode representation of Product Type Mapping."""
        return f"{self.partner.name} - {self.siigo_product_type.code} - {self.product_type}"


class UserMapping(BaseModel):
    """Model definition for User Mapping."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="user_mappings",
    )
    siigo_user = models.ForeignKey(
        SiigoUser,
        verbose_name=_("Siigo User"),
        on_delete=models.CASCADE,
    )

    class Meta:
        """Meta definition for User Mapping."""

        verbose_name = _("Mapping User")
        verbose_name_plural = _("Mapping Users")
        unique_together = ("partner", "siigo_user")

    def __str__(self):
        """Unicode representation of User Mapping."""
        return f"{self.partner.name} - {self.siigo_user.username}"
