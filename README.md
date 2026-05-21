# treecrown-nz

treecrown-nz is a small geospatial Python package for measuring urban tree canopy coverage and estimating shade along walking routes.

The original GISCI 343 assignment brief focused on Auckland tree canopy. This implementation uses Wellington City Council open data because the Auckland canopy layer was unavailable during development. The package keeps the same analytical goal: comparing tree-rich neighbourhoods and estimating how shaded a typical walk is.

## Data sources

- Wellington City Council tree cover polygons
- Wellington City Council suburb boundary polygons
- OpenStreetMap road and walking route geometry through OSMnx

The WCC layers do not require an API key.

## Main functions

- `load_canopy()` loads Wellington tree canopy polygons.
- `load_suburbs()` loads Wellington suburb boundary polygons.
- `canopy_coverage()` calculates canopy percentage for suburb polygons.
- `route_shade()` estimates canopy cover around route segments.

## Installation

```bash
pip install treecrown-nz-jarm704


from treecrown_nz import load_suburbs, load_canopy, canopy_coverage

suburbs = load_suburbs(["Karori", "Kelburn", "Te Aro"])
canopy = load_canopy(tuple(suburbs.total_bounds))

result = canopy_coverage(suburbs, canopy)
print(result[["suburb", "canopy_pct"]])



---

## 7. Install everything in Positron terminal

Make sure you are in your project folder:

```bash
cd C:\Users\joshu\Documents\GitHub\treecrown-nz


uv sync


uv add geopandas pandas requests shapely matplotlib osmnx
uv add --dev pytest