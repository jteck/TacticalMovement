# Abiverd — Resume Handoff, 2026-08-23

Branch `feature/map-development`. **Nothing committed.** Working tree: 17 modified, 67 untracked.
Editor shows **5 Unsaved** — these are the pre-existing in-memory packages from before this session,
not new work. All of today's work is persisted to disk.

---

## 1. Landscape auto-material (DONE, saved)

`MI_Sunscar_LandscapeAuto_v1` at `/Game/Maps/Sunscar/Art/Materials/LandscapeAuto/`,
assigned to `Landscape_Sunscar`. Derived from MW Landscape Auto Material (MAWI United, **free** on Fab).

| MW slot | Texture (all already owned) |
| --- | --- |
| Dirt | Dry Trampled Soil 4K |
| Rock | Sandstone Rocky Ground 4K |
| Stones | Desert Debris 4K |
| Grass | Coarse Desert Sand (repurposed — no vegetation in palette) |
| Snow | disabled |

Switches off: `MW_UseSnow`, `MW_UseWater`, and all five `MW_[x]_UseXProcedurals`
(the last group prevents runtime-spawned foliage — required by the no-runtime-generation
and cover-fairness rules). `MW_UseWorldPositionUVs` stays **True**: this is what makes the
material blend from slope and world height with **no layer painting**, which the bridge cannot do.

Previous material `M_OT_Landscape_Abiverd` is untouched and still on disk if revert is needed.
It is weight-blended (needs hand painting) — that is why the map read as flat uniform sand.

`BP_BakeLandscapeLayers` (bakes procedural layers to splat maps at 1k/2k/4k) ships with the
MW pack and is **not yet used**. That is the route to locking the result to static layers.

---

## 2. Elevation / bunds (DONE, saved and verified)

**Problem measured:** core 320x250 m had **0.28 m median relief per 20 m step**;
**87% of the core was standing-visible**. Total spread 7.88 m, but smoothed across 320 m.

**Built:** 11 linear field bunds, **64 patch actors** (`ABV_BundC_*`, `ABV_BundS_*`, `ABV_BundE_*`).
Crest 1.75 m mid, tapering to ~0.6 m at ends — vaultable, not walls.
Form chosen deliberately: low earth banks match aryk banks / field bunds / qanat spoil.

**Verified — swale-to-swale across the 126 m central corridor:**

| Stance | Before | After |
| --- | --- | --- |
| Standing 1.60 m | 0/6 blocked | 3/6 (50%) |
| Crouch 1.00 m | 0/6 | **6/6 (100%)** |
| Prone 0.40 m | 0/6 | **6/6 (100%)** |

**Persistence confirmed:** 16 landscape streaming proxies (~2 MB each) rewritten,
verified by file size + mtime — not a zero-byte save. `terrain_lib.save_terrain()` encodes the rule.

---

## 3. Open / next

1. **Southern band is under-served.** `BundS_C/D/E` kept only 3-4 of 9 patches after the
   intruder purge. The 230 m southern approach still needs bunds placed in the real gaps.
2. **Eastern corridor leans on buildings**, not terrain, to break sightlines.
3. **Two residual grounding bleeds**: SS_018.nw +15.2 cm, SS_008.sw +7.1 cm.
   *Theory, unconfirmed:* landscape vertex resolution, not patch overlap — the nearest patch
   sits outside its own falloff. Verify against actual quad size before acting.
4. **Dark ring structure east of core** — large circular feature reading dark green/vegetated.
   Biggest remaining visual defect. It is StaticMeshActors with their own materials, NOT landscape.
5. **Poppy field** — solid opaque wall at eye level, well outside concealment spec.
6. **Rooftop sightlines** open at 184-236 m — still an open design decision.
7. **5 unsaved packages** never identified. Path-based `is_dirty` cannot reach them
   (they are in-memory-only). Click the "5 Unsaved" status-bar indicator to list them.

---

## 4. Gotchas learned today (do not repeat)

- **Patch reach = radius + falloff (~9-13 m), not radius.** A clearance test against an 8 m
  site buffer passed 91 patches, 27 of which intruded — 3 were burying building corners under
  ~1.8 m. Always test `rect_dist(patch, site) < radius + falloff + margin`.
- **`is_dirty` on an *actor* refPath returns True for everything** (3546/3546). Meaningless.
  It works correctly on real asset paths only.
- **The bridge returns pretty-printed multi-line JSON.** A per-line `json.loads` parser
  silently returns None for every call. Parse the whole body.
- **`/tmp` lost `mcp.py` and `ue.py` overnight.** Working copies now in
  `Planning/bridge_scripts/` — copy to `/tmp` when resuming (scripts hardcode `/tmp`).
- **Verify before reporting.** Four times today I reported a finding that a check then
  disproved (rock colour correction, the "seam", the actor dirty sweep, bund clearance).
