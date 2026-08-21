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
