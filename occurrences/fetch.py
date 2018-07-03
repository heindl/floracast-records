#!/usr/bin/env python
# encoding: utf-8

from florecords.occurrences.fetchers.utils import FetchParams
from florecords.occurrences.fetchers import gbif, idigb, inat, mycp, muob
import logging

callers = {
    'gbif': gbif.FetchOccurrences,
    'idigbio': idigb.FetchOccurrences,
    'inaturalist': inat.FetchOccurrences,
    'mushroomobserver': muob.FetchOccurrences,
    'mycoportal': mycp.FetchOccurrences,
}

OCCURRENCE_SOURCES = callers.keys()

def FetchOccurrences(
        source, # type: str
        params, # type: FetchParams
):

    if source not in callers:
        raise ValueError("Invalid Occurrence Fetch Source")

    c = 0
    for r in callers.get(source)(params):
        yield r
        c += 1

    logging.info("Occurrences [%d] fetched for source [%s, %s]", c, source, params.family)