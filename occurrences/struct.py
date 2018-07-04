#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime
import numpy
from florecords.occurrences.constants import NorthAmericanMacroFungiFamilies
from florecords.geo.coords import FormatCoordinates

# Note by not using this, the encoding uses pickle and is non-deterministic
# in ordering, which I think should be fine because we're not using it as a key.

# beam.coders.registry.register_coder(Occurrence, OccurrenceCoder)

# class OccurrenceCoder(beam.coders.Coder):
#     def encode(self, o):
#         return '%s|%s|%s|%d|%s|%s|%s' % (
#             o.id,
#             o.name,
#             o.date.strftime('%Y-%m-%d'),
#             o.coord_uncertainty,
#             o.lat,
#             o.lng,
#             o.source
#         )
#
#     def decode(self, s):
#         data = s.split('|')
#         return Occurrence(
#             id=data[0],
#             name=data[1],
#             date=datetime.strptime(data[2], '%Y-%m-%d'),
#             coord_uncertainty=int(data[3]),
#             # Note that lat, lng are strings to preserve precision as long as possible.
#             lat = data[4],
#             lng=data[5],
#             source=data[6],
#         )
#
#     def is_deterministic(self):
#         return True

class Occurrence(object):

    def _validate(self):
        assert isinstance(self._id, int)
        assert len(self._id) > 0, "Invalid occurrence id"

        assert isinstance(self._scientific_name, str)
        assert len(self._scientific_name) > 0, "Invalid occurrence scientific name"

        assert self._observed_at > 0

    def from_bigquery(
            self,
            data # type: Dictionary
    ):
        for k, v in data:
            self.__setattr__('_'+k, v)
        self._validate()
        return self


# if __name__ == '__main__':
#     from geographiclib.geodesic import Geodesic
#     # describe(start_time='2001-01-01', end_time='2001-02-01')
#     bbox = BoundingBox(sw=('33.734','-84.551'))
#     rect = bbox.rectangle()
#     print(rect)
#
#     geod = Geodesic.WGS84
#     g = geod.Inverse(rect[2], rect[3], rect[0], rect[1])
#     print("The distance is {:.3f} m.".format(g['s12']))
