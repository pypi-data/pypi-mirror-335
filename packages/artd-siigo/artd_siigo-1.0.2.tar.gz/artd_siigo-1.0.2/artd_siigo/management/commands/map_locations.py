from artd_partner.models import Partner
from django.core.management.base import BaseCommand, CommandError
import traceback

from artd_siigo.models import CountryMapping, RegionMapping, CityMapping
from artd_siigo.data.mapping import COUNTRY_MAPS, REGIONS_MAPS, CITY_MAPS
from artd_location.models import Country, Region, City


class Command(BaseCommand):
    help = "Mapp countries, regions and cities for a specified partner"

    def add_arguments(self, parser):
        # Define 'slug' argument as required
        parser.add_argument(
            "partner_slug",
            type=str,
            help="The slug for the partner whose account groups need to be imported",  # noqa
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Mapping locations...",
            )
        )
        partner_slug = options["partner_slug"]
        # Validate partner existence
        try:
            partner = Partner.objects.get(partner_slug=partner_slug)
        except Partner.DoesNotExist:
            raise CommandError(
                f"Partner with slug '{partner_slug}' does not exist",
            )

        try:
            for country_map in COUNTRY_MAPS:
                if Country.objects.filter(id=country_map["artd_country_id"]).exists():
                    country = Country.objects.get(id=country_map["artd_country_id"])
                    obj, created = CountryMapping.objects.update_or_create(
                        partner=partner,
                        country=country,
                        defaults={
                            "country_code": country_map["siigo_country_code"],
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created country mapping: {country_map['siigo_country_code']}"  # noqa
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated country mapping: {country_map['siigo_country_code']}"  # noqa
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Country with id {country_map['artd_country_id']} does not exist"  # noqa
                        )
                    )

            self.stdout.write(self.style.SUCCESS("Countries mapped successfully"))

            for region_map in REGIONS_MAPS:
                if Region.objects.filter(id=region_map["artd_region_id"]).exists():
                    region = Region.objects.get(id=region_map["artd_region_id"])
                    obj, created = RegionMapping.objects.update_or_create(
                        partner=partner,
                        region=region,
                        defaults={
                            "state_code": region_map["siigo_region_code"],
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created region mapping: {region_map['siigo_region_code']}"  # noqa
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated region mapping: {region_map['siigo_region_code']}"  # noqa
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Region with id {region_map['artd_region_id']} does not exist"  # noqa
                        )
                    )

            for city_map in CITY_MAPS:
                if City.objects.filter(id=city_map["artd_city_id"]).exists():
                    city = City.objects.get(id=city_map["artd_city_id"])
                    obj, created = CityMapping.objects.update_or_create(
                        partner=partner,
                        city=city,
                        defaults={
                            "city_code": city_map["siigo_city_code"],
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created city mapping: {city_map['siigo_city_code']}"  # noqa
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated city mapping: {city_map['siigo_city_code']}"  # noqa
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"City with id {city_map['artd_city_id']} does not exist"  # noqa
                        )
                    )

        except Exception as e:
            tb_str = traceback.format_exc()
            print(f"Error: {e}")
            print(f"Detalle de la excepción: {tb_str}")
            # raise CommandError(f"Error mapping locations: {e}")
