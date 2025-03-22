from artd_partner.models import Partner
from django.db import models
from django.utils.translation import gettext_lazy as _

from artd_siigo.models.base_models import BaseModel
from artd_siigo.models import SiigoAccountGroup, SiigoTax, SiigoWarehouse
from artd_product.models import Product


class SiigoProductUnit(BaseModel):
    """Model definition for Siigo Product Unit."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the product"),
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code of the product unit"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the product unit"),
        max_length=250,
    )

    class Meta:
        """Meta definition for Siigo Product Unit."""

        verbose_name = _("Siigo Product Unit")
        verbose_name_plural = _("Siigo Product Units")

    def __str__(self):
        """Unicode representation of Siigo Product Unit."""
        return f"{self.name} - {self.partner.name}"


class SiigoProductType(BaseModel):
    """Model definition for Siigo Product Type."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the product"),
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code of the product type"),
        max_length=250,
    )

    class Meta:
        """Meta definition for Siigo Product Type."""

        verbose_name = _("Siigo Product Type")
        verbose_name_plural = _("Siigo Product Types")

    def __str__(self):
        """Unicode representation of Siigo Product Type."""
        return f"{self.code} - {self.partner.name}"


class SiigoProduct(BaseModel):
    """Model definition for Siigo Product."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the product"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the product"),
        max_length=250,
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code of the product"),
        max_length=250,
        blank=True,
        null=True,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the product"),
        max_length=250,
        blank=True,
        null=True,
    )
    account_group = models.ForeignKey(
        SiigoAccountGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Account Group"),
        help_text=_("Account group for the product"),
        blank=True,
        null=True,
    )
    type = models.CharField(
        _("Type"),
        help_text=_("Type of the product"),
        max_length=250,
        blank=True,
        null=True,
    )
    stock_control = models.BooleanField(
        _("Stock Control"),
        help_text=_("Whether the product has stock control or not"),
        default=False,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Whether the product is active or not"),
        default=True,
    )
    tax_classification = models.CharField(
        _("Tax Classification"),
        help_text=_("Tax classification of the product"),
        max_length=250,
        blank=True,
        null=True,
    )
    tax_included = models.BooleanField(
        _("Tax Included"),
        help_text=_("Whether the product has tax included or not"),
        default=False,
    )
    tax_consumption_value = models.FloatField(
        _("Tax Consumption Value"),
        help_text=_("Tax consumption value of the product"),
        default=0,
    )
    taxes = models.ManyToManyField(
        SiigoTax,
        verbose_name=_("Taxes"),
        help_text=_("Taxes for the product"),
        blank=True,
        null=True,
    )
    unit = models.ForeignKey(
        SiigoProductUnit,
        on_delete=models.CASCADE,
        verbose_name=_("Unit"),
        help_text=_("Unit of the product"),
        blank=True,
        null=True,
    )
    unit_label = models.CharField(
        _("Unit Label"),
        help_text=_("Unit label of the product"),
        max_length=250,
        blank=True,
        null=True,
    )
    reference = models.CharField(
        _("Reference"),
        help_text=_("Reference of the product"),
        max_length=250,
        blank=True,
        null=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_("Description of the product"),
        blank=True,
        null=True,
    )
    additional_fields = models.JSONField(
        _("Additional Fields"),
        help_text=_("Additional fields for the product"),
        null=True,
        blank=True,
        default=dict,
    )
    available_quantity = models.FloatField(
        _("Available Quantity"),
        help_text=_("Available quantity of the product"),
        default=0,
        blank=True,
        null=True,
    )
    warehouses = models.ManyToManyField(
        SiigoWarehouse,
        verbose_name=_("Warehouses"),
        help_text=_("Warehouses for the product"),
        blank=True,
        null=True,
    )
    metadata = models.JSONField(
        _("Metadata"),
        help_text=_("Metadata for the product"),
        null=True,
        blank=True,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the product"),
        null=True,
        blank=True,
    )
    source = models.CharField(
        _("Source"),
        help_text=_("Source of the customer"),
        max_length=250,
        default="SIIGO",
        blank=True,
        null=True,
    )
    synchronized = models.BooleanField(
        _("Synchronized"),
        help_text=_("Synchronized status of the customer"),
        default=False,
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Siigo Product."""

        verbose_name = _("Siigo Product")
        verbose_name_plural = _("Siigo Products")

    def __str__(self):
        """Unicode representation of Siigo Product."""
        return f"{self.name} - {self.partner.name}"


class SiigoProductPriceList(BaseModel):
    """Model definition for Siigo Product Price List."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the product"),
    )
    position = models.PositiveIntegerField(
        _("Position"),
        help_text=_("Position of the product price list"),
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the product price list"),
        max_length=250,
    )
    value = models.FloatField(
        _("Value"),
        help_text=_("Value of the product price list"),
    )

    class Meta:
        """Meta definition for Siigo Product Price List."""

        verbose_name = _("Siigo Product Price List")
        verbose_name_plural = _("Siigo Product Price Lists")

    def __str__(self):
        """Unicode representation of Siigo Product Price List."""
        return f"{self.name} - {self.partner.name}"


class SiigoProductPrice(BaseModel):
    """Model definition for Siigo Product Price."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the product"),
    )
    product = models.ForeignKey(
        SiigoProduct,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        help_text=_("Product for the price"),
    )
    currency_code = models.CharField(
        _("Currency Code"),
        help_text=_("Currency code of the product price"),
        max_length=250,
    )
    price_lists = models.ManyToManyField(
        SiigoProductPriceList,
        verbose_name=_("Price Lists"),
        help_text=_("Price lists for the product"),
    )

    class Meta:
        """Meta definition for Siigo Product Price."""

        verbose_name = _("Siigo Product Price")
        verbose_name_plural = _("Siigo Product Prices")

    def __str__(self):
        """Unicode representation of Siigo Product Price."""
        return f"{self.id} - {self.partner.name}"


class SiigoProductProxy(BaseModel):
    """Proxy model for Siigo Product."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        help_text=_("Product for the proxy"),
    )
    siigo_account_group = models.ForeignKey(
        SiigoAccountGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Siigo Account Group"),
        help_text=_("Siigo account group for the product"),
    )

    class Meta:
        """Meta definition for Siigo Product Proxy."""

        verbose_name = _("Siigo Product Account Group")
        verbose_name_plural = _("Siigo Product Account Groups")

    def __str__(self):
        """Unicode representation of Siigo Product Proxy."""
        return f"{self.product.name} - {self.siigo_account_group.name}"
