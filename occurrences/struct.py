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
    def __init__(self,
                 id, # type: str
                 name, # type: str
                 observation_datetime, # type: datetime
                 coord_uncertainty, # type: Union[float, numpy.nan]
                 lat, # type: float
                 lng, # type: float
                 source, # type: str
                 family, # type: str
                 **kwargs
                 ):

        self._id = id
        self._name = name.encode('utf-8', 'replace')
        self._observation_datetime = observation_datetime
        self._latitude = lat
        self._longitude = lng
        self._family = family
        self._coordinate_uncertainty = None if numpy.isnan(coord_uncertainty) else coord_uncertainty
        self._source = source
        self._created_at = datetime.utcnow()
        self._validate()

    def _validate(self):
        assert len(self._id) > 0, "Invalid occurrence id"
        assert len(self._name) > 0, "Invalid occurrence scientific name"
        assert self._observation_datetime > datetime.strptime("2000-01-01", '%Y-%m-%d')
        assert self._observation_datetime.tzname() == 'UTC'

        assert (-90 < self._latitude < 90), "Invalid Latitude: %d" % self._latitude
        assert (-180 < self._longitude < 180), "Invalid Longitude: %d" % self._longitude
        if self._family not in NorthAmericanMacroFungiFamilies:
            raise ValueError("Unrecognized fungi family: %s" % self._family)
        if self._source not in ['idigbio', 'gbif', 'inaturalist', 'mushroomobserver', 'mycoportal']:
            raise ValueError("Invalid source: %s", self._source)


    def observation_datetime(self):
        return self._observation_datetime

    def observation_datestring(self):
        return self._observation_datetime.strftime('%Y-%m-%d')

    def key_name_temporal_geospatial(self):
        return self.key_temporal_geospatial + self.observation_datestring()

    def key_temporal_geospatial(self):
        return self.normalized_location() + self.observation_datestring()

    def key_id(self):
        return self._id, self._source

    def normalized_location(self):
        return FormatCoordinates(self._latitude, self._longitude, self._coordinate_uncertainty)

    @staticmethod
    def schema():
        return [
            ('source', 'string', 'required'),
            ('source_id', 'string', 'required'),
            ('scientific_name', 'string', 'required'),
            ('family', 'string', 'required'),
            ('observation_datetime', 'datetime', 'required'),
            # ('cell_id', 'int', 'required'),
            ('latitude', 'float', 'required'),
            ('longitude', 'float', 'required'),
            ('coordinate_uncertainty', 'float', 'nullable'),
            ('created_at', 'datetime', 'required')
        ]

    def to_bigquery(self):
        res = {}
        for s in self.schema():
            k = s[0]
            res[k] = self.__getattribute__("_"+k)
        return res

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
