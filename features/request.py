from florecords.occurrences.struct import Occurrence
import ee
import uuid
import json

class FeatureRequest():

    def __init__(
            self,
            observation_date, # type: str
            latitude,
            longitude,
            coordinate_uncertainty, # type: int
            occurrence_keys, # type: List[Tuple[str, str]] # Source, SourceID
            # Only for testing. An id will be automatically generated
            request_id=None, # type: str
    ):

        self._observation_date = observation_date
        self._latitude = latitude
        self._longitude = longitude
        self._coordinate_uncertainty = coordinate_uncertainty
        self._occurrence_keys = occurrence_keys

        # The request id is necessary because the response
        # coordinates will not necessarily identically match the request coordinates.
        self._request_id = str(uuid.uuid4()) if request_id is None else request_id

        self._features = {}

    def location(self):
        return self._latitude, self._longitude, self._coordinate_uncertainty

    def id(self):
        return self._request_id

    @staticmethod
    def id_geojson_label():
        return 'request_id'

    def __repr__(self):
        return json.dumps({
            'request_id': self._request_id,
            'date': self._observation_date,
            'lat': self._latitude,
            'lng': self._longitude,
            'occurrence_keys': self._occurrence_keys,
            'features': self._features,
        })

    # def s2_cell_id(self, level):
    #     assert isinstance(level, int)
    #     assert level != 0
    #     cell_id = s2sphere.CellId.from_lat_lng(s2sphere.LatLng(self._latitude, self._longitude))
    #     return cell_id.parent(level=level).id()

    def set_feature(self, key, value):
        assert isinstance(key, str)
        assert len(key.strip()) > 0
        self._features[key] = value

    def get_feature(self, key):
        assert isinstance(key, str)
        assert len(key.strip()) > 0
        return self._features[key]

    def as_geojson_feature(self):
        f = ee.Feature(
            geom=ee.Geometry.Point(
                coords=[self._longitude, self._latitude],
                proj='EPSG:4326'
            ),
            # The request id is necessary because the response
            # coordinates will not necessarily identically match the request coordinates.
            opt_properties={self.id_geojson_label(): self._request_id}
        )
        if self._coordinate_uncertainty is not None and self._coordinate_uncertainty > 0:
            f = f.buffer(self._coordinate_uncertainty)
        return f
