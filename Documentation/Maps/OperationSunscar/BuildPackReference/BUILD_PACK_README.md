# Operation Sunscar — Unreal Build Pack v1

Generated deterministically from `tools/sunscar_build_config.json` and the local
Kaka–Abiverd SRTM 90 m dataset.

## Unreal Landscape import

- Heightmap: `Heightmaps/Sunscar_Height_2017.png`
- Alternate raw heightmap: `Heightmaps/Sunscar_Height_2017.r16`
- Resolution: 2017 × 2017
- Components: 16 × 16
- Sections per component: 2 × 2
- Quads per section: 63
- XY scale: 125.0 cm
- Z scale: 29.296875
- Landscape actor Z: 37500.0 cm
- Enable Landscape Edit Layers
- Row zero is north; only use Flip Y if a test import proves the editor has
  inverted the documented north-up orientation.

The heightmap encodes 300.0–450.0 m.
The generated terrain intentionally uses approximately
310.0–430.0 m.

## Package contents

- `Heightmaps/` — 16-bit PNG and little-endian R16 terrain.
- `Masks/` — 8-bit grayscale Landscape and PCG masks.
- `Manifests/` — blockout actors, splines, routes, and coordinate metadata.
- `Previews/` — human-readable terrain and surface-zone previews.
- `Reports/ValidationReport.json` — dimensions, benchmarks, slopes, hashes.

## Elevation benchmark result

- PASS — North low desert: 316.546 m (target 316 m)
- PASS — Old Town street datum: 347.701 m (target 348 m)
- PASS — Detention Annex pad: 349.848 m (target 350 m)
- PASS — Main Canal invert: 321.114 m (target 321 m)
- PASS — Lower Quarry floor: 364.755 m (target 365 m)
- PASS — Upper Quarry rim: 410.0 m (target 410 m)
- PASS — Signal high point: 428.0 m (target 428 m)

## Regeneration

Run:

```sh
python3 MapDesign/Desert_Glory_Inspired/tools/generate_sunscar_buildpack.py
```

Generated Unreal actors must carry the `SunscarGenerated` tag. Automation may
replace only tagged actors and must preserve every untagged/manual actor.
