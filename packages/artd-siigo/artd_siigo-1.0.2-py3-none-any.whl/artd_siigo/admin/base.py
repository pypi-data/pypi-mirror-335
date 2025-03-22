from django.contrib import admin
from django.db.models import JSONField
from django.forms import ModelForm, PasswordInput
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget

from artd_siigo.models import SiigoCredential


class SiigoCredentialAdminForm(ModelForm):
    class Meta:
        model = SiigoCredential
        fields = "__all__"
        widgets = {
            "sandbox_access_key": PasswordInput(
                render_value=True,
            ),
            "production_access_key": PasswordInput(
                render_value=True,
            ),
        }


@admin.register(SiigoCredential)
class SiigoCredentialAdmin(admin.ModelAdmin):
    form = SiigoCredentialAdminForm
    list_display = (
        "partner",
        "siigo_partner_id",
        "is_in_sandbox",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_in_sandbox",
        "partner__name",
        "created_at",
        "updated_at",
    )
    search_fields = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_partner_id",
                    "is_in_sandbox",
                    "api_url",
                )
            },
        ),
        (
            _("Sandbox Credentials"),
            {
                "fields": (
                    "sandbox_username",
                    "sandbox_access_key",
                ),
            },
        ),
        (
            _("Production Credentials"),
            {
                "fields": (
                    "production_username",
                    "production_access_key",
                ),
            },
        ),
        (
            _("SIIGO Token Data"),
            {
                "fields": ("siigo_credential_data",),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ("partner",)
        return self.readonly_fields
