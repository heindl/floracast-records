#!/usr/bin/env python
# encoding: utf-8

import ee
from ..features.generator import BaseFeatureGenerator, FeatureFetchResult
from ..occurrences.compiler import OccurrenceCompiler
from ..occurrences.bigquery import CompileOccurrenceQuery
from ..geo.cells import GeoJSONFeatureFromCellId
from ..utils import backport
from typing import List, Tuple, Union
import collections

class Landcover(BaseFeatureGenerator):

    @staticmethod
    def table_name():
        return 'LandCover'

    @staticmethod
    def schema():
        return [
            {
                "name": "cell_id",
                "type": "FLOAT",
                "mode": "REQUIRED"
            },
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
                        "name": "count",
                        "type": "INTEGER",
                        "mode": "REQUIRED"
                    },
                ],
            },
            {
                "name": "created_at",
                "type": "TIMESTAMP",
                "mode": "REQUIRED"
            }
        ]

    @staticmethod
    def query(table):
        return CompileOccurrenceQuery(table)

    @staticmethod
    def is_complete(o): # type: (OccurrenceCompiler) -> bool
        return o.get_feature('landcover') is not None

    @staticmethod
    def partition_key(o): # type: (OccurrenceCompiler) -> str
        return str(o.cell_id().parent(7))

    @staticmethod
    def combine(t):
        # type: (Tuple[Tuple[str, str], List[OccurrenceCompiler]]) -> Union[None, OccurrenceCompiler]

        _, occurrences = t

        features = [o.get_feature('landcover') for o in occurrences]

        res = {}
        for feature in features:
            # Important that all cells are accounted for.
            if feature is None:
                return None
            for id, count in feature:
                if id in res:
                    res[id] += count
                else:
                    res[id] = count
        o = occurrences[0]
        o.set_feature('landcover', res)
        return o

    @staticmethod
    def fetch(occurrences): # type: (List[OccurrenceCompiler]) -> FeatureFetchResult

        unique_cell_ids = set([r.cell_id() for r in occurrences])

        fc = ee.FeatureCollection(
            [GeoJSONFeatureFromCellId(c) for c in unique_cell_ids]
        )

        img = ee.Image('ESA/GLOBCOVER_L4_200901_200912_V2_3').select('landcover')
        regions = img.reduceRegions(
            reducer=ee.Reducer.toList().setOutputs(['landcover']),
            collection=fc,
        )

        bigquery_values = []

        for f in regions.getInfo()['features']:
            props = f['properties']
            value = dict(collections.Counter(props['landcover']))

            bigquery_values.append({
                'cell_id': int(props['cell_id']),
                'created_at': backport.timestamp_from_now(),
                'landcover': value,
            })
            for o in occurrences:
                if o.cell_id().ToToken() == props['cell_id']:
                    o.set_feature('landcover', value)

        return FeatureFetchResult(
            bigquery_records=bigquery_values,
            occurrences = occurrences
        )
