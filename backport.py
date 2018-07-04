from datetime import datetime
import time as mod_time

def timestamp(
        dt, # type: datetime
):
    try:
        return dt.timestamp()
    except:
        return mod_time.mktime(dt.timetuple()) + dt.microsecond / 1e6