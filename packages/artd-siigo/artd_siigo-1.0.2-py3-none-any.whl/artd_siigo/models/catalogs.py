from artd_partner.models import Partner
from django.db import models
from django.utils.translation import gettext_lazy as _

from artd_siigo.models.base_models import BaseModel


class SiigoAccountGroup(BaseModel):
    """Model definition for Account Group."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the account group"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the account group"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the account group"),
        max_length=250,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the account group"),
        default=True,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the account group"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for Account Group."""

        verbose_name = _("Siigo Catalog Account Group")
        verbose_name_plural = _("Siigo Catalog Account Groups")

    def __str__(self):
        """Unicode representation of Account Group."""
        return f"{self.name} - {self.partner.name}"


class SiigoTax(BaseModel):
    """Model definition for SiigoTax."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the tax"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the tax"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the tax"),
        max_length=250,
    )
    type = models.CharField(
        _("Type"),
        help_text=_("Type of the tax"),
        max_length=250,
    )
    percentage = models.FloatField(
        _("Percentage"),
        help_text=_("Percentage of the tax"),
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the tax"),
        default=True,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the tax"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for SiigoTax."""

        verbose_name = _("Siigo Catalog Tax")
        verbose_name_plural = _("Siigo Catalog Taxes")

    def __str__(self):
        """Unicode representation of SiigoTax."""
        return f"{self.name} - {self.partner.name}"


class SiigoPriceList(BaseModel):
    """Model definition for Price List."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the price list"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the price list"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the price list"),
        max_length=250,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the price list"),
        default=True,
    )
    position = models.IntegerField(
        _("Position"),
        help_text=_("Position of the price list"),
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the price list"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for Price List."""

        verbose_name = _("Siigo Catalog Price List")
        verbose_name_plural = _("Siigo Catalog Price Lists")

    def __str__(self):
        """Unicode representation of Price List."""
        return f"{self.name} - {self.partner.name}"


class SiigoWarehouse(BaseModel):
    """Model definition for Warehouse."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the warehouse"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the warehouse"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the warehouse"),
        max_length=250,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the warehouse"),
        default=True,
    )
    has_movements = models.BooleanField(
        _("Has Movements"),
        help_text=_("Whether the warehouse has movements or not"),
        default=False,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the warehouse"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for Warehouse."""

        verbose_name = _("Siigo Catalog Warehouse")
        verbose_name_plural = _("Siigo Catalog Warehouses")

    def __str__(self):
        """Unicode representation of Warehouse."""
        return f"{self.name} - {self.partner.name}"


class SiigoUser(BaseModel):
    """Model definition for Siigo User."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the user"),
    )
    username = models.CharField(
        _("Username"),
        help_text=_("Username of the user"),
        max_length=250,
    )
    first_name = models.CharField(
        _("First Name"),
        help_text=_("First name of the user"),
        max_length=250,
    )
    last_name = models.CharField(
        _("Last Name"),
        help_text=_("Last name of the user"),
        max_length=250,
    )
    email = models.EmailField(
        _("Email"),
        help_text=_("Email of the user"),
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the user"),
        default=True,
    )
    identification = models.CharField(
        _("Identification"),
        help_text=_("Identification of the user"),
        max_length=250,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the user"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for Siigo User."""

        verbose_name = _("Siigo Catalog User")
        verbose_name_plural = _("Siigo Catalog Users")

    def __str__(self):
        """Unicode representation of Siigo User."""
        return f"{self.username} - {self.partner.name}"


