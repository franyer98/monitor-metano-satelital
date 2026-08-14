"""Serie de tiempo de concentración de metano atmosférico (Sentinel-5P/TROPOMI)
sobre el área de Campo Rubiales, vía Google Earth Engine.

Dataset: COPERNICUS/S5P/OFFL/L3_CH4 (ESA/Copernicus, público y gratuito,
resolución de revisita ~2 días desde 2019). Earth Engine hace la reducción
espacial (promedio sobre el área de interés) en sus propios servidores; este
módulo solo pide el resultado ya agregado por fecha.
"""
import json
import logging
import time
from datetime import datetime, timedelta, timezone

import ee

from app.config import settings

logger = logging.getLogger("uvicorn.error")

_BANDA = "CH4_column_volume_mixing_ratio_dry_air"
_ee_listo = False

_cache: dict = {"datos": None, "generado_en": None}
_CACHE_TTL_SEGUNDOS = 6 * 3600  # 6 horas — el dataset solo se actualiza cada ~2 días


def _inicializar_ee():
    global _ee_listo
    if _ee_listo:
        return
    if not settings.EE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError(
            "EE_SERVICE_ACCOUNT_JSON no está configurado. Ver README para crear "
            "una cuenta de servicio de Google Earth Engine."
        )
    info = json.loads(settings.EE_SERVICE_ACCOUNT_JSON)
    credenciales = ee.ServiceAccountCredentials(
        info["client_email"], key_data=settings.EE_SERVICE_ACCOUNT_JSON
    )
    ee.Initialize(credenciales, project=settings.EE_PROJECT_ID or info.get("project_id"))
    _ee_listo = True
    logger.info("Google Earth Engine inicializado correctamente.")


def _area_interes() -> "ee.Geometry":
    return ee.Geometry.Rectangle([
        settings.AOI_LON_MIN, settings.AOI_LAT_MIN,
        settings.AOI_LON_MAX, settings.AOI_LAT_MAX,
    ])


def obtener_serie(dias: int = 90, forzar_actualizacion: bool = False) -> list[dict]:
    """Devuelve [{fecha, ch4_ppb}, ...] con el promedio diario de metano sobre
    Campo Rubiales en los últimos `dias` días. Usa una caché en memoria de 6h
    para no golpear Earth Engine en cada visita del dashboard."""
    ahora = time.time()
    if (not forzar_actualizacion and _cache["datos"] is not None
            and ahora - _cache["generado_en"] < _CACHE_TTL_SEGUNDOS):
        return _cache["datos"]

    _inicializar_ee()
    aoi = _area_interes()

    fin = datetime.now(timezone.utc)
    inicio = fin - timedelta(days=dias)

    coleccion = (
        ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CH4")
        .select(_BANDA)
        .filterDate(inicio.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d"))
        .filterBounds(aoi)
    )

    def _reducir(img):
        media = img.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=aoi, scale=7000, maxPixels=1e9
        ).get(_BANDA)
        return ee.Feature(None, {"fecha": img.date().format("YYYY-MM-dd"), "ch4_ppb": media})

    resultado = (
        coleccion.map(_reducir)
        .filter(ee.Filter.notNull(["ch4_ppb"]))
        .getInfo()
    )

    puntos = sorted(
        (
            {"fecha": f["properties"]["fecha"], "ch4_ppb": round(f["properties"]["ch4_ppb"], 2)}
            for f in resultado["features"]
        ),
        key=lambda p: p["fecha"],
    )

    _cache["datos"] = puntos
    _cache["generado_en"] = ahora
    logger.info(f"Serie de metano actualizada: {len(puntos)} puntos en {dias} días.")
    return puntos
