# Operation Sunscar — errors made, and how to not repeat them

Date opened: 2026-08-21 · **Read this before starting work.**

A running record of mistakes made while working on this map, each with the
pattern behind it. Written at Jason's request after several errors reached him as
confident but wrong statements.

**The meta-pattern, stated once:** almost every error below is the same shape —
**a number was produced, trusted, and reported without checking what actually
generated it.** The fix is never "be more careful"; it is "verify what the
measurement hit before believing it."

---

## A. Process errors — the expensive ones

### A1. Did not ask for existing planning material
Spent a large part of 2026-08-20 re-deriving the map's structure — boundary,
road hierarchy, canal placement, cover principles — from actor names and
research. **Two authored master planning images existed the whole time** and
answered nearly all of it, plus a heritage plan with a full rule set.

**Rule:** before designing anything, ask "is there planning material I haven't
seen?" and read every doc in `Planning/` first. Cost: roughly a session.

### A2. Trusted an inferred boundary over an authored one
Derived the phase-1 envelope from a grep of `SS_###` in one document, then built
analysis on it. The authoritative 13-site scope was written in
`ABIVERD_OLD_TOWN_PAUSE_HANDOFF_2026-08-05.md`. **Missed SS_006 and SS_013.**

**Rule:** a list you assembled is a hypothesis. Find the list someone wrote down.

### A3. Built before validating
Built the poppy field before checking it against the heritage plan, violating
four written specs at once: uniform instead of 4–6 belts, high density inside
Old Town where the plan says low, wrong location, and no cull distances. Also
used live runtime PCG, which the plan explicitly forbids on this map.

**Rule:** check the work against the written spec *before* building, not after.

---

## B. Measurement errors — the embarrassing ones

### B1. Traced from site centres to get ground height — hit rooftops
**Caused two separate wrong conclusions.**

- Reported site ground heights spanning 8.86 m. They were roof heights.
- Reported "8 of 10 long pairs have clear standing sightlines at 184–236 m."
  That was **roof-to-roof**. At ground level the real figure was 5 of 10 clear,
  longest 178 m — a genuine problem, but far milder, and it made me recommend a
  much bigger intervention than was needed.

**Rule:** to sample ground, trace in **open ground outside a site's bounds**.
Never at a site centre. If a number looks like it might be a roof, it is.

### B2. Compared a restart test against computed values, not measured ones
Declared "TERRAIN LOST ON RESTART" when it had persisted perfectly. Expected
floors were computed as `grade − depth`, which is wrong wherever patches overlap
and blend.

**Rule:** verification compares **measured before** against **measured after**.
Never against intended values.

### B3. Checked free memory but not swap
Before a large write, reported "4.2 GB free — far more headroom than yesterday"
and proceeded. Swap was already at 41.9 GB of 43 GB. The editor was OOM-killed.

**Rule:** memory checks read swap and compressor, not just free pages.
`/tmp/mem.sh` does this.

### B4. Hardcoded a component suffix
Counted instances via `ISM_<mesh>_0`. PCG renames components to `_1` on
regeneration, so the count read zero and I reported the poppy field as destroyed.

**Rule:** enumerate components and match a prefix. Never hardcode an index.

---

## C. Constraint errors — right rule, wrong problem

### C1. Applied a terrain buffer to an object-placement problem
The 10 m no-sculpt buffer exists to protect building grounding from **terrain
edits**. I applied it to **ruin placement**, concluded only 3 blocker positions
existed and that two sightlines were unfixable. With the correct 2 m object
buffer there are **415** positions and no unfixable pairs.

**Rule:** before reusing a constraint, ask what it was protecting against. A
buffer against heightmap edits says nothing about where a wall can stand.

### C2. Diagnosed the wrong cause and rebuilt on it
Gully terrain vanished on restart. Concluded that multi-component patch actors
fail to re-register, and rebuilt 21 components into 21 separate actors. **That
was not the cause** — UE simply never marks the landscape dirty, so saves wrote
nothing. The rebuild was wasted work.

**Rule:** confirm a cause by testing it in isolation before acting on it.

---

## D. Tooling assumptions

| Assumption | Reality |
|---|---|
| `SetPluginEnabled` enables a plugin | Silent no-op. Edit the `.uproject` directly |
| LandscapePatch provides actors | Provides **components**; attach via `ActorTools.add_component` |
| `save_assets` on a landscape saves patch heights | Writes nothing unless the landscape is dirty. Force it, then **confirm the file count rose** |
| `ExecuteGraphInstance` re-runs the graph | Returns cached results. Respawn the volume |
| `set_properties` can carry bulk instance data | 2,700 entries drove swap 0.6 → 26 GB and killed the editor, three times |
| Optional-looking PCG params are optional | `jsonParams`, `nodeTitle`, `nodeComment` are all required |
| Nested struct scale passes through `AddNode` | Ignored. Set afterwards, and the key is `scale`, not `scale3D` |

Full API detail lives in `ABIVERD_PROJECT_RULES_V1.md` §14.

---

## E. Judgement errors

### E1. Recommended navigation and audio first
Advised doing them early because they were entirely absent. Wrong: navmesh is
built **from** geometry and audio volumes **from** spaces. Doing them before a
terrain pass means building them twice. Corrected to last in the sequence.

**Rule:** "absent" and "urgent" are different. Check what a thing depends on.

### E2. Over-alarmed on a flawed measurement
The roof-to-roof sightline error (B1) led to recommending a large ruins
intervention and declaring parts of the map unfixable. Five placeholder walls
brought it into spec.

**Rule:** before escalating a problem, re-derive the number a second way.

---

## Checklist before reporting any measurement

1. What did the trace actually hit — ground, a roof, a prop?
2. Am I comparing measured-to-measured, or measured-to-intended?
3. Is this constraint the right one for *this* problem?
4. Did the write reach disk? Did the file count change?
5. Can I derive this a second, independent way?
