from artd_partner.models import Partner
from django.db import models
from django.utils.translation import gettext_lazy as _

from artd_siigo.models.base_models import BaseModel
from artd_customer.models import TaxSegment


class PartnerSiigoConfiguration(BaseModel):
    """Model definition for Partner Siigo Configuration."""

    partner = models.OneToOneField(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="+",
        unique=True,
    )
    import_customers_from_siigo = models.BooleanField(
        verbose_name=_("Sync Customers"),
        default=False,
    )
    import_products_from_siigo = models.BooleanField(
        verbose_name=_("Sync Products"),
        default=False,
    )
    export_customers_to_siigo = models.BooleanField(
        verbose_name=_("Export Customers"),
        default=False,
    )
    export_products_to_siigo = models.BooleanField(
        verbose_name=_("Export Products"),
        default=False,
    )
    export_invoices_to_siigo = models.BooleanField(
        verbose_name=_("Export Invoices"),
        default=False,
    )

    class Meta:
        """Meta definition for Partner Siigo Configuration."""

        verbose_name = _("Partner Siigo Configuration")
        verbose_name_plural = _("Partner Siigo Configurations")

    def __str__(self):
        """Unicode representation of Partner Siigo Configuration."""
        return f"{self.partner.name}"


class SiigoConfig(BaseModel):
    """Model definition for Siigo Config."""

    partner = models.OneToOneField(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="+",
    )
    tax_segment = models.ForeignKey(
        TaxSegment,
        verbose_name=_("Tax Segment"),
        on_delete=models.CASCADE,
        related_name="+",
    )
    address = models.JSONField(
        verbose_name=_("Address"),
        default=dict,
    )
    phones = models.JSONField(
        verbose_name=_("Phones"),
        default=list,
    )
    contacts = models.JSONField(
        verbose_name=_("Contacts"),
        default=list,
    )

    class Meta:
        """Meta definition for Siigo Config."""

        verbose_name = _("Siigo Config")
        verbose_name_plural = _("Siigo Configs")

    def __str__(self):
        """Unicode representation of Siigo Config."""
        return f"{self.partner.name}"


class SiigoTaxResponsibilitiesBySegment(BaseModel):
    """Model definition for Siigo Tax Responsibilities By Segment."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="siigo_tax_responsibilities_by_segments",
    )
    tax_segment = models.ForeignKey(
        TaxSegment,
        verbose_name=_("Tax Segment"),
        on_delete=models.CASCADE,
        related_name="siigo_tax_responsibilities_by_segments",
    )
    code = models.CharField(
        verbose_name=_("Code"),
        max_length=255,
    )

    class Meta:
        """Meta definition for Siigo Tax Responsibilities By Segment."""

        verbose_name = _("Siigo Tax Responsibilities By Segment")
        verbose_name_plural = _("Siigo Tax Responsibilities By Segments")

    def __str__(self):
        """Unicode representation of Siigo Tax Responsibilities By Segment."""
        return self.code
