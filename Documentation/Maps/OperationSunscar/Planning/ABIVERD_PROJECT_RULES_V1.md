# Operation Sunscar — consolidated project rules V1

Date: 2026-08-21
Status: **Canonical.** Supersedes the scattered rule sections listed in §1.2.
Author: Claude Code, at Jason's direction, after auditing every rule section in
`Documentation/Maps/OperationSunscar/Planning/`.

Jason's instruction: *"since we are finding discrepancies, please review all
rules and please update all of them... before we are too deep and it's too time
consuming to replace."*

---

## 1. How to use this document

### 1.1 Precedence order

When documents disagree, this is the order of authority:

1. **Jason, in conversation.**
2. **The two master planning images** (they define the map, and were missed for
   weeks — see §2).
3. **This document.**
4. The individual planning docs, for detail this document does not cover.
5. Session handoffs and logs — historical record, not authority.

### 1.2 Rule sections this document consolidates

| Source | Sections absorbed |
|---|---|
| `OLD_TOWN_ART_PRODUCTION_PLAN.md` | §3 gameplay rules, §5 source policy, §12 Nanite, §13 PCG, §14 guardrails |
| `OLD_TOWN_UE_EXECUTION_PACKET.md` | map-owned geometry, material, Nanite, collision policies |
| `OLD_TOWN_UE58_LANDSCAPE_AND_BUILDING_ARCHITECTURE_2026-08-02.md` | Nanite policy, material policy |
| `ABIVERD_HERITAGE_EXPANSION_PLAN_V1.md` | UE 5.8 implementation rules, protected constraints, validation gates |
| `ABIVERD_SS010_LIVE_AUDIT_SPEC_2026-08-18.md` | §0 gate rule, §2 standing constraints |
| `OLD_TOWN_SPATIAL_ASSET_METHOD.md` | asset fit standards, scaling policy, approval gates |
| `ABIVERD_RESUME_HANDOFF_2026-08-19.md` | §5 + later API rule tables |

Those sections remain in place for history. **Where they differ from this
document, this document wins.**

### 1.3 Status key used below

- **[KEPT]** — audited, correct, unchanged.
- **[AMENDED]** — was partly wrong, or right but wrongly scoped. Change and
  reason given.
- **[NEW]** — added because a real gap or violation was found.
- **[RETIRED]** — no longer applies; reason given.

---

## 2. The map, and its boundary

**Read the two master planning images before designing anything:**

```
~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS Game/
    Operation_Sunscar map UE FPS Game/
        Operation_Sunscar_Master_Map.jpg
        Operation_Sunscar_Old_Town_Core.jpg
```

| Layer | Size |
|---|---|
| Terrain envelope | 2,520 × 2,520 m |
| Playable battlefield | 2,000 × 1,600 m (3.2 km²) |
| Inner service town | 640 × 500 m |
| **Old Town core = PHASE 1** | **320 × 250 m** |

**Phase 1 = the 13-site Old Town core:** `SS_003 SS_004 SS_005 SS_006 SS_007
SS_010 SS_011 SS_012 SS_013 SS_015 SS_016 SS_017 SS_018`.
Measured envelope of those 13: X −11,575..14,624, Y −10,652..11,910 cm
(262 × 226 m), inside the authored core.

Outer districts (**not** phase 1): North Karakum Expanse, West Abiverd March,
East Canal Belt, South Kopet Foothills, SE Industrial Works, and the four
approaches.

**[NEW] Rule 2.1 — scope every rule.** Many rules below are correct for the
competitive core and wrong for the 3.2 km² outer map. Every performance and
foliage rule states its scope. Do not apply a core rule to the outer districts
or vice versa.

---

## 3. Gameplay rules — non-negotiable

All **[KEPT]** from `OLD_TOWN_ART_PRODUCTION_PLAN.md` §3. These were audited and
are sound.

1. The graybox remains the source of truth for collision and playable space
   until each art replacement passes a side-by-side traversal test.
2. Art may skin, cap, trim or selectively replace graybox geometry. It may not
   casually change door positions, stairs, cover heights, roof access or route
   widths.
