from artd_partner.models import Partner
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from artd_siigo.models.base_models import BaseModel


class SiigoCredential(BaseModel):
    """Model definition for Siigo Credential."""

    partner = models.OneToOneField(
        Partner,
        on_delete=models.CASCADE,
        verbose_name=_("Partner"),
        help_text=_("Partner associated with the Siigo credential"),
    )
    siigo_partner_id = models.CharField(
        _("Partner ID"),
        help_text=_("Partner ID for Siigo"),
        max_length=250,
    )
    api_url = models.CharField(
        _("API URL"),
        help_text=_("API URL for Siigo"),
        max_length=250,
    )
    sandbox_username = models.CharField(
        _("Sandbox Username"),
        help_text=_("Sandbox username for Siigo"),
        max_length=150,
    )
    sandbox_access_key = models.CharField(
        _("Sand Box Access Key"),
        help_text=_("Sand Box Access Key for Siigo"),
        max_length=150,
    )
    production_username = models.CharField(
        _("Production Username"),
        help_text=_("Production username for Siigo"),
        max_length=150,
        null=True,
        blank=True,
    )  # noqa
    production_access_key = models.CharField(
        _("Production Access Key"),
        help_text=_("Production Access Key for Siigo"),
        max_length=150,
        null=True,
        blank=True,
    )  # noqa
    is_in_sandbox = models.BooleanField(
        _("Is in sandbox"),
        help_text=_("Is in sandbox"),
        default=True,
    )
    siigo_credential_data = models.JSONField(
        _("Siigo Credential Data"),
        help_text=_("Siigo Credential Data"),
        null=True,
        blank=True,
        default=dict,
    )

    class Meta:
        """Meta definition for Siigo Credential."""

        verbose_name = _("Siigo Credential")
        verbose_name_plural = _("Siigo Credentials")

    def __str__(self):
        """Unicode representation of Siigo Credential."""
        return str(self.partner.name)

    def clean(self):
        """
        Custom validation method to ensure production credentials are provided
        when not in sandbox mode.
        """
        super().clean()
        if not self.is_in_sandbox:
            if not self.production_username or not self.production_access_key:
                raise ValidationError(
                    _(
                        "Production username and access key are required when not in sandbox mode."  # noqa
                    )
                )

    def save(self, *args, **kwargs):
        """
        Override the save method to call full_clean before saving.
        This ensures our custom validation is always run.
        """
        self.full_clean()
        super().save(*args, **kwargs)
