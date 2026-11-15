
from datetime import datetime
import numpy as np
import planetary_computer
import rasterio

from pystac_client import Client
from rasterio.mask import mask
from rasterio.warp import transform_geom


STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION = "landsat-c2-l2"

# Canales que vamos a leer.
ASSETS = {
    "red": "red",
    "nir": "nir08",
    "swir": "swir16",
    "quality": "qa_pixel",
}


class LandsatError(Exception):
    """Error controlado al buscar o leer datos Landsat."""


def preparar_geometria(geojson):
    """Acepta una geometría GeoJSON o un Feature."""

    if geojson.get("type") == "Feature":
        geometry = geojson.get("geometry")

    elif geojson.get("type") in ("Polygon", "MultiPolygon"):
        geometry = geojson

    else:
        raise LandsatError(
            "Se necesita un GeoJSON de tipo Polygon, MultiPolygon o Feature."
        )

    if not geometry or geometry.get("type") not in (
        "Polygon", "MultiPolygon"
    ):
        raise LandsatError("La geometría no es válida.")

    return geometry


def buscar_escena(geometry, fecha_inicio, fecha_fin, max_nubes=50):
    """Busca escenas Landsat 8/9 que intersecten el área."""

    catalog = Client.open(
        STAC_URL,
        modifier=planetary_computer.sign_inplace
    )

    search = catalog.search(
        collections=[COLLECTION],
        intersects=geometry,
        datetime=f"{fecha_inicio}/{fecha_fin}",
        max_items=100
    )

    items = list(search.items())

    # Nos quedamos con Landsat 8 y 9, con nubosidad aceptable
    # y con todos los canales que necesitamos.
    candidatos = []

    for item in items:
        plataforma = item.properties.get("platform", "")
        nubes = item.properties.get("eo:cloud_cover", 100)

        if plataforma not in ("landsat-8", "landsat-9"):
            continue

        if nubes is None or nubes > max_nubes:
            continue

        if not all(key in item.assets for key in ASSETS.values()):
            continue

        candidatos.append(item)

    if not candidatos:
        raise LandsatError(
            "No encontramos escenas con esos criterios. "
            "Probá ampliar las fechas o permitir más nubosidad."
        )

    # Elegimos primero la escena con menor nubosidad.
    # En caso de empate, preferimos la más reciente.
    candidatos.sort(
        key=lambda item: (
            item.properties.get("eo:cloud_cover", 100),
            -(item.datetime.timestamp())
        )
    )

    if candidatos:
        print("ASSETS DISPONIBLES:")
        print(list(candidatos[0].assets.keys()))

    return candidatos[0]


def leer_recorte(item, asset_name, geometry):
    """Lee solamente los píxeles que corresponden al padrón."""

    asset = item.assets[asset_name]

    with rasterio.open(asset.href) as src:
        # El GeoJSON del padrón está expresado en EPSG:4326.
        # Lo transformamos al sistema de coordenadas de la imagen.
        geometry_proyectada = transform_geom(
            "EPSG:4326",
            src.crs,
            geometry
        )

        data, _ = mask(
            src,
            [geometry_proyectada],
            crop=True,
            filled=False
        )

    return np.ma.asarray(data[0], dtype=np.float32)


def calcular_estadisticas(array):
    """Devuelve estadísticas básicas de los píxeles válidos."""

    valores = array.compressed()

    if valores.size == 0:
        return {
            "pixeles_validos": 0,
            "media": None,
            "minimo": None,
            "maximo": None,
        }

    return {
        "pixeles_validos": int(valores.size),
        "media": float(np.mean(valores)),
        "minimo": float(np.min(valores)),
        "maximo": float(np.max(valores)),
    }


def obtener_bandas_landsat(
    geojson,
    fecha_inicio,
    fecha_fin,
    max_nubes=50
):
    """
    Busca una escena y devuelve las bandas recortadas al padrón.

    Las fechas deben tener formato YYYY-MM-DD.
    La geometría debe estar en EPSG:4326.
    """

    try:
        geometry = preparar_geometria(geojson)

        # Validamos el formato de las fechas.
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        datetime.strptime(fecha_fin, "%Y-%m-%d")

        if fecha_inicio > fecha_fin:
            raise LandsatError("La fecha inicial supera la fecha final.")

        item = buscar_escena(
            geometry,
            fecha_inicio,
            fecha_fin,
            max_nubes
        )

        # Leemos la banda de control de calidad.
        qa = leer_recorte(
            item,
            ASSETS["quality"],
            geometry
        )

        # Bits 0 a 5: relleno, nube dilatada, cirrus,
        # nube, sombra de nube y nieve.
        qa_values = np.asarray(qa.filled(0), dtype=np.uint16)
        mascara_nubes = (
            np.ma.getmaskarray(qa)
            | ((qa_values & 0b111111) != 0)
        )

        bandas = {}

        # Leemos las tres bandas espectrales.
        for nombre in ("red", "nir", "swir"):
            raw = leer_recorte(
                item,
                ASSETS[nombre],
                geometry
            )

        # Aplicamos la máscara de nubes y píxeles inválidos.
            mascara = np.ma.getmaskarray(raw) | mascara_nubes

        # Convertimos los valores originales a reflectancia.
            reflectancia = raw * 0.0000275 - 0.2

        # Guardamos la banda procesada.
            bandas[nombre] = np.ma.array(
                reflectancia,
                mask=mascara
            )

            # Calculamos las estadísticas de cada banda.
        estadisticas = {
            nombre: calcular_estadisticas(array)
            for nombre, array in bandas.items()
        }

        print("BANDAS:", list(bandas.keys()))
        print("ESTADÍSTICAS:", estadisticas)

        return {
            "scene_id": item.id,
            "fecha": item.datetime.isoformat(),
            "nubosidad_escena": item.properties.get(
                "eo:cloud_cover"
            ),
            "bandas": bandas,
            "estadisticas": estadisticas,
        }

        return {
            "scene_id": item.id,
            "fecha": item.datetime.isoformat(),
            "nubosidad_escena": item.properties.get(
                "eo:cloud_cover"
            ),
            "bandas": bandas,
            "estadisticas": estadisticas,
        }

    except LandsatError:
        raise

    except Exception as error:
        raise LandsatError(
            f"No se pudieron obtener los datos Landsat: {error}"
        ) from error
