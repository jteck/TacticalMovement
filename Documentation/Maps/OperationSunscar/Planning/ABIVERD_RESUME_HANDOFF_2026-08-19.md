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
