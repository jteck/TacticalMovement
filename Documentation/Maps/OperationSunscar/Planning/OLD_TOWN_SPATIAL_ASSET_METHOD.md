# Operation Sunscar — Old Town Spatial Asset Method

Status: planning only
Coordinate origin: Old Town center
World conversion: 1 metre = 100 Unreal units
Orientation: east = positive X, north = positive Y

## 1. What “place the assets” means

The existing graybox, not a purchased mesh, defines the playable dimensions.
Every environment asset is assigned to a measured target envelope and one of
four jobs:

1. **Skin** — cover a verified graybox surface without changing collision.
2. **Cap** — attach doors, windows, parapets, trims or roof pieces to it.
3. **Replace** — replace visible graybox with a render mesh while the verified
   collision shell remains hidden until retested.
4. **Dress** — add props, rubble, vegetation and decals that do not define the
   structure.

The asset plan therefore records two different sizes:

- **Gameplay size:** the existing graybox footprint, opening or cover volume.
- **Art fit size:** the target envelope an Epic/Quixel asset should occupy.

The gameplay size is fixed. The art asset is selected, repeated, trimmed or
lightly scaled to fit it.

## 2. Three levels of spatial planning

### Level 1 — Site bounds

The 20 Old Town macro sites already have world centers and measured footprints.
These decide which district and visual recipe applies.

### Level 2 — Binding sockets

Art is attached to named parts of the verified geometry:

| Socket | Meaning |
| --- | --- |
| `Surface_N/S/E/W` | Existing exterior wall face |
| `Opening_Primary` | Existing main combat doorway |
| `Opening_Alternate` | Existing secondary or risky doorway |
| `Opening_Window_*` | Existing combat-facing window |
| `Roof_Edge_*` | Existing roof perimeter |
| `Roof_Landmark` | Approved non-traversal landmark position |
| `Cover_*` | Existing verified cover location |
| `Dress_Edge_*` | Non-traversal wall or ground edge |
| `Interior_Critical_*` | Approved playable interior treatment area |

Sockets are bound to actual graybox actors when Unreal resumes. This prevents a
planning document from inventing a doorway that is not present in the playable
map.

### Level 3 — Asset instances

After an exact Fab asset is selected, its measured imported bounds are recorded.
The placement record then contains:

- Asset package path.
- Source listing and publisher.
- Socket.
- World transform.
- Intended visible dimensions.
- Scale.
- Collision policy.
- Nanite policy.
- Manual or PCG ownership.

This final transform layer is generated from the editor scan and the recipes in
`OLD_TOWN_SITE_RECIPES.csv`.

## 3. Asset fit standards

Purchased scans should not be stretched to become an entire building. Large
surfaces use tiling materials; architectural meshes use modular repetition.

| Asset role | Target dimensions | Scaling rule |
| --- | --- | --- |
| Wall surface material | Covers any verified wall face | UV/material scale only |
| Modular wall panel | 2–4 m wide × 2.8–3.4 m high | 0.90–1.10 uniform preferred |
| Ground-floor civic panel | 3–5 m wide × 3.0–3.4 m high | Repeat; do not stretch full facade |
| Upper-floor panel | 2.5–4 m wide × 2.8–3.2 m high | Repeat |
| Pedestrian doorway | 1.0–1.2 m clear × 2.1–2.4 m high | Clear opening cannot shrink |
| Wide doorway | 1.5–2.0 m clear × 2.2–2.8 m high | Bind to verified opening |
| Vehicle/garage opening | 3–5 m clear × 3–4.2 m high | Use modular surround |
| Window | 1.2–1.8 m wide × 1.1–1.5 m high | Frame may overlap wall; aperture fixed |
| Shallow arch | 2–3.5 m clear × 2.8–4.2 m high | Preserve pawn and weapon clearance |
| Parapet | 0.9–1.1 m high × 0.20–0.35 m thick | Segment lengths of 2–4 m |
| Compound wall | 2.4–3.2 m high × 0.35–0.70 m thick | Repeat 2–4 m modules |
| Corrugated fence | 2–2.6 m high × 2–4 m long | Repeat with damaged variants |
| Market stall | 2–3 m wide × 1.8–2.5 m deep × 2.2–2.8 m high | Must sit outside route clearance |
| Shade panel | 3–5 m wide × 2.5–4 m deep | Minimum underside 2.5 m |
| Sandbag element | 0.8–1.2 m × 0.35–0.6 m × 0.25–0.45 m | Cluster manually |
| Waist-high barrier | 1.8–2.4 m × 0.4–0.8 m × 0.85–1.05 m | Match verified cover |
| Crouch cover | 1–2 m × 0.4–0.9 m × 0.65–0.85 m | Match movement metrics |
| Crate | 0.5–1.2 m on major axes | Manual if climbable or cover |
| Lamp/utility pole | 0.15–0.4 m diameter × 4–7 m high | Keep base outside travel path |
| Electrical box | 0.4–1.2 m wide × 0.2–0.5 m deep × 0.6–1.8 m high | Wall mount or protected ground edge |
| Drain/pipe | 0.1–0.5 m diameter | Avoid accidental ladder geometry |
| Static car/SUV | 4.2–5.2 m × 1.8–2.1 m × 1.5–1.9 m | Uniform scale only |
| Static pickup/van | 4.8–6.2 m × 1.9–2.3 m × 1.8–2.6 m | Uniform scale only |
| Small rubble | 0.2–0.8 m footprint | PCG outside exclusion volumes |
| Tactical rubble | 0.8–2.5 m footprint | Manual and collision reviewed |
| Dry weed | 0.15–0.8 m footprint × 0.2–1.0 m high | Sparse PCG |
| Wall decal | 0.5–3 m projection footprint | No collision |
| Ground decal | 1–6 m projection footprint | No collision |

