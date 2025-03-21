"""
ED-318 4.2.5 Simple Data Models
"""

from abc import ABC
from datetime import datetime, time, timedelta
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, model_validator

from .util import Lowercase, Translated, Uppercase

CodeAuthorityRole = Uppercase[Translated[Literal["AUTHORIZATION", "NOTIFICATION", "INFORMATION"]]]
"""ED-318 4.2.5.1 CodeAuthorityRole

Allowed Values:
- AUTHORIZATION: The authority shall be contacted to get an authorization before accessing the UAS Geographical Zone.
- NOTIFICATION: The authority shall be notified of the UAS flight prior to accessing the UAS Geographical Zone.
- INFORMATION: The designated authority is a general purpose point of contact for the UAS in the Zone.
"""

CodeDaylightEventType = Uppercase[Literal["BMCT", "SR", "SS", "EECT"]]
"""ED-318 4.2.5.2 CodeDaylightEventType

Allowed Values:
- BMCT: Beginning of morning civil twilight (center of the sun 6 degrees below the horizon).
- SR: Civil Sunrise.
- SS: Civil Sunset.
- EECT: End of evening civil twilight (center of the sun 6 degrees below the horizon).
"""

UomDistance = Lowercase[Literal["m", "ft"]]
"""ED-318 4.2.5.3 UomDistance

Allowed Values:
- m: Meters.
- ft: Feet.
"""

CodeZoneIdentifierType = Annotated[str, Field(min_length=1, max_length=7, pattern=r"[A-Za-z0-9_\-]{1,7}")]
"""ED-318 4.2.5.4 CodeZoneIdentifierType

A string that uniquely identifies the area within a geographical scope.
"""

CodeCountryISOType = Annotated[str, Field(min_length=3, max_length=3)]
"""ED-318 4.2.5.5 CodeCountryISOType

A 3 letter identifier of a country or territory using the ISO 3166-1 alpha-3 standard.
"""

CodeZoneVariantType = Uppercase[Literal["COMMON", "CUSTOMIZED"]]
"""ED-318 4.2.5.6 CodeZoneVariantType

Allowed Values:
- COMMON: The zone is provided with its common definition, valid for any UAS and operator.
- CUSTOMIZED: The zone is provided with a customised definition, for a particular UAS or operator.
  This is a design provision that could be used for example to provide waivers to specific users
  with restrictions removed on given zones for specific purposes. This information enables them to
  identify it is not the common version which has been transferred.
"""

CodeZoneType = Uppercase[
    Translated[Literal["USPACE", "PROHIBITED", "REQ_AUTHORIZATION", "CONDITIONAL", "NO_RESTRICTION"]]
]
"""ED-318 4.2.5.7 CodeZoneType

Allowed Values:
- USPACE: Indicates a zone subject to the requirements of Regulation EU 664/2021.
- PROHIBITED: Indicates that the flight of UAS is prohibited during the applicability time.
- REQ_AUTHORIZATION: Indicates that the flight of UAS is subject to explicit authorization requirements during the
  time of applicability. Note that one Authority contact with role Authorization should be provided in this case.
- CONDITIONAL: Indicates that access in the UAS Geographical Zone is allowed only to operators fulfilling a
  special condition, which is defined as a logical expression.
- NO_RESTRICTION: Indicates that the zone may be used during the applicability time without any restrictions.
"""

ConditionExpressionType = Annotated[str, Field(max_length=10_000)]
"""ED-318 4.2.5.8 ConditionExpressionType

A coded expression that provides information about what is authorized/forbidden in a zone with conditional access.
By difference with the "Message" field per zone, this coded expression is made to be interpreted by a machine,
while the "Message" field is to be interpreted by a human.
"""

CodeZoneReasonType = Uppercase[
    Literal["AIR_TRAFFIC", "SENSITIVE", "PRIVACY", "POPULATION", "NATURE", "NOISE", "EMERGENCY", "DAR", "OTHER"]
]
"""ED-318 4.2.5.9 CodeZoneReasonType

Allowed Values:
- AIR_TRAFFIC: Due to the presence of air traffic.
- SENSITIVE: Due to the presence of a sensitive site, in the vicinity of which the presence of drones could be
  considered a potential threat.
- PRIVACY: Due to the presence of a site for which the presence of drones could raise privacy concerns.
- POPULATION: Due to the presence of a significantly populated area.
- NATURE: Due to the presence of a wildlife/nature sanctuary or another area with sensitive nature/fauna.
- NOISE: Due to noise abatement regulations.
- EMERGENCY: Due to events related to a situation that requires urgent intervention (such as an accident).
- DAR: Due to the application of a dynamic airspace reconfiguration in a U-space volume, temporarily segregating
  the zone for UAS operations.
- OTHER: Due to another reason, which may be specified in the reasonInfo property.
"""


class _TextType(BaseModel, ABC):
    text: str
    lang: Annotated[str, Field(max_length=5, pattern=r"(?i)^[a-z]{2}-[A-Z]{2}$")] | None = None

    @model_validator(mode="before")
    @classmethod
    def coerce_str(cls, data: Any):
        if isinstance(data, str):
            return {"text": data}
        return data


class TextShortType(_TextType):
    """ED-318 4.2.5.10 TextShortType

    A free text with a maximum length of 200 characters, optionally accompanied
    by an indication of the language in which the text is written.
    """

    text: Annotated[str, Field(max_length=200)]


class TextLongType(_TextType):
    """ED-318 4.2.5.11 TextLongType

    A free text with a maximum length of 1000 characters, optionally accompanied
    by an indication of the language in which the text is written.
    """

    text: Annotated[str, Field(max_length=1_000)]


CodeWeekdayType = Uppercase[Literal["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN", "ANY"]]
"""ED-318 4.2.5.12 CodeWeekdayType

Allowed Values:
- MON: Monday.
- TUE: Tuesday.
- WED: Wednesday.
- THU: Thursday.
- FRI: Friday.
- SAT: Saturday.
- SUN: Sunday.
- ANY: Any day of the week.
"""

DateTimeType = datetime
"""ED-318 4.2.5.13 DateTimeType

A date and time instant, represented as a string in the format specified by RFC 3339.

Examples:
- 1990-12-31T15:30:00.00Z
- 1990-12-31T15:30:00.00-08:00 (offset of -8 hours from UTC)
"""

TimeInterval = timedelta
"""ED-318 4.2.5.14 TimeInterval

A time interval.
"""

TimeType = time
"""ED-318 4.2.5.15 TimeType

Time, optionally with time zone.
"""

CodeYesNoType = Uppercase[Literal["YES", "NO"]]
"""ED-318 4.2.5.16 CodeYesNoType

Allowed Values:
- YES: True.
- NO: False.
"""

URNType = Annotated[str, Field(pattern=r"(?i)^urn:.+:.*$")]
"""ED-318 4.2.5.17 URNType

Must comply with the URN syntax defined in RFC 2141.
"""
