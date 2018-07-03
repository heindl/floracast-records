#!/usr/bin/env python
# encoding: utf-8

import requests
import pandas as pd
from io import StringIO
import json
from florecords.occurrences.struct import Occurrence
from florecords.occurrences.fetchers.utils import FilterOccurrenceDataframe, FetchParams

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

def FetchOccurrences(
        params # type: FetchParams
):

    content = _fetch(params)

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
        'eventDate': 'date',
        'decimalLatitude': 'lat',
        'decimalLongitude': 'lng',
        'coordinateUncertaintyInMeters': 'coord_uncertainty'
    }, inplace=True)

    df = df.assign(source = lambda x: 'mycoportal')

    df = FilterOccurrenceDataframe(df, params)

    for record in df.to_dict('records'):
        yield Occurrence(**record)


def _fetch(
        params # type: FetchParams
):

    q = {
        'llbound': "%f;%f;%f;%f" % (params.max_y, params.min_y, params.min_x, params.max_x),
        "usethes": True,
        "taxontype": "1",
        "db": "all",
        "eventdate1": params.observed_after,
        "eventdate2": params.observed_before,
        "taxa": params.family
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