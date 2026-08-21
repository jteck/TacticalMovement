# Abiverd — resume handoff after UE/terminal restart — 2026-08-19

Written by Claude Code immediately before a forced restart (Unreal and terminal
both out of memory). Read this first on resume, then
`ABIVERD_SS010_SESSION_LOG_2026-08-19.md` for full detail.

---

## 1. Exact state at shutdown

| Item | Value |
|---|---|
| Branch | `feature/map-development` |
| HEAD | `e0b856c20cdad11f7057248c851d4d344f43fbe1` (unchanged all session) |
| Tracked modified | **961** |
| Untracked | **163** |
| Staged | **0** |
| External-actor packages written this session | **163** |
| Commits made | **none** |

**There is still no recovery commit.** 163 packages of this session's work exist
only as unstaged working-tree files.

---

## 2. ⚠️ ONE BROKEN ACTOR — fix or delete this first

`ABV_Abiverd_PoppyField_South_V1`
Package: `Content/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/1/X0/GJN2D5IJ1W5ZAKNBQQEJ1Z.uasset`
(written 21:56, the last file of the session)

It was **saved with wrong instance data** and must not be left as-is.

- Actor origin: `(1900, 5400, 34890)`
- Component: `HISM_Poppy_A`, mesh `SM_FieldPoppy_VarA`, 2,700 instances
- **Bug:** instance transforms were written in **world space**, but HISM
  `perInstanceSMData` is **actor-local**. Every instance is therefore offset by
  the actor origin. Measured bounds: `X[1850,5329] Y[5350,11729]
  Z[34840,69885]` — i.e. a column of poppies ~350 m in the air.
- The corrective rewrite (local coords) was issued but **failed/returned null**
  as Unreal ran out of memory. Assume the bad data is still on disk.

**On resume, do one of:**
1. Rewrite `perInstanceSMData` with local coords — subtract `(1900, 5400,
   34890)` from every world position; or
2. Delete the actor and rebuild (recipe in §6).

Nothing else from this session is suspect. Everything else was verified by
readback after writing.

---

## 3. Shutdown — DO NOT SAVE

**On closing Unreal, choose "Don't Save" / discard.**

- All 163 packages were already exact-saved during the session with
  `save_assets`, each verified `true` and each confirmed on disk by mtime.
  Nothing completed depends on a close-save.
- The **only** dirty in-memory state is the failed poppy-field rewrite, which
  returned null as memory ran out. Its state is unknown and possibly partial;
  saving would write that over a package whose broken condition is precisely
  documented in §2 and reproducible from §5.
- A close-save is effectively Save All, which the project rules prohibit for
  automated work.

Discarding leaves disk in a known, documented state.

## 4. Restart procedure

1. Relaunch the editor **detached** (Claude can do this itself):

```sh
nohup "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" \
  /Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject \
  -ModelContextProtocolStartServer > /tmp/ue_map_launch_$(date +%s).log 2>&1 & disown
```

2. If a **"Restore Packages"** autosave prompt appears → **Skip Restore**
   (documented rule; keeps the verified saved work).
3. The editor opens on the startup map `/Game/ThirdPerson/Lvl_ThirdPerson`.
   Claude can switch it with
   `SceneTools.load_level("/Game/Maps/Blockout/Lvl_Blockout_01")`.
4. **The SS_010 region loaded automatically last time** — no manual World
   Partition load was needed. Verify with a `find_actors` on an exact label
   before assuming.

---

## 5. How to reach Unreal — the important discovery

**`/mcp` reconnection is NOT required.** The bridge is reachable directly over
HTTP JSON-RPC from Bash. This is how all of this session's work was done.

- Endpoint `http://127.0.0.1:8000/mcp`
- `initialize` returns an **`Mcp-Session-Id`** header; every later call must
  send it back. Missing it → `-32600`.
- Then `tools/call` the three meta-tools (`list_toolsets`, `describe_toolset`,
  `call_tool`); 68 toolsets are exposed.

Helper scripts written this session (recreate if `/tmp` was cleared):
`/tmp/mcp.py` (session + JSON-RPC), `/tmp/ue.py` (`tool(toolset, name, args)`),
`/tmp/audit.py` (find/label/xform/bounds/props/comps helpers),
`/tmp/field.py` (foliage builder).

### Hard-won API rules — these cost real time, do not rediscover them

