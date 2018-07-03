#!/usr/bin/env python
# encoding: utf-8

import ee
from florecords.features.request import FeatureRequest
from florecords.features.generator import BaseFeatureGenerator

class Landcover(BaseFeatureGenerator):

    def __init__(self):
        ee.Initialize()

    def schema(self):
        return [
            ('landcover', 'string'),
        ]

    def fan_out(
            self,
            request, # type: FeatureRequest
    ):
        yield request

    def partition_key(
            self,
            request, # type: FeatureRequest
    ):
        return request.s2_cell_id(4)

    def database_key_from_request(
            self,
            request, # type: FeatureRequest
    ):
        return request.location()

    def database_key_from_saved(
            self,
            record, # type: Dictionary
    ):
        return record['latitude'], record['longitude'], record['coordinate_uncertainty']

    def fetch(
            self,
            requests, # type: List[FeatureRequest]
    ):

        fc = ee.FeatureCollection([r.as_geojson_feature() for r in requests])
        img = ee.Image('ESA/GLOBCOVER_L4_200901_200912_V2_3')
        regions = img.reduceRegions(
            reducer=ee.Reducer.toList(),
            scale=30,
            # Earth engine complained from this missing,
            # so per the documentation, set it as the first
            # band's projection.
            # crs='EPSG:4326',
            collection=fc,
        )

        for f in regions.getInfo()['features']:
            props = f['properties']
            for r in requests:
                if r.id() == props[FeatureRequest.id_geojson_label()]:
                    r.set_feature('landcover', str(int(props['landcover'])))
                    yield r
                    break