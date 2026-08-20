# Abiverd / Old Town — phase-one defect register — 2026-08-18

Author: Claude Code, first session after the Codex handoff.
**No actor, package, material or Git state was modified to produce this
document.** Unreal was closed throughout; every finding below comes from the
20 August 17 screenshots plus read-only analysis of saved reports.

---

## 1. Session verification (read-only, live)

| Check | Expected per handoff | Live result 2026-08-18 |
|---|---|---|
| Branch | `feature/map-development` | `feature/map-development` ✅ |
| Local HEAD | `e0b856c2…` | `e0b856c20cdad11f7057248c851d4d344f43fbe1` ✅ |
| `origin/feature/map-development` | same | identical ✅ |
| Staged files | 0 | 0 ✅ |
| Tracked modified | 927 | 927 ✅ |
| Untracked | 80 (+1 handoff) | 81 ✅ |
| Non-external-actor modified | 7 named files | exactly those 7 ✅ |
| Untracked non-external content | 2 decal materials | exactly those 2 ✅ |
| `git lfs status` | nothing staged | nothing staged ✅ |
| UnrealEditor running | no | no — only Epic Launcher `EpicWebHelper` PIDs and Apple `UnrealEditorServices` |
| TCP 8000 | not listening | not listening ✅ |

Working tree preserved. No stage, commit, push, merge, rebase, checkout,
reset, restore, clean or stash was run.

This register adds one untracked documentation file, taking the status count
from 1,008 to 1,009.

---

## 2. The finding that reframes everything

I ran a read-only mesh census over the 1,785 actors indexed in
`Saved/OperationSunscar/Reports/abiverd_visual_conversion_preflight_v1.json`:

| Mesh | Actor count |
|---|---|
| `/Game/LevelPrototyping/Meshes/SM_Cube` | 590 |
| `/Engine/BasicShapes/Cube` | 552 |
| `/Game/LevelPrototyping/Meshes/SM_ChamferCube` | 61 |
| `/Engine/BasicShapes/Cylinder` | 40 |
| `/Game/LevelPrototyping/Meshes/SM_Cylinder` | 22 |
| `/Engine/BasicShapes/Sphere` | 1 |
| **Total prototype primitives** | **1,231 of 1,785 (69%)** |

The buildings are built from scaled engine cubes named
`Core_<site>_F<n>_<side>_<part>` — every wall is a 40 cm thick stretched cube,
floor by floor, plus cube floors, cube roofs, cube lintels and cube ramps
(227 `Core_*` actors in total).

> **REVISION HISTORY — this section was withdrawn, then reinstated. Read both
> steps; the second one is the correct reading.**
>
> **Step 1 (withdrawn).** My first draft said "the launch buildings are still
> blockout geometry." I then withdrew that after reading Appendix A's
> *2026-08-16 core-cover production-visual pass*, which says: "A subsequent
> general basic-shape inventory found 415 visible Engine basic shapes, but
> every one already carries an intentional project material… Use concrete
> player-height evidence and exact site labels for any further replacement
> rather than treating Engine basic-shape geometry itself as a defect."
>
> **Step 2 (correct).** Withdrawing was an over-correction. I deferred to a
> prior agent's chronology note instead of reading the primary specification,
> which was in the repository the whole time.
> `OLD_TOWN_UE58_LANDSCAPE_AND_BUILDING_ARCHITECTURE_2026-08-02.md` states
> plainly:
>
> > "The current map is safe as a multiplayer blockout, but **its building art
> > is not yet production geometry**."
>
> and locks a **two-shell production model**: (1) a *gameplay shell* — simple
> **invisible** collision preserving doors, windows, traversal, cover, floor
> support and networking; (2) a *visible art shell* — measured modular
> Epic/Quixel meshes. "The gameplay shell must not be modified to accommodate
> art. The art must fit the validated gameplay geometry."
>
> So the intended end state is that the cubes become **invisible collision**
> with art meshes over them. Visible raw cubes are **not** the target.
> Codex's note is a fair *triage* rule — a basic shape is not automatically a
> defect — but it does not establish that exposed cubes are finished art.

