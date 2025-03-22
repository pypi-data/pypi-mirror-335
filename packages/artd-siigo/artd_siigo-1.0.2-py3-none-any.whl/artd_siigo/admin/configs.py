from django.contrib import admin
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget

from artd_siigo.models import (
    SiigoConfig,
    SiigoTaxResponsibilitiesBySegment,
    PartnerSiigoConfiguration,
)


@admin.register(SiigoConfig)
class SiigoConfigAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }
    list_display = (
        "partner",
        "status",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            _("Siigo"),
            {
                "fields": (
                    "partner",
                    "tax_segment",
                )
            },
        ),
        (
            _("Address"),
            {"fields": ("address",)},
        ),
        (
            _("Phones"),
            {"fields": ("phones",)},
        ),
        (
            _("Timestamp"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(SiigoTaxResponsibilitiesBySegment)
class SiigoTaxResponsibilitiesBySegmentAdmin(admin.ModelAdmin):
    list_display = (
        "partner",
        "tax_segment",
        "code",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            _("Siigo"),
            {
                "fields": (
                    "partner",
                    "tax_segment",
                    "code",
                )
            },
        ),
        (_("Status"), {"fields": ("status",)}),
        (
            _("Timestamp"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(PartnerSiigoConfiguration)
class PartnerSiigoConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "partner",
        "import_customers_from_siigo",
        "import_products_from_siigo",
        "export_customers_to_siigo",
        "export_products_to_siigo",
        "export_invoices_to_siigo",
        "status",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            _("Siigo"),
            {"fields": ("partner",)},
        ),
        (
            _("Sync Import"),
            {
                "fields": (
                    "import_customers_from_siigo",
                    "import_products_from_siigo",
                )
            },
        ),
        (
            _("Sync Export"),
            {
                "fields": (
                    "export_customers_to_siigo",
                    "export_products_to_siigo",
                    "export_invoices_to_siigo",
                )
            },
        ),
        (
            _("Status"),
            {"fields": ("status",)},
        ),
        (
            _("Timestamp"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
