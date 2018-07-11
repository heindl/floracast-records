#!/usr/bin/env python
# encoding: utf-8

from google.cloud import firestore
from datetime import datetime
from ..utils import backport

firestore_collection = u'OccurrenceFetchHistory'

class SyncHistory(object):
    def __init__(self,
                 family, # type: str
                 fetched_at, # type: float
                 source, # type: str
                 ):
        self.family = family
        self.source = source
        self.fetched_at = fetched_at

def FetchOccurrenceSyncHistory(project, source, restrict_families=None):

    if restrict_families is not None:
        restrict_families = [s.lower() for s in restrict_families]

    collection = firestore \
        .Client(project=project) \
        .collection(backport.as_unicode(firestore_collection)) \
        .where(u'source', u'==', backport.as_unicode(source))

    # if limit is not None:
    #     collection = collection.limit(limit)

    # Originally this was a generator but having some issues with beam
    # not receiving all values.
    for doc in collection.get():
        s = SyncHistory(**doc.to_dict())
        if restrict_families is not None and s.family.lower() not in restrict_families:
            continue
        yield s

def RegisterOccurrenceSync(
        project, # type: str
        family, # type: str
        source, # type: str
        fetched_at=None, # type: float
):
    assert family is not None and len(family) > 0
    assert source is not None and len(source) > 0
    key = backport.quote_encode_string('%s|%s' % (source, family))

    if fetched_at is None:
        fetched_at = backport.timestamp(datetime.utcnow())

    collection = firestore.Client(project=project).collection(firestore_collection)
    collection.document(key).set({
        'source': source,
        'family': family,
        'fetched_at': fetched_at
    })

if __name__ == '__main__':
    from ..occurrences.fetch import OCCURRENCE_SOURCES
    from ..utils import default_project

    for src in OCCURRENCE_SOURCES:
        RegisterOccurrenceSync(
            project=default_project(),
            source=src,
            family='amanitaceae',
            fetched_at=backport.timestamp(datetime.strptime("2002-01-01", "%Y-%m-%d"))
        )

    for src in OCCURRENCE_SOURCES:
        for h in FetchOccurrenceSyncHistory(default_project(), src):
            print(h.source, h.family, h.fetched_at)