**The correct reading (Jason, Appendix D §1): hybrid.** Do not wholesale
delete the 227 `Core_*` cubes — they are the authoritative layout/collision
shells. But **exposed raw cubes are not acceptable final phase-one exterior
art.** Each piece is classified **Skin / Cap / Replace / Dress**
(`OLD_TOWN_SPATIAL_ASSET_METHOD.md`, and §9 of
`OLD_TOWN_ART_PRODUCTION_PLAN.md`); Replace explicitly permits a visible art
mesh over a retained hidden collision shell.

The census therefore explains the audits-vs-eyes gap on two levels at once:

- The audits verified **materials** and correctly found zero prototype
  materials — but a good material on a raw cube is still a raw cube.
- Separately, geometry is in the wrong **place**: parapets cantilevered
  9–17 m, a fence floating 120 cm, walls over open sand, buttresses at roof
  height, lintels detached from their windows.

Both are real. The placement defects (Bugs A–D) are cheap transform fixes and
come first; the art-shell conversion is the larger phase-one exterior job.
I am still **not** telling you the buildings are finished.

Two further consequences worth stating plainly:

- The duplicate-geometry audit passed at a 0.1 cm tolerance. The defects
  below are offset by **metres**, so that audit could never have caught them.
- The prototype-material audit swept for `MI_OT_Stucco_WorldAligned`,
  WorldGrid, DefaultMaterial and LevelPrototyping materials. The flat green
  and flat grey surfaces in your screenshots are **`MI_OT_Detention`**, which
  was on neither list, so it was never swept. It is a flat authored colour
  with no texture detail, not a missing material — there are **zero** actors
  with a mesh and no material.

---

## 3. Two systematic authoring bugs behind most of what you photographed

These are not scattered mistakes. They are two bugs, each applied uniformly,
and between them they account for the majority of the floating and
cantilevered geometry in the screenshots.

### Bug A — an obsolete parapet set survives on 8 of 13 sites, each half hanging in mid-air

Every site has a correct modern parapet set, `ABV_<site>_RoofParapet_{North,
South,East,West}`, fitted flush to the roof (measured overhang **0.0 cm**).

Eight sites *also* still carry the older `<site>_Parapet_{N,S,E,W}` set,
sitting exactly **20 cm higher**, and **mis-centred by half its own length**
so that half of every piece cantilevers off the building into open air:

| Site | Obsolete set overhang | Modern `ABV_` set present? |
|---|---|---|
| SS_010 Detention Annex | **1,700 cm** | yes (0.0 cm) |
| SS_007 Municipal Hotel | **1,400 cm** | yes (0.0 cm) |
| SS_005 Old Clinic | **1,200 cm** | yes (0.0 cm) |
| SS_012 Consulate Residence | **1,050 cm** | yes (0.0 cm) |
| SS_018 Telecom Workshop | **1,050 cm** | yes (0.0 cm) |
| SS_011 Checkpoint Office | **1,000 cm** | yes (0.0 cm) |
| SS_003 Canal Pump Station | **900 cm** | **no — no replacement** |
| SS_004 Tea House | **900 cm** | yes (0.0 cm) |

That is **32 obsolete actors**, 28 of which are safely superseded.

This single bug is your screenshot list items 4 and 7: the SS_011 pair
overhangs 10 m, which is the *"very long roof beam extending far beyond the
building"* at the checkpoint; the SS_010 pair overhangs 17 m, which is the
*"large gray wall/beam panels that float or cantilever far beyond plausible
supports"* in the compound.

**Caveat — SS_003 has no replacement parapet.** Deleting or hiding its set
would leave that building with no parapet at all. SS_003 and SS_004 also
received later Codex passes (SS_003 "four visible parapets corrected";
SS_004's four obsolete parapets set to `NoCollision` but **left visually
unchanged**), so their live state may differ from this Aug-12 index. Both
need live re-verification before any change.

### Bug B — the SS_010 detention yard perimeter is built at terrace height but stands over open sand

The six `Core_DetentionYard_F1_*` walls all start at **Z = 34,979.0** and are
250 cm tall. They enclose X −400…4,800 by Y 6,500…10,900 — a 52 m × 44 m
perimeter.

The only foundation under that perimeter is two slabs:

| Slab | X extent | Y extent | Top Z |
|---|---|---|---|
| `Foundation_SS_010_Detention_Terrace` | 2,200 → 5,600 | 9,100 → 11,900 | 35,034.3 |
| `Foundation_SS_010_West_Support` | 500 → 3,900 | 7,700 → 10,500 | 34,984.8 |

