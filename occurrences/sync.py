#!/usr/bin/env python
# encoding: utf-8

from google.cloud import firestore
from datetime import datetime
import logging

firestore_collection = 'OccurrenceFetchHistory'

class SyncHistory(object):
    def __init__(self, source, family, dt):
        self.family = family
        self.source = source
        self.date = dt.strftime('%Y-%m-%d')

def FetchOccurrenceSyncHistory(project, limit=None):

    collection = firestore \
        .Client(project=project) \
        .collection(firestore_collection)

    if limit is not None:
        collection = collection.limit(limit)

    # Originally this was a generator but having some issues with beam
    # not receiving all values.
    records = []
    for doc in collection.get():
        s = doc.id.split("+")
        records.append(SyncHistory(
            source=s[0],
            family=s[1],
            dt=doc.to_dict()['t']
        ))
    logging.info("Occurrence sync records delivered: %d", len(records))
    return records

def RegisterOccurrenceSync(
        project, # type: str
        family, # type: str
        source, # type: str
        dt=None, # type: datetime
):
    assert family is not None and len(family) > 0
    assert source is not None and len(source) > 0
    key = '%s+%s' % (source, family)

    if dt is None:
        dt = datetime.now()

    collection = firestore.Client(project=project).collection(firestore_collection)
    collection.document(key).set({'t': dt})

if __name__ == '__main__':
    from pyflora.occurrences.combined import OCCURRENCE_SOURCES
    from pyflora.cloud.utils import default_project

    for src in OCCURRENCE_SOURCES:
        RegisterOccurrenceSync(
            project=default_project(),
            source=src,
            family='amanitaceae',
            dt=datetime.strptime("2002-01-01", "%Y-%m-%d")
        )

    for h in FetchOccurrenceSyncHistory(default_project()):
        print(h.source, h.family, h.date)