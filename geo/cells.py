from geographiclib.geodesic import Geodesic
WGS84 = Geodesic.WGS84
from s2_py import S2LatLng, S2LatLngRect, S2RegionCoverer

def GenerateS2CellIds(
        centre_lat, # type: float
        centre_lng, # type: float
        uncertainty_threshold, # type: float
        s2_cell_level, # type: int
        coordinate_uncertainty=None, # type: Union[None, float]
    ):

    if coordinate_uncertainty > uncertainty_threshold:
        return []

    radius = coordinate_uncertainty / 2 if (coordinate_uncertainty is not None) else 0

    w = WGS84.Direct(centre_lat, centre_lng, 270, radius)['lon2']
    n = WGS84.Direct(centre_lat, centre_lng, 0, radius)['lat2']
    e = WGS84.Direct(centre_lat, centre_lng, 90, radius)['lon2']
    s = WGS84.Direct(centre_lat, centre_lng, 180, radius)['lat2']

    rectangle = S2LatLngRect(
        S2LatLng.FromDegrees(s, w),
        S2LatLng.FromDegrees(n, e),
    )

    # print("area", rectangle.Area() / 12.56637 * 510072000000)

    region = S2RegionCoverer()
    region.set_max_cells(10000) # Irrelevant number but necessary because it appears to cap cells to 8.
    region.set_min_level(s2_cell_level)
    region.set_max_level(s2_cell_level)

    cell_ids = region.GetInteriorCovering(rectangle)
    if len(cell_ids) == 0:
        cell_ids = region.GetCovering(rectangle)

    return [i.id() for i in cell_ids]