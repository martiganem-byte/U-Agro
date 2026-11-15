import requests

from shapely.geometry import shape, mapping
from shapely.ops import transform
from pyproj import Transformer


MGAP_URL = (
    "https://mapas.mgap.gub.uy/arcgis/rest/services/"
    "SNIA_Temas/Parcelas_catastrales/MapServer/0/query"
)


class ParcelServiceError(Exception):
    pass


def find_rural_parcels(department, parcel_number):

    where = (
        f"PADRON = {parcel_number} "
        f"AND NOMDEPTO = '{department}'"
    )

    params = {
        "where": where,
        "outFields": (
            "PADRON,NOMDEPTO,CODDEPTO,"
            "SECCAT,AREAHA,AREAMC"
        ),
        "returnGeometry": "true",
        "outSR": 4326,
        "f": "geojson"
    }

    try:
        response = requests.get(
            MGAP_URL,
            params=params,
            timeout=25
        )

        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as error:
        raise ParcelServiceError(
            "Could not communicate with MGAP"
        ) from error

    if "error" in data:
        raise ParcelServiceError(
            "MGAP returned an error"
        )

    features = data.get("features", [])

    if not features:
        return []

    # Coordinate transformations
    to_utm = Transformer.from_crs(
        "EPSG:4326",
        "EPSG:32721",
        always_xy=True
    )

    to_wgs84 = Transformer.from_crs(
        "EPSG:32721",
        "EPSG:4326",
        always_xy=True
    )

    results = []

    for feature in features:

        geometry = shape(feature["geometry"])

        # Calculate centroid in projected coordinates
        geometry_utm = transform(
            to_utm.transform,
            geometry
        )

        centroid_utm = geometry_utm.centroid

        # Convert centroid back to longitude/latitude
        centroid = transform(
            to_wgs84.transform,
            centroid_utm
        )

        results.append({
            "properties": feature.get("properties", {}),
            "geometry": mapping(geometry),
            "centroid": {
                "longitude": centroid.x,
                "latitude": centroid.y,
                "coordinates": [
                    centroid.x,
                    centroid.y
                ]
            }
        })

    return results
