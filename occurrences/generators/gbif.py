#!/usr/bin/env python
# encoding: utf-8

from pygbif import occurrences, species
import pandas as pd
from .. import Occurrence
from ...utils import TimeStamp
from .base import _BaseOccurrenceGenerator
from typing import Dict

gbif_fields = [
    # "acceptedNameUsage",
    # "accessRights",
    # "basisOfRecord",
    # "bibliographicCitation",
    # "catalogNumber",
    # "class",
    # "classKey",
    # "collectionCode",
    # "collectionID",
    # "continent",
    "coordinateUncertaintyInMeters",
    # "country",
    # "countryCode",
    # "county",
    # "crawlId",
    # "datasetID",
    # "datasetKey",
    # "datasetName",
    # "dateIdentified",
    # "day",
    "decimalLatitude",
    "decimalLongitude",
    # "elevation",
    # "elevationAccuracy",
    # "endDayOfYear",
    "eventDate",
    # "extensions",
    # "facts",
    "family",
    # "familyKey",
    "gbifID",
    # "genericName",
    # "genus",
    # "genusKey",
    # "geodeticDatum",
    # "georeferenceProtocol",
    # "georeferenceSources",
    # "georeferencedBy",
    # "georeferencedDate",
    # "habitat",
    # "http://unknown.org/http_//rs.gbif.org/terms/1.0/Multimedia",
    # "http://unknown.org/http_//rs.tdwg.org/dwc/terms/Identification",
    # "identificationQualifier",
    # "identificationRemarks",
    # "identifier",
    # "identifiers",
    # "institutionCode",
    # "institutionID",
    # "issues",
    # "key",
    # "kingdom",
    # "kingdomKey",
    # "language",
    # "lastCrawled",
    # "lastInterpreted",
    # "lastParsed",
    # "license",
    # "locality",
    # "locationRemarks",
    "modified",
    # "month",
    # "municipality",
    # "nomenclaturalCode",
    # "occurrenceID",
    # "occurrenceRemarks",
    # "order",
    # "orderKey",
    # "ownerInstitutionCode",
    # "phylum",
    # "phylumKey",
    # "preparations",
    # "protocol",
    # "publishingCountry",
    # "publishingOrgKey",
    # "recordNumber",
    # "recordedBy",
    # "references",
    # "relations",
    # "rightsHolder",
    "scientificName",
    # "species",
    # "speciesKey",
    # "specificEpithet",
    # "startDayOfYear",
    # "stateProvince",
    # "taxonKey",
    # "taxonRank",
    # "type",
    # "verbatimElevation",
    # "verbatimEventDate",
    # "year",
]

class _Generator(_BaseOccurrenceGenerator):

    @staticmethod
    def source_key():
        return 'gbif'

    def generate(self):
        offset = 0
        family_key = self._family_key()

        while True:

            j = occurrences.search(
                eventDate="%s,%s" % (
                    TimeStamp.format(self._observed_after, "%Y-%m-%d"),
                    TimeStamp.format(self._observed_before, "%Y-%m-%d"),
                ),
                decimalLongitude="%f,%f" % (self._min_x, self._max_x),
                decimalLatitude="%f,%f" % (self._min_y, self._max_y),
                # Using year month here because narrowing
                modified="%s,%s" % (
                    TimeStamp.format(self._updated_after, "%Y-%m-%d"),
                    TimeStamp.format(self._updated_before, "%Y-%m-%d"),
                ),
                taxonKey=family_key,
                hasCoordinate=True,
                offset=offset,
                fields=tuple(gbif_fields)
            )

            if 'results' not in j:
                raise IOError("Results expected for all GBIF requests")

            offset += len(j['results'])

            for record in self._parse_results(j['results']):
                yield Occurrence(**record)

            if j['endOfRecords'] is True:
                break

    def _parse_results(
            self,
            results, # type: Dict
    ):

        df = pd.DataFrame.from_records(results, columns=gbif_fields)

        df.rename(columns={
            'scientificName': 'name',
            'eventDate': 'observed_at',
            'modified': 'modified_at',
            'coordinateUncertaintyInMeters': 'coord_uncertainty',
            'decimalLatitude': 'lat',
            'decimalLongitude': 'lng',
            'gbifID': 'source_id',
            # 'lastInterpreted': 'modified'
        }, inplace=True)

        df = df.assign(source = lambda x: 'gbif')

        # Convert to EpochTime
        df['observed_at']  = pd.to_datetime(df['observed_at'])
        df['observed_at'] = (df['observed_at'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

        df['modified_at']  = pd.to_datetime(df['modified_at'])
        df['modified_at'] = (df['modified_at'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

        df = self.filter_occurrence_dataframe(df)

        for record in df.to_dict('records'):
            yield record


    def _get_family_key(self):
        if self._family is None or self._family.strip() == '':
            raise ValueError("Invalid family name in GBIF taxon family key request")

        res = species.name_lookup(q=self._family, rank='family')

        if res is None or 'results' not in res or len(res['results']) == 0:
            raise ValueError("Missing GBIF results for GBIF taxon family key query")

        first_result = res['results'][0]

        if 'nubKey' not in first_result or first_result['nubKey'] == 0:
            raise ValueError("Invalid 'nubKey' for GBIF taxon family key query")

        return first_result['nubKey']
