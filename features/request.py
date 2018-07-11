#!/usr/bin/env python
# encoding: utf-8

import ee
import uuid
import json
import datetime
from records.geo.cells import DecodeCellIDAsGeoJSONRectangle

class FeatureRequest():

    def __init__(
            self,
            observed_at, # type: float
            cell_id, # type: int
            occurrence_ids, # type: List[int] # Source, SourceID
    ):
        self._observed_at = observed_at
        self._cell_id = cell_id
        self._occurrence_ids = occurrence_ids
        self._features = {}

    def cell_id(self):
        return self._cell_id

    def __repr__(self):
        return json.dumps({
            'observed_at': str(datetime.datetime.fromtimestamp(self._observed_at)),
            'cell_id': self._cell_id,
            'occurrence_ids': self._occurrence_ids,
            'features': self._features,
        })

    def set_feature(self, key, value):
        assert isinstance(key, str)
        assert len(key.strip()) > 0
        self._features[key] = value

    def get_feature(self, key):
        assert isinstance(key, str)
        assert len(key.strip()) > 0
        return self._features[key]

    def as_geojson_feature(self):
        return ee.Feature(
            geom=ee.Geometry.Rectangle(
                coords=DecodeCellIDAsGeoJSONRectangle(self._cell_id),
                proj='EPSG:4326',
                geodesic=True,
            ),
            opt_properties=ee.Dictionary({
                "cell_id": str(self._cell_id) # Note this will error if not a string.
            }),
        )