Combined coverage is roughly X 500…5,600 by Y 7,700…11,900. Therefore:

- the **entire south wall** (Y ≈ 6,500) sits ~12 m clear of any foundation;
- the **entire west wall** (X ≈ −400) sits ~9 m clear of any foundation;
- the lower east wall (Y 6,500…7,700) is likewise unsupported.

**Correction to my float estimate (2026-08-18).** I first quoted ~185–215 cm
by using *other sites'* ground floors (SS_011 at 34,766; SS_015 at 34,794) as
the grade proxy. That was the wrong reference — grade varies across the map
and those sites are far away. Local actors that genuinely sit on the ground
near this yard put grade much higher:

| Local ground-contact actor | Bottom Z |
|---|---|
| `QX_Square_Detention_West_End` | 34,869.7 |
| `QX_Sandbag_Detention_West_A` | 34,879.2 |
| `QX_Sandbag_Detention_East_Return` | 34,884.1 |
| `Detention_SouthStep_01` (first tread) | 34,917.6 |

So local grade is roughly **34,870–34,920**, and the yard walls at 34,979.0
float approximately **60–110 cm**, not 185–215 cm. Still a clear defect and
still consistent with the daylight and hard cast shadows under the walls in
8.16.32 / 8.16.12 — but roughly half my first figure. **Grade must be settled
by live traces, not by proxy actors; the audit does exactly that.**

**Note:** the two foundation slabs are the ones Codex added in the
2026-08-14 pass to close "two previously missed support gaps" on the rear and
east edges. That fix was real but scoped to the *building* terrace; the
*yard* perimeter was never in scope.

**Material update (added 2026-08-18 after reading Appendix A).** On
2026-08-16 these same six walls were re-materialed from the flat teal
`MI_OT_Detention` to `MI_ABV_RuinBrick_WorldAligned`, explicitly because they
"dominated every exterior approach". That pass changed **material only** and
states it "preserves all transforms" — so **the floating is untouched and
still live.** This also re-identifies the screenshot: the long *tan brick*
wall hovering clear of the sand in 8.16.32 and 8.16.12 is this yard
perimeter, now brick-textured but still ~2 m in the air.

Consequently the flat mint-green surfaces in 8.12.11–8.15.04 are **not** the
yard walls — they are the `Core_SS_010_F1_*` / `F2_*` **building** shell,
which still carries `MI_OT_Detention`. Only the six yard walls were changed.

### Bug D — the SS_016 substation fence has *both* faults at once

This is the flat grey panel family in 8.18.32, 8.18.44, 8.19.08, 8.19.49 and
8.20.20 — the ones you selected with the gizmo. They are **not** detention-yard
walls and **not** `CoreCover_*` proxies (all 34 of those were hidden and
replaced with HISM sandbag/corrugated visuals on 2026-08-16).

The SS_016 compound floor is X 4,700→7,300, Y −8,000→−6,000 at Z 34,791.3.
The fence:

| Actor | Extent | Fault |
|---|---|---|
| `SS_016_Fence_N` | X 6,000→8,600 @ Y −6,000 | 1,300 cm past the compound east edge |
| `SS_016_Fence_S` | X 6,000→8,600 @ Y −8,000 | 1,300 cm past the compound east edge |
| `SS_016_Fence_E` | Y −7,000→−5,000 @ X 7,300 | 1,000 cm past the compound north edge |
| `SS_016_Fence_W` | Y −7,000→−5,000 @ X 4,700 | 1,000 cm past the compound north edge |

All four are 12 cm thin, 240 cm tall, on `MI_OT_Metal`, and all four start at
**Z 34,911.3 — 120 cm above the compound floor.**

So each panel is mis-centred by half its own length (the Bug A signature) *and*
floats 1.2 m off the ground (the Bug B signature). A 12 cm thick, 26 m long
flat metal panel hanging in mid-air is exactly what those screenshots show,
including the daylight and cast shadow underneath.

Four actors, one fix, and it clears the most-photographed defect in the set.

### Bug C (smaller) — six buttresses placed at roof height instead of on the ground

