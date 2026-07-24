# Operation Sunscar — Topography and Site Specification

Status: pre-production terrain lock
Target level: `/Game/Maps/Graybox/L_GB_Sunscar`
Geographic influence: Kaka–Abiverd corridor, Ahal Province, Turkmenistan
Fictional site center: **37.3200° N, 59.5600° E**

## 1. What is real and what is authored

Operation Sunscar is not placed on the protected Abiverd ruins or inside modern
Kaka. It is a fictional abandoned service town between them, influenced by the
same terrain, climate, transport corridor, and building traditions.

Two terrain layers must be kept separate:

1. **Regional reference terrain** — SRTM 90 m elevation data for a roughly
   29 km north–south by 24 km east–west window around Kaka and Abiverd.
2. **Playable terrain** — a hand-authored 2,520 m landscape envelope that
   preserves the real north–south fall and drainage direction but develops the
   southern foothills, quarry system, wadis, and northern desert into a full
   battlefield.

Across the new 2.52 km envelope, the sampled real terrain ranges from
approximately 317 m in the northwest to 363 m in the southeast. That gives us a
credible 46 m regional rise before any gameplay sculpting. The playable version
keeps that large-scale slope and increases total relief to approximately 120 m,
concentrated in believable southern ridges and excavated quarry faces.

## 2. Coordinate and elevation control

### Regional control points

| Location | Latitude | Longitude | Approx. elevation | Use |
| --- | ---: | ---: | ---: | --- |
| Abiverd archaeological area | 37.394797 | 59.567231 | 270 m | Western historic and earthen-ruin reference |
| Kaka | 37.348210 | 59.614310 | 291 m | Settlement, road, rail, and service-town reference |
| Fictional Sunscar center | 37.320000 | 59.560000 | 329 m | Landscape and georeferencing origin |

The regional DEM shows the expected rise toward the Kopet-Dag:

| Latitude on 59.55° E transect | Approx. elevation |
| ---: | ---: |
| 37.45° N | 239 m |
| 37.40° N | 270 m |
| 37.35° N | 299 m |
| 37.30° N | 370 m |
| 37.25° N | 496 m |
| 37.20° N | 643 m |
| 37.10° N | 919 m |

This produces the master environmental rule: **rocky high ground is south;
water, sediment, roads, and open desert trend north or northeast.**

### Site envelope

| Corner | Latitude | Longitude | SRTM elevation |
| --- | ---: | ---: | ---: |
| Northwest | 37.33126 | 59.54588 | 317 m |
| Northeast | 37.33126 | 59.57412 | 319 m |
| Southwest | 37.30874 | 59.54588 | 352 m |
| Southeast | 37.30874 | 59.57412 | 363 m |

Recommended projected coordinate reference system: **WGS 84 / UTM zone 40N,
EPSG:32640**. The fictional site center is approximately:

- Easting: **726,841 m**
- Northing: **4,133,445 m**
- Elevation datum: **329 m**

Use georeferencing for source alignment and documentation. Keep gameplay actors
near the Unreal local origin to avoid unnecessary world-coordinate precision
problems.

## 3. Authored playable topography

Local map coordinates use X east and Y north. The playable boundary is
2,000 m × 1,600 m. The landscape envelope is 2,520 m × 2,520 m, giving room for
skyline slopes, inaccessible ridges, long vehicle approaches, and vista terrain.
The earlier 640 m × 500 m Inner Service Town remains centered inside it.

### Elevation targets

| District | Authored elevation | Terrain character |
| --- | ---: | --- |
| Karakum Expanse — north | 310–338 m | Fixed dunes, deflation hollows, road berms, ruined wells |
| Canal Agricultural Belt — east | 315–355 m | Canal invert, banks, fields, rail and service roads |
| Inner Service Town / Old Town | 328–365 m | Terraced streets, drainage, built-up pads, inner ridge |
| Abiverd March — west | 320–375 m | Tells, eroded walls, caravan cuts, kiln and cave mounds |
| Kopet Foothills — south | 350–430 m | Rock benches, quarry system, talus, cliffs, signal high point |

Authored minimum: approximately **310 m**
Authored maximum: approximately **430 m**
Authored relief: approximately **120 m**

Important feature benchmarks:

| Feature | Target elevation or change |
| --- | --- |
| Main Canal invert | 315–327 m along its full grade |
| Canal bank top | 2–4 m above local invert |
| North dry depressions | 310–320 m |
| Old Town street datum | 344–350 m |
| Detention Annex pad | 348–352 m |
| Abiverd ruin mounds | +3–12 m above adjacent road |
| Lower Quarry floor | 360–370 m |
| Upper Quarry floor | 382–392 m |
| Quarry rims | 390–418 m |
| Signal Mast bench | 424–430 m |
| Major southern rock faces | 20–55 m exposed vertical change |

The quarry is an excavated notch in the natural south-to-north slope. It should
not look like an isolated fantasy mountain. Rock bedding, gullies, talus fans,
and the ridge road must all connect into the larger southern landform.

