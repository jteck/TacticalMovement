# Abiverd — Resume Handoff, 2026-08-25

Branch `feature/map-development`. Worktree `/Users/jasonteck/UnrealEngine/_worktrees/map-development`.
Bridge: HTTP JSON-RPC at `127.0.0.1:8000/mcp` (UE must be running with `-ModelContextProtocolStartServer`).

## FIRST THING ON RESUME

`/tmp` is cleared nightly and takes the bridge scripts with it:

```
cp Documentation/Maps/OperationSunscar/Planning/bridge_scripts/*.py /tmp/
cp Documentation/Maps/OperationSunscar/Planning/bridge_scripts/*.json /tmp/
```

Then sanity-check the bridge:

```
cd /tmp && python3 -c "import sys; sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
T=SourceFileLoader('tl','/tmp/terrain_lib.py').load_module()
print(T.ground(0,0))"
```

Should print ~34882. If it errors, UE is closed or the transport is missing.

---

## STATE: Layer 0 complete, §0.6 passes all seven criteria

| Criterion | Target | Measured |
|---|---|---|
| Elevation built, no site height change | no change | **0.00 cm** across 32 site points |
| Longest core sightline | <= 140 m | **126 m** (site-to-site, ground level) |
| Hard cover on exposed routes | every 8-12 m | **median 10.0 m**, max 18.7 m, 560 objects |
| No spawn-to-spawn sightline | zero | **0 of 16** opposing core spawn pairs |
| Canal reaches, infantry crossings | >=2 within 30 m | **97%** of canal length |
| Vehicle crossings | deliberate, drivable | **2**, 7 m decks flush at grade |
| Plays with layers 1-3 deleted | yes | all work is Layer 0 geometry |

Object seating verified: **148 objects at 0.0 cm median, 0 off by >25 cm.**

### What Layer 0 contains

| Element | Built |
|---|---|
| Core relief | **1 LandscapeTexturePatch**, authored fractal heightmap, +/-150 cm, sites painted to exact zero |
| Roads | 588 m **graded into the heightmap**, not meshes — main street 13 m + 4 service lanes |
| Broad grading | 64 chained circle patches, 51-85 cm |
| Canal | 244 m raised bunded dry canal, 28 bunds @115 cm, 10 infantry + 2 vehicle crossings |
| Ruins | 90 segments (75% @110-120 cm crouch, 25% @165-190 cm full) |
| Koshk masses | 13 @ 6.2-10.5 m, placed on traced sightlines |
| Silt | dried-watercourse traces both flanks, 15 east-side |

---

## NEXT: Sequence step 3 — Layer 1 (trees)

**BLOCKED on asset acquisition.** Nothing else blocks it.

**Buy: Megascans Trees — Lombardy poplar + tamarisk/saltcedar.**
**NOT Megaplants** — those need Procedural Vegetation Editor + Nanite Foliage
(Experimental), which rules §6/§7 forbid in the competitive core.

Planting is fully planned: `ABIVERD_LAYER1_PLANTING_PLAN.md` has **134 positions with
coordinates**, validated with proxies before purchase.

Measured effect of the shelterbelt (proxy test):
- cover median 10.0 m -> **7.1 m**
- longest sightline **126 m -> 126 m, unchanged** — trees serve cover rhythm, NOT sightlines
- 134 trees (8 m spacing) == 182 trees (6 m): no measurable difference

Layer 1 acceptance still to do: trunk collision, seasonal variants sharing trunk
transforms, cull distances recorded, non-Nanite in core.

---

## OPEN ITEMS (none block Layer 1)

1. **Roads are graded but not legible.** Corridors are flat and driveable, but the
   auto-material gives them no distinct surface — they read as flatter sand. Needs
   MW's `BP_BakeLandscapeLayers` splat bake, or terrain-conforming decals.
2. **Wheel ruts unplaced.** `OT_EXT_Wear_*` is the pattern: 2.56 m slabs in L/R pairs.
3. **Poppy field awaiting Layer 2 rebuild.** PCG volumes removed (rule 7.2 closed).
   Rebuild to §7.9: 4-6 irregular belts 12-25 m x 5-10 m, low density, OUTSIDE the
   dense core, 250-500 instance guardrail. Graph `PCG_ABV_PoppyField_V1` and 8 poppy
   meshes retained.
4. **Roads/canals must become PCG exclusion volumes** when PCG returns, or the poppy
   rebuild grows flowers down the middle of the main street.
5. **Open-ground sightlines up to 248 m** near map edges. NOT the §0.6 gate (that is
   site-to-site) but real.

---

## HARD-WON TOOLING RULES — read before touching geometry

- **`set_actor_transform` RESETS omitted fields.** Sending only `location` reset scale
  to (1,1,1) and yaw to 0 on 148 actors. **Always send location + rotation + scale.**
  And verify the *whole object*, not the field you set.
- **Ground traces hit whatever is first — including the object you are placing.**
  To measure true terrain under an object: lift ALL nearby actors, trace, place back.
  `terrain_lib.ground_under()` and `ground_clear()` exist for this.
- **`import_file` will not overwrite** an existing texture. Import under a versioned
  name (`_v2`) and repoint the patch.
- **`python3 x.py 2>&1 | tail -n` masks the exit code.** Redirect to a log, echo `$?`.
- **`save_terrain` verifies by mtime**, not git count (git only rises for NEW files).
- **Heightmap re-import resets compression.** Re-apply `TC_SingleFloat`, `srgb=false`,
  `TMGS_NoMipmaps`, then verify all 16 site footprints read <=1 cm.

## Heightmap workflow

Source PNG is **outside Content** at `Documentation/.../SourceArt/Heightmaps/`.
Edit `bridge_scripts/gen_heightmap.py`, run it, import as a new `_vN` name, re-apply
compression, repoint `ABV_CoreReliefPatch.TexPatch`, verify site points at zero.
