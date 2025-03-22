from django.contrib import admin
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget

from artd_siigo.models import (
    SiigoProductPriceList,
    SiigoProductPrice,
    SiigoProductUnit,
    SiigoProductType,
    SiigoProduct,
    SiigoProductProxy,
)


from artd_product.admin import ProductImageInline, Product
from django.db import models
from dal import autocomplete


@admin.register(SiigoProductPriceList)
class SiigoProductPriceListAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "position",
        "name",
        "value",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "position",
        "name",
        "value",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "partner",
        "position",
        "name",
        "value",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(SiigoProductPrice)
class SiigoProductPriceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "currency_code",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("partner__name",)
    search_fields = (
        "product__name",
        "price_list__name",
    )
    readonly_fields = (
        "partner",
        "product",
        "price_lists",
        "currency_code",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(SiigoProductUnit)
class SiigoProductUnitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "name",
        "code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "code",
    )
    readonly_fields = (
        "partner",
        "name",
        "code",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(SiigoProduct)
class SiigoProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_id",
        "code",
        "name",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "siigo_id",
        "code",
        "name",
    )
    readonly_fields = (
        "partner",
        "siigo_id",
        "code",
        "name",
        "account_group",
        "type",
        "stock_control",
        "active",
        "tax_classification",
        "tax_included",
        "tax_consumption_value",
        "taxes",
        "unit",
        "unit_label",
        "reference",
        "description",
        "available_quantity",
        "warehouses",
        "source",
        "synchronized",
        "product",
        "status",
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
                )
            },
        ),
        (
            _("Product Details"),
            {
                "fields": (
                    "account_group",
                    "type",
                    "active",
                    "unit",
                    "unit_label",
                    "reference",
                    "description",
                    "source",
                    "product",
                )
            },
        ),
        (
            _("Taxes"),
            {
                "fields": (
                    "tax_classification",
                    "tax_included",
                    "tax_consumption_value",
                    "taxes",
                ),
            },
        ),
        (
            _("Stock"),
            {
                "fields": (
                    "stock_control",
                    "available_quantity",
                    "warehouses",
                ),
            },
        ),
        (
            _("JSON Data"),
            {
                "fields": ("json_data",),
            },
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


@admin.register(SiigoProductType)
class SiigoProductTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "code",
    )
    readonly_fields = (
        "partner",
        "code",
        "status",
        "created_at",
        "updated_at",
    )


# Desregistrar el modelo Product si ya está registrado
admin.site.unregister(Product)


@admin.register(Product)
class CustomProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "grouped_product_name",
        "sku",
        "grouped_product_sku",
        "brand",
        "status",
        # "siigo_account_group",
    )
    list_filter = (
        "name",
        "brand",
        "status",
    )
    search_fields = (
        "id",
        "name",
        "brand__name",
        "status",
        "sku",
        "url_key",
        "meta_title",
        "meta_description",
        "meta_keywords",
        "groupedproduct__name",
        "groupedproduct__sku",
        "siigoproductproxy__siigo_account_group__name",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            _("Product Information"),
            {
                "fields": (
                    "partner",
                    "url_key",
                    "name",
                    "type",
                    "brand",
                    "sku",
                    "short_description",
                    "description",
                    "tax",
                )
            },
        ),
        (
            _("Measurement Information"),
            {
                "fields": (
                    "weight",
                    "unit_of_measure",
                    "measure",
                ),
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Category Information"),
            {
                "fields": ("categories",),
            },
        ),
        (
            _("SEO Information"),
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                ),
            },
        ),
        (
            _("Other Information"),
            {
                "fields": ("json_data",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    inlines = [ProductImageInline]

    class SiigoProductProxyInline(admin.StackedInline):
        model = SiigoProductProxy
        extra = 1

    inlines += [SiigoProductProxyInline]

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
        models.ManyToManyField: {"widget": autocomplete.ModelSelect2Multiple()},
    }
