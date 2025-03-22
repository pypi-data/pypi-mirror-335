from django.contrib import admin
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget

from artd_siigo.models import (
    SiigoAccountGroup,
    SiigoTax,
    SiigoPriceList,
    SiigoWarehouse,
    SiigoUser,
    SiigoDocumentType,
    SiigoPaymentType,
    SiigoCostCenter,
    SiigoFixedAsset,
)


@admin.register(SiigoAccountGroup)
class SiigoAccountGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "name",
                    "active",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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


@admin.register(SiigoTax)
class TaxAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
        "type",
        "percentage",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "name",
        "type",
        "percentage",
        "active",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "name",
                    "type",
                    "percentage",
                    "active",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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


@admin.register(SiigoPriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "name",
        "active",
        "position",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "name",
                    "active",
                    "position",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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


@admin.register(SiigoWarehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "name",
                    "active",
                    "has_movements",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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


@admin.register(SiigoUser)
class SiigoUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "username",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "username",
        "first_name",
        "last_name",
        "email",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "username",
        "first_name",
        "last_name",
        "email",
        "identification",
        "active",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "identification",
                    "active",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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


@admin.register(SiigoDocumentType)
class SiigoDocumentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "code",
        "name",
        "description",
        "type",
        "active",
        "seller_by_item",
        "cost_center",
        "cost_center_mandatory",
        "automatic_number",
        "consecutive",
        "discount_type",
        "decimals",
        "advance_payment",
        "reteiva",
        "reteica",
        "self_withholding",
        "self_withholding_limit",
        "electronic_type",
        "cargo_transportation",
        "healthcare_company",
        "customer_by_item",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "code",
                    "name",
                    "description",
                    "type",
                    "active",
                    "seller_by_item",
                    "cost_center",
                    "cost_center_mandatory",
                    "automatic_number",
                    "consecutive",
                    "discount_type",
                    "decimals",
                    "advance_payment",
                    "reteiva",
                    "reteica",
                    "self_withholding",
                    "self_withholding_limit",
                    "electronic_type",
                    "cargo_transportation",
                    "healthcare_company",
                    "customer_by_item",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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


@admin.register(SiigoPaymentType)
class SiigoPaymentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "name",
        "type",
        "active",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "name",
                    "type",
                    "active",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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


@admin.register(SiigoCostCenter)
class SiigoCostCenterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
        "code",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "code",
        "name",
        "active",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "code",
                    "name",
                    "active",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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


@admin.register(SiigoFixedAsset)
class SiigoFixedAssetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "name",
        "active",
        "created_at",
        "updated_at",
        "status",
    )
    list_filter = (
        "partner__name",
        "active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
        "group",
        "siigo_id",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "name",
        "group",
        "active",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "name",
                    "group",
                    "active",
                    "json_data",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("status",),
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