### Slope bands

| Slope | Gameplay use |
| --- | --- |
| 0–5% | Streets, objective pads, primary paths, canal roads |
| 5–12% | Normal natural traversal and broad flanks |
| 12–25% | Slower movement, switchbacks, rough approaches |
| 25–45% | Generally blocked by rocks, walls, or deliberate traversal aids |
| Over 45% | Cliff, quarry face, or hard map boundary |

Keep critical combat surfaces under 12%. Do not use landscape collision alone
to communicate an unwalkable 25–45% slope; reinforce it with rock meshes,
retaining walls, fencing, or a readable cliff edge.

## 4. Drainage and water logic

All major drainage begins on Kopet Ridge and moves north or northeast.

- Two dry wadis descend from the southern ridge.
- The western wadi dissipates into a broad sediment fan near Abiverd Road.
- The eastern wadi passes beneath Old Town through a culvert and reaches the
  Canal Works collector ditch.
- The main irrigation canal runs along the eastern district on a very shallow
  northward grade.
- A pump hall, sluice gates, narrow maintenance bridge, culverts, and a dry
  retention basin explain the infrastructure.
- Buildings sit on pads 0.3–0.8 m above adjacent streets.
- Street crowns and shallow side drains should be visible even in the dry state.
- Avoid permanent blue water unless the mission or season specifically calls
  for an operating canal. Damp sediment, salt crusts, reeds near leakage points,
  and dark culvert interiors can imply intermittent water.

## 5. Surface geology and landscape materials

Use a blended transition from mountain-derived sediment in the south to finer
desert deposits in the north.

| Zone | Primary material | Secondary detail |
| --- | --- | --- |
| South ridge | Tan-gray sedimentary rock | Fractured faces, scree, pale dust |
| Wadis and fans | Gravelly alluvium | Braided channels, cobbles, silt pockets |
| Settlement corridor | Compacted loess and road dust | Tire polish, repair patches, salt staining |
| East canal | Fine silt and disturbed fill | Damp darkening, reeds, concrete fragments |
| North desert | Fine sand over hardpan | Fixed dunes, scrub hummocks, wind streaks |
| Abiverd influence | Sun-dried earthen fabric | Erosion caps, collapsed wall debris, baked brick |

Landscape material layers:

1. bedrock;
2. talus and coarse gravel;
3. compacted earth;
4. fine windblown sand;
5. wadi silt;
6. salt/damp staining;
7. sparse dry scrub;
8. localized irrigated or seasonal vegetation.

Macro variation must follow landform and drainage. Do not scatter color noise
uniformly across the landscape.

## 6. Roads, rail, and built form

The Kaka–Abiverd setting supports an east–west transport town below the
mountains.

- Main freight road: east–west, 7–10 m wide through the service district.
- Historic caravan road: western approach, irregular 4.5–7 m compacted track.
- Ridge road: switchback service route cut into the southern slope.
- Canal maintenance road: narrow linear route along the eastern bank.
- Rail influence: use a freight platform, ballast, utility sheds, and a short
  service spur as environmental storytelling. A live main line is not required.

Architecture should remain a fictional composite:

- one- and two-storey earthen or plastered masonry compounds;
- flat roofs, parapets, exterior stairs, shaded balconies, and enclosed courts;
- selected Soviet-era concrete utility structures at the canal and freight
  edge;
- a small number of taller civic or military landmarks;
- repaired walls made from mixed brick, concrete block, sheet metal, and timber;
- deep window reveals and limited glazing because of heat and dust.

Do not directly reconstruct standing protected monuments. Use Abiverd only for
mass, erosion language, wall thickness, and regional material influence.

## 7. Vegetation and climate presentation

The level should read as arid continental terrain, not a uniform sand sea.

- Karakum edge: saxaul-like shrubs, tamarisk-like scrub, dry grasses, and bare
  hardpan between fixed dunes.
- Wadis: slightly denser scrub following moisture and sediment.
- Canal works: reeds, salt-tolerant plants, weeds around leaks and culverts.
- Compounds: a few stressed fruit trees, poplars, or vines where irrigation
  remnants are plausible.
- South ridge: sparse plants concentrated in cracks and sheltered gullies.

Seasonal art direction:

- default: late summer, dry, dusty, hard light;
- alternate: early spring with a restrained green flush in drainage lines;
- wind event: airborne dust concentrated along roads, courtyards, and the open
  north rather than a constant full-screen sandstorm.

## 8. Unreal Engine landscape setup

Recommended first-production landscape:

- heightmap: **2017 × 2017**, 16-bit grayscale PNG or R16;
- components: **16 × 16**;
- sections per component: **2 × 2**;
- quads per section: **63 × 63**;
- quads per component: **126 × 126**;
- XY scale: **125 cm per vertex**;
- resulting landscape: **2,520 m × 2,520 m**;
- playable area: centered 2,000 m × 1,600 m;
- Inner Service Town: centered 640 m × 500 m;
- outer buffer: approximately 260 m east/west and 460 m north/south.

