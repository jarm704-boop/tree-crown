# treecrown-nz

treecrown-nz is a Python package for measuring urban tree canopy coverage and estimating shade along walking routes in Wellington, New Zealand.

It uses Wellington City Council open data (no API key required) and OpenStreetMap routing via OSMnx.

## Requirements

- Python 3.10 or higher
- An internet connection (the package fetches live data from the WCC ArcGIS API and OpenStreetMap)

## Installation

### From TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ treecrown-nz-jarm704
```

### With uv (recommended for new users)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager. If you do not have it yet, install it with:

```bash
pip install uv
```

Then create a virtual environment and install the package:

```bash
uv venv
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ treecrown-nz-jarm704
```

### Development setup (cloning this repo)

Clone the repo, move into the folder, then let uv install everything:

```bash
git clone https://github.com/jarm704-boop/tree-crown.git
cd tree-crown
uv sync
```

`uv sync` reads `uv.lock` and installs all dependencies at the exact pinned versions, including dev tools like pytest.

## Quick-start

```python
from treecrown_nz import load_suburbs, load_canopy, canopy_coverage

suburbs = load_suburbs(["Highbury", "Aro Valley", "Karaka Bays"])
canopy = load_canopy(tuple(suburbs.total_bounds))
result = canopy_coverage(suburbs, canopy)
print(result[["suburb", "canopy_pct"]])
```

Expected output (values may vary slightly with WCC data updates):

```
        suburb  canopy_pct
35    Highbury   71.640717
43  Aro Valley   44.584114
24 Karaka Bays   39.546921
```

## Demo notebook

[`demo_treecrown_nz.ipynb`](demo_treecrown_nz.ipynb) walks through a complete real-world analysis:

- Calculates canopy coverage for all 57 Wellington suburbs and ranks them
- Maps the top three suburbs by tree cover (Highbury, Aro Valley, Karaka Bays)
- Fetches the walking network for Karaka Bay and runs `route_shade()` along Karaka Bay Road
- Produces a colour-coded map showing shade percentage along the walking corridor

To run it, clone the repo and launch Jupyter after `uv sync`:

```bash
jupyter notebook demo_treecrown_nz.ipynb
```

## API reference

| Function | Description |
|---|---|
| `load_canopy(bbox)` | Load Wellington tree canopy polygons, optionally filtered to a bounding box |
| `load_suburbs(names)` | Load Wellington suburb boundary polygons, optionally filtered by name |
| `canopy_coverage(area_gdf, canopy_gdf)` | Calculate canopy percentage for each input area polygon |
| `route_shade(route_gdf, canopy_gdf, buffer_m)` | Estimate canopy cover within a buffer around each route segment |

All functions work in EPSG:2193 (NZTM) and reproject input data automatically.

## Running the tests

After cloning the repo and running `uv sync`, you can run the test suite with:

```bash
uv run pytest
```

To also see a coverage report:

```bash
uv run pytest --cov=treecrown_nz --cov-report=term-missing
```

Tests are in the `tests/` folder and cover the core functions `canopy_coverage` and `route_shade`. They run offline using synthetic geometry so no internet connection is needed.

GitHub Actions runs the tests automatically on every push to the repository.

## Data sources

- Wellington City Council tree cover polygons (WCC ArcGIS REST API)
- Wellington City Council suburb boundary polygons (WCC ArcGIS REST API)
- OpenStreetMap road and walking route geometry via OSMnx

## Licence

MIT, see [LICENSE](LICENSE).
