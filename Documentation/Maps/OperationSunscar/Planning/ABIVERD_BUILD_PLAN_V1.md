# Operation Sunscar — build plan V1

Date: 2026-08-21 · Status: **Active plan.** Rules: `ABIVERD_PROJECT_RULES_V1.md`

---

## The principle: build in order of permanence

Jason's structure. Each layer is finished and signed off before the next starts,
because each layer is the substrate for the one above it.

| Layer | Contents | Changes? | Carries gameplay? |
|---|---|---|---|
| **0 — Terrain** | Elevation, landforms, waterway *channels*, road and path *grading*, ruins | Never | **Yes — fully** |
| **1 — Standing vegetation** | Trees, whether living or dead | Never (only its foliage does) | **Yes** |
| **2 — Seasonal cover** | Poppies, grasses, dead stalks, water *state* | Every season | **No — concealment only** |
| **3 — Placed objects** | Sandbags, barriers, crates, barrels, debris, dressing | Freely | Cover items yes; dressing no |

**Why this order.** Layers 0 and 1 are permanent, so they can be trusted as
cover. Layer 2 changes three times a year and scales with graphics settings, so
it can never be trusted. Layer 3 is cheap to move, so it goes last, once the
spaces it dresses actually exist.

**The test for Layer 0 + 1:** the map must play correctly with layers 2 and 3
entirely deleted. If it doesn't, Layer 0 is unfinished.

---

## Gate 0 — Measure the character (before any terrain)

Half a session. Everything in Layer 0 is a height decision, and we do not
currently know the numbers.

- Place the TacticalMovement character; capture standing, crouched, prone.
- Record: eye height standing / crouched / prone, capsule height and radius,
  step height, max walkable slope, jump and vault reach.
- Derive and record the **cover height table**: what height blocks a standing
  player, a crouched player, a prone player.

Output: a short table appended to this plan. Every berm, bund, wall and ruin
height afterwards references it. (This is validation gate 2 from the heritage
plan; it has never been run.)

---

## Layer 0 — Terrain

### 0.1 Elevation

Authored (master plan) vs measured today:

| Zone | Authored | Measured |
|---|---|---|
| Core | 328–365 m | **348 m, ±1.85 m — flat** |
| North | 310–338 m | not built |
| East | 315–355 m | not built |
| West | 320–375 m | not built |
| South | 350–430 m (Signal Ridge 428, quarry floor 365) | not built |

Drainage falls **north / north-east**; the **southern rim owns the strongest
high ground**.

**Hard constraint:** no landscape height change inside any of the 13 sites'
measured bounds **+5–10 m**. Committed grounding work (fitted plinths,
buttresses at grade with 5 cm embed, foundation skirts, re-grounded fences) is
fitted to current height and will break. Use `LandscapePatch` — non-destructive,
removable — never direct sculpting.

**Micro-relief is the point.** Not dramatic landforms: 1–3 m of constant local
variation, so cover changes every ~20 m of movement. Sources, all authentic:
canal bunds, field bunds (0.3–0.8 m), takir depressions (0.5–1.5 m below grade),
erosion gullies, qanat spoil-mounds (1–2 m rings in a line).

### 0.2 Landforms, by district

| District | Landform |
|---|---|
| Old Town core | Micro-relief only: bunds, takir pans, gully. Nothing that competes with the water tower or breaks "limit continuous rooftop chains" |
| South Kopet foothills | The strong high ground. Quarry bowl at 365 m, Signal Ridge 428 m |
| North Karakum | Low dunes, 318 m, sparse and readable |
| West Abiverd March | **The tell** — 18 m tall, ~68 m across, authentic Abiverd dimensions. Ruined citadel walls on the crown so firing lines are restricted to gaps. Three or four separate approaches |
| East Canal Belt | Graded agricultural terraces, raised canal bunds |

### 0.3 Waterways — the channel is terrain, the water is not

**The channel, bunds and crossings are permanent Layer 0 geometry.** Water state
is Layer 2 and changes with season: spring full and muddy · summer low or dry
with cracked bed · winter low and still.

- **Core canal is DRY** — "a low, exposed bypass with culverts, not a safe
  tunnel." No live water inside phase 1.
- **East Canal Belt** carries the wet, engineered canal, outside phase 1.
- **SS_003 Canal Pump Station** is the head of the system — it already exists.
- On flat ground, real irrigation canals are **raised and bunded**, not trenched.
  This means the whole system is additive geometry: no sculpting under buildings,
  no risk to grounding work.

