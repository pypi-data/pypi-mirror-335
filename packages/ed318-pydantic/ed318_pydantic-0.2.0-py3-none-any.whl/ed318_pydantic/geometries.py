from __future__ import annotations

from typing import Annotated, ClassVar, Literal, TypeVar, Union

import geojson_pydantic as geojson
from pydantic import BaseModel, Field, model_validator

from .types import UomDistance
from .util import Uppercase, get_list_depth

T = TypeVar("T")

CodeVerticalReferenceType = Uppercase[Literal["AGL", "AMSL", "WGS84"]]
"""ED-318 4.2.3.3 CodeVerticalReferenceType

Allowed Values:
- AGL: Height above ground/surface level
- AMSL: Altitude above Mean Sea Level as defined by EGM-96 or a geoid model specified in the dataset metadata
- WGS84: Height above the WGS-84 ellipsoid
"""


class HorizontalExtent(BaseModel):
    """ED-318 4.2.3.1 HorizontalExtent

    Extension to GeoJSON which provides the possibility to specify a horizontal "circle" extent for a Point geometry.
    """

    subType: Literal["Circle"]
    radius: float
    """Distance, in meters, from the associated point along the
    WGS84 ellipsoidal surface of the Earth that this geometry extends."""


class VerticalLayer(BaseModel):
    """ED-318 4.2.3.2 VerticalLayer

    Extension to GeoJSON which provides a vertical extent to all standard GeoJSON geometries.
    """

    upper: float
    """The value of the upper limit of the UAS Geographical Zone expressed in a unit of measurement specified in uom,
    in relation with the vertical datum specified in the upperReference member."""
    upperReference: CodeVerticalReferenceType
    """The vertical reference for the upper limit of the UAS Geographical Zone."""
    lower: float
    """The value of the lower limit of the UAS Geographical Zone expressed in a unit of measurement specified in uom,
    in relation with the vertical datum specified in the lowerReference member."""
    lowerReference: CodeVerticalReferenceType
    """The vertical reference for the lower limit of the UAS Geographical Zone."""
    uom: UomDistance = "m"
    """The unit of measurement in which the upper and lower values are expressed (m) or (ft)."""


class _ED318GeometryMixin(BaseModel):
    layer: VerticalLayer
    _expected_coordinate_list_depth: ClassVar[int]

    @model_validator(mode="before")
    @classmethod
    def validate_coordinates(cls, data: T) -> T:
        if not isinstance(data, dict) or "coordinates" not in data:
            return data

        list_depth = get_list_depth(data["coordinates"])
        if list_depth != cls._expected_coordinate_list_depth:
            possible_types = {name for name, depth in coordinate_depth_map.items() if depth == list_depth}
            raise ValueError(
                f"a {cls.__name__} is expected to have a coordinate array "
                f"with {cls._expected_coordinate_list_depth} levels of depth, "
                f"got {list_depth} levels instead. "
                f"Possible types: {possible_types}"
            )

        return data


class Point(geojson.Point, _ED318GeometryMixin):
    extent: HorizontalExtent | None = None
    _expected_coordinate_list_depth = 1


class MultiPoint(geojson.MultiPoint, _ED318GeometryMixin):
    _expected_coordinate_list_depth = 2


class LineString(geojson.LineString, _ED318GeometryMixin):
    _expected_coordinate_list_depth = 2


class MultiLineString(geojson.MultiLineString, _ED318GeometryMixin):
    _expected_coordinate_list_depth = 3


class Polygon(geojson.Polygon, _ED318GeometryMixin):
    _expected_coordinate_list_depth = 3


class MultiPolygon(geojson.MultiPolygon, _ED318GeometryMixin):
    _expected_coordinate_list_depth = 4


coordinate_depth_map = {
    cls.__name__: cls._expected_coordinate_list_depth
    for cls in _ED318GeometryMixin.__subclasses__()
    if hasattr(cls, "_expected_coordinate_list_depth")
}


class GeometryCollection(geojson.GeometryCollection):
    geometries: list[Geometry]


Geometry = Annotated[
    Union[
        Point,
        MultiPoint,
        LineString,
        MultiLineString,
        Polygon,
        MultiPolygon,
        GeometryCollection,
    ],
    Field(discriminator="type"),
]

GeometryCollection.model_rebuild()
