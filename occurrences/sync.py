#!/usr/bin/env python
# encoding: utf-8

from google.cloud import firestore
from ..utils import as_unicode, quote_encode_string, TimeStamp

_firestore_collection = u'OccurrenceFetchHistory'

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
        .collection(as_unicode(_firestore_collection)) \
        .where(u'source', u'==', as_unicode(source))

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
    key = quote_encode_string('%s|%s' % (source, family))

    if fetched_at is None:
        fetched_at = TimeStamp.from_now()

    collection = firestore.Client(project=project).collection(_firestore_collection)
    collection.document(key).set({
        'source': source,
        'family': family,
        'fetched_at': fetched_at
    })

if __name__ == '__main__':
    from .generators import OccurrenceGenerators
    from ..utils import default_project

    for g in OccurrenceGenerators():
        RegisterOccurrenceSync(
            project=default_project(),
            source=g.source_key(),
            family='amanitaceae',
            fetched_at=TimeStamp.from_date(2002, 1, 1)
        )

    for g in OccurrenceGenerators():
        for h in FetchOccurrenceSyncHistory(default_project(), g.source_key()):
            print(h.source, h.family, h.fetched_at)
