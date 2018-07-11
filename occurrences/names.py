#!/usr/bin/env python
# encoding: utf-8

from google.cloud import firestore, exceptions
import requests
from ..utils import backport
import logging

firestore_collection = 'CanonicalNameLabels'

class ScientificNameParser():
    def __init__(self, project):
        self._firestore = firestore.Client(project=project)
        self._cache = {}

    def parse(self, name):
        key = self._encode(name)  # encoding as utf-8 for firestore
        assert len(name) > 0

        # 1. Check in memory cache.
        if key in self._cache:
            return self._cache[key]

        # 2. Check firestore.
        label = self._get_firestore(key)

        # 3. Ping global names parser.
        # Use name instead of key because I do not know how
        # the parser works and capitalization may be a factor.
        if label is None or len(label) == 0:
            label = self._get_global_names(name)
            self._set_firestore(key, label)

        self._cache[key] = label
        self._cache[self._encode(label)] = label
        return label

    def _get_global_names(self, name):

        res = requests.get(
            url='https://parser.globalnames.org/api',
            params={'q': name}
        )

        json_array = res.json()['namesJson']

        if len(json_array) == 0 or 'canonical_name' not in json_array[0] or 'value' not in json_array[0]['canonical_name']:
            logging.warning("Global CanonicalName missing for species [%s]" % name)
            return name

        return json_array[0]['canonical_name']['value'].lower()

    def _encode(self, s):
        return backport.quote_encode_string(s.lower())

    def _get_firestore(
        self,
        key, # type: str
    ):
        try:
            doc = self._firestore \
                .collection(firestore_collection) \
                .document(key) \
                .get()
            return doc.to_dict()["n"]
        except exceptions.NotFound:
            return None

    def _set_firestore(
            self,
            key, # type: str
            label, # type: str
    ):
        """
            Label should be the CanonicalName.
            It will be added twice, once for the search key and again for itself.
            """
        collection = self._firestore.collection(firestore_collection)
        collection.document(key).set({'n': label})
        collection.document(self._encode(label)).set({'n': label})