**Crossings — channel vehicles, not infantry.**
Infantry get a crossing choice within ~30 m: plank footbridges, culvert tops,
collapsed banks, fords, sluice gates. Vehicle crossings are deliberately few, and
where you put them *is* the vehicle road network.

### 0.4 Roads and paths — the grading is terrain

Three tiers, following the master plan and Abiverd's own single-gate plan:

1. **Approach road** — one compacted route along the oasis strip, linking to the
   outer districts.
2. **Gate spur and main street** — a single spur into the core, echoing Abiverd's
   one gate and one straight street.
3. **Service tracks** — narrow, rutted, irregular; thinnest wear.

Core widths are fixed by spec: primary street 12–15 m · service lanes 5–8 m ·
combat alleys 2.5–4 m · vehicle gates 6–8 m.

Surface is `DryTrampledSoil` plus the Dirt Road material, with wear decals.
**Roads and canals become PCG exclusion volumes** so no vegetation can ever grow
on a driving surface.

### 0.5 Ruins — confirmed wanted, and they are cover

Ruins are Layer 0: permanent, and they carry gameplay.

- **Hand-placed, never scattered.** Cover determines firefights (rules §8.1).
- Vocabulary from Merv: many walls eroded to **low mudbrick outlines** — ideal
  chest-high cover and authentic. Occasional standing köshk-type mass.
- Placed against the measured sightlines: **hard cover every 8–12 m** on exposed
  routes in the core, **15–20 m** in the heritage precinct.
- Avoid parallel walls that create uninterrupted head-glitch lanes.
- Spacing irregular, 6–14 m, with intentional open lanes retained.

### 0.6 Layer 0 acceptance

- [ ] Authored elevation built; no height change within any site buffer
- [ ] Longest sightline in the core ≤ **140 m** (currently 155–208 m)
- [ ] Hard cover or terrain interruption every **8–12 m** on exposed routes
- [ ] No spawn-to-spawn sightline
- [ ] Every canal reach has ≥2 infantry crossings within ~30 m
- [ ] Vehicle crossings placed deliberately and drivable
- [ ] **Map plays correctly with layers 1–3 deleted**

---

## Layer 1 — Standing vegetation

Trees are permanent. A dead tree still blocks sight and stops bullets, so trees —
unlike grass — **can** be trusted as cover. That is why they are their own layer.

- **Shelterbelt poplars along canals and roads** — documented Turkmen practice,
  and the most efficient sightline breaker available for long crossings.
- Tamarisk / saltcedar at canal edges.
- Living and dead-appearing variants of the same trunks, so seasonal swaps change
  only the canopy, never the blocking geometry.
- Placed to serve §0.6 sightline targets — they count toward the cover rhythm.
- **Non-Nanite in the core** (cull-distance control); Nanite permitted outside.

### Acceptance
- [ ] Trunks have collision and are recorded as cover
- [ ] Seasonal variants share identical trunk geometry and transforms
- [ ] Cull distances set and recorded

---

## Layer 2 — Seasonal cover

Everything here is **non-authoritative concealment**. It may hide a player; it
may never be the reason a route is safe.

| Season | Vegetation | Water |
|---|---|---|
| Spring (Mar–May) | Poppies in bloom, green grass | Canals full, muddy tracks |
| Summer (Jun–Sep) | Dead stalks, dry grass, dust | Low or dry, cracked beds |
| Winter (Dec–Feb) | Bare ground, dry remnants | Low, still |

- Poppies: **4–6 irregular belts**, 12–25 m long × 5–10 m deep. Never uniform.
- **Low density inside Old Town.** The strong red identity belongs *outside* the
  dense street core.
- Vegetation-clear margins: 1.5–2.0 m around primary paths, 4–6 m around
  objectives and spawn protection.
- Cull distances mandatory. Collision, nav influence, ticking, replication all
  off. Masked materials, never translucent.
- Generated by seeded PCG in-editor, then **baked to static instances** — no
  runtime PCG on a competitive map.

Season swap should be a **layer/data-layer toggle**, not a rebuild.

### Acceptance
- [ ] Deleting all of Layer 2 does not make any route unplayable
- [ ] Each season builds from the same Layer 0/1 geometry
- [ ] Baked, culled, collisionless, verified

---

## Layer 3 — Placed objects

Two distinct kinds, and they follow different rules:

