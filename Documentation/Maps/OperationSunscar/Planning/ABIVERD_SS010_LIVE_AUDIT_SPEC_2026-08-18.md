# SS_010 Detention Annex — read-only live audit specification — 2026-08-18

Author: Claude Code. **This document authorises no mutation.** It is the exact
query plan for step 1 of Jason's approved SS_010 sequence (Appendix D §C).

Predicted values are from `abiverd_visual_conversion_preflight_v1.json`
(**2026-08-12**). Codex mutated heavily 14–17 August, so every predicted value
below is a hypothesis. The audit's product is a **delta table**: predicted vs
live, per actor.

---

## 0. The gate rule

Every pass/fail condition in this document must **fail on the current map**.
A condition that already passes is not evidence of quality — it is a broken
test, and I will discard it rather than report it as a pass.

---

## 1. Preconditions — Jason

1. Launch the editor **detached**, map worktree only:

```sh
nohup "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" \
  /Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject \
  -ModelContextProtocolStartServer \
  > /tmp/ue_map_launch_$(date +%s).log 2>&1 & disown
```

2. Confirm `Lvl_Blockout_01` is open.
3. **Manually load the SS_010 World Partition region in the UI.** No scripted
   World Partition descriptor/intersection/region-loading calls — that hang is
   documented and reproducible.
4. Wait for port 8000 `LISTEN` and `GET 127.0.0.1:8000/mcp` → 405.
5. Run **`/mcp`** so the `unreal-mcp` tools register. They are **not** bound in
   this session because the editor was closed at session start.

I will not send a single query before 4 and 5 are confirmed.

## 2. Standing constraints

- ≤ 10 actors per query, addressed by **exact label**. No broad enumeration.
- ≤ 8 world traces total for terrain (batch F).
- Stop at the first sign of a stalled query; do not retry blindly.
- Read-only. No `modify()`, no property set, no save, no `reload_packages`.
- Compare transforms as **numeric** translation/quaternion/scale — never the
  string form, which embeds a temporary struct address.

**Do not touch, this pass or any pass, without separate approval:**
`CoreTarget_DetentionObjective`, `CoreVolume_DetentionObjective` (1000 × 1000 ×
500 trigger), the 288 hidden legacy ground overlays, and any `COL_*` authoritative
collision proxy.

## 3. Fields to read per actor

`label` · `folder` · numeric world transform · `bounds_origin` / `bounds_extent` ·
`static_mesh` · material overrides · `bHidden` / `bHiddenInGame` ·
collision profile + `CollisionEnabled` · `can_ever_affect_navigation` ·
`GenerateOverlapEvents` · replication · tick · **outermost package path**

---

## 4. Batch A — the six yard walls (Bug B) · 6 actors

| Actor | Predicted bottom Z | Predicted size (cm) |
|---|---|---|
| `Core_DetentionYard_F1_S_Left` | 34,979.0 | 1600 × 40 × 250 |
| `Core_DetentionYard_F1_S_Right` | 34,979.0 | 3200 × 40 × 250 |
| `Core_DetentionYard_F1_W_Wall` | 34,979.0 | 40 × 4400 × 250 |
| `Core_DetentionYard_F1_N_Wall` | 34,979.0 | 5200 × 40 × 250 |
| `Core_DetentionYard_F1_E_Left` | 34,979.0 | 40 × 2700 × 250 |
| `Core_DetentionYard_F1_E_Right` | 34,979.0 | 40 × 1300 × 250 |

Predicted material: **`MI_ABV_RuinBrick_WorldAligned`** — changed from
`MI_OT_Detention` on 2026-08-16 in a material-only pass that states it
"preserves all transforms". **If the transform is unchanged and the material is
ruin brick, Bug B is confirmed as live and untouched.**

Design cross-check: `Desert_Glory_Inspired_Map_Plan.md` §4 specifies exterior
wall height **2.2–2.8 m**. These are 250 cm — the correct height. Only Z is
wrong, which argues for **re-grounding** over adding a plinth.

**Pass condition:** every wall's underside sits within 5 cm of traced grade, or
on an authored foundation, along its whole run.
**Predicted result: FAIL on all six.**

## 5. Batch B — obsolete parapets (Bug A) · 4 actors

`SS_010_Parapet_N` · `_S` · `_E` · `_W` — predicted bottom Z **35,664.8**,
sizes 3400 × 30 × 80 and 30 × 2800 × 80, material `MI_OT_Detention`.

Predicted overhang beyond the 3400 × 2800 roof: **1,700 cm** (N/S) and
**1,400 cm** (E/W) — each mis-centred by half its own length.

**Critical read: `bHidden` / `bHiddenInGame` per actor.** The 8.21.34 screenshot
shows selection outlines containing no visible geometry at another site, so this
family is already hidden inconsistently. Do not assume all four are visible.

**Pass condition:** zero *visible* actors of this family, and any retained
actor is `NoCollision` with navigation off.

## 6. Batch C — replacement parapets + the spec problem · 4 actors

`ABV_SS_010_RoofParapet_North` · `_South` · `_East` · `_West` — predicted
bottom Z **35,644.8**, height **88 cm**, `MI_ABV_RuinBrick_WorldAligned`,
overhang **0.0 cm**.

> **Open design issue — needs Jason's decision, do not act on it this pass.**
> `Desert_Glory_Inspired_Map_Plan.md` §4 specifies **parapet height 1.0–1.2 m**.
> This set is **88 cm** and the obsolete set is **80 cm** — *both under spec*.
> SS_010's roof is reached by an authored ramp and landing, so under Appendix D
> §4 it is phase-one gameplay space, and art-plan rule 2 forbids casually
> changing cover heights. Hiding the obsolete set and keeping these therefore
> leaves under-height cover on a playable roof. I will report the measured
> height and propose, not adjust.

## 7. Batch D — foundations and skirts · 6 actors

| Actor | Predicted bottom Z | Predicted top Z | Predicted extent |
|---|---|---|---|
| `Foundation_SS_010_Detention_Terrace` | 34,939.3 | 35,034.3 | X 2200→5600, Y 9100→11900 |
| `Foundation_SS_010_West_Support` | 34,924.8 | 34,984.8 | X 500→3900, Y 7700→10500 |
| `ABV_SS_010_FoundationSkirt_North` | 34,980.7 | — | 3400 × 24 × 35 |
| `ABV_SS_010_FoundationSkirt_South` | 34,980.7 | — | 3400 × 24 × 35 |
| `ABV_SS_010_FoundationSkirt_East` | 34,980.7 | — | 24 × 2800 × 35 |
| `ABV_SS_010_FoundationSkirt_West` | 34,980.7 | — | 24 × 2800 × 35 |

Purpose: establish **which yard-wall runs have real support and which do not**.
Predicted combined foundation cover is X 500→5,600 by Y 7,700→11,900, against a
yard perimeter of X −400→4,800 by Y 6,500→10,900 — leaving the **entire south
wall** and **entire west wall** unsupported. The four skirts serve the
**building** footprint (3400 × 2800), not the yard.

## 8. Batch E — roof access, read-only · 4 actors

`Core_SS_010_UpperRamp` (958 × 280 × 344, bottom Z 34,973.0) ·
`Core_SS_010_UpperLanding` (300 × 300 × 20, bottom Z 35,284.8) ·
`Detention_SouthStep_01` · `Detention_SouthStep_05`.

Per Appendix D §5 these are **assumed intended access** — audit, do not remove.

Design cross-check: exterior stair clear width spec **2.4–3.0 m**; the ramp is
280 cm wide → in spec. The five south steps rise ~7.7 cm each against a spec of
**17–19 cm** — record it, defer it.

**This batch gates everything else.** Route verification comes before any
ramp/landing change, and re-grounding the yard walls must not break the gate,
objective approach or extraction traversal.

## 9. Batch F — terrain traces · exactly 8

Eight downward traces at the wall lines, to settle grade properly. Record
returned actor, class and Z for each.

| # | X | Y | Wall run |
|---|---|---|---|
| 1 | 400 | 6,500 | S_Left |
| 2 | 3,200 | 6,500 | S_Right |
| 3 | −400 | 7,500 | W_Wall south end |
| 4 | −400 | 9,800 | W_Wall north end |
| 5 | 1,000 | 10,900 | N_Wall west end |
| 6 | 3,800 | 10,900 | N_Wall east end |
| 7 | 4,800 | 7,800 | E_Left |
| 8 | 4,800 | 10,200 | E_Right |

**This is the measurement that decides the Bug B fix**, and it supersedes every
grade figure I have quoted so far. My earlier 185–215 cm float estimate used
distant sites' floors as a grade proxy and was too high; local ground-contact
actors near this yard (`QX_Square_Detention_West_End` 34,869.7,
`QX_Sandbag_Detention_West_A` 34,879.2, `Detention_SouthStep_01` 34,917.6) put
grade nearer **34,870–34,920**, i.e. a float of roughly **60–110 cm**. Neither
figure is authoritative. The traces are.

Each trace must **ignore** the wall being tested and any overhead blocker —
`CoreCover_A06` previously returned an overhead compound floor and produced a
wrong conform. Verify each hit is Landscape or an intended foundation.

---

## 10. Deliverable

A delta table — predicted vs live, per actor — plus:

1. Which of Bugs A/B confirm live, which are already partly fixed, which are stale.
2. Exact per-wall correction deltas for Bug B, derived from batch F.
3. Exact visibility/collision state of the four obsolete parapets.
4. Measured parapet height against the 1.0–1.2 m spec, as a proposal.
5. Anything found that is **not** in the register — expected, since the register
   is built on a nine-day-old snapshot.

Then I stop and show Jason before proposing any change.
