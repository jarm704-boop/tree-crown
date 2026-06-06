import geopandas as gpd
import pytest
from shapely.geometry import LineString, Polygon

from treecrown_nz import canopy_coverage, route_shade


def test_canopy_coverage_returns_expected_percentage():
    area = gpd.GeoDataFrame(
        {"suburb": ["Test"]},
        geometry=[Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])],
        crs="EPSG:2193",
    )

    canopy = gpd.GeoDataFrame(
        {"id": [1]},
        geometry=[Polygon([(0, 0), (50, 0), (50, 100), (0, 100)])],
        crs="EPSG:2193",
    )

    result = canopy_coverage(area, canopy)

    assert result.loc[0, "canopy_pct"] == pytest.approx(50.0)


def test_canopy_coverage_output_crs_is_nztm():
    area = gpd.GeoDataFrame(
        {"suburb": ["Test"]},
        geometry=[Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])],
        crs="EPSG:2193",
    )

    canopy = gpd.GeoDataFrame(
        {"id": [1]},
        geometry=[Polygon([(0, 0), (20, 0), (20, 20), (0, 20)])],
        crs="EPSG:2193",
    )

    result = canopy_coverage(area, canopy)

    assert result.crs.to_string() == "EPSG:2193"


def test_route_shade_returns_shade_percentage():
    route = gpd.GeoDataFrame(
        {"road": ["Test Road"]},
        geometry=[LineString([(0, 50), (100, 50)])],
        crs="EPSG:2193",
    )

    canopy = gpd.GeoDataFrame(
        {"id": [1]},
        geometry=[Polygon([(-20, 30), (120, 30), (120, 70), (-20, 70)])],
        crs="EPSG:2193",
    )

    result = route_shade(route, canopy, buffer_m=10)

    assert result.loc[0, "shade_pct"] > 90


def test_route_shade_rejects_negative_buffer():
    route = gpd.GeoDataFrame(
        {"road": ["Test Road"]},
        geometry=[LineString([(0, 0), (100, 0)])],
        crs="EPSG:2193",
    )

    with pytest.raises(ValueError):
        route_shade(route, buffer_m=-5)


def test_canopy_coverage_raises_on_empty_input():
    empty = gpd.GeoDataFrame(geometry=[], crs="EPSG:2193")
    canopy = gpd.GeoDataFrame(geometry=[], crs="EPSG:2193")

    with pytest.raises(ValueError):
        canopy_coverage(empty, canopy)


def test_canopy_coverage_raises_on_missing_crs():
    area = gpd.GeoDataFrame(
        geometry=[Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])]
    )

    with pytest.raises(ValueError):
        canopy_coverage(area)


def test_canopy_coverage_returns_zero_when_canopy_is_empty():
    area = gpd.GeoDataFrame(
        {"suburb": ["Test"]},
        geometry=[Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])],
        crs="EPSG:2193",
    )
    empty_canopy = gpd.GeoDataFrame(geometry=[], crs="EPSG:2193")

    result = canopy_coverage(area, empty_canopy)

    assert result.loc[0, "canopy_pct"] == 0.0
    assert result.loc[0, "canopy_area_m2"] == 0.0


def test_canopy_coverage_returns_zero_when_canopy_does_not_overlap():
    area = gpd.GeoDataFrame(
        {"suburb": ["Test"]},
        geometry=[Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])],
        crs="EPSG:2193",
    )
    canopy = gpd.GeoDataFrame(
        {"id": [1]},
        geometry=[Polygon([(500, 500), (600, 500), (600, 600), (500, 600)])],
        crs="EPSG:2193",
    )

    result = canopy_coverage(area, canopy)

    assert result.loc[0, "canopy_pct"] == 0.0


def test_route_shade_raises_on_empty_input():
    empty = gpd.GeoDataFrame(geometry=[], crs="EPSG:2193")

    with pytest.raises(ValueError):
        route_shade(empty)


def test_route_shade_raises_on_missing_crs():
    route = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (100, 0)])]
    )

    with pytest.raises(ValueError):
        route_shade(route)


def test_route_shade_returns_zero_when_canopy_is_empty():
    route = gpd.GeoDataFrame(
        {"road": ["Test Road"]},
        geometry=[LineString([(0, 50), (100, 50)])],
        crs="EPSG:2193",
    )
    empty_canopy = gpd.GeoDataFrame(geometry=[], crs="EPSG:2193")

    result = route_shade(route, empty_canopy, buffer_m=10)

    assert result.loc[0, "shade_pct"] == 0.0
    assert result.loc[0, "canopy_area_m2"] == 0.0


def test_route_shade_returns_zero_when_canopy_does_not_overlap():
    route = gpd.GeoDataFrame(
        {"road": ["Test Road"]},
        geometry=[LineString([(0, 50), (100, 50)])],
        crs="EPSG:2193",
    )
    canopy = gpd.GeoDataFrame(
        {"id": [1]},
        geometry=[Polygon([(500, 500), (600, 500), (600, 600), (500, 600)])],
        crs="EPSG:2193",
    )

    result = route_shade(route, canopy, buffer_m=10)

    assert result.loc[0, "shade_pct"] == 0.0