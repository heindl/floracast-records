#!/usr/bin/env python
# encoding: utf-8

import ee
from records.features.request import FeatureRequest
from records.features.generator import BaseFeatureGenerator

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
        yield request.cell_id()

    def partition_key(
            self,
            request, # type: FeatureRequest
    ):
        return request.cell_id()

    def fetch(
            self,
            requests, # type: List[FeatureRequest]
    ):

        fc = ee.FeatureCollection([r.as_geojson_feature() for r in requests])

        # Necessary to buffer to select slope from neighboring cells.
        bounds = fc.geometry().buffer(1000)

        elevation = ee.Image('CGIAR/SRTM90_V4').clip(bounds)

        terrain = ee.Terrain.products(elevation)
        terrain = terrain.select([
            'slope',
            'aspect',
            'elevation'
        ])

        regions = terrain.reduceRegions(
            reducer=ee.Reducer.toList().forEachBand(terrain),
            # scale=30,
            # Earth engine complained from this missing,
            # so per the documentation, set it as the first
            # band's projection.
            # crs='EPSG:4326',
            collection=fc,
        )

        print(regions.getInfo())

        return []

        # for f in regions.getInfo()['features']:
        #     props = f['properties']
        #     for r in requests:
        #         if r.cell_id() == props['cell_id']:
        #             for k in ['elevation', 'slope', 'aspect']:
        #                 r.set_feature(k, props[k])
        #             yield r
        #             break
