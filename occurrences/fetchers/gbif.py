#!/usr/bin/env python
# encoding: utf-8

from pygbif import occurrences, species
import pandas as pd
from florecords.occurrences.struct import Occurrence
from florecords.occurrences.fetchers.utils import FilterOccurrenceDataframe, FetchParams

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

def FetchOccurrences(
    params # type: FetchParams
):
    offset = 0
    family_key = _family_key(params.family)

    while True:

        j = occurrences.search(
            eventDate="%s,%s" % (params.observed_after, params.observed_before),
            decimalLongitude="%f,%f" % (params.min_x, params.max_x),
            decimalLatitude="%f,%f" % (params.min_y, params.max_y),
            # Using year month here because narrowing
            modified="%s,%s" % (params.updated_after, params.updated_before),
            taxonKey=family_key,
            hasCoordinate=True,
            offset=offset,
            fields=tuple(gbif_fields)
        )

        if 'results' not in j:
            raise IOError("Results expected for all GBIF requests")

        offset += len(j['results'])

        for record in _parse_results(j['results'], params):
            yield Occurrence(**record)

        if j['endOfRecords'] is True:
            break



def _parse_results(
        results, # type: Dict
        params, # type: FetchParams
):

    df = pd.DataFrame.from_records(results, columns=gbif_fields)

    df.rename(columns={
        'scientificName': 'name',
        'eventDate': 'date',
        'coordinateUncertaintyInMeters': 'coord_uncertainty',
        'decimalLatitude': 'lat',
        'decimalLongitude': 'lng',
        'gbifID': 'id',
        # 'lastInterpreted': 'modified'
    }, inplace=True)

    df = df.assign(source = lambda x: 'gbif')

    df = FilterOccurrenceDataframe(df, params)

    for record in df.to_dict('records'):
        yield record


def _family_key(family):
    if family is None or family.strip() == '':
        raise ValueError("Invalid family name in GBIF taxon family key request")

    res = species.name_lookup(q=family, rank='family')

    if res is None or 'results' not in res or len(res['results']) == 0:
        raise ValueError("Missing GBIF results for GBIF taxon family key query")

    first_result = res['results'][0]

    if 'nubKey' not in first_result or first_result['nubKey'] == 0:
        raise ValueError("Invalid 'nubKey' for GBIF taxon family key query")

    return first_result['nubKey']
