#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime
import time as mod_time

try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

class TimeStamp():

    @staticmethod
    def format(i, fmt): # type: (int, str) -> str
        return datetime.fromtimestamp(i).strftime(fmt)

    @staticmethod
    def from_datetime(dt): # type: (datetime) -> int
        try:
            return int(dt.timestamp())
        except:
            return int(mod_time.mktime(dt.timetuple()) + dt.microsecond / 1e6)

    @classmethod
    def from_date(cls, y, m, d): # type: (int, int, int) -> int
        return TimeStamp.from_datetime(
            datetime.utcnow().replace(y, m, d, 0, 0, 0, 0)
        )

    @staticmethod
    def from_now(): # type: () -> int
        return TimeStamp.from_datetime(
            datetime.utcnow()
        )


def quote_encode_string(
        str, # type: str
):
    return quote_plus(str)

# def as_unicode(s):
#     # return s.decode('utf-8')
#     try:
#         return s.decode('utf-8')
#     except:
#         return s
