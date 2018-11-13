#!/usr/bin/env python
# encoding: utf-8


if __name__ == '__main__':
    import os, sys
    os.environ['__CONSTANTS__'] = 'PRODUCTION'
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    print(sys.path)
    from yoccurrences.generators import OccurrenceGenerators, OccurrenceSourceKeys
    from yoccurrences import NorthAmericanMacroFungiFamilies
else:
    from .generators import OccurrenceSourceKeys
    from .taxa import  NorthAmericanMacroFungiFamilies

from google.cloud import firestore
from yutils import quote_encode_string, TimeStamp, default_project
from typing import NamedTuple, Union, List

_firestore_collection = u'OccurrenceFetchHistory'

SyncHistory = NamedTuple("SyncHistory", [
    ('family', str),
    ('fetched_at', int),
    ('source_key', str),
])

def fetch_occurrence_sync_history(project, source_key, restrict_families=None):
    # type: (str, str, Union[List[str], None]) -> List[SyncHistory]

    if source_key not in OccurrenceSourceKeys:
        raise ValueError("Invalid occurrence source key: %s" % source_key)

    if restrict_families is not None:
        restrict_families = [s.lower() for s in restrict_families]

    collection = firestore \
        .Client(project=project) \
        .collection(_firestore_collection) \
        .where('source_key', '==', source_key)

    # if limit is not None:
    #     collection = collection.limit(limit)

    # Originally this was a generator but having some issues with beam
    # not receiving all values.
    res = []
    for doc in collection.get():
        s = SyncHistory(**doc.to_dict())
        if restrict_families is not None and s.family.lower() not in restrict_families:
            continue
        res.append(s)
    return res

def register_occurrence_sync(project, family, source_key, fetched_at=None):
    # type: (str, str, str, Union[int, None]) -> None

    if source_key not in OccurrenceSourceKeys:
        raise ValueError("Invalid occurrence source key: %s" % source_key)

    if family not in NorthAmericanMacroFungiFamilies:
        raise ValueError("Invalid occurrence family: %s" % family)

    key = quote_encode_string('%s|%s' % (source_key, family))

    if fetched_at is None:
        fetched_at = TimeStamp.from_now()

    collection = firestore.Client(project=project).collection(_firestore_collection)
    collection.document(key).set({
        'source_key': source_key,
        'family': family,
        'fetched_at': fetched_at
    })

if __name__ == '__main__':

    for g in OccurrenceGenerators():
        register_occurrence_sync(
            project=default_project(),
            source_key=g.source_key(),
            family='amanitaceae',
            fetched_at=TimeStamp.from_date(2002, 1, 1)
        )

    for g in OccurrenceGenerators():
        for h in fetch_occurrence_sync_history(
                project=default_project(),
                source_key=g.source_key()
        ):
            print(h.source_key, h.family, h.fetched_at)
