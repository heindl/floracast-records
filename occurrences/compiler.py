#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime
import numpy
from florecords.occurrences.constants import NorthAmericanMacroFungiFamilies
from florecords.geo.cells import GenerateS2CellIds
from florecords.occurrences import constants
import hashlib

class OccurrenceCompiler(object):

    def __init__(self,
                 source_id, # type: str
                 source, # type: str
                 name, # type: str
                 observed_at, # type: float
                 lat, # type: float
                 lng, # type: float
                 coord_uncertainty, # type: float
                 family, # type: str
                 **kwargs
                 ):

        self._source_id = source_id
        self._scientific_name = name.encode('utf-8', 'replace')
        self._observed_at = observed_at
        self._latitude = lat
        self._longitude = lng
        self._coordinate_uncertainty = None if numpy.isnan(coord_uncertainty) else coord_uncertainty
        self._source = source
        self._created_at = datetime.utcnow()
        self._family = family
        self._validate()

    def scientific_name(self):
        return self._scientific_name

    def set_scientific_name(self, name):
        self._scientific_name = name

    def _validate(self):
        assert len(self._source_id) > 0, "Invalid occurrence id"
        assert len(self._scientific_name) > 0, "Invalid occurrence scientific name"
        assert self._observed_at > constants.MINIMUM_OCCURRENCE_TIME_SECONDS

        assert (-90 < self._latitude < 90), "Invalid Latitude: %d" % self._latitude
        assert (-180 < self._longitude < 180), "Invalid Longitude: %d" % self._longitude
        if self._family not in NorthAmericanMacroFungiFamilies:
            raise ValueError("Unrecognized fungi family: %s" % self._family)
        if self._source not in ['idigbio', 'gbif', 'inaturalist', 'mushroomobserver', 'mycoportal']:
            raise ValueError("Invalid source: %s", self._source)

    def decompose(self):
        return GenerateS2CellIds(
            centre_lat=self._latitude,
            centre_lng=self._longitude,
            coordinate_uncertainty=self._coordinate_uncertainty,
            uncertainty_threshold=constants.MAX_COORDINATE_UNCERTAINTY_METERS,
            s2_cell_level=constants.STANDARD_S2_CELL_LEVEL,
        )


    def to_bigquery(self):

        cell_ids = [{'id': x} for x in self.decompose()]

        if len(cell_ids) == 0:
            return None

        return {
            'scientific_name': self._scientific_name,
            'source_id': hashlib.md5(self._source + "+" + self._source_id).hexdigest(),
            'created_at': datetime.utcnow().timestamp(),
            'observed_at': self._observed_at,
            'cell': cell_ids,
        }


    @staticmethod
    def schema():
        return [
            {
                'name': 'source_id',
                'type': 'INTEGER',
                'mode': 'REQUIRED'
            }, # 8 bytes
            {
                'name': 'scientific_name',
                'type': 'STRING',
                'mode': 'REQUIRED'
            }, # 20 bytes average
            {
                'name': 'observed_at',
                'type': 'TIMESTAMP',
                'mode': 'REQUIRED'
            }, # 8 bytes
            {
                'name': 'created_at',
                'type': 'TIMESTAMP',
                'mode': 'REQUIRED'
            }, # 8 bytes
            {
                "name": "cell",
                "type": "RECORD",
                "mode": "REPEATED",
                "fields": [
                    {
                        "name": "id",
                        "type": "int",
                        "mode": "REQUIRED"
                    },
                ],
            } # 8 bytes * number of cells
        ]