| Rule | Detail |
|---|---|
| **`set_properties` `values` is a STRING** | JSON-encoded string, not an object. Passing an object silently returns `false`. This one mistake made me wrongly declare the tool broken. |
| **Property names are camelCase** | `overrideMaterials`, not `OverrideMaterials`. Use `list_properties` — they cannot be guessed. |
| **Saving = `AssetTools.save_assets` with the ACTOR's refPath** | Not the package path. `SceneTools.save_actor` always fails with "Asset does not exist" on World Partition external actors, new or existing. |
| **`CollisionEnabled` cannot be set** | `set_properties` returns `true` and silently ignores it, on both nested and full-struct writes. Needs `SetCollisionEnabled()` via Python. **Only remaining capability gap.** |
| **HISM `perInstanceSMData`** | Readable/writable. **Growing** the array works; **shrinking** silently fails (returns null, count unchanged). To "delete" an instance, collapse it to ~1e-5 scale. |
| **HISM instances are ACTOR-LOCAL** | Subtract the actor origin. This is what broke the poppy field. |
| **Pivots vary — always verify** | `/Engine/BasicShapes/Cube` spawned via `add_to_scene_from_asset` = **centre** pivot. `SS_014_Fence_*` meshes = **min-corner** pivot. `WindowTrim` HISM cube = centre pivot. Read bounds back after every write. |
| **`find_assets`** | Params are `folder_path` + `name` (not `path`). |
| **`CaptureViewport`** | Requires `annotations: []` or it errors. Returns base64 → decode to PNG and Read it. Call it **twice** and keep the second (warm-up frame). |
| **`SlateInspector.Snapshot`** | Cannot traverse the docked editor UI — returns only 3 image widgets. Do not rely on it. Also, a full-depth snapshot **hangs**; it was the last heavy call before the OOM. |
| **Avoid** | Broad `find_actors` with no name/bounds filter; full-depth Slate snapshots. Both are memory-expensive. |

---

## 6. Poppy field — the current task (Jason's brief)

Jason supplied five Turkmenistan reference photos and this brief:

> "The areas surrounding the building where you should have references to these
> fields should look like this… It needs **major ground coverage** and it should
> be **very tall** which will help players use **low cover** when moving around
> open areas."

Fab source he owns: https://www.fab.com/listings/66cb2706-bc30-4f26-92ec-cad48723bd4a

### Assets confirmed present (8 + 8 variants, more than the old handoff claims)

`/Game/Maps/Sunscar/Art/Heritage/Foliage/FieldPoppy/SM_FieldPoppy_VarA…VarH`
`/Game/Maps/Sunscar/Art/Heritage/Foliage/WildGrass/SM_WildGrass_VarA…VarH`
plus `MI_FieldPoppy`, `MI_WildGrass` and their BaseColor/Mask/Normal textures.

### Measured native heights

- Poppies: **49–70 cm** (VarA 64.4, VarC 69.1, VarF 49)
- Grass: **VarA is the only tall one at ~35 cm**; VarB–VarH are 10–19 cm

### Target for Jason's brief

- Poppies scaled **1.15–1.45** → 74–93 cm (crouch concealment)
- Grass VarA scaled **1.5–2.0** → 52–70 cm understory
- Density for the reference read: ~10–12 poppies/m², ~20–25 grass/m²
- Layered: green understory below, red poppy heads above

### Pilot patch that was in progress

Area `X 400→3400, Y 4500→6300` (30 m × 18 m), open ground south of the
detention yard. Ground sampled on a 4×3 grid, bilinearly interpolated:

```
(400,4500) 34767.8   (1400,4500) 34883.6   (2400,4500) 34891.0   (3400,4500) 34885.3
(400,5400) 34903.4   (1400,5400) 34900.4   (2400,5400) 34897.0   (3400,5400) 34892.9
(400,6300) 34904.9   (1400,6300) 34903.1   (2400,6300) 34901.4   (3400,6300) 34899.2
```

Saved at `/tmp/field_grid.json` (recreate if cleared).

### Still unverified for foliage

- Whether `MI_FieldPoppy` / `MI_WildGrass` have **Used with Instanced Static
  Meshes = true**. If false the foliage renders dark/wrong — the documented
  trap. The pilot never rendered, so this was never confirmed either way.
- Whether the meshes are collisionless (the old handoff says yes for the two it
  tested). Art-plan rule 7: foliage may conceal but must never become unplanned
  hard cover.
- **Memory cost.** The OOM happened while working on ~2,700 instances plus a
  heavy Slate snapshot. Scale foliage up in stages and watch memory.

---

## 7. Completed and saved this session (163 packages)

| Fix | Actors |
|---|---|
| SS_010 fitted plinths (S_Left, S_Right, E_Left partial) | 3 new |
| Obsolete parapets neutralised — shadows/nav/overlaps off + tagged `SunscarOldTownObsoleteArchitectureHiddenV1` | 28 (7 sites) |
| Buttresses lowered to grade, 5 cm embed | 6 |
| SS_014 fence re-centred + grounded (enclosure now closes) | 4 |
| SS_010 F2 shell: `MI_OT_Detention` → `MI_OT_FlakedPaint_WorldAligned` | 6 |
| **StoreyBand** actors closing the 20 cm inter-storey seam | 28 new |
| **CorniceBand** actors closing the 20 cm roofline seam (all 12 buildings) | 48 new |
| Cyan signboards `MI_OT_Accent` → `MI_OT_Timber` | 8 |
| `QX_PlasterDamage_*` pasted strips hidden (rejected treatment) | 6 |
| SS_010 door dressing moved onto the real opening; 2 blank-wall doors hidden | 3 + 6 HISM instances |
| SS_012 windows + trim lowered 75 cm; glass centred in frames | 20 + 16 instances + 8 |

### Systematic bugs found this session (not in the original register)

