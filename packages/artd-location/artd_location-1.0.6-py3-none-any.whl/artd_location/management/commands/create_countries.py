"""
 * Copyright (C) ArtD SAS - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Jonathan Favian Urzola Maldonado <jonathan@artd.com.co>, 2023
"""

from django.core.management.base import BaseCommand

from artd_location.data.countries import COUNTRIES
from artd_location.models import Country


class Command(BaseCommand):
    help = "Create countries"

    def handle(self, *args, **kwargs):
        for country in COUNTRIES:
            if Country.objects.filter(id=country[0]).count() == 0:
                Country.objects.create(
                    id=country[0],
                    spanish_name=country[1],
                    english_name=country[2],
                    nom=country[3],
                    iso2=country[4],
                    iso3=country[5],
                    phone_code=country[6],
                )
                self.stdout.write(self.style.SUCCESS(f"{country[1]} was created"))
            else:
                country_obj = Country.objects.get(
                    id=country[0],
                )
                country_obj.spanish_name = country[1]
                country_obj.english_name = country[2]
                country_obj.nom = country[3]
                country_obj.iso2 = country[4]
                country_obj.iso3 = country[5]
                country_obj.phone_code = country[6]
                country_obj.save()
                self.stdout.write(self.style.WARNING(f"{country[1]} was updated"))
