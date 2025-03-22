from django.contrib import admin
from artd_modules.models import Module
from django.utils.translation import gettext_lazy as _


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "version",
        "description",
        "is_plugin",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = (
        "name",
        "description",
    )
    readonly_fields = (
        "id",
        "name",
        "description",
        "version",
        "is_plugin",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "General",
            {
                "fields": (
                    "name",
                    "description",
                    "version",
                    "is_plugin",
                )
            },
        ),
        (
            _("Status Information"),
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
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
