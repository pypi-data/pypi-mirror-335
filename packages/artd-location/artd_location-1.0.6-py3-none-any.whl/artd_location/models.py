"""
 * Copyright (C) ArtD SAS - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Jonathan Favian Urzola Maldonado <jonathan@artd.com.co>, 2024
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ColombianCitiesBaseModel(models.Model):
    created_at = models.DateTimeField(
        _("Created at"),
        help_text=_("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        help_text=_("Updated at"),
        auto_now=True,
    )
    status = models.BooleanField(
        _("Status"),
        help_text=_("Status"),
        default=True,
    )

    class Meta:
        abstract = True


class Country(ColombianCitiesBaseModel):
    """Model definition for Country."""

    spanish_name = models.CharField(
        _("Country spanish name"),
        help_text=_("Country spanish name"),
        max_length=250,
    )
    english_name = models.CharField(
        _("Country english name"),
        help_text=_("Country english name"),
        max_length=250,
    )
    nom = models.CharField(
        _("Country nom"),
        help_text=_("Country nom"),
        max_length=250,
    )
    iso2 = models.CharField(
        _("Country iso2"),
        help_text=_("Country iso2"),
        max_length=250,
    )
    iso3 = models.CharField(
        _("Country iso3"),
        help_text=_("Country iso3"),
        max_length=250,
    )
    phone_code = models.CharField(
        _("Country phone code"),
        help_text=_("Country phone code"),
        max_length=250,
    )

    @property
    def flag(self):
        return f"https://flagsapi.com/{self.iso2}/flat/64.png"

    class Meta:
        """Meta definition for Country."""

        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    def __str__(self):
        """Unicode representation of Country."""
        return self.spanish_name


class Region(ColombianCitiesBaseModel):
    """Model definition for Region."""

    name = models.CharField(
        _("Region name"),
        help_text=_("Region name"),
        max_length=100,
    )
    country = models.ForeignKey(
        Country,
        related_name="region_country",
        on_delete=models.CASCADE,
    )

    class Meta:
        """Meta definition for Region."""

        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    def __str__(self):
        """Unicode representation of Region."""
        return self.name


class City(ColombianCitiesBaseModel):
    """Model definition for City."""

    name = models.CharField(
        _("City name"),
        help_text=_("City name"),
        max_length=100,
    )
    name_in_capital_letters = models.CharField(
        _("Name in capital letters"),
        help_text=_("Name in capital letters"),
        max_length=100,
    )
    code = models.CharField(
        _("City code"),
        help_text=_("City code"),
        max_length=10,
    )
    region = models.ForeignKey(
        Region,
        related_name="city_region",
        on_delete=models.CASCADE,
        help_text=_("Region"),
    )

    @property
    def country_spanish_name(self):
        return self.region.country.spanish_name

    @property
    def country_english_name(self):
        return self.region.country.english_name

    @property
    def region_name(self):
        return self.region.name

    class Meta:
        """Meta definition for City."""

        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def __str__(self):
        """Unicode representation of City."""
        return self.name