**Tactical (hand-placed, is cover):** sandbag barriers, corrugated panels,
concrete blocks, barrels used as cover, vehicle hulks. Counts toward the 8–12 m
rhythm. Custom simple collision matching the visual.

**Dressing (PCG, is not cover):** small rubble, litter, wall-edge debris, roof
clutter, decals. No collision. Never placed where it could affect movement.

### Acceptance
- [ ] Every tactical object has collision matching its silhouette
- [ ] No dressing object narrows a combat alley below verified clearance
- [ ] Dressing is deterministic, seeded, zone-organised, hand-editable

---

## Sequence

| # | Step | Gate before moving on |
|---|---|---|
| 0 | Measure the character | Cover height table recorded |
| 1 | Pay off current debt: bake PCG, set cull distances, verify nav/tick/replication | §16 items 1, 2, 8 closed |
| 2 | **Layer 0** — elevation, landforms, waterway channels, roads, ruins | §0.6 acceptance passes |
| 3 | **Layer 1** — trees | Sightline targets met with layers 2–3 absent |
| 4 | **Layer 2** — current season only (spring) | Deleting it changes nothing structural |
| 5 | **Layer 3** — tactical cover, then dressing | Alley clearances verified |
| 6 | Navigation and audio | Built from settled geometry |

Navigation and audio are last **on purpose**: navmesh is built from geometry and
audio volumes from spaces. Doing them earlier means building them twice.

---

## Immediately next

1. Gate 0 — measure the character. Half a session, unblocks every height
   decision in Layer 0.
2. Buy the two ground surfaces (~$2): Dry Cracked Mud (takir), Desert Outback
   Ground Mud Rocky 01. Needed the moment terrain starts.
3. Then Layer 0, beginning with core elevation via LandscapePatch.

Everything else — trees, poppies, sandbags, culverts, bridges — waits for its
layer. Nothing gets bought or built out of order.

---

## Gate 0 RESULT — character metrics, measured 2026-08-21

Measured by spawning `BP_ThirdPersonCharacter` and reading live component
properties. **The Blueprint overrides the C++ constructor** — BP values below are
authoritative (C++ sets 42/96; the BP uses 35/90).

### Measured

| Property | Value | Source |
|---|---|---|
| Capsule radius | **35 cm** | `CollisionCylinder` |
| Capsule half-height | **90 cm** → **180 cm tall standing** | `CollisionCylinder` |
| Crouched half-height | **40 cm** → 80 cm tall crouched | `CharMoveComp` |
| Base eye height | 64 cm (above capsule centre) | actor |
| Crouched eye height | 32 cm (above crouched centre) | actor |
| Max step height | **45 cm** | `CharMoveComp` (matches `MovementProfileRow.StepHeight`) |
| Walkable floor angle | **44.77°** (walkableFloorZ 0.71) | `CharMoveComp` |
| Jump Z velocity | **500 cm/s** | `CharMoveComp` |
| Max walk speed | 500 / crouched 300 | `CharMoveComp` |
| Nav agent | radius 35, height 180 | `navAgentProps` |

### Derived eye heights above ground

| Stance | Capsule centre | Eye height | Status |
|---|---|---|---|
| Standing | 90 cm | **154 cm** | works |
| Crouched | 40 cm | **72 cm** | **DISABLED** |
| Prone | — | — | **NOT IMPLEMENTED** |

### THREE BLOCKING FINDINGS

**1. Crouch is disabled.** `navAgentProps.bCanCrouch = false`. The character
cannot crouch, despite `ECombatStance` defining Standing/Crouched/Prone and
`MovementProfileRow` carrying `CrouchSpeedMultiplier = 0.45`.

**2. Prone does not exist.** No prone half-height, no prone eye height, no
capsule resize. `ProneSpeedMultiplier = 0.20` exists but nothing implements the
stance.

**3. Crouched eye at 72 cm is very low** even once enabled — that is UE's stock
default (40 + 32), not a tuned tactical value. Most tactical shooters sit around
110–120 cm. This needs a deliberate decision, because **it sets the height of
every piece of crouch cover on the map.**

### Why this blocks Layer 0

Cover heights are meaningless without stance heights. Right now only standing
exists, so the only sightline that can be designed against is **154 cm**. If
cover is built to that and crouch is later enabled at a tuned height, **every
cover object on the map is the wrong height** and the terrain pass is redone.

### Cover height table — provisional

Usable now for standing. Crouch and prone rows are **projections**, valid only
once those stances are implemented and their heights confirmed.

