from datetime import date, timedelta

import pandas as pd
import requests


NASA_POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
)

PARAMETERS = [
    "PRECTOTCORR",
    "T2M_MAX",
    "T2M_MIN",
    "T2M",
]


class NASAPowerError(Exception):
    """Error al consultar o procesar datos de NASA POWER."""
    pass


def obtener_periodo_30_anios():
    """
    Calcula un período de 30 años hasta ayer.
    """
    fecha_fin = date.today() - timedelta(days=1)

    try:
        fecha_inicio = fecha_fin.replace(
            year=fecha_fin.year - 30
        )
    except ValueError:
        # Caso especial: 29 de febrero.
        fecha_inicio = fecha_fin.replace(
            year=fecha_fin.year - 30,
            day=28
        )

    return fecha_inicio, fecha_fin


def obtener_datos_nasa_power(latitud, longitud):
    """
    Consulta datos meteorológicos diarios de NASA POWER
    para un punto geográfico durante los últimos 30 años.

    Devuelve un DataFrame con:
    - Precipitación diaria (mm/día).
    - Temperatura máxima (°C).
    - Temperatura mínima (°C).
    - Temperatura media (°C).
    """

    if not -90 <= latitud <= 90:
        raise NASAPowerError("Invalid latitude.")

    if not -180 <= longitud <= 180:
        raise NASAPowerError("Invalid longitude.")

    fecha_inicio, fecha_fin = obtener_periodo_30_anios()

    parametros = {
        "parameters": ",".join(PARAMETERS),
        "community": "AG",
        "longitude": longitud,
        "latitude": latitud,
        "start": fecha_inicio.strftime("%Y%m%d"),
        "end": fecha_fin.strftime("%Y%m%d"),
        "format": "JSON",
        "time-standard": "UTC",
    }

    try:
        respuesta = requests.get(
            NASA_POWER_URL,
            params=parametros,
            timeout=60
        )

        respuesta.raise_for_status()
        datos = respuesta.json()

    except requests.RequestException as error:
        raise NASAPowerError(
            f"Could not connect to NASA POWER: {error}"
        ) from error

    except ValueError as error:
        raise NASAPowerError(
            "NASA POWER returned an invalid response."
        ) from error

    try:
        valores = datos["properties"]["parameter"]

        df = pd.DataFrame({
            nombre: pd.Series(valores[nombre])
            for nombre in PARAMETERS
        })

    except (KeyError, TypeError) as error:
        raise NASAPowerError(
            "The NASA POWER response does not contain "
            "the expected meteorological parameters."
        ) from error

    # Las fechas vienen como YYYYMMDD.
    df.index = pd.to_datetime(
        df.index,
        format="%Y%m%d"
    )

    df.index.name = "date"

    # NASA POWER utiliza -999 para representar datos faltantes.
    df = df.replace(-999, pd.NA)

    df = df.apply(pd.to_numeric, errors="coerce")

    # Nombres más fáciles de utilizar en el resto del programa.
    df = df.rename(columns={
        "PRECTOTCORR": "precipitacion",
        "T2M_MAX": "temperatura_maxima",
        "T2M_MIN": "temperatura_minima",
        "T2M": "temperatura_media",
    })

    return df
