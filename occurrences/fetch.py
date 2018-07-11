#!/usr/bin/env python
# encoding: utf-8

from ..occurrences.fetchers.utils import FetchParams
from ..occurrences.fetchers import gbif, idigb, inat, mycp, muob
import logging
from typing import List
import itertools

callers = {
    'gbif': gbif.FetchOccurrences,
    'idigbio': idigb.FetchOccurrences,
    'inaturalist': inat.FetchOccurrences,
    'mushroomobserver': muob.FetchOccurrences,
    'mycoportal': mycp.FetchOccurrences,
}

OCCURRENCE_SOURCES = callers.keys()

def FetchOccurrences(
        params, # type: FetchParams,
        sources, # type: List[str]
):
    chained = []
    for source in sources:
        if source not in callers:
            raise ValueError("Invalid Occurrence Fetch Source")
        chained.append(callers.get(source)(params))

    c = 0
    for r in itertools.chain(*chained):
        yield r
        c += 1

    logging.info("Occurrences [%d] fetched for sources [%s] and family [%s]", c, sources, params.family)
