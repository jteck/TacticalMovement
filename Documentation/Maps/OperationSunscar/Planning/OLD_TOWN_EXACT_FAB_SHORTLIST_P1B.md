# Operation Sunscar — Exact Fab Shortlist, P1B

Research snapshot: 2026-07-24
Scope: doors, shade, roof equipment, furniture and remaining surfaces
Unreal status: not opened
Purchases or library additions made: none

## Result

This pass evaluates 20 additional official Quixel Megascans listings.

| Decision | Count |
| --- | ---: |
| Essential or useful free sources | 14 |
| Free alternate held for visual review | 1 |
| Optional paid roof detail | 1 |
| Paid candidate held because dimensions are missing | 1 |
| Rejected or redundant | 3 |

Detailed evidence is in `OLD_TOWN_EXACT_FAB_SHORTLIST_P1B.csv`.

## Locked implementation decisions

### Bazaar and Tea House shade

The two selected Quixel Tarp listings are free 2 × 2 m scanned materials, not
canopy meshes. Old Town will therefore use lightweight map-owned shade panels:

- Typical panel: 3–5 m long × 2.5–4 m wide.
- Minimum underside: 2.5 m.
- Simple static geometry for the first round; no cloth simulation.
- Neutral tarp on 65–80 percent of panels.
- Weathered tarp on 20–35 percent of panels.
- Poles, beams and attachment points remain map-owned modular pieces.

This is faster, easier to control tactically, and avoids buying a third-party
tarp pack.

### Doors and windows

The free 1.20 × 2.43 m Old Wooden Door physically matches the normal Old Town
pedestrian opening. Its Western styling means it should be used sparingly and
previewed before repetition.

The 1.41 × 2.33 m free alternate is held for wider Tea House, residence or
bazaar openings. The 2.00 m-wide version is rejected for the first pass.

No paid window listing is approved. The retained weathered window lacks public
dimensions. Window frames, simple glass and shutters will be built as
map-owned modules at the already verified opening sizes:

- Width: 1.2–1.8 m.
- Height: 1.1–1.5 m.
- Sill and head positions remain bound to graybox openings.

### Roof equipment

The paid rusted factory vent is dimensionally useful at
0.20 × 0.71 × 1.00 m, but it is deferred. The first pass uses map-owned vent
boxes, the already selected free Metal Water Tank and electrical assets.

Roof dressing remains non-traversable and cannot establish a mantle chain.

### Residential and market props

The free set is deliberately small:

- Old Metal Stool: 0.35 × 0.39 × 0.58 m.
- Wooden Table: 0.53 × 0.93 × 0.65 m.
- Wooden Bench: 0.20 × 1.24 × 0.28 m.

These are dressing, not new tactical cover. They are manually placed at Tea
House, bazaar, courtyard and residence edges.

### Surface family

The free surface set now covers:

- Smooth wall paint.
- Rough exterior stucco.
- Localized flaked paint.
- Fresh asphalt as a clean base.
- Crushed asphalt as the dominant worn variant.
- Cracked asphalt as masked breakup.
- Small asphalt debris at road edges.
- Galvanized garage/shutter metal.

The material instances will be dust-tinted and macro-varied. Flaked paint and
cracked asphalt are restricted to patches so they do not tile visibly.

## Cost conclusion

Required paid cost from P1B:

`$0.00 before tax`

Deferred paid candidates:

- Rusted factory vent: public snapshot $2.99.
- Weathered window: public snapshot $4.99, but purchase is blocked by missing
  dimensions.

The free-first Old Town draft can proceed without either.

## Remaining unknowns

The web catalog cannot establish:

- Internal Unreal asset paths.
- Imported pivot/orientation.
- Actual texture memory after chosen quality tier.
- Exact City Sample and Junkyard sub-mesh names.
- Whether a source material needs conversion for the project's master
  material.

Those are staging-project checks for the later Unreal phase. They do not
require opening TacticalMovement during planning.
