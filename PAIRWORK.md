# Pairwork: treecrown-nz

## Group members

- Joel
- Hayden
- Josh Armstrong

---

## Division of labour

### Component One: initial planning and conceptual development

The project began with Joel and Hayden, who led the early conceptual planning and put together the Component One submission.

- **Joel:** visualised the intended outputs and drafted the design direction for the package.
- **Hayden:** wrote the theoretical background and researched tree canopy analysis methods.

### Component Two: dataset selection and design review

Josh joined the group at this stage. Together, the three of us decided to switch from the originally proposed Auckland dataset to Wellington City Council open data, which offered pre-classified canopy polygons and was much easier to work with.

- **Joel:** found the Wellington City Council dataset as a viable alternative.
- **Josh:** confirmed that the original Auckland dataset would not work and validated the WCC data structure.
- **All three members:** attended the Component Two design review interview and contributed to the discussion.

### Component Three: poster, showcase, and core code

- **Josh** was the primary code contributor for this phase:
  - `_read_arcgis_layer()`: rewrote Hayden's initial draft into a reusable ArcGIS REST query helper with optional bounding box filtering.
  - `load_canopy()`: fetches WCC tree cover polygons using the layer helper above.
  - `load_suburbs()`: fetches WCC suburb boundaries, with optional filtering by name.
  - `canopy_coverage()`: calculates canopy area and percentage for each input area polygon using spatial intersection.
  - `route_shade()`: estimates canopy cover within a configurable buffer around each route segment.
  - `__init__.py`: the package entry point and public API.
  - `demo_treecrown_nz.ipynb`: an end-to-end demonstration notebook covering suburb ranking, canopy mapping, and walking shade analysis.
  - Set up a new GitHub repository and kept the documentation up to date throughout.
- **Hayden:** wrote the initial API call function that `_read_arcgis_layer()` is based on, contributed to the poster design, and attended the showcase.
- **Joel:** led the poster design and layout, attended the showcase, and helped present the work.

### Component Four: package release and final submission

- **Josh:** polished the package, got the TestPyPI release (`treecrown-nz-jarm704`) working, and made the final push to GitHub.
- **Hayden:** contributed to the final documentation and helped with submission preparation.
- **Joel:** contributed to the final documentation and helped with submission preparation.

---

## Contribution summary

| Member | Primary contributions |
|---|---|
| Joel | Initial planning, finding the WCC dataset, poster design, documentation |
| Hayden | Background research, initial API call draft, poster design, documentation |
| Josh | Package code (`loader.py`, `__init__.py`), demo notebook, repo management, TestPyPI release |

---

## What went well

Finding a suitable dataset was the group's biggest challenge. Once we landed on the Wellington City Council canopy data, things moved along pretty smoothly. We communicated well throughout the project and got tasks done in good time rather than leaving things to the last minute. The final package came out better than expected: it does what we set out to do, it is well documented, and it has been properly tested.

## Aspects to improve

The coding was not evenly split across the group. Josh did the bulk of the implementation, while Joel and Hayden contributed more on the documentation and design side. That said, the main reason for this was the time pressure we faced after the Auckland dataset fell through. We had no working code to build from without the dataset and needed to move quickly before the presentation date, so it made sense to lean on whoever could get things done fastest. In an ideal situation, everyone would have had more of a hand in the code itself.

There is also room to grow the package further. Given more time, we would have liked to add functions with a temporal element, for example exploring how canopy coverage changes across seasons or tracking total coverage over multiple years. More varied visualisation options would also be useful for users who want to compare different areas in different ways.

---

## Integration approach and problems encountered

The package pulls data from three sources: the WCC ArcGIS REST API for canopy and suburb polygons, and the OpenStreetMap road network via OSMnx. The trickiest part was making sure all the data lined up in the same coordinate system. We resolved this by reprojecting everything to EPSG:2193 (NZTM) on load, which kept things consistent across all the functions.

Hayden's early prototype queried the WCC API directly, but it did not handle bounding box filtering or CRS normalisation, which made it impractical for suburb-level analysis. Josh took that prototype and built it into `_read_arcgis_layer()`, the shared helper that all the public loader functions now use. The other main difficulty was performance: fetching the full canopy dataset for all 57 suburbs at once was very slow, so we switched to a per-suburb bounding box approach. That is the strategy now baked into both `canopy_coverage()` and `route_shade()`.
