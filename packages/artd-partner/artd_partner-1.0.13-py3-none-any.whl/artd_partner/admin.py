from django.contrib import admin

# Register your models here.
from django.contrib import admin
from artd_partner.models import Partner, Headquarter, Position, Coworker
from django.utils.translation import gettext_lazy as _


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Admin view for Partner."""

    list_display = (
        "name",
        "id",
        "email",
        "partner_slug",
        "dni",
        "address",
        "city",
    )
    list_filter = (
        "city",
        "partner_slug",
    )
    search_fields = (
        "name",
        "partner_slug",
        "dni",
        "address",
        "city__name",
    )
    readonly_fields = (
        "updated_at",
        "created_at",
    )
    fieldsets = (
        (
            _("Partner"),
            {
                "fields": (
                    "name",
                    "partner_slug",
                    "document_type",
                    "dni",
                    "email",
                    "signed_key",
                )
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "address",
                    "city",
                )
            },
        ),
        (
            _("Services"),
            {"fields": ("services",)},
        ),
        (
            _("Status"),
            {"fields": ("status",)},
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


@admin.register(Headquarter)
class HeadquarterAdmin(admin.ModelAdmin):
    """Admin view for Headquarter."""

    list_display = (
        "name",
        "id",
        "partner",
        "address",
        "city",
        "phone",
        "status",
    )
    list_filter = (
        "city",
        "partner",
    )
    readonly_fields = (
        "updated_at",
        "created_at",
    )
    search_fields = (
        "name",
        "address",
        "city__name",
        "phone",
        "partner__name",
    )
    fieldsets = (
        (
            _("Headquarter"),
            {
                "fields": (
                    "name",
                    "partner",
                    "address",
                    "city",
                    "phone",
                )
            },
        ),
        (
            _("Status"),
            {"fields": ("status",)},
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


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Admin view for Position."""

    list_display = (
        "name",
        "status",
    )
    search_fields = ("name",)
    readonly_fields = (
        "updated_at",
        "created_at",
    )
    fieldsets = (
        (
            _("Position"),
            {"fields": ("name", "partner")},
        ),
        (
            _("Status"),
            {"fields": ("status",)},
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


@admin.register(Coworker)
class CoworkerAdmin(admin.ModelAdmin):
    """Admin view for Coworker."""

    list_display = (
        "first_name",
        "last_name",
        "id",
        "dni",
        "phone",
        "position",
        "headquarter",
        "status",
    )
    readonly_fields = (
        "updated_at",
        "created_at",
    )
    search_fields = (
        "first_name",
        "last_name",
        "dni",
        "phone",
        "position__name",
        "headquarter__name",
    )
    fieldsets = (
        (
            _("Coworker"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "dni",
                    "phone",
                    "position",
                    "headquarter",
                )
            },
        ),
        (
            _("Status"),
            {"fields": ("status",)},
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
    list_filter = (
        "position",
        "headquarter",
    )