| Actor pair | Bottom Z | Site ground | Floating by |
|---|---|---|---|
| `ABV_SS_012_Buttress_NE` / `_SW` | 35,501.5 | 34,769.5 | **+732 cm** |
| `ABV_SS_005_Buttress_NE` / `_SW` | 35,494.9 | 34,762.9 | **+732 cm** |
| `ABV_SS_004_Buttress_NE` / `_SW` | 35,175.7 | 34,763.7 | **+412 cm** |

Each is a 55 × 55 × 220 cm post. They are meant to stand at the wall base and
are instead standing on the roof parapet — one full building height too high.
`ABV_SS_012_Buttress_NE` at XY (12850, 5800) is precisely the "oversized roof
post/chimney" you selected in the 8.23.37 screenshot.

(`ABV_SS021_Buttress_*` — a different, no-underscore naming — sits at Z
34,236–34,271, i.e. *buried*. SS_021 is outside phase one; noted only so it
is not mistaken for a phase-one item.)

---

## 4. Defect register by site

Classification key, per the handoff:
**[R]** verified runtime geometry defect · **[E]** likely editor-only/helper ·
**[O]** outside phase-one playable area · **[I]** needs in-editor inspection

### SS_010 Detention Annex + Detention Yard — worst site
*Screenshots: 8.12.11, 8.12.49, 8.14.00, 8.15.04, 8.15.34, 8.18.32, 8.18.44, 8.19.08, 8.19.49, 8.20.20*

| # | Defect | Class | Evidence |
|---|---|---|---|
| 1 | 6 yard perimeter walls float ~185–215 cm over sand | **R** | Bug B, measured |
| 2 | 4 obsolete parapets cantilever 17 m | **R** | Bug A, measured |
| 3 | Upper storey reads as one flat untextured mint-green plane spanning the whole elevation, overhanging the lower storey and extending past the building end | **R** | `MI_OT_Detention` on `Core_SS_010_F2_*`; 8.14.00 shows it as a single selected actor |
| 4 | Hard seam + dark void between upper and lower storeys; tan strips visible through the gap | **R** | 8.12.49 |
| 5 | Window sills/lintels misaligned — some float in the seam void detached from any window, some offset horizontally from their opening | **R** | 8.12.49, 8 selected slabs |
| 6 | Two cyan strips above the main doorway | **I** | 8.12.11, 8.12.49 — material or a stray actor; identify live |
| 7 | Blank pale panel jutting from the wall right of the lower-right window | **I** | 8.12.11, 8.12.49 |
| 8 | Oversized roof cap slab overhangs and floats above the green plane with a gap | **R** | 8.14.00, 8.15.04 |
| 9 | ~~Grey untextured cubes loose in the yard as prototype cover blocks~~ **WITHDRAWN** | — | All 34 `CoreCover_*` prototype blocks were hidden on 2026-08-16 and replaced by HISM sandbag/corrugated/rubble visuals. The corrugated-and-sandbag barriers visible in those shots are the *finished* result. Small red/green cubes remain **[I]** — likely editor gizmo/selection handles, per Appendix A's warning not to classify editor sprites as runtime defects. |
| 10 | `Core_SS_010_UpperRamp` (958 × 280 × 344 cm) overhangs footprint by 1,004 cm | **I** | intended external ramp; verify it lands on something |
| 11 | Yellow polyline crossing the whole scene | **E** | landscape/road spline visualisation |

### SS_011 Checkpoint Office
*Screenshot: 8.24.11*

| # | Defect | Class | Evidence |
|---|---|---|---|
| 12 | "Very long roof beam" extending far past the building = `SS_011_Parapet_N`/`_S`, 10 m overhang | **R** | Bug A, measured |
| 13 | Long detached ramp landing in open sand = `Core_SS_011_UpperRamp`, 958 × 280 × 344 cm, 1,004 cm beyond footprint, from a 300 × 300 × 20 cm landing | **R** | measured; the landing is too small to read as an entrance |
| 14 | ~~Three front pillars that connect to nothing~~ **WITHDRAWN** | — | Appendix A, 2026-08-16: these are the **intentional grounded vehicle gate posts**, verified 2–3 cm above local ground and re-finished to `MI_OT_Timber`. Not a defect. |
| 15 | Long thin tan slab floating at mid-height to the west | **I** | 8.24.11 — but note Appendix A records "the long overhead shade edge belongs to the existing checkpoint composition"; confirm live before touching |