- **Bug E — 20 cm seam.** Every multi-storey junction *and* every roofline has an
  exact 20 cm gap; the floor slab sits above it and is inset, so it never closes
  the exterior. All 12 buildings. **Fixed.**
- **Bug F — windows ~30 cm too high.** Heads and lintels punch through the wall
  top into the band/cornice — this is what looked like "lintels floating on the
  roof band". **Fixed at SS_012 only; SS_010 confirmed affected; other sites not
  yet done.**

---

## 8. Outstanding queue

**Blocked on the Python route (one capability):**
- `NoCollision` on the 28 neutralised obsolete parapets. Ready-to-run script at
  `/private/tmp/abv_parapet_nocollision_v1.py` (syntax-checked, triple-gated,
  SS_003 deliberately excluded). Run from the Output Log in **Python** mode:
  `exec(open(r"/private/tmp/abv_parapet_nocollision_v1.py").read())`
  Worth extending it with HISM `remove_instance` for the 6 collapsed door
  surrounds.

**Unblocked:**
1. Poppy field (§5) — Jason's current priority.
2. Roll Bug F (window height) out to the remaining sites.
3. SS_012 crooked door awnings.
4. SS_017 bazaar awnings → align to existing `ABV_SS_017_BazaarCanopyPost_A–D_V1`.
5. SS_010 F2 west doorway — open black void with a light leak; needs a door or
   closed reveal.
6. SS_011 checkpoint ramp/landing, after route verification.

**Open decisions for Jason:**
- **Git checkpoint.** Still none. He reserved it for the exact phrase
  *"Approve local checkpoint commit"*.
- **SS_014 Salvage Yard** is outside the 13-site phase-one scope but its fence
  was fixed (egregious and visible). Confirm that was wanted.
- **Muted green plaster** for SS_010 is **not reachable** — all three facade
  materials share one master with no tint parameter, and no green base-colour
  texture exists. Needs a texture authored, then it is a one-line swap on the
  same six overrides.

---

## 9. Backups written

- `/private/tmp/abv_doorsurround_brick_backup.json` — original 24 door-surround
  instances before 6 were collapsed.
- `/private/tmp/abv_parapet_nocollision_v1.py` — the pending collision script.
- `/tmp/field_grid.json` — ground samples for the poppy patch.

`/private/tmp` survives reboots less reliably than the repo; copy anything still
needed into `Documentation/` if it matters.

---

## 10. Artifacts now copied into the repo (2026-08-19 22:14)

The three `/private/tmp` files are no longer only in tmp. Copies live at:

`Documentation/Maps/OperationSunscar/Planning/Abiverd_SessionArtifacts_2026-08-19/`
- `abv_doorsurround_brick_backup.json` — original 24 door-surround instances,
  before 6 were collapsed. Restore source if the collapse needs undoing.
- `abv_parapet_nocollision_v1.py` — the pending NoCollision script (syntax
  checked, triple-gated, SS_003 deliberately excluded). Run from the Output Log
  in **Python** mode:
  `exec(open(r"Documentation/Maps/OperationSunscar/Planning/Abiverd_SessionArtifacts_2026-08-19/abv_parapet_nocollision_v1.py").read())`
  (use an absolute path; the tmp copy still works too while it survives)
- `field_grid.json` — ground-height samples for the poppy patch.

These are untracked like the rest of the session's work — see §11.

---

## 11. Carry-forward — three open items

1. **No recovery commit exists.** 163 packages of work are unstaged, plus these
   docs and artifacts. Jason reserved the trigger phrase — take one local
   commit, nothing else, only when he says exactly:
   **"Approve local checkpoint commit"**. Do not push. Do not commit otherwise.

2. **One capability gap: `CollisionEnabled`.** Not reachable over the bridge.
   Script is ready (§10). Worth having Codex run it and extend it with HISM
   `remove_instance` for the 6 collapsed door surrounds.

3. **Poppy field is the first job on resume**, after fixing or deleting the one
   broken actor in §2 (`ABV_Abiverd_PoppyField_South_V1` — 2,700 poppies saved
   with world-space instance coords instead of actor-local, sitting ~350 m in
   the air).

---

## 12. Verbatim prompt for the fresh chat

Paste this into the new session:

> Continuing Abiverd map work on the TacticalMovement UE5.8 map worktree at
> `/Users/jasonteck/UnrealEngine/_worktrees/map-development`.
>
> Read `Documentation/Maps/OperationSunscar/Planning/ABIVERD_RESUME_HANDOFF_2026-08-19.md`
> first — it has the exact state, the restart procedure, and the API rules from
> the last session. Then read `ABIVERD_SS010_SESSION_LOG_2026-08-19.md` for
> detail.
>
> Unreal and the terminal were restarted after running out of memory. Launch the
> editor yourself (detached, command is in §4), open
> `/Game/Maps/Blockout/Lvl_Blockout_01`, and reach Unreal over the HTTP JSON-RPC
> bridge on `127.0.0.1:8000` — `/mcp` is not needed, see §5.
>
> First job: fix or delete the one broken actor in §2 —
> `ABV_Abiverd_PoppyField_South_V1` was saved with world-space instance coords
> instead of actor-local, so 2,700 poppies sit ~350 m in the air.
>
> Then: build the poppy field per §6 — dense, tall enough for crouch
> concealment, matching the Turkmenistan references. Verify the foliage
> materials have **Used with Instanced Static Meshes = true** before scaling up,
> and watch memory.
>
> Working rules: verify every write by reading geometry back, capture
> before/after from player height, exact-save only intended packages, no commits
> without my explicit approval.

---

## 13. Shutdown checklist (do these in order)

1. Close Unreal → **Don't Save / discard**. Everything intended is already on
   disk (163 packages, all verified, all carrying today's mtime). The only dirty
   state is the failed poppy rewrite, whose in-memory state is unknown. See §3.
2. Close the terminal.
3. Clear the chat.
4. Resume with the prompt in §12.

---

## 14. ROOT CAUSE OF THE OOMs — found 2026-08-20

**`set_properties` on `perInstanceSMData` with a large array is the memory bomb.**
Not the level, not World Partition, not Slate snapshots.

Measured on 2026-08-20, 16 GB machine, one editor session:

| Step | Swap used | Compressed |
|---|---|---|
| After launch | 0.6 GB | 0.19 GB |
| After loading the **entire** Blockout WP level | 0.6 GB | 0.75 GB |
| **After ONE `set_properties` of 2,700 `perInstanceSMData` entries** | **26.0 GB** | **7.89 GB** |

The editor was then OOM-killed by the OS. Loading the whole map costs
essentially nothing; one bulk instance write costs ~25 GB.

This has now killed three sessions (2026-08-19 twice, 2026-08-20 once), every
time on this same call. Yesterday's note blaming the Slate snapshot was wrong —
the snapshot was a bystander.

**Suspected mechanism (inferred, not proven):** the setter opens an editor
transaction and the undo system snapshots the array; if that happens per element
rather than once, 2,700 matrices become an enormous transaction buffer. Fits the
shape (huge, sudden, on write but never on read). Not worth another 25 GB to
confirm.

### Consequence — supersedes the §5 guidance for bulk work

**Do NOT place foliage (or any bulk instance data) over the MCP bridge.**
Use in-editor Python instead: `add_instances(transforms)` batches natively,
writes straight into the component, and does not marshal a giant JSON payload or
build a per-element transaction. This is also why Codex never hit the OOM — the
collision script route runs as in-editor Python from the Output Log.

The brief needs far more than 2,700 anyway (10–12 poppies/m² + 20–25 grass/m²
over the field = tens of thousands of instances). `set_properties` was never
going to carry that.

**Keep using the bridge for what it is good at:** `find_actors`, reading
properties, verifying geometry by readback, and `AssetTools.save_assets`.

### Launch flags that DID help (keep them)

```
-nosplash
'-ini:Engine:[DevOptions.Shaders]:NumUnusedShaderCompilingThreads=0'
'-ExecCmds=r.Streaming.PoolSize 512, r.Streaming.LimitPoolSizeToVRAM 1, r.Shadow.DistanceScale 0.5'
```
(quote the bracketed arg — zsh globs it otherwise)
Level load under these settings: UE RSS ~3.1 GB, swap flat.

### Still-true state after all three crashes

Disk never changed. Poppy package still the `Aug 19 21:56` bad version, HEAD
still `e0b856c`, 961 modified / 165 untracked, no commits. The §2 defect is
exactly as documented and the local-space fix data is precomputed at
`/tmp/poppy_fixed_instances.json` (copy in the SessionArtifacts folder).

---

## 15. RESOLVED 2026-08-20 — poppy field built with PCG

Both the §2 defect and the §6 task are done. The approach changed: **PCG, not
hand-placed HISM.**

### What exists now

| Item | Path |
|---|---|
| PCG graph | `/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1` |
| PCG volume actor | `ABV_PCG_PoppyField_South_V1` in `Lvl_Blockout_01` |
| Volume package | `Content/__ExternalActors__/.../8/44/IF6AJ9QMLCI1NAJDG8H8OS.uasset` (2.3 MB) |

Graph shape (7 nodes, 6 edges):
```
Get Landscape Data ─┬─> Surface Sampler 11/m2 -> Transform Points -> Static Mesh Spawner (8 poppy vars)
                    └─> Surface Sampler 22/m2 -> Transform Points -> Static Mesh Spawner (5 grass vars)
```

Volume transform: loc `(1900, 5400, 34890)`, scale `(15, 9, 10)` → bounds exactly
`X 400..3400, Y 4500..6300` (the §6 footprint).
**Note:** `SpawnGraphInstance` ignores the `transform.scale3D` argument — it
spawns at scale 1. Set scale afterwards with `ActorTools.set_actor_transform`.

### Result — measured, meets the brief

| | Generated | Density | §6 target |
|---|---|---|---|
| Poppies | 5,841 | 10.8/m² | 10–12 ✓ |
| Grass | 11,844 | 21.9/m² | 20–25 ✓ |
| **Total** | **17,685** | | |

Scales: poppies 1.15–1.45, grass 1.5–2.0, random yaw + ±4–6° lean.
Weights favour tall variants (poppy VarF down-weighted; grass VarA at 60%).
Verified at crouch height: canopy sits on the sightline — low cover works.

**Collision: `NoCollision` on every spawned ISM**, confirmed by readback.
Art-plan rule 7 satisfied, and this sidesteps the §5 `CollisionEnabled`
capability gap entirely for foliage.

**Memory: flat throughout.** UE 2.1–3.5 GB, swap 0.7 GB, generation took 1.7 s
for 17,685 instances — 6.5× the count that OOM'd via `set_properties`.

### Broken pilot actor — retired

`ABV_Abiverd_PoppyField_South_V1` removed from the level; its untracked package
moved to the session scratchpad as `RETIRED_pilot_poppyfield_*.uasset`. The
repaired local-space data is preserved at
`Abiverd_SessionArtifacts_2026-08-19/poppy_fixed_instances.json` if it is ever
wanted. **§2 is closed.**

### Open art note — hard rectangular edge

The field is a crisp rectangle on bare sand; real fields feather out. Fix is
parameters, not a rebuild:
- add **Spatial Noise** into the sampler density for patchiness;
- add a **density falloff** at the volume edge, or use a spline/polygon bounding
  shape instead of the box volume;
- the brief says "areas *surrounding* the building" — this is one 30×18 m patch,
  so more volumes (or one larger noise-driven one) are still wanted.

### Scripts (all in `Abiverd_SessionArtifacts_2026-08-19/`)

`pcg_build.py` (nodes), `pcg_wire.py` (edges), `pcg_meshes.py` (weighted mesh
lists, resolves selector subobject paths from the graph), `capture.py`
(viewport PNGs), `mem.sh` (memory watchdog).
Captures: `poppyfield_01_across_field_eye.png`, `_02_crouch_height.png`,
`_03_oblique_overview.png`.

### API rules learned today (add to §5)

| Rule | Detail |
|---|---|
| **PCG tool params are all REQUIRED** | `AddNode` needs `jsonParams`, `nodeTitle`, `nodeComment` even when "optional"; `SpawnGraphInstance` needs `jsonParams`. Omitting → schema error. |
| **`save_assets` takes `asset_paths`** | An array of **strings**, not `{assets:[{refPath}]}`. Actor refPath works as a string. |
| **Saving a WP level does not save its actors** | `save_assets` on the `.umap` returns `true` and writes nothing. Save the **actor** refPath to write its `__ExternalActors__` package. |
| **Deleting a WP actor leaves its package** | `remove_from_scene` returns `true` but the `__ExternalActors__` `.uasset` stays on disk; remove the file to complete the delete. |
| **Mesh selector lives in a subobject** | `<node>.PCGStaticMeshSpawnerSettings_N.DefaultSelectorInstance`, and **N differs per node**. Read the real path from `GetGraphStructure` — do not hardcode. |
| **`CaptureViewport` returns** | `returnValue.image.data` (base64) + `image.mimeType`. |
| **`ProgrammaticToolset` has no `unreal` module** | Only `re/json/copy/math/datetime/time` + `execute_tool`. Cannot do bulk instance work. |

---

## 16. Edge treatment + density variation — 2026-08-20 (second pass)

Addresses the §15 "hard rectangular edge" note. **Partly solved.**

### Final state — four PCG volumes, one shared graph

| Volume | Poppies | Grass | Total |
|---|---|---|---|
| `ABV_PCG_PoppyField_South_V1` (main) | 5,914 | 11,867 | 17,781 |
| `..._LobeS_V1` (yaw +22°) | 717 | 1,200 | 1,917 |
| `..._LobeSW_V1` (yaw −28°) | 537 | 900 | 1,437 |
| `..._LobeW_V1` (yaw +15°) | 578 | 960 | 1,538 |
| **Total** | **7,746** | **14,927** | **22,673** |

Main field density unchanged at **11.0 poppies/m², 22.0 grass/m²** — still on brief.
Memory stayed flat (UE 1.2–1.7 GB, swap 0.7 GB) throughout.

The three rotated lobes straddle the main volume's south and west edges, so the
boundary now reads as an irregular organic outline instead of a rectangle.
Verified in `poppyfield_v3_03_oblique_overview.png`.

### What did NOT work — Spatial Noise does not give spatial patches

Graph now has `Spatial Noise -> Filter Attribute Elements by Range` on both
branches (samplers raised to 18/m² and 30/m², filter culls back to target).
**But the noise is effectively per-point random, not spatial.** Measured:

- Output never spans 0–1. Perlin2D/FractionalBrownian2D sit compressed in a
  narrow band (~0.46–0.70); Voronoi2D returns raw distances in the hundreds.
- **Larger `transform.scale` = MORE spread**, the opposite of the usual
  frequency convention. At scale 0.0025 the whole field collapses to a single
  constant value (0.664 across all 9,856 points → filter culls 0%).
- At scale 1.0 (the only useful setting) the first 300 *adjacent* points show
  the same spread as the whole field ⇒ neighbours uncorrelated ⇒ random
  thinning, not blobs.

So the noise pass maintains density but does **not** change the silhouette;
compare `poppyfield_v2_*` (thinning only, still rectangular) against
`poppyfield_v3_*` (lobes added, irregular). The lobes did the work.

Thresholds are **calibrated to the measured distribution**, not guessed —
`pcg_calibrate.py` samples the real density values and picks the percentile that
hits the target cull (poppy 0.6241 for 40%, grass 0.1707 for 27%). Re-run it if
the noise settings change; hardcoded thresholds will silently cull 0% or 100%.

### Still open

- **NE edge** still runs straight along the compound wall. Arguably fine (a wall
  is a real boundary) — art call.
- **Coverage.** The brief says "areas *surrounding* the building". Still one
  field plus three lobes on its south/west. More volumes elsewhere are wanted.
- `LobeSE` was attempted at (3180, 4820) and generated **0 instances** — its
  bounds reach X 3500, past the landscape edge. Removed. Keep satellite volumes
  inside the landscape footprint.
- For true patchiness, Spatial Noise is a dead end as configured. Options: a
  texture mask via `Sample Texture`, `Get Landscape Data` layer weights, or
  simply more hand-placed overlapping volumes.

### More API rules (add to §5)

| Rule | Detail |
|---|---|
| **`ExecuteGraphInstance` does not invalidate its cache** | Editing the graph then re-executing returns identical results. To force a real rebuild, delete and respawn the volume (`pcg_respawn.py`), or enable inspection via `GetNodeDataView` first. |
| **PCG renames ISM components on regeneration** | `ISM_SM_FieldPoppy_VarA_0` became `..._1`. **Never hardcode the `_0` suffix** — enumerate `get_components` and match the `ISM_` prefix, or you will read 0 and think generation failed. |
| **`GetGraphStructure` misreports selector params** | It showed `valueTarget: None` while the settings object held `"$Density"`. Trust `ObjectTools.get_properties` on `<node>.settingsInterface`, not the structure dump. |
| **`AddNode`/`UpdateNode` `jsonParams` ignores nested struct scale** | `transform.scale3D` passed to `AddNode` silently stayed `(1,1,1)`. Set nested transforms afterwards via `set_properties` on the settings object, using key `scale` (not `scale3D`). |
| **`GetNodeDataView` needs two passes** | The first call only enables inspection and returns "produced no data"; re-execute the graph, then read. |
| **Removing a PCG volume orphans its package** | Same as any WP actor — delete the `__ExternalActors__` file too. |

---

## 17. STOP POINT 2026-08-20 — planning pass, and a major correction

Work stopped mid-**planning**, not mid-build. Nothing is half-written to the level.
Read this section plus §18 before touching anything.

### 17.1 THE AUTHORITATIVE DESIGN DOCS — read these FIRST, always

Jason has two master planning images in iCloud. **They were not discovered until
late on 2026-08-20 and they supersede a great deal of guesswork:**

```
~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS Game/
    Operation_Sunscar map UE FPS Game/
        Operation_Sunscar_Master_Map.jpg      <- whole 3.2 km2 battlefield
        Operation_Sunscar_Old_Town_Core.jpg   <- the 320 x 250 m phase-1 core
```

Read them with the Read tool (they are images). Do not plan without them.

### 17.2 The boundary — settled

| Layer | Size |
|---|---|
| Terrain envelope | 2,520 x 2,520 m |
| Playable battlefield | 2,000 x 1,600 m (3.2 km2) |
| Inner service town | 640 x 500 m |
| **Old Town core = PHASE 1** | **320 x 250 m** |

"The legacy-style core stays intact; expansion happens around it."

**Phase 1 = Old Town core = 13 sites**, authoritative list from
`ABIVERD_OLD_TOWN_PAUSE_HANDOFF_2026-08-05.md` (2026-08-14 entry):
`SS_003 SS_004 SS_005 SS_006 SS_007 SS_010 SS_011 SS_012 SS_013 SS_015 SS_016
SS_017 SS_018`.

Measured envelope of those 13: **X -11,575..14,624, Y -10,652..11,910 cm
= 262 x 226 m**, which sits inside the authored 320 x 250 m core. Consistent.

Outer districts (NOT phase 1): North Karakum Expanse, West Abiverd March,
East Canal Belt, South Kopet Foothills, SE Industrial Works, NW/NE/SW approaches.

### 17.3 CORRECTIONS to earlier analysis in this file — do not reuse the old numbers

- An earlier pass used **11 sites**, missing **SS_006 (Water Tower Compound)** and
  **SS_013 (Freight Depot)**. Every figure derived from it is void.
- The claim of a **"0.85 ha empty core"** was **WRONG**. `SS_008 Central Courtyard`
  (115 actors), `SS_009 Transit Plaza` and `SS_014 Salvage Yard` sit inside the
  envelope; they are simply outside the 13-site *completion* scope. The middle is
  the Central Courtyard (~86 x 42 m) and it is an objective.
- The proposed **18 m tell in the core is wrong** for this design. The core's tall
  landmark is the **water tower at 12-18 m**, and there is a defined objective
  triangle. Abiverd-style ruins belong in the **West Abiverd March** per the
  master map.
- **Live water in the core is wrong.** Core feature 12 is **DRY CANAL / CULVERTS**
  - "a low, exposed bypass with culverts, not a safe tunnel". Wet, engineered
  canal is the **East Canal Belt, outside phase 1**.

### 17.4 Authored specs that the built map currently violates

From `Operation_Sunscar_Old_Town_Core.jpg` (BLOCKOUT METRICS):
primary street 12-15 m | service lanes 5-8 m | combat alleys 2.5-4 m |
vehicle gates 6-8 m | central courtyard ~86 x 42 m |
**hard-cover rhythm every 8-12 m** | **longest intentional sightline 110-140 m**

Verticality tiers: ground | balconies/roofs 3-5 m | hotel & detention roofs
7-9 m | water tower/mast 12-18 m | limit continuous rooftop chains.
Routes: ALPHA (north compounds+hotel) / BRAVO (central road+courtyard) /
CHARLIE (bazaar, yards, dry canal) + cross-links + managed sightlines.
Objective triangle: Detention Annex, Central Courtyard, Water Tower.

| # | Violation | Measured |
|---|---|---|
| 1 | **Authored elevation was never built.** Plan: core 328-365 m, south rim to 430 m, Signal Ridge 428 m, quarry floor 365 m. | Core has **1.85 m** of variation around 348 m (168-point grid). Service town is at correct height; the relief around it does not exist. |
| 2 | Sightlines exceed the 110-140 m spec | crossings of **155-208 m** |
| 3 | Hard cover every 8-12 m | effectively **none** between sites |
| 4 | "Low-density poppies within Old Town; strongest red-field identity belongs outside the dense street core"; heritage plan wants **4-6 irregular belts 12-25 m x 5-10 m** | built a uniform **30 x 18 m rectangle at 11/m2 inside the core** |

### 17.5 TECHNICAL DEBT INTRODUCED — must fix before any build

`ABIVERD_HERITAGE_EXPANSION_PLAN_V1.md` states: *"Use ordinary PCG only as an
editor-time authoring tool, save the generated instances, and avoid runtime PCG
generation for this competitive multiplayer map"* and *"Save generated
static-mesh instances; do not regenerate the meadow at runtime."*

**The four PCG volumes built on 2026-08-20 are live PCG components.** It has NOT
been verified whether they regenerate at runtime. They likely must be baked to
static instances or converted to Static Mesh Foliage. Also unverified against the
same plan: navigation influence, ticking, replication disabled; cull distances
(`instanceStartCullDistance`/`EndCullDistance` were never set); non-Nanite plant
meshes. Collision **is** verified `NoCollision`; materials **are** verified
`BLEND_Masked`.

### 17.6 Systems audit — what exists in the level (2026-08-20)

| System | State |
|---|---|
| Spawns | PlayerStart 8, Spawn 31, Insertion 2, Extraction 3 |
| Objectives | 19 actors |
| Lighting | DirectionalLight, SkyLight, SkyAtmosphere, ExponentialHeightFog (1 each) |
| Post process | 1 volume |
| VFX | Dust 80, Wind 25, Weather 12 |
| Traversal | Ladder 1, Ramp 10 |
| Barriers | 29 |
| **Navigation** | **NONE — no NavMesh bounds/modifiers/links found** |
| **Audio** | **NONE — no ambient sound, audio or reverb volumes** |
| Reflection captures | none found |

### 17.7 Plugins — enable these

Not enabled but wanted (895 discovered, 280 enabled):
- **`LandscapePatch`** — non-destructive landscape height edits via *patch actors*.
  Actor-based, therefore drivable over the MCP bridge, and removable if a patch
  breaks a building's grounding. This is the answer to "what landscape toolset".
- `PCGWaterInterop`, `PCGGeometryScriptInterop`, `WaterAdvanced`, `WaterExtras`.
Already enabled: `Water`, `GeometryScripting`, `PCGToolset`, `MeshModelingToolset`.

### 17.8 Asset gaps (full list in chat 2026-08-20)

Missing Epic packs named in Jason's own master-map palette: **Urban Prison**
(objective A art), **African Slate Quarry** (objective B art), **Abandoned
Factory** (SE Industrial Works), **Megaplants Greasewood**. `Old Mine` only
partial (6 files).
Caveat: Megaplants need Procedural Vegetation Editor + Nanite Foliage
(Experimental), which conflicts with the heritage plan's non-Nanite rule.
Greasewood: https://www.fab.com/listings/1b8d0a76-276f-406e-9536-330243bb42cf

Also missing entirely: culverts, footbridge, vehicle slab bridge, sluice gate,
canal channel modules, tyre-rut decals, takir/cracked-clay ground material,
adobe/pakhsa modular walls, poplar, tamarisk, reeds, and dry/dead grass (without
which seasons are impossible).

### 17.9 Design principle agreed with Jason

> **Permanent geometry carries the gameplay. Vegetation is a modifier on top.**

Tune the map to play correctly in its barest winter state; poppies and grass then
*add* concealment without anything collapsing when they go. This matches the
heritage plan's existing rule that vegetation is "not treated as authoritative
gameplay cover" and that "no route may depend on flowers or grass for protection
from a standing sniper".

Seasons: spring (Mar-May) canals full, poppies red, muddy tracks; summer
(Jun-Sep) 40C+, dry/low channels, dead stalks, dust; winter (Dec-Feb) 0-10C,
bare fields, still water. Poppy bloom is a few weeks only — the current red field
pins the map to April-May.

## 18. NEXT ACTIONS (in order)

1. **Ask Jason for any further planning material** before designing anything else.
2. Enable `LandscapePatch` (+ the PCG interop plugins); restart editor; verify the
   patch actor classes are reachable over the bridge.
3. **Resolve the PCG runtime question in §17.5** — bake to static instances if
   they regenerate at runtime. This is a correctness issue, not cosmetic.
4. Rework the poppy field to spec: low density inside Old Town, 4-6 irregular
   belts 12-25 m x 5-10 m, strongest red identity *outside* the core.
5. Terrain pass: build the authored elevation (core 328-365 m) via LandscapePatch,
   with a **no-sculpt buffer around each of the 13 sites** (bounds + 5-10 m) so the
   committed grounding work (plinths, buttresses, foundation skirts) is not broken.
6. Roads/canal per the core plan's own metrics; dry canal + culverts in core.
7. Cover pass against the 8-12 m rhythm and 110-140 m sightline spec.
8. Navigation and audio: both entirely absent.

**Working rules unchanged:** verify every write by readback; exact-save only
intended packages; no Save All; no commits without Jason's explicit approval.

---

## 19. RESUME PROMPT — paste this into the fresh chat

> Continuing Abiverd / Operation Sunscar map work in the UE5.8 worktree at
> `/Users/jasonteck/UnrealEngine/_worktrees/map-development` (branch
> `feature/map-development`, HEAD `edb4dc9`, working tree clean, nothing pushed).
>
> **Read these first, in this order, before proposing anything:**
> 1. My two master planning images — use the Read tool, they are images:
>    `~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS Game/Operation_Sunscar map UE FPS Game/Operation_Sunscar_Master_Map.jpg`
>    and `Operation_Sunscar_Old_Town_Core.jpg`
> 2. `Documentation/Maps/OperationSunscar/Planning/ABIVERD_RESUME_HANDOFF_2026-08-19.md`
>    — go to **§17, §18 and §19**. Sections 1-16 are older and partly superseded;
>    §17.3 lists numbers that are now void, do not reuse them.
> 3. `ABIVERD_HERITAGE_EXPANSION_PLAN_V1.md` — the foliage/ruins rules and the
>    seven validation gates.
>
> We stopped during **planning**, not building. Nothing is half-written to the
> level. UE is closed and everything is saved.
>
> Ask me for any further planning material before designing anything — last
> session a lot of work was wasted re-deriving decisions I had already made in
> those two images.
>
> Working rules: verify every write by reading geometry back; exact-save only
> the packages you intended; never Save All; no commits without my explicit
> approval.

### 19.1 Open questions Jason still owes an answer on

1. Any further planning material beyond the two master images?
2. The tell — wanted at all, and if so in the **West Abiverd March**, not the core?
3. Which asset gaps to pursue (§17.8) so Fab purchases can be made.
4. Whether to enable `LandscapePatch` + PCG interop plugins (§17.7).

### 19.2 Highest-value next actions, cheapest first

Ranked at the end of 2026-08-20 as better value than the terrain pass, because
they are cheap now and get more expensive once the map is dressed:

1. **Audio and navigation** — both entirely absent from the level (§17.6).
   Audio is gameplay in a tactical shooter, not polish.
2. **Roof access** — the core plan specifies three verticality tiers but the
   level has **1 ladder and 10 ramps**, so a whole designed tier is unreachable.
3. **Player-metrics validation** (heritage gate 2) — place the TacticalMovement
   character beside cover, capture standing/crouched/prone. Cheap, and it
   retroactively validates or invalidates every cover decision made so far,
   including the poppy scaling.
4. **Streaming + cull distance setup** — 3.2 km2 with uncapped foliage will not
   hold frame rate. The PCG foliage currently has **no cull distances set**.
5. Then the bigger passes: PCG runtime bake (§17.5), poppy rework to belts,
   terrain elevation via LandscapePatch, roads/canal, cover rhythm.

### 19.3 State at pause — 2026-08-20

| | |
|---|---|
| Branch | `feature/map-development` |
| HEAD | `edb4dc9` |
| Working tree | clean, 0 changes |
| Unpushed commits | 2 (`c090ff9`, `edb4dc9`) — local only, by design |
| Unreal | closed cleanly on SIGTERM, no save prompt, nothing dirty |
| Field in level | 4 PCG volumes, 22,673 instances (7,746 poppy / 14,927 grass) |

Helper scripts live in `/tmp` (`mcp.py`, `ue.py`, `audit.py`, `mem.sh`, the
`pcg_*.py` set) with copies in `Abiverd_SessionArtifacts_2026-08-19/`.
`/tmp` may not survive a reboot; the repo copies will.
