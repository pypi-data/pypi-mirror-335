from typing import Annotated, Any

import geojson_pydantic as geojson
from pydantic import BaseModel, BeforeValidator, Field, model_validator

from .geometries import Geometry
from .types import (
    CodeAuthorityRole,
    CodeCountryISOType,
    CodeDaylightEventType,
    CodeWeekdayType,
    CodeYesNoType,
    CodeZoneIdentifierType,
    CodeZoneReasonType,
    CodeZoneType,
    CodeZoneVariantType,
    ConditionExpressionType,
    DateTimeType,
    TextLongType,
    TextShortType,
    TimeInterval,
    TimeType,
    URNType,
)
from .util import CoercedList, CoercedOptional, convert_to_list


class DailyPeriod(BaseModel):
    """ED-318 4.2.4.4 DailyPeriod

    Daily applicability schedule of the zone.
    """

    day: Annotated[list[CodeWeekdayType], Field(min_length=1, max_length=7), BeforeValidator(convert_to_list)]
    startTime: CoercedOptional[TimeType] = None
    startEvent: CoercedOptional[CodeDaylightEventType] = None
    endTime: CoercedOptional[TimeType] = None
    endEvent: CoercedOptional[CodeDaylightEventType] = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.startTime and self.startEvent:
            raise ValueError("startTime and startEvent cannot be present simultaneously")
        if self.endTime and self.endEvent:
            raise ValueError("endTime and endEvent cannot be present simultaneously")
        return self


class TimePeriod(BaseModel):
    """ED-318 4.2.4.3 TimePeriod

    Date and time period of applicability of the zone, including an eventual daily/weekly schedule.
    """

    startDateTime: CoercedOptional[DateTimeType] = None
    endDateTime: CoercedOptional[DateTimeType] = None
    schedule: CoercedOptional[list[DailyPeriod]] = None


class DatasetMetadata(BaseModel):
    """ED-318 4.2.4.1 DatasetMetadata

    Global information that qualifies and constrains the usage of the data in the associated data set.
    """

    provider: CoercedOptional[CoercedList[TextShortType]] = None
    issued: CoercedOptional[DateTimeType] = None
    validFrom: CoercedOptional[DateTimeType] = None
    validTo: CoercedOptional[DateTimeType] = None
    description: CoercedOptional[CoercedList[TextShortType]] = None
    otherGeoid: CoercedOptional[URNType] = None
    technicalLimitation: CoercedOptional[CoercedList[TextShortType]] = None


class Authority(BaseModel):
    """ED-318 4.2.4.5 Authority

    A relevant authority that is in charge for authorizing, being notified or providing information for
    UAS operations in the UAS Geographical Zone.
    """

    purpose: CodeAuthorityRole
    intervalBefore: CoercedOptional[TimeInterval] = None
    name: CoercedOptional[CoercedList[TextShortType]] = None
    service: CoercedOptional[CoercedList[TextShortType]] = None
    contactName: CoercedOptional[CoercedList[TextShortType]] = None
    siteURL: CoercedOptional[TextShortType] = None
    email: CoercedOptional[TextShortType] = None
    phone: CoercedOptional[TextShortType] = None


class Metadata(BaseModel):
    """ED-318 4.2.4.6 Metadata

    Information that qualifies and provides traceability for the Zone operational data.
    """

    creationDateTime: CoercedOptional[DateTimeType] = None
    updateDateTime: CoercedOptional[DateTimeType] = None
    originator: CoercedOptional[str] = None


class UASZone(BaseModel):
    """ED-318 4.2.2.2 UASZone

    A specific version of an airspace of defined dimensions, above the land areas or territorial
    waters of a State, within which a particular restriction or condition for UAS flights applies.
    """

    identifier: CodeZoneIdentifierType
    country: CodeCountryISOType
    name: CoercedOptional[CoercedList[TextShortType]] = None
    type: CodeZoneType
    variant: CodeZoneVariantType
    restrictionConditions: CoercedOptional[ConditionExpressionType] = None
    region: CoercedOptional[Annotated[int, Field(ge=0, le=65535)]] = None
    reasons: CoercedOptional[
        Annotated[list[CodeZoneReasonType], Field(max_length=9), BeforeValidator(convert_to_list)]
    ] = None
    otherReasonInfo: CoercedOptional[CoercedList[TextShortType]] = None
    regulationExemption: CoercedOptional[CodeYesNoType] = None
    message: CoercedOptional[CoercedList[TextLongType]] = None
    extendedProperties: CoercedOptional[
        Annotated[dict[str, Any], BeforeValidator(lambda v: v if isinstance(v, dict) else {"prop": v})]
    ] = None
    limitedApplicability: CoercedOptional[CoercedList[TimePeriod]] = None
    zoneAuthority: CoercedList[Authority]
    dataSource: CoercedOptional[Metadata] = None


class Feature(geojson.Feature):
    geometry: Geometry
    properties: UASZone

    @model_validator(mode="before")
    @classmethod
    def parse_properties(cls, data: Any):
        if not isinstance(data, dict) or "properties" not in data or "geometry" not in data:
            return data

        properties = data["properties"]
        geometry = data["geometry"]
        if not isinstance(properties, dict) or not isinstance(geometry, dict):
            return data

        if "UASZone" in properties:
            uas_zone = properties.pop("UASZone")
            properties.update(uas_zone)

        if "verticalLayer" in properties:
            layer = properties.pop("verticalLayer")
            geometry.setdefault("layer", layer)

        return data


class FeatureCollection(geojson.FeatureCollection[Feature]):
    """ED-318 4.2.2.1 FeatureCollection

    GeoJSON FeatureCollection containing zero or more GeoJSON Features representing UAS Geographical Zones,
    plus additional foreign members capturing data set information.
    """

    name: Annotated[str, Field(max_length=200)] | None = None
    """A free text name that can be used to identifiy the UAS Geographical Zone data set."""
    metadata: DatasetMetadata = {}
    """Qualification and constraint of the usage of the data in this data set."""
