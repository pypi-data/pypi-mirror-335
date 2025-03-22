from django.contrib import admin
from artd_siigo.models import (
    CountryMapping,
    RegionMapping,
    CityMapping,
    FiscalResponsibilitiesMapping,
    CustomerDocumentTypeMapping,
    CustomerPersonTypeMapping,
    CustomerTypeMapping,
    TaxMapping,
    ProductTypeMapping,
)


@admin.register(CountryMapping)
class CountryMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "country",
        "country_code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "country__spanish_name",
        "country__english_name",
        "country__nom",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(RegionMapping)
class RegionMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "region",
        "state_code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "region__name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(CityMapping)
class CityMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "city",
        "city_code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "city__name",
        "city__name_in_capital_letters",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(FiscalResponsibilitiesMapping)
class FiscalResponsibilitiesMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "tax_segment",
        "code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "tax_segment__name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(CustomerDocumentTypeMapping)
class CustomerDocumentTypeMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "customer_document_type",
        "code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "customer_document_type__name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(CustomerPersonTypeMapping)
class CustomerPersonTypeMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "customer_person_type",
        "code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "customer_person_type__name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(CustomerTypeMapping)
class CustomerTypeMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "customer_type",
        "code",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "customer_type__name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(TaxMapping)
class TaxMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "siigo_tax",
        "tax",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "siigo_tax__name",
        "tax__name",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(ProductTypeMapping)
class ProductTypeMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "product_type",
        "siigo_product_type",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "partner__name",
        "siigo_product_type__code",
    )
    list_filter = ("partner__name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
