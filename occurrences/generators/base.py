#!/usr/bin/env python
# encoding: utf-8

import pandas
import constants
consts = constants.Constants()
from utils import TimeStamp
from .. import Occurrence, NorthAmericanMacroFungiFamilies
import abc, six
from typing import Generator, Union

@six.add_metaclass(abc.ABCMeta)
class BaseOccurrenceGenerator(object):
    __metaclass__  = abc.ABCMeta

    def __init__(self,
                 family, # type: str
                 min_x=consts['min_x'], # type: float
                 max_x=consts['max_x'], # type: float
                 min_y=consts['min_y'], # type: float
                 max_y=consts['max_y'], # type: float
                 observed_after=consts['minimum_occurrence_observed_timestamp'], # type: int
                 observed_before=TimeStamp.from_now(), # type: int
                 updated_after=consts['minimum_occurrence_observed_timestamp'], # type: int
                 updated_before=TimeStamp.from_now(), # type: int
        ):
            self._family = family
            self._min_x = min_x
            self._max_x = max_x
            self._min_y = min_y
            self._max_y = max_y
            self._observed_after=observed_after
            self._observed_before=observed_before
            self._updated_after=updated_after
            self._updated_before=updated_before

            if self._family not in NorthAmericanMacroFungiFamilies:
                raise ValueError("Invalid occurrence family: %s" % self.family)

    def filter_occurrence_dataframe(self, df): # type: (pandas.DataFrame) -> pandas.DataFrame

        given_columns = df.columns.values

        for expected in [
            'name',
            'lat',
            'lng',
            'observed_at',
            'modified_at',
            'source_id',
            'family',
            'source_key'
        ]:
            if expected not in given_columns:
                raise ValueError("Missing expected DataFrame column: %s" % expected)

        df.dropna(subset=[
            'name',
            'lat',
            'lng',
            'observed_at',
            'source_id'
        ], inplace=True)

        df = df.assign(
            family = df.family.str.lower(),
            source_id = df.source_id.astype(dtype=str),
            # modified = df.modified.str.slice(0, 10),
            # date = df.date.str.slice(0, 10),
        )

        df = df[
            df.family.str.match(self._family, case=False) &
            (self._updated_after <= df.modified_at) &
            (df.modified_at <= self._updated_before) &
            (df.lat <= self._max_y) &
            (df.lat >= self._min_y) &
            (df.lng <= self._max_x) &
            (df.lng >= self._min_x) &
            (df.observed_at >= self._observed_after) &
            (df.observed_at <= self._observed_before)
            ]

        # Encode lat/lng to preserve precision
        # df = df.assign(
        #     lat = df.lat.astype(dtype=str),
        #     lng = df.lng.astype(dtype=str),
        # )

        return df

    @staticmethod
    @abc.abstractmethod
    def source_key():
        # type: () -> str
        """
        Returns static name of table
        """
        raise NotImplementedError

    @abc.abstractmethod
    def generate(self):
        # type: () -> Generator[Union[None, Occurrence]]
        """
        Returns static name of table
        """
        raise NotImplementedError