class SiigoDocumentType(BaseModel):
    """Model definition for Siigo Document Type."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the document type"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the document type"),
        max_length=250,
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code of the document type"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the document type"),
        max_length=250,
    )
    description = models.CharField(
        _("Description"),
        help_text=_("Description of the document type"),
        max_length=250,
    )
    type = models.CharField(
        _("Type"),
        help_text=_("Type of the document type"),
        max_length=250,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the document type"),
        default=True,
    )
    seller_by_item = models.BooleanField(
        _("Seller By Item"),
        help_text=_("Whether the document type is seller by item or not"),
        default=False,
    )
    cost_center = models.BooleanField(
        _("Cost Center"),
        help_text=_("Whether the document type has a cost center or not"),
        default=False,
    )
    cost_center_mandatory = models.BooleanField(
        _("Cost Center Mandatory"),
        help_text=_("Whether the cost center is mandatory or not"),
        default=False,
    )
    automatic_number = models.BooleanField(
        _("Automatic Number"),
        help_text=_("Whether the document type has an automatic number or not"),
        default=False,
    )
    consecutive = models.IntegerField(
        _("Consecutive"),
        help_text=_("Consecutive of the document type"),
    )
    discount_type = models.CharField(
        _("Discount Type"),
        help_text=_("Discount type of the document type"),
        max_length=250,
    )
    decimals = models.BooleanField(
        _("Decimals"),
        help_text=_("Whether the document type has decimals or not"),
        default=False,
    )
    advance_payment = models.BooleanField(
        _("Advance Payment"),
        help_text=_("Whether the document type has advance payment or not"),
        default=False,
    )
    reteiva = models.BooleanField(
        _("Rete IVA"),
        help_text=_("Whether the document type has rete IVA or not"),
        default=False,
    )
    reteica = models.BooleanField(
        _("Rete ICA"),
        help_text=_("Whether the document type has rete ICA or not"),
        default=False,
    )
    self_withholding = models.BooleanField(
        _("Self Withholding"),
        help_text=_("Whether the document type has self withholding or not"),
        default=False,
    )
    self_withholding_limit = models.FloatField(
        _("Self Withholding Limit"),
        help_text=_("Self withholding limit of the document type"),
    )
    electronic_type = models.CharField(
        _("Electronic Type"),
        help_text=_("Electronic type of the document type"),
        max_length=250,
    )
    cargo_transportation = models.BooleanField(
        _("Cargo Transportation"),
        help_text=_("Whether the document type has cargo transportation or not"),
        default=False,
    )
    healthcare_company = models.BooleanField(
        _("Healthcare Company"),
        help_text=_("Whether the document type has a healthcare company or not"),
        default=False,
    )
    customer_by_item = models.BooleanField(
        _("Customer By Item"),
        help_text=_("Whether the document type is customer by item or not"),
        default=False,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the document type"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for Siigo Document Type."""

        verbose_name = _("Siigo Catalog Document Type")
        verbose_name_plural = _("Siigo Catalog Document Types")

    def __str__(self):
        """Unicode representation of Siigo Document Type."""
        return f"{self.name} - {self.partner.name}"


class SiigoPaymentType(BaseModel):
    """Model definition for Siigo Payment Type."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the payment type"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the payment type"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the payment type"),
        max_length=250,
    )
    type = models.CharField(
        _("Type"),
        help_text=_("Type of the payment type"),
        max_length=250,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the payment type"),
        default=True,
    )
    due_date = models.BooleanField(
        _("Due Date"),
        help_text=_("Whether the payment type has a due date or not"),
        default=False,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the payment type"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for Siigo Payment Type."""

        verbose_name = _("Siigo Catalog Payment Type")
        verbose_name_plural = _("Siigo Catalog Payment Types")

    def __str__(self):
        """Unicode representation of Siigo Payment Type."""
        return f"{self.name} - {self.partner.name}"


class SiigoCostCenter(BaseModel):
    """Model definition for Siigo Cost Center."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the cost center"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the cost center"),
        max_length=250,
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code of the cost center"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the cost center"),
        max_length=250,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the cost center"),
        default=True,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the cost center"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for SiigoCost Center."""

        verbose_name = _("Siigo Catalog Cost Center")
        verbose_name_plural = _("Siigo Catalog Cost Centers")

    def __str__(self):
        """Unicode representation of Siigo Cost Center."""
        return f"{self.name} - {self.partner.name}"


class SiigoFixedAsset(BaseModel):
    """Model definition for Siigo Fixed Asset."""

    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the fixed asset"),
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the fixed asset"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the fixed asset"),
        max_length=250,
    )
    group = models.CharField(
        _("Group"),
        help_text=_("Group of the fixed asset"),
        max_length=250,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the fixed asset"),
        default=True,
    )
    json_data = models.JSONField(
        _("JSON Data"),
        help_text=_("JSON data for the fixed asset"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for Siigo Fixed Asset."""

        verbose_name = _("Siigo Catalog Fixed Asset")
        verbose_name_plural = _("Siigo Catalog Fixed Assets")

    def __str__(self):
        """Unicode representation of Siigo Fixed Asset."""
        return f"{self.name} - {self.partner.name}"
