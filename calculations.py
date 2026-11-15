from landsat_stac import obtener_bandas_landsat


def calculate_indices(geojson, fecha_inicio, fecha_fin):

    # Obtener las bandas de Landsat
    resultado = obtener_bandas_landsat(
        geojson,
        fecha_inicio,
        fecha_fin
    )

    # Extraer las estadísticas
    estadisticas = resultado["estadisticas"]

    red = estadisticas["red"]["media"]
    nir = estadisticas["nir"]["media"]
    swir = estadisticas["swir"]["media"]

    # Calcular los índices
    ndvi = calculate_ndvi(nir, red)
    ndmi = calculate_ndmi(nir, swir)

    return {
        "ndvi": ndvi,
        "ndmi": ndmi,
        "resultado": resultado
    }


def calculate_ndvi(nir, red):
    if nir is None or red is None or nir + red == 0:
        return None

    return (nir - red) / (nir + red)


def calculate_ndmi(nir, swir):
    if nir is None or swir is None or nir + swir == 0:
        return None

    return (nir - swir) / (nir + swir)
