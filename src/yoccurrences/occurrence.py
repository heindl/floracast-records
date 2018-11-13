#!/usr/bin/env python
# encoding: utf-8

import numpy
from .taxa import NorthAmericanMacroFungiFamilies
from ygeo import Cell
from yutils import TimeStamp
from typing import Dict, Union, Generator
import constants
consts = constants.Constants()

class Occurrence(object):

    def __init__(self,
                 source_id, # type: str
                 source_key, # type: str
                 name, # type: str
                 observed_at, # type: float
                 cell_ids, # List[int]
                 created_at=None, # type: int
        ):

        self._source_id = source_id
        self._source_key = source_key
        self._name = name # A hack, but the two are separate because a normalized ScientificName is created later.
        self._observed_at = observed_at
        self._cell_ids = cell_ids
        self._created_at = created_at if created_at is not None else TimeStamp.from_now()
        self._features = {}
        self._validate()

    def name(self): # type: () -> str
        if self._name == "":
            raise ValueError('Invalid occurrence name')
        return self._name

    def set_name(self, name):
        assert isinstance(name, str)
        assert len(name.strip()) > 0
        self._name = name

    def observed_at(self): # type: () -> int
        return int(self._observed_at)

    def source_key(self): # type: () -> str
        return self._source_key

    def source_id(self): # type: () -> str
        return self._source_id

    def get_feature(self, label): # type: (str) -> Union[Dict, None]
        assert isinstance(label, str)
        assert len(label.strip()) > 0
        if label in self._features:
            return self._features[label]
        return None

    def set_feature(self, label, value): # type: (str, Dict) -> None
        assert isinstance(label, str)
        assert len(label.strip()) > 0
        self._features[label] = value

    def cell(self): # type: () -> Cell
        if len(self._cell_ids) != 1:
            raise ValueError("If cell is called, the occurrence is expected to have only one cell.")
        return Cell(self._cell_ids[0])

    def split(self): # type: () -> Generator[Occurrence]
        for c in self._cell_ids:
            yield Occurrence(
                source_id=self.source_id(),
                source_key=self.source_key(),
                name=self.name(),
                observed_at=self.observed_at(),
                cell_ids=[c],
                created_at=self._created_at,
            )

    def _validate(self):
        assert len(self._source_id) > 0, "Invalid occurrence id"
        assert len(self._cell_ids) > 0, "Invalid number of cell ids"
        assert len(self._name) > 0, "Invalid occurrence scientific name"

        assert self._observed_at > consts['minimum_occurrence_observed_timestamp'], \
            "Occurrence timestamp [%s] is earlier than minimum expected timestamp [%s]" % (self._observed_at, consts['minimum_occurrence_observed_timestamp'])
        assert isinstance(self._source_key, str) and len(self._source_key) > 0

    # def source_id(self):
    #     return int(hashlib.md5(("%s+%s" % (self._source, self._source_id)).encode("utf-8")).hexdigest(), 16)



    def merge(
            self,
            new_occurrence, # type: Occurrence
    ):
        return NotImplemented

    @classmethod
    def from_raw(cls,
                 source_id, # type: str
                 source_key, # type: str
                 name, # type: str
                 observed_at, # type: float
                 lat, # type: float
                 lng, # type: float
                 coord_uncertainty, # type: float
                 family, # type: str
                 **kwargs
                 ): # type: () -> Union[Occurrence, None]

        assert (-90 < lat < 90), "Invalid Latitude: %d" % lat
        assert (-180 < lng < 180), "Invalid Longitude: %d" % lng

        cell_ids = Cell.from_coordinates(
            lat=lat,
            lng=lng,
            uncertainty_meters=None if numpy.isnan(coord_uncertainty) else coord_uncertainty,
        )

        if cell_ids is None or len(cell_ids) == 0:
            return None

        if family not in NorthAmericanMacroFungiFamilies:
            raise ValueError("Unrecognized fungi family: %s" % family)

        return cls(
            source_id=source_id,
            name=name.encode("utf-8", "replace").decode('utf-8'),
            observed_at=observed_at,
            source_key=source_key,
            cell_ids=[c.id() for c in cell_ids],
        )

    @classmethod
    def decode(cls, obj):

        c = cls(
            name=obj['name'],
            source_id=obj['source_id'],
            source_key=obj['source_key'],
            observed_at=obj['observed_at'],
            cell_ids=[int(obj['cell_id'])],
        )
        if 'features' in obj:
            for k, v in obj['features']:
                c.set_feature(k, v)
        return c

    def encode(self):
        # type: () -> Dict

        return {
            "name": self.name(),
            "source_id": self.source_id(),
            "source_key": self.source_key(),
            "created_at": self._created_at,
            "observed_at": int(round(self._observed_at)),
            "cell_ids": self._cell_ids,
        }

    @staticmethod
    def schema():
        return [
            {
                "name": "source_id",
                "type": "STRING",
                "mode": "REQUIRED"
            },
            {
                "name": "source_key",
                "type": "STRING",
                "mode": "REQUIRED"
            },
            {
                "name": "name",
                "type": "STRING",
                "mode": "REQUIRED"
            },
            {
                "name": "observed_at",
                "type": "TIMESTAMP",
                "mode": "REQUIRED"
            },
            {
                "name": "created_at",
                "type": "TIMESTAMP",
                "mode": "REQUIRED"
            },
            {
                "name": "cell_ids",
                "type": "FLOAT",
                "mode": "REPEATED"
            }
        ]