| Cover type | Blocks | Height | Confidence |
|---|---|---|---|
| Full cover | standing eye 154 cm | **≥ 165 cm** | **Confirmed** |
| Crouch cover | crouched eye, exposes standing | 80–100 cm at stock 72 cm eye; **120–135 cm if tuned to ~110** | **Projection — depends on decision** |
| Prone cover | prone eye | 40–55 cm | **Projection — stance not implemented** |
| Vaultable / step-over | step height 45 cm | ≤ 45 cm | **Confirmed** |
| Blocks movement, not sight | above step, below crouch | 46–79 cm | **Confirmed** |
| Max walkable slope | — | **44.77°** | **Confirmed** |

### DECISION — approved by Jason 2026-08-21

Crouch and prone **will** exist; they are simply not implemented yet (movement
work is in progress). Rather than wait, the stance heights were agreed as a
**design target**, so the map and the character are built to the same numbers.

| Stance | Capsule half-height | Total | Eye height |
|---|---|---|---|
| Standing | 90 (existing) | 180 cm | **154 cm** |
| Crouched | **60** | 120 cm | **~100 cm** |
| Prone | **34** | 68 cm | **~35 cm** |

**Character work must implement to these numbers.** `bCanCrouch` must be enabled
and `crouchedHalfHeight` raised from UE's stock 40 to 60. Prone needs
implementing at half-height 34.

Reasoning: UE's stock crouch (72 cm eye) is a deep squat, and cover built for it
lands at 80–90 cm, which matches no real architectural form. At a 100 cm eye,
crouch cover sits at 110–120 cm — a waist-high wall, parapet, canal bund or field
wall. Prone cover then lands at 45–55 cm, the same band as irrigation bunds, and
just above the 45 cm step height, so a bund is nearly step-over-able while still
giving prone concealment.

### FINAL COVER TABLE — build to this

| Cover type | Height | Blocks | Exposes |
|---|---|---|---|
| **Full cover** | **≥ 165 cm** | standing (eye 154) | nobody |
| **Crouch cover** | **110–120 cm** | crouched (eye 100) | standing |
| **Prone cover** | **45–55 cm** | prone (eye 35) | crouched |
| **Step-over** | **≤ 45 cm** | nothing | — |
| Blocks movement, not sight | 46–79 cm | — | — |
| Max walkable slope | **44.77°** | — | — |

### Remaining code decisions (not blocking Layer 0)

1. Reconcile jump velocity: C++ constructor and BP both say 500;
   `MovementProfileRow` defaults to 420. Confirm which governs at runtime.

---

## Layer 0 — terrain findings, 2026-08-21

### Landscape specification (measured)

| Property | Value |
|---|---|
| Landscape scale | **(125, 125, 29.296875)** |
| **Quad size** | **125 cm = 1.25 m** |
| Origin Z | 37,500 cm = 375 m |
| **Usable height range** | **≈ 300–450 m** (512 m × ZScale/100, centred on 375 m) |
| Extent | −63,000 .. 63,000 cm = 1.26 × 1.26 km, 16 streaming proxies |

The authored 310–430 m range fits comfortably inside the available 300–450 m, so
the landscape was configured deliberately for it.

**The 1.25 m quad size dictates a split in how relief gets built:**

| Feature | Built as | Why |
|---|---|---|
| Hills, dunes, the tell, takir pans, broad grading | **Landscape (LandscapePatch)** | Wider than ~4 m, so the heightmap can represent them |
| Canal bunds, field bunds, road berms, ditch lips | **Meshes** | 0.5–3 m wide — finer than the heightmap can express |

This also confirms the earlier conclusion that raised canal bunds are additive
geometry: they were never going to be sculpted anyway.

### Terrain as actually built vs authored

From a 168-point grid across phase 1, excluding building hits:

| | Measured | Authored |
|---|---|---|
| Ground spread across phase 1 | **3.12 m** | core 328–365 m (37 m) |
| Gradient, north | **+0.26 m per 100 m (rises north)** | drainage *falls* north/north-east |
| Gradient, east | −0.18 m per 100 m | — |

**The authored drainage was never built, and the residual gradient runs
backwards.** Band means run 347.9 m in the south to 348.8 m in the north across
240 m — flat.

### DECISION — the authored core range cannot be built as written

