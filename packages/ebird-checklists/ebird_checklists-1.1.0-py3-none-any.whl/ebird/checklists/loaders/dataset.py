import csv
import datetime as dt
import logging
import re
from decimal import Decimal
from pathlib import Path

from django.utils.timezone import get_default_timezone

from ..models import (
    Checklist,
    Country,
    Location,
    Observation,
    Observer,
    Region,
    Species,
    District,
)

logger = logging.getLogger(__name__)


class BasicDatasetLoader:
    @staticmethod
    def add_country(data: dict) -> Country:
        code: str = data["COUNTRY CODE"]
        country: Country

        values: dict = {
            "name": data["COUNTRY"],
            "place": data["COUNTRY"],
        }

        if country := Country.objects.filter(code=code).first():
            for key, value in values.items():
                setattr(country, key, value)
            country.save()
        else:
            country = Country.objects.create(code=code, **values)
        return country

    @staticmethod
    def add_region(data: dict) -> Region:
        code: str = data["STATE CODE"]
        region: Region

        values: dict = {
            "name": data["STATE"],
            "place": "%s, %s" % (data["STATE"], data["COUNTRY"]),
        }

        if region := Region.objects.filter(code=code).first():
            for key, value in values.items():
                setattr(region, key, value)
            region.save()
        else:
            region = Region.objects.create(code=code, **values)
        return region

    @staticmethod
    def add_district(data: dict) -> District:
        code: str = data["COUNTY CODE"]
        district: District

        values: dict = {
            "name": data["COUNTY"],
            "place": "%s, %s, %s" % (data["COUNTY"], data["STATE"], data["COUNTRY"]),
        }

        if district := District.objects.filter(code=code).first():
            for key, value in values.items():
                setattr(district, key, value)
            district.save()
        else:
            district = District.objects.create(code=code, **values)
        return district

    def add_location(self, data: dict) -> Location:
        identifier: str = data["LOCALITY ID"]
        location: Location

        values: dict = {
            "identifier": identifier,
            "type": data["LOCALITY TYPE"],
            "name": data["LOCALITY"],
            "district": None,
            "region": self.add_region(data),
            "country": self.add_country(data),
            "latitude": Decimal(data["LATITUDE"]),
            "longitude": Decimal(data["LONGITUDE"]),
            "iba_code": data["IBA CODE"],
            "bcr_code": data["BCR CODE"],
            "usfws_code": data["USFWS CODE"],
            "atlas_block": data["ATLAS BLOCK"],
            "url": "https://ebird.org/region/%s" % identifier,
        }

        if "COUNTY CODE" in data and data["COUNTY CODE"]:
            values["district"] = self.add_district(data)

        if location := Location.objects.filter(identifier=identifier).first():
            for key, value in values.items():
                setattr(location, key, value)
            location.save()
        else:
            location = Location.objects.create(**values)
        return location

    @staticmethod
    def add_observer(data: dict) -> Observer:
        identifier: str = data["OBSERVER ID"]
        observer: Observer

        values: dict = {
            "identifier": identifier,
            "name": "_%s" % identifier,
        }

        if observer := Observer.objects.filter(identifier=identifier).first():
            for key, value in values.items():
                setattr(observer, key, value)
            observer.save()
        else:
            observer = Observer.objects.create(**values)
        return observer

    @staticmethod
    def add_species(data: dict) -> Species:
        taxon_order = data["TAXONOMIC ORDER"]
        species: Species

        values: dict = {
            "taxon_order": taxon_order,
            "order": "",
            "category": data["CATEGORY"],
            "species_code": "",
            "family_code": "",
            "common_name": data["COMMON NAME"],
            "scientific_name": data["SCIENTIFIC NAME"],
            "family_common_name": "",
            "family_scientific_name": "",
            "subspecies_common_name": data["SUBSPECIES COMMON NAME"],
            "subspecies_scientific_name": data["SUBSPECIES SCIENTIFIC NAME"],
            "exotic_code": data["EXOTIC CODE"],
        }

        if species := Species.objects.filter(taxon_order=taxon_order).first():
            for key, value in values.items():
                setattr(species, key, value)
            species.save()
        else:
            species = Species.objects.create(**values)
        return species

    @staticmethod
    def add_observation(
        data: dict, checklist: Checklist, species: Species
    ) -> Observation:
        identifier = data["GLOBAL UNIQUE IDENTIFIER"].split(":")[-1]
        observation: Observation

        values: dict = {
            "edited": checklist.edited,
            "identifier": identifier,
            "checklist": checklist,
            "country": checklist.country,
            "region": checklist.region,
            "district": checklist.district,
            "area": checklist.area,
            "location": checklist.location,
            "observer": checklist.observer,
            "species": species,
            "identified": species.is_identified(),
            "date": checklist.date,
            "count": None,
            "breeding_code": data["BREEDING CODE"],
            "breeding_category": data["BREEDING CATEGORY"],
            "behavior_code": data["BEHAVIOR CODE"],
            "age_sex": data["AGE/SEX"],
            "media": bool(data["HAS MEDIA"]),
            "approved": bool(data["APPROVED"]),
            "reviewed": bool(data["REVIEWED"]),
            "reason": data["REASON"] or "",
            "comments": data["SPECIES COMMENTS"] or "",
            "urn": data["GLOBAL UNIQUE IDENTIFIER"],
        }

        if re.match(r"\d+", data["OBSERVATION COUNT"]):
            values["count"] = int(data["OBSERVATION COUNT"]) or None

        if observation := Observation.objects.filter(identifier=identifier).first():
            for key, value in values.items():
                setattr(observation, key, value)
            observation.save()
        else:
            observation = Observation.objects.create(**values)

        return observation

    @staticmethod
    def add_checklist(
        row: dict,
        location: Location,
        observer: Observer,
    ) -> Checklist:
        identifier: str = row["SAMPLING EVENT IDENTIFIER"]
        checklist: Checklist

        values: dict = {
            "identifier": identifier,
            "edited": dt.datetime.fromisoformat(row["LAST EDITED DATE"]).replace(
                tzinfo=get_default_timezone()
            ),
            "country": location.country,
            "region": location.region,
            "district": location.district,
            "area": location.area,
            "location": location,
            "observer": observer,
            "group": row["GROUP IDENTIFIER"],
            "observer_count": row["NUMBER OBSERVERS"],
            "date": dt.datetime.strptime(row["OBSERVATION DATE"], "%Y-%m-%d").date(),
            "time": None,
            "protocol": row["PROTOCOL TYPE"],
            "protocol_code": row["PROTOCOL CODE"],
            "project_code": row["PROJECT CODE"],
            "duration": None,
            "distance": None,
            "coverage": None,
            "complete": bool(row["ALL SPECIES REPORTED"]),
            "comments": row["TRIP COMMENTS"] or "",
            "url": "https://ebird.org/checklist/%s" % identifier,
        }

        if time := row["TIME OBSERVATIONS STARTED"]:
            values["time"] = dt.datetime.strptime(time, "%H:%M:%S").time()

        if duration := row["DURATION MINUTES"]:
            values["duration"] = Decimal(duration)

        if distance := row["EFFORT DISTANCE KM"]:
            values["distance"] = Decimal(distance)

        if coverage := row["EFFORT AREA HA"]:
            values["coverage"] = Decimal(coverage)

        if checklist := Checklist.objects.filter(identifier=identifier).first():
            for key, value in values.items():
                setattr(checklist, key, value)
            checklist.save()
        else:
            checklist = Checklist.objects.create(**values)

        return checklist

    def load(self, path: Path) -> None:
        if not path.exists():
            raise IOError('File "%s" does not exist' % path)

        loaded: int = 0

        logger.info("Loading eBird Basic Dataset", extra={"path": path})

        with open(path) as csvfile:
            reader = csv.DictReader(csvfile, delimiter="\t")
            for row in reader:
                location: Location = self.add_location(row)
                observer: Observer = self.add_observer(row)
                checklist: Checklist = self.add_checklist(row, location, observer)
                species: Species = self.add_species(row)
                self.add_observation(row, checklist, species)

                loaded += 1

        logger.info(
            "Loaded eBird Basic Dataset",
            extra={
                "path": path,
                "loaded": loaded,
            },
        )
