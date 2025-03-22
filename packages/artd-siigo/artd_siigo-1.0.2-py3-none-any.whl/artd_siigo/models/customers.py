from artd_partner.models import Partner
from django.db import models
from django.utils.translation import gettext_lazy as _

from artd_siigo.models.base_models import BaseModel


class SiigoCustomerType(BaseModel):
    """Model definition for Siigo Customer Type."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="siigo_customer_types",
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the customer type"),
        max_length=250,
    )

    class Meta:
        """Meta definition for Siigo Customer Type."""

        verbose_name = _("Siigo Customer Type")
        verbose_name_plural = _("Siigo Customer Types")

    def __str__(self):
        """Unicode representation of Siigo Customer Type."""
        return f"{self.name} - {self.partner.name}"


class SiigoCustomerPersonType(BaseModel):
    """Model definition for Siigo Customer Person Type."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="siigo_customer_person_types",
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the customer person type"),
        max_length=250,
    )

    class Meta:
        """Meta definition for Siigo Customer Person Type."""

        verbose_name = _("Siigo Customer Person Type")
        verbose_name_plural = _("Siigo Customer Person Types")

    def __str__(self):
        """Unicode representation of Siigo Customer Person Type."""
        return f"{self.name} - {self.partner.name}"


class SiigoCustomerDocumentType(BaseModel):
    """Model definition for Siigo Customer Document Type."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="siigo_customer_document_types",
    )
    code = models.CharField(
        _("Code"),
        help_text=_("Code of the customer document type"),
        max_length=250,
    )
    name = models.CharField(
        _("Name"),
        help_text=_("Name of the customer document type"),
        max_length=250,
    )

    class Meta:
        """Meta definition for Siigo Customer Document Type."""

        verbose_name = _("Siigo Customer Document Type")
        verbose_name_plural = _("Siigo Customer Document Types")

    def __str__(self):
        """Unicode representation of Siigo Customer Document Type."""
        return f"{self.name} - {self.partner.name}"


class SiigoCustomer(BaseModel):
    """Model definition for Siigo Customer."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="siigo_customers",
    )
    siigo_id = models.CharField(
        _("Siigo ID"),
        help_text=_("Siigo ID for the customer"),
        max_length=250,
    )
    siigo_customer_type = models.ForeignKey(
        SiigoCustomerType,
        verbose_name=_("Siigo Customer Type"),
        on_delete=models.CASCADE,
        related_name="siigo_customers",
        blank=True,
        null=True,
    )
    siigo_customer_person_type = models.ForeignKey(
        SiigoCustomerPersonType,
        verbose_name=_("Siigo Customer Person Type"),
        on_delete=models.CASCADE,
        related_name="siigo_customers",
        blank=True,
        null=True,
    )
    siigo_customer_document_type = models.ForeignKey(
        SiigoCustomerDocumentType,
        verbose_name=_("Siigo Customer Document Type"),
        on_delete=models.CASCADE,
        related_name="siigo_customers",
        blank=True,
        null=True,
    )
    identification = models.CharField(
        _("Identification"),
        help_text=_("Identification of the customer"),
        max_length=25,
        null=True,
        blank=True,
    )
    check_digit = models.CharField(
        _("Check Digit"),
        help_text=_("Check digit of the customer"),
        max_length=10,
        null=True,
        blank=True,
    )
    name = models.JSONField(
        _("Name"),
        help_text=_("Name of the customer"),
        default=list,
    )
    commercial_name = models.CharField(
        _("Commercial Name"),
        help_text=_("Commercial name of the customer"),
        max_length=250,
        null=True,
        blank=True,
    )
    branch_office = models.PositiveIntegerField(
        _("Branch Office"),
        help_text=_("Branch office of the customer"),
        blank=True,
        null=True,
    )
    active = models.BooleanField(
        _("Active"),
        help_text=_("Active status of the customer"),
        default=True,
    )
    vat_responsible = models.BooleanField(
        _("VAT Responsible"),
        help_text=_("VAT responsible status of the customer"),
        default=True,
    )
    fiscal_responsibilities = models.JSONField(
        _("Fiscal Responsibilities"),
        help_text=_("Fiscal responsibilities of the customer"),
        default=list,
    )
    address = models.JSONField(
        _("Address"),
        help_text=_("Address of the customer"),
        default=dict,
    )
    phones = models.JSONField(
        _("Phones"),
        help_text=_("Phones of the customer"),
        default=list,
    )
    contacts = models.JSONField(
        _("Contacts"),
        help_text=_("Contacts of the customer"),
        default=list,
    )
    comments = models.TextField(
        _("Comments"),
        help_text=_("Comments of the customer"),
        blank=True,
        null=True,
    )
    related_users = models.JSONField(
        _("Related Users"),
        help_text=_("Related users of the customer"),
        default=list,
    )
    metadata = models.JSONField(
        _("Metadata"),
        help_text=_("Metadata of the customer"),
        default=dict,
    )
    source = models.CharField(
        _("Source"),
        help_text=_("Source of the customer"),
        max_length=250,
        default="SIIGO",
    )
    synchronized = models.BooleanField(
        _("Synchronized"),
        help_text=_("Synchronized status of the customer"),
        default=False,
    )
    customer = models.ForeignKey(
        "artd_customer.Customer",
        verbose_name=_("Customer"),
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Siigo Customer."""

        verbose_name = _("Siigo Customer")
        verbose_name_plural = _("Siigo Customers")

    def __str__(self):
        """Unicode representation of Siigo Customer."""
        return f"{self.identification} - {self.partner.name}"