## 4. Scaling policy

1. Prefer exact-size assets.
2. Prefer modular repetition over non-uniform scaling.
3. Uniform scale between 0.90 and 1.10 is normally acceptable.
4. Uniform scale between 0.75 and 1.25 requires visual review.
5. Larger changes require choosing a different mesh or building a repeated
   assembly.
6. Door, window, stair, railing, vehicle and cover assets are never scaled in a
   way that changes their gameplay dimensions.
7. Photogrammetry damage, bricks and rubble must retain believable real-world
   scale.

## 5. Surface measurement method

For a rectangular building:

```text
exterior wall area = 2 × (width + depth) × visible height
```

Doors and windows are subtracted after socket binding. Surface quantities in
the recipe ledger are deliberately expressed as ranges because the exact
opening areas come from the final editor scan.

Example — Municipal Hotel:

- Footprint: 28 × 22 m.
- Visible height: 9.6 m.
- Gross wall area: `2 × (28 + 22) × 9.6 = 960 m²`.
- Planned facade modules: 30–40 modules, usually 2.5–4 m wide.
- Planned openings: three doors and 18–24 windows bound to existing openings.
- Planned balcony/parapet length: approximately 50–65 m.
- The tiling wall material covers the full verified shell; modular meshes add
  silhouette and detail rather than replacing 960 m² with one distorted scan.

## 6. Placement density bands

| Band | Rule | Typical area |
| --- | --- | --- |
| D0 — Clear | No loose props | Spawn safety, door clearance, stairs |
| D1 — Sparse | One small cluster per 20–30 m² | Civic plaza, canal center |
| D2 — Moderate | One cluster per 10–15 m² | Residential and street edges |
| D3 — Dense edge | One cluster per 5–8 m², edges only | Bazaar and salvage perimeter |
| D4 — Manual tactical | Every object deliberately placed | Cover pockets and objectives |

Density never authorizes an object inside a gameplay exclusion volume.

## 7. Exclusion envelopes

The later placement automation must create or infer:

- 1.5 m clear radius at ordinary doors.
- 2.5 m clear approach at objective doors.
- Full verified width plus 0.3 m on each side for alleys and stairs.
- 2 m clear radius around ladder access.
- Existing cover peek lanes plus 0.5 m.
- Spawn and extraction volumes plus their first movement path.
- 1 m setback from the playable edge of roofs.
- No procedural instance inside a sightline test corridor.

## 8. Old Town coordinate frame

The spatial ledger uses metres. Convert to Unreal centimetres only during
automation.

| Site range | Approximate value |
| --- | --- |
| West–east | X = -130 to +128 m |
| South–north | Y = -105 to +97 m |
| Review footprint | Approximately 320 × 250 m |
| Street datum | Approximately 348 m elevation |

The existing site height remains authoritative. Art meshes bind to surface
sockets instead of using the macro site's landscape elevation as an arbitrary
placement Z.

## 9. Planned output when Unreal resumes

The first editor automation pass will be read-only and will export:

```text
OldTown_GrayboxActorScan.json
OldTown_SurfaceSockets.json
OldTown_OpeningSockets.json
OldTown_CoverSockets.json
OldTown_ExclusionVolumes.json
```

The planning recipes and the imported asset-bounds catalog will then compile
into:

```text
OldTown_ResolvedArtPlacements.json
```

Only the resolved file contains final transforms. It can be inspected before
any placement script modifies the level.

## 10. Approval gates

1. **Geometry scan approved** — sockets match the visible graybox.
2. **Asset bounds approved** — every selected Epic/Quixel mesh has measured
   dimensions and a permitted scale.
3. **P0 placement preview approved** — Hotel, Water Tower, Courtyard, Bazaar,
   Tea House, Detention and Dry Canal prove the look.
4. **Traversal approved** — the three routes and critical interiors still pass.
5. **P1 dressing approved** — the remaining sites can be completed.
6. **Performance approved** — memory and frame-time remain within the planned
   guardrails.
