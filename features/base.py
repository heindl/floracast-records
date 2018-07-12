#!/usr/bin/env python
# encoding: utf-8

from occurrences import Occurrence
# Outlines required methods
import abc, six
from typing import Dict, Tuple, Union, List, NamedTuple
import ee
import google.auth
import os

@six.add_metaclass(abc.ABCMeta)
class BaseFeatureGenerator(object):
    __metaclass__  = abc.ABCMeta

    def __init__(self):
        if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is not None:
            credentials, project_id = google.auth.default()
            ee.Initialize(credentials=credentials)
        else:
            ee.Initialize() # Local authentication

    @staticmethod
    @abc.abstractmethod
    def table_name(): # type: () -> str
        """
        Returns static name of table
        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def query(table): # type: (str) -> str
        """
        Return BigQuery request string that joins with class feature table data.
        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def combine(t):
        # type: (Tuple[Tuple[str, str], List[Occurrence]]) -> Union[None, Occurrence]
        """
        Returns static name of table
        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def is_complete(o): # type: (Occurrence) -> bool
        """
        Checks that an occurrence already has the expected feature
        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def schema(): # type: () -> List[Dict]
        """
        Return an array of schema column definitions for class table
        """
        raise NotImplementedError


    @staticmethod
    @abc.abstractmethod
    def partition_key(occurrence): # type: (Occurrence) -> Union[Tuple[str, str], str]
        """
           Return a key to group feature requests for efficient processing by the generator.
           In most cases, each fetcher will request one date.
           """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def fetch(occurrences): # type: (List[Occurrence]) -> FeatureResponse
        """
        Generate new features for each request
        The first result
        """
        raise NotImplementedError

FeatureResponse = NamedTuple("FeatureResponse", [
    ('bigquery_records', List[Dict]),
    ('occurrences', List[Occurrence])
])

# class FeatureFetchResult(NamedTuple):
#     bigquery_records: List[Dict]
#     occurrences: List[OccurrenceCompiler]