3. Primary doors and windows must remain visually obvious under gameplay
   lighting.
4. No new prop may narrow a combat alley below its verified clearance.
5. No decorative roof element may create an unintended new firing position.
6. No elevated location may gain control over more than two major combat spaces.
7. Foliage and cloth may provide concealment, but may not become unplanned hard
   cover.
8. Temporary review labels remain hideable and are never baked into production
   art.

**[NEW] Rule 3.9 — no direct spawn-to-spawn sightline.** Stated as a core design
goal in the Old Town Core plan but never written as a rule and never verified.
Must be tested whenever spawns or large geometry move.

---

## 4. Cover and concealment — the fairness principle

**[AMENDED / promoted]** — this existed only as scattered remarks. It is the
single most important principle in the project and now leads.

> **Permanent geometry carries the gameplay. Vegetation is a modifier on top.**

**Rule 4.1.** The map must play correctly with **zero vegetation**. Tune cover
using terrain, ruins, walls, berms and built geometry alone. Foliage then *adds*
concealment; nothing collapses when it is absent.

**Why this is not merely aesthetic — three independent reasons converge:**

1. **Graphics settings.** Foliage density scales with quality settings. A player
   on low settings sees through grass that a player on high settings is hiding
   in. (Original wording: *"Foliage scalability may reduce cosmetic density, so
   terrain and ruins must remain sufficient cover at the lowest supported
   foliage setting."*)
2. **Cull distance.** Distant foliage culls. A sniper at 150 m may not render
   the grass concealing someone at 20 m from their target.
3. **Seasons.** Poppies bloom for a few weeks in spring. In summer they are dead
   stalks; in winter, bare ground. A route safe in April is open ground in
   December. If concealment carried the gameplay, the map would rebalance itself
   three times a year.

**Rule 4.2 [KEPT].** No route may depend on flowers or grass for protection from
a standing sniper.

**Rule 4.3 [KEPT].** Vegetation is non-authoritative concealment. It is never
recorded as cover in any cover budget or review.

**Rule 4.4 [KEPT, and currently violated].** Hard cover or terrain interruption
every **8–12 m** on exposed movement routes inside the Old Town core; every
**15–20 m** in the heritage precinct.
*Current state: effectively no hard cover between sites. Open crossings measured
at 155–208 m.*

**Rule 4.5 [KEPT, and currently violated].** Longest intentional sightline in
the core: **110–140 m**.
*Current state: five crossings between 155 m and 208 m.*

---

## 5. Spatial metrics — Old Town core

**[KEPT]** from `Operation_Sunscar_Old_Town_Core.jpg`. Authoritative.

| Element | Spec |
|---|---|
| Primary street | 12–15 m |
| Service lanes | 5–8 m |
| Combat alleys | 2.5–4 m |
| Vehicle gates | 6–8 m |
| Central courtyard | ~86 × 42 m |
| Hard-cover rhythm | every 8–12 m |
| Longest intentional sightline | 110–140 m |

**Verticality tiers:** ground (streets, canal, courtyards) · Tier 1 balconies and
roofs 3–5 m · Tier 2 hotel and detention roofs 7–9 m · landmarks (water tower,
mast) 12–18 m. **Limit continuous rooftop chains.**

**Routes:** ALPHA (northern compounds and hotel) · BRAVO (central road and
courtyard) · CHARLIE (bazaar, yards, dry canal) · plus cross-links and managed
sightline opportunities.

**Objective triangle:** Detention Annex, Central Courtyard, Water Tower.
Every building gets one obvious entrance, one risky alternate, one readable
exterior landmark.

**[NEW] Rule 5.1 — the core canal is DRY.** *"A low, exposed bypass with
culverts, not a safe tunnel."* Wet, engineered canal belongs to the **East Canal
Belt, outside phase 1.** Do not put live water in the core.

**[NEW] Rule 5.2 — channel vehicles, not infantry.** Canal and terrain crossings
must give infantry a choice of route within roughly 30 m. Vehicle-capable
crossings are deliberately few, and their placement *is* the vehicle road
network. Never leave a single crossing that all foot traffic must use.

---

## 6. Nanite policy — consolidated and scoped

Three separate and slightly different "Nanite policy" sections existed. Merged
here.

**[KEPT] 6.1 — Enable Nanite for:** high-detail Quixel rock and rubble; historic
ruin scans and dense masonry; large occluding architecture; high-detail static
vehicle exteriors where compatible; repeated dense opaque or masked static
geometry that measurably benefits.

**[KEPT] 6.2 — Do not enable automatically for:** simple graybox collision
shells; tiny low-poly props; transparent glass; cloth needing unsupported
deformation; any mesh whose material or gameplay behaviour is incompatible.

**[KEPT] 6.3 — Landscape Nanite stays disabled** until profiled. Epic documents
that Nanite Landscape data streams *alongside* the normal Landscape
representation, increasing resident and streaming cost.

**[KEPT] 6.4 — Nanite is a rendering choice, not permission** to use scan meshes
as player collision. Collision stays simpler than render geometry.

**[AMENDED] 6.5 — Nanite foliage.** Previous rule: *"Begin with non-Nanite legacy
Quixel plant meshes so Start/End Cull Distance, PerInstanceFadeAmount and
foliage density scaling remain usable."*

Audited against Epic's UE 5.8 documentation. Findings:

- **True:** Nanite-enabled meshes are not affected by cull distance or instance
  fading. The stated reason is accurate.
- **True:** the Nanite Foliage system (5.7/5.8) is **Experimental**. Epic:
  *"Learn to use this Experimental feature, but use caution when shipping."*
- **Obsolete:** the historical objection was World Position Offset forcing
  conservative bounds and overdraw. Nanite Foliage **does not use WPO at all** —
  it animates by skeletal skinning via the Dynamic Wind plugin, giving accurate
  bounds and fixed-function rasterisation.
- **Understated:** the wins are large. A 41M-triangle tree compresses to ~29 MB
  from 3.5 GB; streaming drops from 36 MB to 2.7 MB per instance.

**Amended rule, scoped:**

| Scope | Foliage rendering | Reason |
|---|---|---|
| **Old Town core (phase 1)** | **Non-Nanite traditional instanced foliage** | Needs explicit cull-distance control to verify §4 fairness; needs deterministic scalability; Experimental is disqualifying for a shipping competitive core |
| **Outer districts (3.2 km²)** | **Nanite Foliage permitted — revisit when it leaves Experimental** | This is where compression and instance-count wins matter and competitive fairness matters least |
| **Ruins, rocks, architecture (everywhere)** | **Nanite** | Unchanged, correct |

**Rule 6.6 [KEPT].** A/B profile Nanite only after a non-Nanite baseline is
captured. Good methodology; keep.

**Rule 6.7 [NEW].** Prefer **Megascans Trees** (static scanned, direct use) over
**Megaplants** (procedural, requires the Experimental Procedural Vegetation
Editor) for anything in phase 1. Megaplants are not banned — they are deferred to
the outer districts.

---

## 7. Foliage implementation

**[KEPT] 7.1** Generate vegetation in editor with a deterministic PCG graph and
a fixed seed.

**[KEPT, and currently violated] 7.2** **Save generated static-mesh instances.
Do not regenerate at runtime.** Runtime PCG on a competitive multiplayer map
means nondeterminism and hitching.
*Current state: the four PCG volumes built 2026-08-20 are live components and
have not been verified or baked. This must be resolved before any build.*

**[KEPT] 7.3** Use Static Mesh Foliage or PCG Static Mesh Spawner output, never
Actor Foliage.

**[KEPT] 7.4** Disable collision, navigation influence, ticking, replication and
individual actor creation for plants.
*Verified: collision is `NoCollision`. Nav influence, ticking and replication are
NOT yet verified.*

**[KEPT] 7.5** Masked materials, never translucent.
*Verified: `BLEND_Masked`, `twoSided`, `bUsedWithInstancedStaticMeshes` true.*

**[NEW] 7.6 — cull distances are mandatory in the core.** Every foliage type in
phase 1 must have `instanceStartCullDistance` and `instanceEndCullDistance` set
and recorded. Unset culling is the default and is not acceptable — it is both a
performance risk and, per §4, a fairness one.
*Current state: the PCG foliage has no cull distances set.*

**[AMENDED] 7.7 — wind.** Previous rule: *"Clamp wind WPO and reduce or disable
it for distant vegetation."* Correct **for traditional instanced foliage only**.
Nanite Foliage animates by skinning, not WPO, so the rule does not transfer.
Annotated to prevent misapplication.

**[KEPT] 7.8** 2K runtime vegetation textures initially. 4K reserved for the
mosque portal and hero close-view masonry, only where profiling supports it.

**[KEPT] 7.9** Density and layout, heritage precinct: 4–6 irregular poppy belts
approximately 12–25 m long × 5–10 m deep. Do not cover uniformly. Keep 1.5–2.0 m
vegetation-clear margins around primary paths and 4–6 m around objectives and
spawn-protection areas.

**[KEPT, and currently violated] 7.10** **Low-density poppies inside Old Town.**
The strongest red-field identity belongs *outside* the dense street core.
*Current state: a uniform 30 × 18 m rectangle at ~11 poppies/m² sits inside the
core. Wrong shape, wrong density, wrong place. Scheduled for rework.*

---

## 8. PCG policy

**[KEPT] 8.1 — manual placement only** for: cover; door and window frames;
route-defining rubble; vehicles; landmark elements; props affecting line of
sight; **any object close enough to affect movement.**

This settles a question raised on 2026-08-20: **ruins used as cover are
hand-placed, never scattered.** Cover determines firefights and is a gameplay
decision.

**[KEPT] 8.2 — PCG or instanced placement** for: small rubble; dry weeds; minor
litter; repeated wall-edge debris; non-gameplay roof clutter; surface decals
where deterministic projection is verified.

**[KEPT] 8.3** PCG output must be deterministic, seeded, organised by zone and
manually editable. Gameplay exclusion volumes protect routes, doors, stairs,
objectives, spawn space and traversal edges.

**[NEW] 8.4 — roads and canals are exclusion volumes.** Foliage must be
subtracted from driving and walking surfaces via a PCG `Difference` against the
corridor, not policed by hand. Poppies cannot grow where vehicles drive.

---

## 9. Material policy

**[KEPT]** Runtime default 2K; 4K hero only after visible comparison. Shared
opaque masters with Material Instances; no unique material per actor. Packed
masks and bounded texture families. Expose tint, roughness, normal strength,
macro variation, dust and damage-mask parameters. Vertex paint or masks for sand
accumulation and facade wear. No displacement that changes traversable geometry.
Landscape macro variation and layer blending to eliminate visible tiling. Two-
metre physical projection baseline for the world-aligned facade family. No
virtual-texture project-setting dependency in this conversion.

Palette stays intentionally muted: warm sand / off-white plaster, pale landmark
plaster, dusty concrete, dark grey-brown worn asphalt, muted galvanised metal,
tan and brown-grey canvas.

---

## 10. Collision policy

**[KEPT]**

| Asset class | Collision |
|---|---|
| Building shell and opening modules | Simple exact |
| Vehicles, large scrap, tactical rocks | Manual simple |
| Sandbags and tactical barriers | Custom simple, matching cover |
| Large cabinet and barrel | Simple box/cylinder |
| Bazaar stalls and poles | Simple; canopy none |
| Minor rubble, tools, signs, decals | None |
| Dry grass and tiny debris | None |
| Hero water tower | Purpose-built simple |

**Never use a raw photogrammetry scan as complex player collision.**

---

## 11. Performance guardrails

**[KEPT]** First-round planning targets, not shipping budgets. Scope: **Old Town
core.**

| Measure | Target |
|---|---|
| Source-asset library | 35–50 selected assets |
| Resident editor RAM, its cells only | below 12–16 GB |
| Unique surface families | 8–10 |
| Simultaneous local shadowed lights in a combat view | ≤ 4 |
| Small procedural dressing instances | ~250–500 |
| Hero 4K texture sets | ≤ 12 before profiling |
| Unjustified 8K texture sets | 0 |
| Driveable vehicle systems | 0 (first round) |
| Imported sample-project maps | 0 |

**[NEW] 11.1 — the RAM guardrail is a hard constraint on current hardware.**
The development machine has **16 GB total**. A 12–16 GB editor working set leaves
no headroom, and this has already caused three editor OOM kills. Treat it as a
ceiling to stay well under, not a target to approach. Check memory before and
after any bulk operation.

**[NEW] 11.2 — the current foliage exceeds a guardrail.** §11 allows ~250–500
procedural dressing instances. The present field is **22,673**. Either the
guardrail is scoped only to *dressing* (and foliage needs its own budget), or the
field is far over. **This needs an explicit decision, not silent divergence.**

---

## 12. Protected assets — do not touch without separate approval

**[KEPT — promoted to top level, was buried in an audit spec]**

- `CoreTarget_DetentionObjective`
- `CoreVolume_DetentionObjective` (1000 × 1000 × 500 trigger)
- The 288 hidden legacy ground overlays
- Any `COL_*` authoritative collision proxy

**[NEW] 12.1 — terrain no-sculpt buffer.** Do not modify landscape height within
any of the 13 sites' measured bounds **+ 5–10 m**. The committed grounding work
(fitted plinths, buttresses lowered to grade with 5 cm embed, foundation skirts,
re-grounded fences) is fitted to *current* terrain height and will break.
Use `LandscapePatch` (non-destructive, removable) rather than direct sculpting.

---

## 13. Process and approval

**[KEPT] 13.1 — the gate rule.** Every pass/fail condition in an audit must
**fail on the current map**. A condition that already passes is not evidence of
quality — it is a broken test; discard it rather than report a pass.

**[KEPT] 13.2 — validation gates before final foliage placement.** Import to a
staging folder and record bounds, pivot, LODs, material count, texture sizes,
collision and Nanite state · place the TacticalMovement character beside each
plant and capture standing, crouched and prone · establish minimum supported
foliage density and verify reducing it does not reveal a route designed as safe
cover · measure GPU cost in near, middle and far views · validate spawn
protection before adding hard cover · first-pass sightline review from every
accessible roof and elevated ruin · commit only after Map Check, multiplayer PIE
traversal and exact Git-scope review.
*None of these has been formally run.*

**[KEPT] 13.3 — working rules for automated sessions.** Verify every write by
reading geometry back. Exact-save only intended packages. **Never Save All.**
No commits without Jason's explicit approval. On any problem close, choose
Don't Save.

**[NEW] 13.4 — read the planning material first.** Before designing anything,
read the two master images and ask Jason whether further material exists. A
substantial amount of 2026-08-20 was spent re-deriving decisions already made in
documents nobody had opened.

---

## 14. Bridge / API rules

Consolidated from the handoff. These are behavioural facts about the MCP bridge,
not design choices. Full detail in `ABIVERD_RESUME_HANDOFF_2026-08-19.md` §5,
§15 and §16.

- `set_properties` `values` is a **JSON-encoded string**, not an object.
- Property names are **camelCase**; use `list_properties`, never guess.
- Saving uses `AssetTools.save_assets` with **`asset_paths`** — an array of
  **strings**. `SceneTools.save_actor` fails on World Partition external actors.
- **Saving a WP level does not save its actors.** Save the actor's refPath.
- **Deleting a WP actor leaves its `__ExternalActors__` package on disk.**
- **`set_properties` on a large `perInstanceSMData` array is a memory bomb** —
  2,700 entries drove swap from 0.6 GB to 26 GB and got the editor OOM-killed,
  three sessions running. **Never push bulk instance data over the bridge.**
  Use PCG, or in-editor Python.
- `ExecuteGraphInstance` **does not invalidate its cache**; respawn the volume.
- PCG **renames ISM components on regeneration** (`_0` → `_1`). Never hardcode
  the suffix; enumerate components.
- `GetGraphStructure` misreports selector params; trust `ObjectTools` on
  `<node>.settingsInterface`.
- PCG tool params marked optional are **required** (`jsonParams`, `nodeTitle`,
  `nodeComment`).
- Nested struct scale passed to `AddNode` is ignored; set it afterwards via
  `set_properties` using key `scale`, not `scale3D`.
- `SpawnGraphInstance` ignores `transform.scale3D`; set scale afterwards.
- `CaptureViewport` returns `returnValue.image.data` (base64); needs
  `annotations: []`; call twice and keep the second.
- **`PluginToolset.SetPluginEnabled` is a silent no-op** — it does not write the
  `.uproject` even on clean exit. Edit the `.uproject` directly.
- `ProgrammaticToolset` has no `unreal` module — only `re/json/copy/math/
  datetime/time` plus `execute_tool`. It cannot do bulk instance work.
- `LandscapePatch` provides **components**, not actors. Attach
  `LandscapeCircleHeightPatch` / `LandscapeTexturePatch` to a host actor via
  `ActorTools.add_component`. **Verified reachable over the bridge 2026-08-21.**
- Avoid broad `find_actors` with no filter, and full-depth Slate snapshots.

---

## 15. What changed in this revision

| # | Change | Reason |
|---|---|---|
| 1 | Three separate Nanite policies merged into §6 | They were scattered and slightly divergent |
| 2 | Nanite-foliage rule **scoped** to the core rather than global | The WPO objection is obsolete in 5.8; the real objections are Experimental status and cull-distance control, which only bind in the competitive core |
| 3 | Wind-WPO rule annotated as traditional-foliage-only | Does not transfer to Nanite Foliage, which uses skinning |
| 4 | Cover/concealment fairness promoted to §4 and given its three reasons | It was scattered remarks; it is the most important principle in the project |
| 5 | Cull distances made mandatory in the core (7.6) | Currently unset on all PCG foliage |
| 6 | Roads/canals as PCG exclusion volumes (8.4) | New requirement from the circulation work |
| 7 | "Core canal is dry" written as a rule (5.1) | Was only implicit in an image |
| 8 | "Channel vehicles, not infantry" written as a rule (5.2) | Jason's requirement, previously unrecorded |
| 9 | Protected-asset list promoted to §12 | Was buried in an audit spec and nearly missed |
| 10 | Terrain no-sculpt buffer added (12.1) | Protects committed grounding work |
| 11 | RAM guardrail flagged as a hard constraint (11.1) | Three OOM kills on a 16 GB machine |
| 12 | Foliage instance-count divergence flagged (11.2) | 22,673 vs a ~250–500 guardrail — needs a decision |
| 13 | "Read the planning material first" added (13.4) | Two master documents were missed for weeks |
| 14 | No spawn-to-spawn sightline written as a rule (3.9) | Stated as a goal, never a rule, never verified |
| 15 | Bridge API rules consolidated into §14 | Were spread across three handoff sections |

**Nothing was retired.** Every audited rule was either sound or needed scoping.
The original rule set was in better shape than the scattering suggested; the
problem was that it lived in ten files and no single place said what won.

---

## 16. Known open violations

Tracked so they are not forgotten. Each needs a decision or a fix.

| # | Violation | Rule |
|---|---|---|
| 1 | PCG volumes are live components, not baked instances | 7.2 |
| 2 | No cull distances set on any foliage | 7.6 |
| 3 | Poppy field is a uniform dense rectangle inside the core | 7.9, 7.10 |
| 4 | 22,673 instances vs a ~250–500 guardrail | 11.2 |
| 5 | Open crossings of 155–208 m | 4.5 |
| 6 | No hard cover between sites | 4.4 |
| 7 | Authored core elevation (328–365 m) never built; 1.85 m measured | master plan |
| 8 | Nav influence / ticking / replication unverified on foliage | 7.4 |
| 9 | No navigation and no audio anywhere in the level | — |
| 10 | Spawn-to-spawn sightline never verified | 3.9 |
