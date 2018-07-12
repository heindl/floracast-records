#!/usr/bin/env python
# encoding: utf-8

import requests
import pandas as pd
from io import StringIO
import json
from .base import _BaseOccurrenceGenerator
from ..occurrence import Occurrence
from ...utils import TimeStamp

fields = [
    "id",
    # "institutionCode",
    # "collectionCode",
    # "ownerInstitutionCode",
    # "basisOfRecord",
    # "occurrenceID",
    # "catalogNumber",
    # "otherCatalogNumbers",
    # "kingdom",
    # "phylum",
    # "class",
    # "order",
    "family",
    "scientificName",
    # "taxonID",
    # "scientificNameAuthorship",
    # "genus",
    # "specificEpithet",
    # "taxonRank",
    # "infraspecificEpithet",
    # "identifiedBy",
    # "dateIdentified",
    # "identificationReferences",
    # "identificationRemarks",
    # "taxonRemarks",
    # "identificationQualifier",
    # "typeStatus",
    # "recordedBy",
    # "recordedByID",
    # "associatedCollectors",
    # "recordNumber",
    "eventDate",
    # "year",
    # "month",
    # "day",
    # "startDayOfYear",
    # "endDayOfYear",
    # "verbatimEventDate",
    # "occurrenceRemarks",
    # "habitat",
    # "substrate",
    # "host",
    # "verbatimAttributes",
    # "fieldNumber",
    # "informationWithheld",
    # "dataGeneralizations",
    # "dynamicProperties",
    # "associatedTaxa",
    # "reproductiveCondition",
    # "establishmentMeans",
    # "cultivationStatus",
    # "lifeStage",
    # "sex",
    # "individualCount",
    # "samplingProtocol",
    # "samplingEffort",
    # "preparations",
    # "country",
    # "stateProvince",
    # "county",
    # "municipality",
    # "locality",
    # "locationRemarks",
    # "localitySecurity",
    # "localitySecurityReason",
    "decimalLatitude",
    "decimalLongitude",
    # "geodeticDatum",
    "coordinateUncertaintyInMeters",
    # "verbatimCoordinates",
    # "georeferencedBy",
    # "georeferenceProtocol",
    # "georeferenceSources",
    # "georeferenceVerificationStatus",
    # "georeferenceRemarks",
    # "minimumElevationInMeters",
    # "maximumElevationInMeters",
    # "minimumDepthInMeters",
    # "maximumDepthInMeters",
    # "verbatimDepth",
    # "verbatimElevation",
    # "disposition",
    # "language",
    # "recordEnteredBy",
    "modified",
    # "sourcePrimaryKey-dbpk",
    # "collId",
    # "recordId",
    # "references",
]

class _Generator(_BaseOccurrenceGenerator):

    @staticmethod
    def source_key():
        return 'mycoportal'

    def generate(self):

        content = self._fetch()

        if content is None:
            return

        df = pd.read_csv(
            StringIO(content),
            header=0,
            usecols=fields,
            parse_dates=False,
            encoding='utf-8'
            # index_col='id'
        )

        df.rename(columns={
            'scientificName': 'name',
            'eventDate': 'observed_at',
            'modified': 'modified_at',
            'decimalLatitude': 'lat',
            'decimalLongitude': 'lng',
            'coordinateUncertaintyInMeters': 'coord_uncertainty',
            'id': 'source_id'
        }, inplace=True)

        df = df.assign(source = lambda x: 'mycoportal')

        # Convert to EpochTime
        df['observed_at']  = pd.to_datetime(df['observed_at'])
        df['observed_at'] = (df['observed_at'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

        try:
            df['modified_at']  = pd.to_datetime(df['modified_at'])
        except:
            df = df.assign(modified_at = lambda x: pd.Timestamp.now())

        df['modified_at'] = (df['modified_at'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

        df = self.filter_occurrence_dataframe(df)

        for record in df.to_dict('records'):
            yield Occurrence(**record)


    def _fetch(self):

        q = {
            'llbound': "%f;%f;%f;%f" % (self._max_y, self._min_y, self._min_x, self._max_x),
            "usethes": True,
            "taxontype": "1",
            "db": "all",
            "eventdate1": TimeStamp.format(self._observed_after, "%Y-%m-%d"),
            "eventdate2": TimeStamp.format(self._observed_before, "%Y-%m-%d"),
            "taxa": self._family
        }

        payload = {
            'schema': 'symbiota',
            'format': 'csv',
            'cset': 'iso-8859-1',
            'publicsearch': 1,
            'taxonFilterCode': 0,
            'jsoncollstarr': json.dumps({"db":"all"}),
            'starr': json.dumps(q),
            'submitaction': 'Download Data',
        }

        content = requests.post(
            'http://mycoportal.org/portal/collections/download/downloadhandler.php',
            data=payload
        ).text

        if len(content) == 0:
            return None

        return content
