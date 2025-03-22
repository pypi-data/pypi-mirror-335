"""
 * Copyright (C) ArtD SAS - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Jonathan Favian Urzola Maldonado <jonathan@artd.com.co>, 2023
"""

from django.core.management.base import BaseCommand

from artd_location.data.cities import CITIES
from artd_location.models import City, Region


class Command(BaseCommand):
    help = "Create colombian cities"

    def handle(self, *args, **kwargs):
        for city in CITIES:
            region = Region.objects.get(id=city[4])
            if City.objects.filter(id=city[0]).count() == 0:
                City.objects.create(
                    id=city[0],
                    name=city[3],
                    name_in_capital_letters=city[2],
                    code=city[1],
                    region=region,
                )
                self.stdout.write(self.style.SUCCESS(f"{city[3]} was created"))
            else:
                city_obj = City.objects.get(
                    id=city[0],
                )
                city_obj.name = city[3]
                city_obj.name_in_capital_letters = city[2]
                city_obj.code = city[1]
                city_obj.region = region
                city_obj.save()
                self.stdout.write(self.style.WARNING(f"{city[3]} was updated"))