### SS_012 Consulate Residence
*Screenshots: 8.22.29, 8.23.37*

| # | Defect | Class | Evidence |
|---|---|---|---|
| 16 | Two buttresses on the roof, 732 cm too high | **R** | Bug C, measured |
| 17 | 4 obsolete parapets cantilever 10.5 m | **R** | Bug A, measured |
| 18 | Pale-blue upper storey (`MI_OT_WallPaint_WorldAligned`) overhangs the dark lower storey on all sides and projects past the building end | **R** | 8.22.29, 8.23.37 |
| 19 | 16 lintels/sills misaligned — top row embedded in the roof band detached from any window; one row floats between storeys | **R** | 8.22.29, all 16 selected |
| 20 | Two door awnings crooked, at differing heights and angles | **R** | 8.22.29. Note these are the *replacement* corrugated + `MI_OT_Timber` awnings from the 2026-08-16 recovery pass, so the remaining fault is alignment only, not the asset |
| 21 | Harsh material break between storeys; inconsistent window framing (outer two framed, inner two bare) | **R** | 8.22.29 |
| 22 | Actor pivot far from its geometry on the selected roof post | **R** | 8.23.37 — gizmo well above/left of the mesh |
| 23 | Conspicuous grey-green ground pad rectangle under the building | **R** | `Ground_Earth_SS_012_R*C*`, 4 slabs 1,092 × 936 × 1 cm |

### SS_017 Covered Bazaar
*Screenshots: 8.16.57, 8.17.28*

| # | Defect | Class | Evidence |
|---|---|---|---|
| 24 | Four fabric awnings float ~1 m above and behind their counters. **Corrected:** not "no posts" — four canopy posts exist (`ABV_SS_017_BazaarCanopyPost_A_V1`…`_D_V1`, 12 × 12 × 300 cm cylinders, `BlockAll`). The defect is that the awnings do not meet them | **R** | 8.17.28 + Appendix A 2026-08-16 canopy-post finish |
| 25 | Counters not aligned with the awnings above them | **R** | 8.16.57, 8.17.28 |
| 26 | ~~Six `Core_SS_017_Stall_*` on `MI_DefaultColorway`~~ **likely stale** | — | Appendix A: the six prototype stall blocks were replaced in place with Quixel `Wooden_Table_veigfjmaw_High` during the interiors pass. My Aug-12 index predates that. Verify only. |
| 27 | Long flat roof slab overhangs the whole frontage | **R** | 8.16.57 |
| 28 | Unlit black interior visible through the central doorway | **R** | 8.16.57, 8.17.28 |

*SS_017 is the one site with a clean parapet set (modern only, 0.0 cm).*

### Unidentified phase-one facades — need in-editor ID
*Screenshots: 8.10.38, 8.16.12, 8.16.32, 8.21.34, 8.26.01*

| # | Defect | Class |
|---|---|---|
| 29 | Doorway surround visibly leaning off vertical, oversized for its opening, standing proud of the wall | **R** |
| 30 | Small repeated surround-like trim pieces scattered along the storey seam | **R** |
| 31 | Long tan brick wall floating clear of the ground, cantilevered and tilted | **R** |
| 32 | Grey untextured panel jammed diagonally into a building corner | **R** |
| 33 | ~8 actors with selection outlines but **no visible geometry** — invisible actors that may still carry collision | **I** — highest diagnostic value; matches the known "invisible obsolete parapets retained collision" pattern |
| 34 | Interior almost entirely black — no interior lighting | **R** |
| 35 | Bright light leak along the full ceiling/wall junction, and a second along the floor at the doorway | **R** |
| 36 | Cabinet/panel actor standing **inside** the doorway, blocking it | **R** |
| 37 | Small white plant sprites recurring across many sites | **I** — likely foliage rendering unlit/white; check `M_ABV_Foliage_Masked` instancing usage survived |

### Explicitly out of scope

| # | Item | Class |
|---|---|---|
| 38 | Large field of floating grey slabs, boxes and ribbons on the horizon | **O** — beyond the 13 sites; Codex recorded these as later world-vista/streaming scope |
| 39 | Black catenary arcs with regularly spaced hardware and a lattice tower | **O/I** — read as power-line spans; distant, classify before touching |
| 40 | `ABV_SS021_Buttress_*` buried ~500 cm below grade | **O** — SS_021 not in phase one |

