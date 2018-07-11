#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime
import time as mod_time

try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

def timestamp(
        dt, # type: datetime
):
    try:
        return int(dt.timestamp())
    except:
        return int(mod_time.mktime(dt.timetuple()) + dt.microsecond / 1e6)

def timestamp_from_date(y, m, d):
    dt = datetime.utcnow().replace(y, m, d, 0, 0, 0, 0)
    return timestamp(dt)

def timestamp_from_now():
    dt = datetime.utcnow()
    return timestamp(dt)


def quote_encode_string(
        str, # type: str
):
    return quote_plus(str)

def as_unicode(s):
    # return s.decode('utf-8')
    try:
        return s.decode('utf-8')
    except:
        return s
