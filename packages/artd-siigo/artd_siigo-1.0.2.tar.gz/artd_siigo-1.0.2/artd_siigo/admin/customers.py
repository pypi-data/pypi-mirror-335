from django.contrib import admin
from django.db.models import JSONField
from artd_siigo.models import (
    SiigoCustomerType,
    SiigoCustomerPersonType,
    SiigoCustomerDocumentType,
    SiigoCustomer,
)
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget


@admin.register(SiigoCustomerType)
class SiigoCustomerTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "name",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "partner",
        "name",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(SiigoCustomerPersonType)
class SiigoCustomerPersonTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "name",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "partner",
        "name",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(SiigoCustomerDocumentType)
class SiigoCustomerDocumentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "code",
        "name",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "code",
        "name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "partner",
        "code",
        "name",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(SiigoCustomer)
class SiigoCustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "identification",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "identification",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "partner",
        "siigo_id",
        "identification",
        "check_digit",
        "commercial_name",
        "branch_office",
        "active",
        "vat_responsible",
        "comments",
        "status",
        "created_at",
        "updated_at",
        "siigo_customer_type",
        "siigo_customer_person_type",
        "siigo_customer_document_type",
        "customer",
        "source",
        "synchronized",
        "metadata",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "partner",
                    "siigo_id",
                    "identification",
                    "siigo_customer_type",
                    "siigo_customer_person_type",
                    "siigo_customer_document_type",
                    "check_digit",
                    "name",
                    "commercial_name",
                    "branch_office",
                    "active",
                    "vat_responsible",
                    "comments",
                    "source",
                    "customer",
                )
            },
        ),
        (
            _("Contact Information"),
            {"fields": ("contacts",)},
        ),
        (
            _("Address Information"),
            {"fields": ("address",)},
        ),
        (
            _("Phone Information"),
            {"fields": ("phones",)},
        ),
        (
            _("Related user Information"),
            {"fields": ("related_users",)},
        ),
        (
            _("Fiscal responsibilities"),
            {"fields": ("fiscal_responsibilities",)},
        ),
        (
            _("Metadata"),
            {"fields": ("metadata",)},
        ),
        (
            _("Status"),
            {
                "fields": (
                    "status",
                    "synchronized",
                ),
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
