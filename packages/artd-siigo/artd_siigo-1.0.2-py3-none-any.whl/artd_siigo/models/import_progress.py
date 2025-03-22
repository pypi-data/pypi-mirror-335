from artd_partner.models import Partner
from django.db import models
from django.utils.translation import gettext_lazy as _

from artd_siigo.models.base_models import BaseModel

siigo_entity = (
    ("customer", _("Customer")),
    ("supplier", _("Supplier")),
    ("product", _("Product")),
    ("category", _("Category")),
    ("account", _("Account")),
    ("tax", _("Tax")),
    ("unit", _("Unit")),
)


class EntityImportStatus(BaseModel):
    """Model definition for Entity Import Status."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        related_name="+",
    )
    siigo_entity = models.CharField(
        verbose_name=_("Siigo Entity"),
        max_length=255,
        choices=siigo_entity,
        unique=True,
    )
    last_imported_id = models.PositiveIntegerField(
        verbose_name=_("Last Imported ID"),
        default=0,
        blank=True,
        null=True,
    )
    page = models.PositiveIntegerField(
        verbose_name=_("Page"),
        default=1,
        blank=True,
        null=True,
    )
    page_size = models.PositiveIntegerField(
        verbose_name=_("Page Size"),
        default=25,
        blank=True,
        null=True,
    )
    url_complement = models.CharField(
        verbose_name=_("URL Complement"),
        max_length=255,
        default="",
        blank=True,
        null=True,
    )
    next_url = models.CharField(
        verbose_name=_("Next URL"),
        max_length=255,
        default="",
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Entity Import Status."""

        verbose_name = _("Entity Import Status")
        verbose_name_plural = _("Entity Import Statuss")

    def __str__(self):
        """Unicode representation of Entity Import Status."""
        return f"{self.siigo_entity} - {self.partner.name}"
