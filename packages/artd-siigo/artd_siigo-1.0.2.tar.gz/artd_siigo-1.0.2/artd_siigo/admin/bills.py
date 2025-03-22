from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget

from artd_siigo.models import (
    BillType,
    BillConfig,
    SiigoInvoice,
)


@admin.register(BillType)
class BillTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "partner",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "partner",
        "status",
    )
    search_fields = (
        "name",
        "code",
        "partner__name",
    )


@admin.register(BillConfig)
class BillConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bill_type",
        "siigo_document_type",
        "generate_electronic_document",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "bill_type",
        "status",
    )
    search_fields = (
        "bill_type__name",
        "bill_type__code",
        "bill_type__partner__name",
    )


@admin.register(SiigoInvoice)
class SiigoInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "number",
        "name",
        "date",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "partner",
        "status",
    )
    search_fields = ("partner__name", "siigo_id", "name", "number")
    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }
