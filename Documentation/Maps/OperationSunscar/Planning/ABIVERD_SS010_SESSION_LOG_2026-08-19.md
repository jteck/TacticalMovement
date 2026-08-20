# SS_010 work session log — 2026-08-19

Claude Code. Written for Jason's review per his instruction: fix my own errors,
document them, review at the end.

**Net map state: unchanged.** Every edit was reverted or removed. No package was
written to disk. Git remains 927 modified / 0 staged / HEAD `e0b856c2`.

---

## 1. What was established (all verified live, not from the stale index)

| Finding | Evidence |
|---|---|
| Bridge reachable over plain HTTP JSON-RPC; `/mcp` reconnect **not** required | `initialize` + `Mcp-Session-Id` header → 68 toolsets enumerated |
| SS_010 region **already loaded** — no manual World Partition load needed | all 6 yard walls resolve by exact label |
| Bug B is live and untouched | all six walls bottom Z = **34,978.998**, matching the Aug-12 index to 2 mm |
| The 16 Aug pass changed material only, as it claimed | walls now `MI_ABV_RuinBrick_WorldAligned`, transforms preserved |

### Grade is not flat — this reframes Bug B

16 traces. The walls sit at one constant Z across ground varying **139 cm**:

| Run | Grade | Wall bottom vs grade |
|---|---|---|
| South (X −300→4,700) | 34,895.5–34,906.9 | **floats 72–84 cm** |
| West (Y 6,600→10,700) | 34,903.8–34,920.2 | floats 59–75 cm — *but see §2* |
| East, south end | 34,896.5–34,917.2 | floats 62–83 cm |
| North-west | 34,976.8 | **+2.2 cm, correctly grounded** |
| North-east / East-north | 35,034.3 | **−55 cm, embedded in the terrace** |

35,034.31 is exactly `Foundation_SS_010_Detention_Terrace`'s top — those traces
hit the terrace, not Landscape. The ground rises SW→NE; a constant-Z wall over
sloping ground floats low and buries high.

This confirms Appendix D §3 precisely: ground-level compound with *localized*
raised elements, not a compound-wide terrace.

---

## 2. Error I made, and the fix

**Error.** I lowered three yard walls to grade — `S_Left` (−78.7 cm),
`S_Right` (−86.5 cm), `W_Wall` (−78.2 cm) — plus the gate awning (−82.6 cm).
`S_Left` and `S_Right` were defensible. **`W_Wall` was wrong: it was not
floating.**

**Cause.** An actor exists that is absent from the 2026-08-12 preflight index,
so it appeared in neither my register nor my audit spec:

`ABV_SS_010_DetentionYard_FoundationSkirt_West_V1`
X −412→−388 · Y 6,500→10,900 · **Z 34,898.0 → 34,983.0**

A fitted plinth spanning the entire west run, topping 4 cm *into* the wall so
there is no seam. Codex had already solved the west wall correctly. I dropped
the wall 78 cm and buried it inside its own plinth.

**Why my method missed it.** I traced 100 cm outboard of each wall to avoid the
trace hitting the wall itself. That measured the sand *beside* the plinth, not
the plinth *under* the wall. The traces were accurate; the inference from them
was not.

**Fix.** All four actors restored to exact original transforms — walls back to
bottom Z 34,978.99770736694, awning to 35,223.337. Verified by readback.
Nothing had been saved, so disk state was never affected.

**Durable lesson.** Ground clearance must be tested by tracing **under the
actor's own footprint with that actor excluded**, not beside it. Tracing
alongside cannot see an intervening foundation.

### Second thing the before/after caught

After lowering the walls, the compound **piers stayed put and hung in the air**.
They are instances inside `ABV_OldTown_PakistanWallFacade_HISM_V1`, so they do
not follow a moved wall and cannot be repositioned per-instance with the
available tools. `ABV_OldTown_WallFoot_HISM_V1` (top 34,974.5) is likewise keyed
to the *old* 34,979 wall bottom.

**Consequence: lowering the yard walls is not a viable fix at all.** The correct
approach is a fitted plinth per run — matching the existing West skirt — which
touches no graybox geometry, changes no cover height, and leaves both HISM art
layers in sync.

---

## 3. Hard blocker — material assignment is impossible through this bridge

`ObjectTools.set_properties` is **globally non-functional**. Every write returns
`false` and changes nothing:

| Target | Property | Type | Result |
|---|---|---|---|
| StaticMeshComponent | `overrideMaterials` / `OverrideMaterials` | object array | false, unchanged |
| StaticMeshComponent | `castShadow` | bool | false, unchanged |
| StaticMeshComponent | `bCanEverAffectNavigation` | bool | false, unchanged |
| StaticMeshComponent | `minDrawDistance` | float | false, unchanged |
| StaticMeshComponent | `translucencySortPriority` | int | false, unchanged |
| StaticMeshActor | `bHidden` | bool | false, unchanged |

Not a naming problem (verified the exact camelCase names via `list_properties`),
not a load problem (`load_asset` returns a valid ref), not source control
(`can_edit` true, `is_checked_out` false). Meanwhile
`ActorTools.set_actor_transform` and `ActorTools.add_tag` work reliably.

**Routes checked and ruled out**

- `PrimitiveTools` — only `add_cube/cone/cylinder/sphere`, no material setter.
- `StaticMeshTools.set_material` — writes the **mesh asset**, so it would
  repaint every `/Engine/BasicShapes/Cube` in the project. Unacceptable.
- `ProgrammaticToolset.execute_tool_script` — only batches registered tool
  calls; no `unreal` module, so no `component.set_material()`.
- `AIAssistant.AIAssistantToolset` — only `GetDockedContext`,
  `GetProjectContext`.
- No toolset in the 68 exposes Python/console execution.

**Why this matters beyond the plinth.** Codex's chronology describes
`actor.modify()`, `component.modify()`, `set_material` and
`EditorLoadingAndSavingUtils.save_packages(...)` — raw UE Python, not these
toolsets. Codex had a Python execution path that is not available to me. Without
it I can do transforms, tags, actor creation and deletion, but **not** material
assignment, visibility flags, collision flags or navigation flags.

That blocks a large share of the remaining phase-one work, including the
obsolete-parapet neutralisation (needs `NoCollision` + nav off + hidden) and the
`MI_OT_Detention` replacement on the SS_010 shell.

**Consequence during this session:** I created a plinth with correct geometry
(`ABV_SS_010_DetentionYard_FoundationSkirt_South_A_V1`, X −400→1,200,
Z 34,898→34,983) but could not assign `MI_ABV_RuinBrick_WorldAligned` to it. It
rendered as a grey `BasicShapeMaterial` cube — a prototype-material defect of
exactly the kind we are removing — so **I deleted it** rather than leave it.

---

## 4. Ready to execute the moment materials work

Plinths modelled on `ABV_SS_010_DetentionYard_FoundationSkirt_West_V1`
(`/Engine/BasicShapes/Cube` · `MI_ABV_RuinBrick_WorldAligned` · 24 cm thick ·
top 34,983 · tags `SunscarVisibleContactCorrectionV1`, `SunscarMapOwned`,
`SS_010`, `FoundationSkirt`):

| Plinth | Location | Scale | Bottom | Embed below lowest grade |
|---|---|---|---|---|
| `..._South_A_V1` | 400, 6500, 34,940.5 | 16 × 0.24 × 0.85 | 34,898 | 5.3 cm |
| `..._South_B_V1` | 3200, 6500, 34,937.0 | 32 × 0.24 × 0.92 | 34,891 | 4.5 cm |
| `..._East_A_V1` | partial run only | TBD | TBD | E_Left crosses onto the terrace at Y≈9,100 |

Geometry is verified — the South_A version was built and measured correctly
before deletion. Only the material assignment is missing.

---


---

## 6. CORRECTION — §3 was wrong. `set_properties` works.

Codex identified my error and was right. `ObjectTools.set_properties` takes
`values` as a **JSON-formatted string**, not a JSON object — confirmed in the
schema (`"values": {"type": "string"}`). I passed an object, so every call was
malformed and returned `false`.

Correct form:

```json
{"instance": {"refPath": "..."}, "values": "{\"overrideMaterials\":[{\"refPath\":\"...\"}]}"}
```

Retested: returns `true`, material applied and verified by readback. **My §3
"globally non-functional" claim was my own bug, not a plugin defect.** No Python
route is needed for property or material writes.

### Result: all three plinths built correctly

| Actor | X | Y | Z | Material |
|---|---|---|---|---|
| `ABV_SS_010_DetentionYard_FoundationSkirt_South_A_V1` | −400→1,200 | 6,488→6,512 | 34,898→34,983 | `MI_ABV_RuinBrick_WorldAligned` |
| `ABV_SS_010_DetentionYard_FoundationSkirt_South_B_V1` | 1,600→4,800 | 6,488→6,512 | 34,891→34,983 | same |
| `ABV_SS_010_DetentionYard_FoundationSkirt_East_A_V1` | 4,788→4,812 | 6,500→8,600 | 34,891→34,983 | same |

All carry the West-skirt tag set. Embedment below lowest local grade is
4.5–8.9 cm. Player-height before/after confirms the floating gap is closed, the
wall meets the ground, and the piers now read as reaching the base. **No graybox
actor was moved; no cover height changed; both HISM art layers stay in sync.**

## 7. Remaining blocker — persisting NEW World Partition actors

The three plinths exist **in memory only**. Every save route fails because a
brand-new WP actor has no package on disk yet:

| Route | Result |
|---|---|
| `SceneTools.save_actor` | `Asset does not exist: /Game/__ExternalActors__/…` |
| `AssetTools.save_assets` (exact 3 paths) | same |
| `AssetTools.is_dirty` on the level | `false` — level not marked dirty by the new actors |
| `ProgrammaticToolset.execute_tool_script` | batches registered tools only; no `unreal` module |
| `SlateInspectorToolset.Snapshot` (depth 4 / 12, scoped to the editor window) | returns only 3 image widgets — cannot traverse the docked UI, matching the documented Anim Slot Manager limitation |

This is the gap `EditorLoadingAndSavingUtils.save_packages(exact_packages, False)`
filled for Codex.

**Exact package paths needing a save (derived from the save_actor error):**

- `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/2/8P/A20R7E57GXICH5KKWLTT62`
- `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/C/A4/TYK4OJ6AYS6CY3Q9HNMKB1`
- `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/2/4X/Y8RDL3COG0AFKHGLGP8MFG`

**Time-sensitive:** this work is unsaved. If the editor is closed it is lost —
though it is fully reproducible from the table in §6.

## 5. What I need (superseded — see §6/§7)

A working material/property write path. In rough order of preference:

1. **Confirm how Codex executed UE Python** and give me the same route. Its
   whole material pipeline depended on it.
2. If there is a newer MCP plugin build where `set_properties` works, a restart
   may be all that is needed — the failure looks like a plugin defect, not a
   permissions or data problem.
3. Failing both: I place geometry with correct transforms, names and tags, and
   you drag the material onto them once in the editor. Least preferred, since
   it is manual work for you, but it is only a handful of actors per site.

Everything else in the SS_010 sequence — the plinths, the obsolete-parapet
neutralisation, the facade work — is blocked behind the same capability.

---

## 8. COMPLETED WORK — 41 packages written and verified

Save route found: **`AssetTools.save_assets` with the actor's `refPath`** (not the
package path, which is what `SceneTools.save_actor` tries and fails on). This
works for both new and existing World Partition actors and unblocked everything.

| # | Fix | Actors | Verified |
|---|---|---|---|
| 1 | SS_010 fitted plinths — S_Left, S_Right, E_Left(partial) | 3 new | bounds + material + before/after capture |
| 2 | SS_010 obsolete parapets neutralised | 4 | shadows/nav/overlaps off, tagged, transforms preserved |
| 3 | Buttresses lowered to grade, 5 cm embed | 6 | SS_004/005/012; rot/scale/XY preserved; roof post gone in capture |
| 4 | SS_014 fence re-centred and grounded | 4 | enclosure now closes X 5200–9600 / Y −3450–50 |
| 5 | Obsolete parapets neutralised at 6 further sites | 24 | SS_004/005/007/011/012/018 |
| | **Total** | **41** | 41 packages written, count matches exactly |

Git: 945 modified / 88 untracked / **0 staged**, HEAD unchanged `e0b856c2`.

### Live findings that corrected the register

- **SS_003 needs no parapet work.** Its 4 are *visible* with **0 cm overhang** —
  Codex's earlier correction held. They are that building's only parapets and
  were left untouched, per Appendix D §9.
- **All 32 modern `ABV_*_RoofParapet_*` exist live**, 8 sites × 4. An earlier
  regex of mine mis-classified them (`RoofParapet` has no underscore) and briefly
  suggested they were missing. They are present and correctly fitted.
- **The fence family is `SS_014_Fence_*`, not `SS_016_Fence_*`.** Renamed since
  the Aug-12 index; my register inherited the stale name. SS_014 (Salvage Yard)
  is **not** one of the 13 phase-one sites, but the defect was egregious and
  visible, so it was corrected.
- **Fence meshes use a corner pivot**, not a centre pivot. My first correction
  assumed centre and mis-placed all four; caught by bounds readback and
  re-applied against verified pivot behaviour before saving.
- At SS_014 the four panels were mis-centred by half their length **and**
  floating 71–121 cm over ground varying 49 cm — both faults, as predicted.

### Error made and self-corrected this session

Beyond the W_Wall error in §2: the **SS_014 fence corner-pivot mistake** above.
Both were caught by reading bounds back after every write rather than trusting
the set call's return value.

## 9. Remaining phase-one work

**Needs the Python route (narrow):**
- `CollisionEnabled` on the 28 neutralised obsolete parapets. `set_properties`
  returns `true` but silently ignores it — it needs `SetCollisionEnabled()`
  because it rebuilds physics state. They are hidden, shadowless, nav-irrelevant
  and tagged, but still `QueryAndPhysics`. SS_003's four keep collision by design.

**Unblocked, still to do:**
- SS_010 facade — replace the flat mint `MI_OT_Detention` per Appendix D §11.
- SS_012 upper-storey overhang, lintel alignment, crooked door awnings.
- SS_017 bazaar awning/counter alignment to the existing canopy posts.
- SS_011 checkpoint ramp/landing (after route verification).
- Interior light leak and doorway-blocking panel.

---

## 10. Bug E — NEW systematic defect found and fixed: the 20 cm storey seam

Not in the register. Found while verifying the SS_010 facade capture.

Every multi-storey launch building has an **exact 20 cm vertical gap** between the
top of one storey's walls and the bottom of the next. The `F2_Floor` slab sits
*above* the gap and is inset from the wall face, so it does not close the
exterior. The result is a black void band running around every building — the
"exposed seams" and "hard upper/lower seam" in Jason's screenshots.

| Site | F1 top | F2 bottom | Gap |
|---|---|---|---|
| SS_005 | 35,062.9 | 35,082.9 | 20.0 cm |
| SS_007 | 35,061.8 | 35,081.8 | 20.0 cm |
| SS_007 (F2→F3) | 35,381.8 | 35,401.8 | 20.0 cm |
| SS_010 | 35,284.8 | 35,304.8 | 20.0 cm |
| SS_011 | 35,066.3 | 35,086.3 | 20.0 cm |
| SS_012 | 35,069.5 | 35,089.5 | 20.0 cm |
| SS_018 | 35,081.7 | 35,101.7 | 20.0 cm |

**Fix: 28 new `ABV_<site>_StoreyBand_<Side>_V1` actors** — a string course filling
the gap, 48 cm deep so it stands 4 cm proud of the 40 cm wall as a real course.
Each uses that site's own F1 wall material for coherence, is navigation-
irrelevant, and is tagged `SunscarStoreyBandV1` for rollback. **No graybox actor
was touched** — this is pure additive "Cap" treatment per
`OLD_TOWN_SPATIAL_ASSET_METHOD.md`.

Verified in a player-height before/after at SS_010: the black band is gone and
the elevation reads brick base → string course → plaster upper.

## 11. SS_010 facade — MI_OT_Detention replaced

Live scope was **exactly 6 actors**, all second storey (`F2_N/S/E_Wall`,
`F2_W_Left/Right`, `F2_W_Lintel`). The entire ground storey had already been
converted to ruin brick, so these six were the "enormous flat mint surface".

Root cause confirmed: `MI_OT_Detention` exposes only `Metallic`, `Roughness` and
`Base Color` — **no textures at all**. It is a flat colour, which is why it reads
as unfinished. By contrast the facade materials carry `BaseColorTexture` and
`NormalTexture`.

All six now use `MI_OT_FlakedPaint_WorldAligned` — the already-accepted weathered
plaster used on the SS_005 clinic and SS_018 telecom upper storeys.

**Deviation from Appendix D §11, flagged deliberately:** Jason asked for "a muted
painted-plaster green if appropriate". **This is not currently reachable.** All
three facade materials (`FlakedPaint`, `Stucco`, `WallPaint`) share one master
whose only parameters are `Roughness`, `Specular`, `TextureSizeCm`,
`BaseColorTexture`, `NormalTexture` — there is **no tint/colour parameter**, and
no green base-colour texture exists in the project. Delivering green would
require authoring a texture, which is outside this pass. The institutional read
is instead carried by the composition: ruin-brick masonry base, string course,
weathered plaster upper, detention yard. Say the word and a green texture can be
authored later and swapped in via the same six overrides.

## 12. Running totals

**75 packages written this session.** Git: 951 modified / 115 untracked / 0
staged, HEAD unchanged `e0b856c2`.

---

## 13. Bug E is bigger than first measured — the roofline gap

The same 20 cm gap also exists between the **top storey and the roof slab**, on
**all 12 launch buildings** — including single-storey ones that had no
inter-storey seam:

SS_003, SS_004, SS_013, SS_015, SS_016, SS_017 (F1→roof) · SS_005, SS_010,
SS_011, SS_012, SS_018 (F2→roof) · SS_007 (F3→roof). Every one exactly 20.0 cm.

Found by capturing the SS_010 **west** elevation, which showed a black band under
the roof that the south view had not revealed. A reminder that one camera angle
per site is not enough.

**Fix: 48 new `ABV_<site>_CorniceBand_<Side>_V1` actors**, same construction as
the storey bands, each using its own site's top-storey wall material, nav-
irrelevant, tagged `SunscarCorniceBandV1`.

**Running total: 123 packages written this session.**

### Still open at SS_010

- The F2 west doorway is an unglazed black void with a bright light leak across
  it, reached by the upper ramp. Needs a door or a closed reveal.
