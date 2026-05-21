"""Core functions for treecrown-nz.

This module loads Wellington tree canopy and suburb boundary data,
then calculates canopy coverage and route shade.
"""

from __future__ import annotations

from io import BytesIO
from typing import Optional

import geopandas as gpd
import pandas as pd
import requests


NZTM = "EPSG:2193"

WCC_TREE_COVER_URL = (
    "https://gis.wcc.govt.nz/arcgis/rest/services/"
    "Parks/TreeCover/MapServer/57/query"
)

WCC_SUBURBS_URL = (
    "https://gis.wcc.govt.nz/arcgis/rest/services/"
    "PropertyAndBoundaries/WCC_Boundaries/MapServer/2/query"
)


def _read_arcgis_layer(
    url: str,
    bbox: Optional[tuple[float, float, float, float]] = None,
) -> gpd.GeoDataFrame:
    """Read a public ArcGIS REST layer as GeoJSON.

    Parameters
    ----------
    url : str
        ArcGIS REST query endpoint.
    bbox : tuple of float, optional
        Bounding box in EPSG:2193 as xmin, ymin, xmax, ymax.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame in EPSG:2193.
    """
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": "2193",
    }

    if bbox is not None:
        xmin, ymin, xmax, ymax = bbox
        params.update(
            {
                "geometry": f"{xmin},{ymin},{xmax},{ymax}",
                "geometryType": "esriGeometryEnvelope",
                "inSR": "2193",
                "spatialRel": "esriSpatialRelIntersects",
            }
        )

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    gdf = gpd.read_file(BytesIO(response.content))

    if gdf.empty:
        return gpd.GeoDataFrame(geometry=[], crs=NZTM)

    if gdf.crs is None:
        gdf = gdf.set_crs(NZTM)
    else:
        gdf = gdf.to_crs(NZTM)

    return gdf


def load_canopy(
    bbox: Optional[tuple[float, float, float, float]] = None,
) -> gpd.GeoDataFrame:
    """Load Wellington tree canopy polygons.

    Parameters
    ----------
    bbox : tuple of float, optional
        Bounding box in EPSG:2193 as xmin, ymin, xmax, ymax.

    Returns
    -------
    geopandas.GeoDataFrame
        Tree canopy polygons in EPSG:2193.
    """
    return _read_arcgis_layer(WCC_TREE_COVER_URL, bbox=bbox)


def load_suburbs(
    names: Optional[list[str]] = None,
) -> gpd.GeoDataFrame:
    """Load Wellington suburb boundary polygons.

    Parameters
    ----------
    names : list of str, optional
        Suburb names to keep. If None, all suburbs are returned.

    Returns
    -------
    geopandas.GeoDataFrame
        Suburb boundary polygons in EPSG:2193.
    """
    suburbs = _read_arcgis_layer(WCC_SUBURBS_URL)

    if names is None:
        return suburbs

    name_col = "suburb"

    if name_col not in suburbs.columns:
        raise ValueError("Expected a 'suburb' column in the WCC suburb layer.")

    selected = suburbs[suburbs[name_col].isin(names)].copy()

    if selected.empty:
        raise ValueError("No matching suburbs found. Check spelling and capitalisation.")

    return selected


def canopy_coverage(
    area_gdf: gpd.GeoDataFrame,
    canopy_gdf: Optional[gpd.GeoDataFrame] = None,
) -> gpd.GeoDataFrame:
    """Calculate canopy coverage percentage for each input area.

    Parameters
    ----------
    area_gdf : geopandas.GeoDataFrame
        Area polygons such as suburbs.
    canopy_gdf : geopandas.GeoDataFrame, optional
        Tree canopy polygons. If None, canopy is loaded using area_gdf bounds.

    Returns
    -------
    geopandas.GeoDataFrame
        Copy of area_gdf with area_m2, canopy_area_m2, and canopy_pct.
    """
    if area_gdf.empty:
        raise ValueError("area_gdf is empty.")

    if area_gdf.crs is None:
        raise ValueError("area_gdf must have a CRS.")

    areas = area_gdf.copy().to_crs(NZTM)

    if canopy_gdf is None:
        canopy_gdf = load_canopy(tuple(areas.total_bounds))

    if canopy_gdf.empty:
        areas["area_m2"] = areas.geometry.area
        areas["canopy_area_m2"] = 0.0
        areas["canopy_pct"] = 0.0
        return areas

    canopy = canopy_gdf.copy().to_crs(NZTM)

    area_values = []
    canopy_values = []
    pct_values = []

    for _, row in areas.iterrows():
        geom = row.geometry
        area_m2 = geom.area

        possible = canopy[canopy.intersects(geom)]

        if possible.empty:
            canopy_area_m2 = 0.0
        else:
            clipped = gpd.clip(possible, geom)
            canopy_area_m2 = clipped.geometry.area.sum()

        canopy_pct = (canopy_area_m2 / area_m2) * 100 if area_m2 > 0 else 0.0

        area_values.append(area_m2)
        canopy_values.append(canopy_area_m2)
        pct_values.append(canopy_pct)

    areas["area_m2"] = area_values
    areas["canopy_area_m2"] = canopy_values
    areas["canopy_pct"] = pct_values

    return areas


def route_shade(
    route_gdf: gpd.GeoDataFrame,
    canopy_gdf: Optional[gpd.GeoDataFrame] = None,
    buffer_m: float = 10,
) -> gpd.GeoDataFrame:
    """Estimate tree shade around route segments.

    Parameters
    ----------
    route_gdf : geopandas.GeoDataFrame
        Route line geometries.
    canopy_gdf : geopandas.GeoDataFrame, optional
        Tree canopy polygons. If None, canopy is loaded using route bounds.
    buffer_m : float, default 10
        Buffer distance in metres around each route segment.

    Returns
    -------
    geopandas.GeoDataFrame
        Copy of route_gdf with buffer_area_m2, canopy_area_m2, and shade_pct.
    """
    if route_gdf.empty:
        raise ValueError("route_gdf is empty.")

    if route_gdf.crs is None:
        raise ValueError("route_gdf must have a CRS.")

    if buffer_m <= 0:
        raise ValueError("buffer_m must be greater than zero.")

    route = route_gdf.copy().to_crs(NZTM)

    if canopy_gdf is None:
        route_buffer = route.geometry.buffer(buffer_m)
        bbox = tuple(gpd.GeoSeries(route_buffer, crs=NZTM).total_bounds)
        canopy_gdf = load_canopy(bbox)

    if canopy_gdf.empty:
        route["buffer_area_m2"] = route.geometry.buffer(buffer_m).area
        route["canopy_area_m2"] = 0.0
        route["shade_pct"] = 0.0
        return route

    canopy = canopy_gdf.copy().to_crs(NZTM)

    buffer_values = []
    canopy_values = []
    shade_values = []

    for _, row in route.iterrows():
        buffer_geom = row.geometry.buffer(buffer_m)
        buffer_area_m2 = buffer_geom.area

        possible = canopy[canopy.intersects(buffer_geom)]

        if possible.empty:
            canopy_area_m2 = 0.0
        else:
            clipped = gpd.clip(possible, buffer_geom)
            canopy_area_m2 = clipped.geometry.area.sum()

        shade_pct = (canopy_area_m2 / buffer_area_m2) * 100 if buffer_area_m2 > 0 else 0.0

        buffer_values.append(buffer_area_m2)
        canopy_values.append(canopy_area_m2)
        shade_values.append(shade_pct)

    route["buffer_area_m2"] = buffer_values
    route["canopy_area_m2"] = canopy_values
    route["shade_pct"] = shade_values

    return route