A 37 m fall across a 250 m core is a ~15 % slope. The 13 buildings are grounded
to flat terrain with committed plinths, buttresses at grade and foundation
skirts. Introducing that gradient would strand every building on a plinth or in a
pit and destroy work already paid for twice.

**Therefore:**

- **Old Town core: micro-relief only** — roughly 1–3 m, terraced around each
  site's existing pad height. This is also what the gameplay actually needs; the
  sightline problem is solved by local variation plus ruins and trees, not by a
  regional gradient.
- **Outer districts: build the full authored range** — south rim 350–430 m,
  Signal Ridge 428 m, quarry floor 365 m, north 310–338 m. Nothing is grounded
  out there, so the relief is free.
- Read "core 328–365 m" as describing the core *region and its transitions*, not
  the built-up 320 × 250 m.

*Flagged for Jason's review — this diverges from the master plan, deliberately.*

### LandscapePatch — validated 2026-08-21

Proven end to end over the bridge at (20000, 0), outside the phase-1 envelope.

| Distance from centre | Patch enabled | Patch disabled |
|---|---|---|
| centre | 34,800.1 | 34,397.7 |
| 5 m | 34,800.1 | 34,419.0 |
| 9 m | 34,800.1 | 34,437.1 |
| 16 m | 34,690.6 | 34,468.5 |
| **40 m** | **34,539.0** | **34,539.0** |

Findings:

- `LandscapeCircleHeightPatch` sets landscape height to **the host actor's own
  world Z** within `radius`, blending outward over `falloff`.
- **Strictly bounded** — 40 m out is byte-identical either way.
- **Fully reversible** — toggling `bIsEnabled`, or deleting the host actor,
  restores the original heights exactly.
- Memory never moved (1.81–1.86 GB).

**How to drive it:**
1. Spawn any actor (a `StaticMeshActor` works) at the target X/Y and **the Z you
   want the terrain to become**.
2. `ActorTools.add_component` with
   `/Script/LandscapePatch.LandscapeCircleHeightPatch`.
3. Set `radius` and `falloff` via `ObjectTools.set_properties`.
4. Verify with `SceneTools.trace_world` before and after.

**Requires a landscape edit layer.** UE prompts to create one on first use; it
appears as a layer named **"Patches"**. This is what makes patches
non-destructive: the base heightmap is untouched and patches stack above it.

**Caution:** edit layers duplicate heightmap storage per layer across 16 proxies
on a 1.26 km landscape. Memory held fine for one test patch; watch it during the
real pass. This is the most likely reason to move to the 32 GB machine.

**State: the edit layer exists in memory only and has not been saved.** Nothing
is on disk; git is clean.

---

## LandscapePatch persistence — the rule that took three restart tests

**Symptom:** terrain built with LandscapePatch vanishes after an editor restart,
even though the patch actors and their components survive intact.

**Cause:** UE **does not mark the landscape dirty** when a LandscapePatch changes
it. `AssetTools.save_assets` on the landscape therefore finds it clean and writes
nothing — every save after the first reports success and writes zero bytes. Patch
heights are computed live in-session and never reach disk.

This masks itself twice over:
- An in-session **level reload** appears to work, because the patch re-applies
  from the still-loaded components.
- The **first** batch of patches appears to persist, because the landscape was
  genuinely dirty when the edit layer was created, so that one save baked them.

### THE RULE — after any patch change

1. Apply the patches.
2. **Force every landscape actor dirty** — read a property and write the same
   value straight back (`streamingDistanceMultiplier` works).
3. `AssetTools.save_assets` on all 17 landscape actors.
4. **Confirm files actually changed on disk.** A save that writes 0 packages
   means nothing baked. This is the check that catches it.
5. Save the patch actors too — they carry the shape.

Verified: after doing this, seven sample points matched to **0.0 cm** across a
full editor restart.

### Things that were NOT the cause

- **One patch per actor vs many on one host.** The gully was rebuilt from 21
  components on one actor into 21 separate actors on the theory that offset
  components fail to re-register. It made no difference — the dirty flag was the
  real problem. Whether the multi-component form also survives is **untested**;
  it is more efficient and worth retesting if actor count becomes a concern.
- **Toggling `bIsEnabled`.** Forces an in-session re-render, useful for
  verifying, but does nothing for persistence.

### Testing lesson

The third restart test reported failure because the expected floor was computed
as `grade − depth`. That is wrong wherever patches overlap: neighbouring circles
blend and the real floor differs. **Always compare against measured
pre-restart values, never against intended ones.**
