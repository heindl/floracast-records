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
            {
                "name": "landcover",
                "type": "RECORD",
                "mode": "REPEATED",
                "fields": [
                    {
                        "name": "id",
                        "type": "INTEGER",
                        "mode": "REQUIRED"
                    },
                    {
                        "name": "number",
                        "type": "INTEGER",
                        "mode": "REQUIRED"
                    },
                ],
            } # 8 bytes * number of cells
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
        return request.cell_id()

    def database_key_from_request(
            self,
            request, # type: FeatureRequest
    ):
        return request.cell_id()

    def database_key_from_saved(
            self,
            record, # type: Dictionary
    ):
        return record['cell_id']

    def fetch(
            self,
            requests, # type: List[FeatureRequest]
    ):

        features = [r.as_geojson_feature() for r in requests]

        print(features)

        fc = ee.FeatureCollection(features)

        img = ee.Image('ESA/GLOBCOVER_L4_200901_200912_V2_3').select('landcover')
        regions = img.reduceRegions(
            reducer=ee.Reducer.toList().setOutputs(['landcover']),
            collection=fc,
        )
        for f in regions.getInfo()['features']:
            props = f['properties']
            for r in requests:
                if str(r.cell_id()) == props['cell_id']:
                    r.set_feature('landcover', props['landcover'])
                    yield r
                    break