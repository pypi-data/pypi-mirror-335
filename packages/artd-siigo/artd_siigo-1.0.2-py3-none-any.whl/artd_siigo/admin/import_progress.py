from django.contrib import admin
from artd_siigo.models import EntityImportStatus


@admin.register(EntityImportStatus)
class EntityImportStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "siigo_entity",
        "partner",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "siigo_entity",
        "partner__name",
    )
    list_filter = (
        "siigo_entity",
        "partner__name",
        "status",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