---

## 5. Data provenance and required re-verification

The numeric findings come from
`abiverd_visual_conversion_preflight_v1.json`, dated **2026-08-12**. Codex ran
many mutation passes on 14–17 August after that snapshot. The measurements
are therefore **strong, specific hypotheses — not live truth**.

Before changing anything, each target must be re-read live:

1. Jason manually loads only the required World Partition region in the UI.
   No descriptor/intersection/region-loading scripts — that hang is documented
   and reproducible.
2. Query ≤10 actors at a time, by exact label.
3. Confirm label, transform, bounds, materials, visibility and collision.
4. Confirm authoritative dirty state is zero *before* mutating.

Items most likely to have moved since Aug 12: SS_003 and SS_004 parapets,
SS_005 and SS_018 wall materials, SS_007's upper shell, and anything touched
by the physical-material rebuild you ran on Aug 17/18.

### False-positive guards I applied after reading Appendix A

Reading the full chronology killed several of my own candidate findings.
Recording them so they are not re-raised later:

- **Engine basic-shape geometry is not itself a defect.** 415 visible basic
  shapes all carry intentional project materials. See the revision box in §2.
- **`CoreCover_*` prototype blocks are already resolved** — all 34 hidden,
  production HISM visuals in place.
- **`OT_EXT_Weather_*` actors** (SS_012/015/016, 256 × 368 × 256, no mesh)
  are editor-only volumes — these are the green wireframe boxes Appendix A
  warns about. **[E]**, not runtime geometry.
- **"Above the F1 floor" is not "floating."** My first automated sweep flagged
  ~200 actors as floating; almost all were upper storeys, roofs, roof
  utilities, masts, signs and lintels that are *correctly* elevated. Only
  overhang-beyond-footprint plus a genuine unsupported span is diagnostic. The
  four real cases are Bugs A–D.
- **Editor sprites, selection outlines and helper visualisation** in viewport
  captures are not defects. Confirm via exact actor flags, collision and Game
  View before proposing any change.

---

## 6. Recommended first correction pass

The handoff's sequencing still holds, and I am not going to run a broad
scripted pass before your visual feedback loop.

**Highest value, lowest risk, in order:**

0. **SS_016 substation fence (Bug D)** — promoted to first after the
   Appendix A review. Four actors, one transform fix each, and it clears the
   single most-photographed defect in the set. Smallest possible blast radius,
   so it also serves as the calibration job for the whole workflow.
1. **SS_010 detention yard** — the worst site and the one with the clearest
   mechanical fix. Two bounded jobs: re-ground the six yard walls (material
   already corrected on 2026-08-16; the transform was never touched), and
   resolve the four obsolete parapets. Both are transform/visibility changes,
   not modelling.
2. **SS_011 checkpoint** — the parapet pair and the ramp/landing. Small,
   isolated, and it is the site whose silhouette reads worst on approach.
3. **SS_012 consulate** — drop the two buttresses to grade, resolve the
   parapets, then the storey overhang.
4. **SS_017 bazaar** — awning supports. This one is genuinely additive art
   (stall posts), not a correction, so it is slower.

Bug A is the single best first move: on 7 of the 8 sites a proven-good
replacement parapet already exists, so resolving the obsolete set is a
**hide-or-remove decision, not a modelling decision**, and it removes the most
visually alarming geometry in your screenshots. Per the handoff I will not
delete any actor until runtime-vs-editor status, package ownership and
replacement coverage are each proven, and I will not delete anything without
your explicit approval — hide-with-rollback is the default proposal.

**What I need from you to proceed:**

- The before/after screenshots of your manual corrections, so I can calibrate
  to your intended standard rather than guessing — this is the step the
  handoff asks for and I would rather not skip it.
- Confirmation of which site to open first.
- The editor launched and the region loaded manually, per the stability rules.

**Open question I could not resolve from the files:** whether the phase-one
plan intends the `Core_*` cubes to be replaced with modelled/modular
architecture, or to remain cubes dressed with materials for the beta. That
answer changes whether items 3, 18 and 21 are "fix the transform" or "replace
the geometry", and I did not want to assume. Everything above is written so
that it is useful either way.
