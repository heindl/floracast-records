#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime
import numpy
from florecords.occurrences.constants import NorthAmericanMacroFungiFamilies
from florecords.geo.coords import FormatCoordinates
from florecords.geo.cells import GenerateS2CellIds
from florecords.occurrences import constants

class OccurrenceGenerator(object):

    def __init__(self,
                 source_id, # type: str
                 source, # type: str
                 name, # type: str
                 observed_at, # type: int
                 coord_uncertainty, # type: Union[float, numpy.nan]
                 lat, # type: float
                 lng, # type: float
                 family, # type: str
                 **kwargs
                 ):

        self._source_id = source_id
        self._name = name.encode('utf-8', 'replace')
        self._observed_at = observed_at
        self._latitude = lat
        self._longitude = lng
        self._family = family
        self._coordinate_uncertainty = None if numpy.isnan(coord_uncertainty) else coord_uncertainty
        self._source = source
        self._created_at = datetime.utcnow()
        self._validate()

    def _validate(self):
        assert len(self._source_id) > 0, "Invalid occurrence id"
        assert len(self._name) > 0, "Invalid occurrence scientific name"
        assert self._observed_at > constants.MINIMUM_OCCURRENCE_TIME_SECONDS

        assert (-90 < self._latitude < 90), "Invalid Latitude: %d" % self._latitude
        assert (-180 < self._longitude < 180), "Invalid Longitude: %d" % self._longitude
        if self._family not in NorthAmericanMacroFungiFamilies:
            raise ValueError("Unrecognized fungi family: %s" % self._family)
        if self._source not in ['idigbio', 'gbif', 'inaturalist', 'mushroomobserver', 'mycoportal']:
            raise ValueError("Invalid source: %s", self._source)

    def decompose(self):
        lat, lng, uncertainty = FormatCoordinates(
            self._latitude,
            self._longitude,
            self._coordinate_uncertainty
        )
        return GenerateS2CellIds(
            centre_lat=lat,
            centre_lng=lng,
            coordinate_uncertainty=uncertainty,
            uncertainty_threshold=constants.MAX_COORDINATE_UNCERTAINTY_METERS,
            s2_cell_level=constants.STANDARD_S2_CELL_LEVEL,
        )