Reserve a 160 m vertical encoding range centered near 360 m:

- encoded terrain range: approximately 280–440 m;
- Landscape actor Z: **36,000 cm** if preserving the real-world elevation datum;
- Landscape Z Scale: **31.25**, using Epic's documented calculation for a
  160 m total range;
- intended used range: 310–430 m, leaving headroom for later skyline work.

Place control-point markers before sculpting:

- landscape low benchmark: 310 m;
- Old Town datum: 347 m;
- Detention Annex pad: 350 m;
- lower quarry floor: 365 m;
- upper quarry rim: 410 m;
- signal high point: 428 m.

Verify those six points after every heightmap import. A visually plausible
heightmap can still be vertically wrong if its encoding range or actor Z offset
is misinterpreted.

Recommended Landscape Edit Layers:

1. `EL_00_RegionalBase`
2. `EL_10_RidgeQuarry`
3. `EL_20_WadisCanal`
4. `EL_30_RoadPads`
5. `EL_40_CombatReadability`
6. `EL_90_VistaOnly`

Enable the GeoReferencing plugin only if geographic alignment will be retained.
Use EPSG:32640 for projected reference data and document the local-origin
offset. Use World Partition, Data Layers, and Level Instances so the Old Town,
Inner Service Town, outer battlefield, mission variants, and vista terrain can
be loaded independently.

## 9. Data package

Local source files:

- `data/kaka_abiverd_srtm90m.json` — 31 × 31 georeferenced elevation grid.
- `data/kaka_abiverd_srtm90m.csv` — the same grid for GIS, spreadsheet, or
  procedural-tool use.
- `data/fetch_kaka_abiverd_dem.mjs` — reproducible OpenTopoData request script.

Dataset statistics:

- bounds: 37.20–37.46° N, 59.43–59.70° E;
- samples: 961;
- minimum: 208 m;
- maximum: 749 m;
- mean: 370.87 m;
- source resolution: SRTM 90 m;
- fetched: 2026-07-23.

SRTM 90 m is suitable for regional form and slope direction. It is not detailed
enough to generate the playable quarry, canal banks, streets, walls, or cover.
Those belong in the authored terrain and mesh passes.

## 10. Source hierarchy and confidence

| Information | Source | Confidence / limitation |
| --- | --- | --- |
| Regional elevation | SRTM 90 m through OpenTopoData | High for regional form; too coarse for local combat terrain |
| Kaka location | GeoNames | High for settlement location |
| Abiverd context | UNESCO Silk Roads documentation | High for regional historic context |
| Karakum character | UNESCO Repetek documentation | High for landscape character; not a site survey |
| Kopet-Dag setting | UNESCO Nisa documentation | High for regional mountain relationship |
| Irrigation patterns | NASA Earth Observatory imagery | High for regional land-use logic |
| Confrontation spatial feel | Supplied gameplay/flythrough videos | Strong visual reference; no survey dimensions |
| Playable elevations | This specification | Design targets, to be validated in graybox |

Primary online references:

- OpenTopoData SRTM 90 m API:
  https://www.opentopodata.org/
- Epic Games, Importing and Exporting Landscape Heightmaps:
  https://dev.epicgames.com/documentation/unreal-engine/importing-and-exporting-landscape-heightmaps-in-unreal-engine
- Epic Games, Landscape Technical Guide:
  https://dev.epicgames.com/documentation/unreal-engine/landscape-technical-guide-in-unreal-engine
- Epic Games, Georeferencing a Level:
  https://dev.epicgames.com/documentation/unreal-engine/georeferencing-a-level-in-unreal-engine
- UNESCO, Silk Roads Sites in Turkmenistan:
  https://whc.unesco.org/en/tentativelists/5521
- UNESCO, Repetek Biosphere Reserve:
  https://whc.unesco.org/en/tentativelists/5435/
- UNESCO, Parthian Fortresses of Nisa:
  https://whc.unesco.org/en/list/1242/
- NASA Earth Observatory, Agriculture Fans Out in Turkmenistan:
  https://science.nasa.gov/earth/earth-observatory/agriculture-fans-out-in-turkmenistan-149577/

## 11. Terrain production order

1. Import or recreate the regional north–south base slope.
2. Lock the six elevation benchmarks.
3. Sculpt Kopet Ridge and excavate the Quarry Bowl.
4. Cut both wadis and establish the Canal Works drainage grade.
5. Grade the Old Town, road, objective, and building pads.
6. Block all traversable slopes and cliff boundaries.
7. Place the 640 m × 500 m Inner Service Town at `(680 m, 550 m)`.
8. Place the preserved 320 m × 250 m core at `(840 m, 675 m)`.
9. Add outer-region combat pockets, roads, and landmark meshes.
10. Run infantry, vehicle, sightline, and grenade-roll tests.
11. Only then add erosion detail, material blending, vegetation, and vista
    terrain.