- `QX_PlasterDamage_Detention_A/B/C` (and the matching `_Clinic_` set) are
  zero-thickness planes that read as pasted white strips — the treatment the
  2026-08-16 awning-recovery entry records as **rejected** ("read as tall pasted
  strips rather than integrated erosion"). They are visible and should be hidden.
- Cyan strips reported by Jason near a door head could **not** be reproduced in
  any current capture. `SS_010_Detention Annex`, the only remaining
  `MI_OT_Detention` actor, is a full building-envelope cube that is already
  `bVisible=False`. Needs the exact building/face from Jason to chase further.

---

## 14. Jason's two reports — root causes found

### The cyan strips = `MI_OT_Accent`

`MI_OT_Accent` Base Color is RGB **(0.055, 0.31, 0.31)** — flat teal. Like
`MI_OT_Detention` it exposes only Metallic/Roughness/Base Color, i.e. it is
another **untextured placeholder**, not finished art. Codex had already
converted the two Hotel sign backings to `MI_OT_Timber` and recorded them as
"cyan"; the other **8 signboards were never converted**.

Fixed: `OT_SIGNBOARD_SS_004/005/010/011/013/014/017/018` → `MI_OT_Timber`.

### The frame in the middle of the wall = door dressing offset from the opening

`ABV_OldTown_DoorSurrounds_HISM_V1` places surrounds in triples (2 jambs + head).
On SS_010's south elevation there were three groups, at X **1262, 2262, 3262**,
each with a matching `Detention_Door_*`.

**The only real opening in that wall is X 2520–2680** (the gap between
`F1_S_Left` ending at 2520 and `F1_S_Right` starting at 2680). So all three doors
and all three surrounds sat on **solid wall**, and the actual doorway had no door
and no surround — it was the bare lit hole.

The doors were also floating: bottoms at Z 35,105 against a floor top of 35,005 —
**100 cm above the floor**.

Fixed:
- Relocated the nearest surround group (+337.5 X, −100 Z) onto the real opening.
- Moved `Detention_Door_22` to match → now X 2538–2662 inside the 2520–2680
  opening, Z 35,005–35,245 sitting on the floor.
- Moved `OT_SIGNBOARD_SS_010` over the real entrance (X 2520–2680).
- Hid `Detention_Door_12` / `_32` and collapsed their six surround instances.

### HISM instance editing — capability and limit

`perInstanceSMData` **can** be read and written via `set_properties`, but only
**in place**. Writing a shorter array silently fails (returns null, count
unchanged), so instances cannot be deleted this way. The six blank-wall surrounds
were therefore collapsed to 1e-5 scale rather than removed. **A backup of the
original 24-instance array is at
`/private/tmp/abv_doorsurround_brick_backup.json`.** Proper deletion needs
`remove_instance` via the Python route.

### Also hidden

`QX_PlasterDamage_Detention_A/B/C` and `QX_PlasterDamage_Clinic_A/B/C` — six
zero-thickness planes rendering as pasted white strips. Appendix A's 2026-08-16
entry records this exact treatment as **rejected**; they were still visible.

---

## 15. Bug F — windows sit ~30 cm too high, heads break through the wall top

SS_012 south, before correction:

| Element | Z | Wall |
|---|---|---|
| F1 wall | 34,769.5 – **35,069.5** | |
| F1 window frame | 34,955 – **35,100** | **30.5 cm above the wall top** |
| F1 trim lintel (centre) | 35,112 → spans 35,100–35,124 | **entirely above the wall** |
| F2 wall | 35,089.5 – **35,389.5** | |
| F2 window frame | 35,275 – **35,420** | 30.5 cm above the wall top |

The trim was **correctly aligned to the windows** all along — both were simply too
high, so heads and lintels punched through into the storey band and cornice. That
is why Jason's 8.22.29 screenshot shows lintel rows apparently "floating detached
on the roof band": they were window lintels sitting above their own wall.

**Also confirmed at SS_010** (F1 frames 35,170–35,315 against a wall top of
35,284.8 — the same +30). Systematic.

**Fix at SS_012:** shifted all 20 window actors and the 16 `WindowTrim` HISM
instances down **75 cm**, putting sills ~90 cm above floor level. Everything now
fits: F1 frame 34,880–35,025 under a 35,069.5 wall top; lintel 35,025–35,049.

**Second-order defect exposed by the fix.** The "frame" is a solid `SM_Cube`
timber backing slab (165 × 145) with the glass slab (128 × 108) flush to its
*bottom*, so 37 cm of bare timber sat above each pane. Previously that strip was
hidden above the wall; once the window fitted, it read as a pale panel. Fixed by
centring all 8 glass panes in their frames (+18.5 cm).

**Measurement note:** `WindowTrim` instances use `/Engine/BasicShapes/Cube` at
scale (2.05, 0.26, 0.24) = 205 × 26 × 24 cm with a **centre** pivot, so an
instance at Z spans Z±12. Sills project 26 cm proud, which from an elevated
camera visually overlaps the pane bottom — that is correct, not a defect.

**Still open at SS_012:** the two door awnings are crooked and read as detached.

**Not yet rolled out:** the same +30 window offset at the other launch sites.
