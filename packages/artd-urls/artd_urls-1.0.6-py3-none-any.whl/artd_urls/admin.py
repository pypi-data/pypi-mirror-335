from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from dal import autocomplete
from artd_urls.models import Url, UrlConfiguration


@admin.register(UrlConfiguration)
class UrlConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "partner",
        "include_admin_urls",
        "include_dinamic_urls",
        "status",
    )
    search_fields = (
        "partner__name",
        "include_admin_urls",
        "include_dinamic_urls",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Configuration"),
            {
                "fields": (
                    "partner",
                    "include_admin_urls",
                    "include_dinamic_urls",
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


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display = (
        "partner",
        "url",
        "status",
    )
    search_fields = (
        "partner__name",
        "url",
        "module",
        "name",
        "decorators",
    )
    readonly_fields = [
        "partner",
        "url",
        "module",
        "name",
        "decorators",
        "created_at",
        "updated_at",
        "status",
    ]
    fieldsets = (
        (
            _("Configuration"),
            {
                "fields": (
                    "partner",
                    "url",
                    "module",
                    "name",
                    "decorators",
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
    formfield_overrides = {
        models.ManyToManyField: {"widget": autocomplete.ModelSelect2Multiple()},
    }

    def has_add_permission(self, request):
        return False
