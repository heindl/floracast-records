#!/usr/bin/env python
# encoding: utf-8

import ee
from florecords.features.request import FeatureRequest
from florecords.features.generator import BaseFeatureGenerator

class Terrain(BaseFeatureGenerator):

    def __init__(self):
        ee.Initialize()

    def schema(self):
        return [
            ('slope', 'float'),
            ('aspect', 'float'),
            ('elevation', 'float'),
        ]

    def fan_out(self,
                request # type: FeatureRequest
    ):
        yield request

    def partition_key(
            self,
            request, # type: FeatureRequest
    ):
        return request.s2_cell_id(4)

    def fetch(
            self,
            requests, # type: List[FeatureRequest]
    ):

        fc = ee.FeatureCollection([r.as_geojson_feature() for r in requests])
        bounds = fc.geometry().buffer(1000)

        elevation = ee.Image('CGIAR/SRTM90_V4').clip(bounds)

        terrain = ee.Terrain.products(elevation)
        terrain = terrain.select([
            'slope',
            'aspect',
            'elevation'
        ])

        regions = terrain.reduceRegions(
            reducer=ee.Reducer.mean(),
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
                    for k in ['elevation', 'slope', 'aspect']:
                        r.set_feature(k, props[k])
                    yield r
                    break