"""
 * Copyright (C) ArtD SAS - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Jonathan Favian Urzola Maldonado <jonathan@artd.com.co>, 2023
"""

from django.contrib import admin

from artd_location.models import City, Country, Region
from django.utils.translation import gettext_lazy as _


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = [
        "spanish_name",
        "english_name",
        "nom",
        "iso2",
        "iso3",
        "phone_code",
        "id",
    ]
    list_display = [
        "spanish_name",
        "id",
        "english_name",
        "nom",
        "iso2",
        "iso3",
        "phone_code",
        "status",
    ]
    readonly_fields = [
        "spanish_name",
        "english_name",
        "nom",
        "iso2",
        "iso3",
        "phone_code",
        "status",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "spanish_name",
                    "english_name",
                    "nom",
                    "status",
                )
            },
        ),
        (
            _("ISO codes"),
            {
                "fields": (
                    "iso2",
                    "iso3",
                ),
            },
        ),
        (
            _("Phone code"),
            {
                "fields": ("phone_code",),
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

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "id",
        "country__spanish_name",
        "country__english_name",
    ]
    list_display = [
        "name",
        "id",
        "country",
        "status",
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "name_in_capital_letters",
        "code",
        "region__name",
        "id",
    ]
    list_display = [
        "name",
        "id",
        "name_in_capital_letters",
        "region",
        "code",
        "status",
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
