# CLAUDE.md — TacticalMovement (UE 5.8)

Durable project context, auto-loaded every session. This file is a **self-contained handoff**: a fresh Claude Code session should be able to continue from it without prior chat history.

> **Golden rule: "Borrow the rails, keep our train."** Use Epic UE 5.8 systems / tools / sample patterns (and Infima FP animation assets) for scaffolding and plumbing; keep TacticalMovement's readiness/movement identity custom. **Before any new subsystem, run the Epic-First Gate** (docs `10`, Section 11) and log the decision in the Decision Log.
>
> **Do not merge or push anything without the user's explicit approval.** Commit and push are **separate** approval gates, per slice. Always verify live state with `git`/GitHub before acting — the status below is a point-in-time snapshot.

---

## HANDOFF — current state (2026-07-11)

> **Verify live git state before acting** (`git status`, `git log --oneline --decorate`). Hashes below were verified on 2026-07-11 but re-check.

### 1. Current repo state (verified 2026-07-11)
- **Active UE project:** `~/UnrealEngine/TacticalMovement_UE58` (UE 5.8; `.uproject` EngineAssociation = 5.8).
- **GitHub:** https://github.com/jteck/TacticalMovement (remote `origin`).
- **ACTIVE BRANCH:** `feature/fp3-tactical-fp-ads-blend` @ **`6910085d655a246df56abc2d0e07a5a52a4810fa`** ("Add Tactical FP ADS pose blend", FP-3).
  - **Pushed; local == `origin/feature/fp3-tactical-fp-ads-blend`** (upstream set).
- **`origin/main` = `acae9cb`** — unchanged this session (FP work never touched `main`).
- **FP commit chain (newest first):** `6910085` FP-3 → `2314dbf` FP-2 (`origin/feature/fp2-tactical-fp-idle-animbp`, pushed) → `df2367e` FP-1 → `deed772` FP-0 → `cebdf56` (Slice-2 handoff) → …
- **Local branches:** `main`, `checkpoint/pre-ue58-upgrade`, `feature/fp0-infima-viewmodel-assets`, `feature/fp1-first-person-viewmodel-component`, `feature/fp2-tactical-fp-idle-animbp`, `feature/fp3-tactical-fp-ads-blend` (current), `feature/weapon-posture-visualization`.
- **Working tree clean.** Readiness suite **12/12**.

### 2. First-person (Infima) slices — FP-0 … FP-3 COMPLETE
TacticalMovement is a **first-person (FPS)** game. The **Infima "Tactical FPS Animation Pack – Assault Rifle"** is used **only** as an authored FP arms/weapon animation source — **not Lyra, no MoCap, no GAS, no Gameplay Tags.**
- **FP-0 (`deed772`)** — copied the minimal Infima FP viewmodel asset closure (13 `.uasset`) into `/Game/InfimaGames/TacticalFPSAnimations/…`: 2 poses (`A_TFA_FP_AR_Idle_Pose_Standing`, `A_TFA_FP_AR_Aim_Pose`), skeleton `SKEL_TFA_Mannequin`, mesh `SKM_FP_Manny_Simple`, `M_Mannequin` + `MI_Manny_01/02` + 6 `T_Manny` textures. Excluded full-body preview meshes. No demo/TP/Lyra deps.
- **FP-1 (`df2367e`)** — added to `BP_ThirdPersonCharacter` (Blueprint-only): `FirstPersonCamera` (`UCameraComponent`, `bAutoActivate=FALSE` — NOT the gameplay view) on the capsule; `FirstPersonArms` (`USkeletalMeshComponent`) under it, mesh `SKM_FP_Manny_Simple`, `bOnlyOwnerSee=true`. `FollowCamera`/`CameraBoom` remain the active TP gameplay view.
- **FP-2 (`2314dbf`)** — created `/Game/FirstPerson/Animations/ABP_TacticalFP` (skeleton `SKEL_TFA_Mannequin`, AnimGraph = idle pose Sequence Player → Output). `FirstPersonArms.animClass = ABP_TacticalFP_C`.
- **FP-3 (`6910085`)** — MovementReady↔ADS pose blend on `ABP_TacticalFP`. Verified: **compile 0/0**; EventGraph logic confirmed via DSL read (`bIsADS = OwningCharacter.CombatReadinessState == ADS`, cast to the **C++ class** `TacticalMovementCharacter` — not `BP_ThirdPersonCharacter`; resilient owner reacquire; `bIsADS` set only when owner valid); AnimGraph `Blend Poses by Bool` (Active=`bIsADS`, True=Aim pose, False=Idle pose, **0.2s** both blend times); **deps clean** (no `BP_ThirdPersonCharacter`/demo/TP/Lyra); **12/12**; git scope = only `ABP_TacticalFP.uasset`; **user visual verification passed** (RMB-hold→aim, release→idle; key `4` latch, `1/2/3` exit; smooth 0.2s blend).

**Expected visual caveat (normal, not a bug):** from the TP view the FP arms look wrong (posed for a rifle, no FP weapon attached, TP body still visible). The FP arms only "make sense" through `FirstPersonCamera` with the TP body hidden + an FP weapon — all deferred.

### 3. FP-4 — PROPOSAL / PREFLIGHT ONLY (NOT implemented, NOT approved)
Scope: add `DefaultSlot` + `Aiming` **montage slot plumbing** to `ABP_TacticalFP` — **no montage created or played**, FP-3 behavior unchanged.
- **Provisional topology (two parallel empty Slot branches — NOT yet approved):**
  - `Idle Sequence Player → Slot 'DefaultSlot' → Blend Poses by Bool [False]`
  - `Aim Sequence Player  → Slot 'Aiming'      → Blend Poses by Bool [True]`
  - Existing `bIsADS` Boolean blend → Output Pose. Empty slots pass base poses through unchanged.
- **Not approved** because direct read-only inspection of the **Infima reference** (`ABP_TFA_FP_BaseCharacter` AnimGraph, Infima `SKEL_TFA_Mannequin` slot groups, `AM_TFA_FP_AR_Reload` slot tracks) is **incomplete**.
- **Pivotal open question:** whether the **`Aiming`** slot survived FP-0 on the TacticalMovement copy of `SKEL_TFA_Mannequin`, and its group. `DefaultSlot`/`DefaultGroup` is a UE default; `Aiming` is Infima-custom. If `Aiming` is missing, registering it would edit an FP-0 Infima asset (guardrail) → FP-4 must halt/re-scope.

### 4. NEXT ACTION tomorrow (resume here)
1. Reopen TacticalMovement (detached launch + MCP bridge; see Editor section).
2. Open the TacticalMovement copy of `SKEL_TFA_Mannequin` → **Window → Anim Slot Manager**.
3. **User provides an OS screenshot** showing every expanded group/slot pair (MCP/Slate could not see the docked panel — see lessons).
4. Discard any in-memory skeleton dirtiness and shut TacticalMovement down (SIGTERM discards; **do not save**).
5. Launch the **Infima evaluation project alone** with the MCP bridge (one editor at a time; TM must be down first — port 8000 conflict).
6. Inspect (read-only) `ABP_TFA_FP_BaseCharacter` AnimGraph, the Infima skeleton's slot groups, and `AM_TFA_FP_AR_Reload` (its `SlotAnimTracks` ARE MCP-readable).
7. Confirm or revise the FP-4 topology from direct observation; then **wait for explicit FP-4 implementation approval.**

### 5. Guardrails in force for FP work (unchanged)
- FP slices touch **only** the presentation layer. Do **not**: activate `FirstPersonCamera`, hide the TP body, attach an FP weapon, add ADS/montages/firing/recoil/ammo/inventory/pickup/drop, Gameplay Tags, or GAS — unless the approved slice says so.
- Do **not** edit imported FP-0 Infima assets, or the **Infima source project** (`~/UnrealEngine/Infima_TacticalFPS_Test/Infima_TacticalFPS/` — **read-only**).
- Do **not** change C++, Enhanced Input, movement DataTables, readiness logic (`ECombatReadinessState`), `ABP_TacticalRifle`, or `ABP_Unarmed`.
- Only `Content/FirstPerson/Animations/ABP_TacticalFP.uasset` should change when an approved FP slice is implemented.

### 6. Prior work still in the tree (durable lessons; not current focus)
- **Equipped-rifle baseline** (branch `feature/equipped-weapon-static-attach`, not merged): character holds `SM_Rifle` via `ABP_TacticalRifle` attached at the **`HandGrip_R`** socket. **Durable lesson:** a believable hold is an **animation pose**, not a static transform; `weapon_r`/`weapon_r_hold`/`weapon_r_muzzle` were rejected on this skeleton. **Alpha standard: a slice isn't complete if it looks broken to an external reviewer.**
- **Weapon-posture Slice 2** (branch `feature/weapon-posture-visualization`): **spine-bow / Modify Bone on `spine_03` REJECTED** ("looking at the floor"). **LOCKED RULE:** posture keeps the soldier upright; the **weapon/arms/hands/shoulders** carry the posture — the torso must NOT bow. (This branch's `ABP_TacticalRifle` `PosturePitch` work is committed on that branch; it is **not** part of the FP track and is not current WIP.)

---

## Standing guardrails (do not violate without explicit approval)
- Do **not** migrate to Lyra (reference only). Do **not** introduce **GAS** without explicit approval.
- Do **not** replace `ECombatReadinessState` or the DataTable movement-profile system (`DT_MovementProfiles`); do **not** change movement values without approval.
- Do **not** start weapon firing, inventory, pickup/drop, mantle, AI, GAS, or (for FP) camera activation / body hiding / FP weapon until approved **as a slice**.
- **Do** use Epic / built-in Unreal systems and Infima FP animation assets to speed up beta dev (borrow the rails). Keep TacticalMovement's **custom readiness/movement identity**.
- **Never merge or push without explicit user approval.** Commit and push are **separate** gates. Work on a `feature/*` branch, not `main`. **Completed, verified feature branches may be pushed after explicit push approval.** **No merge or PR without separate approval.**

## Gameplay identity (custom — never flatten to a sample's feel)
Readiness ladder = **Sul / Low Ready / Movement Ready / ADS** (`ECombatReadinessState`; identity — do not replace). Low Ready is the default firearm posture; Movement Ready is deliberate; ADS is most committed; Sul is lower-readiness but mobile. Mobility-vs-readiness tradeoff + directional movement (distinct fwd/strafe/back speeds, readiness multipliers) are the product. Epic/Infima assets express the model; they do not define it.

## Readiness behavior (current)
- **`1/2/3`** → Sul/LowReady/MovementReady (Enhanced Input → `SetReadiness*` C++).
- **RMB / `IA_ADS` = hold-to-ADS:** Press (`EnterADSHold`) captures previous non-ADS readiness then enters ADS; Release (`ExitADSHold`) restores it; invalid → fallback LowReady; a 1/2/3 change while holding RMB is not clobbered on release. ADS cancels an active sprint and blocks starting one.
- **`4` / `IA_ADS_DevLatch`** = discrete ADS latch (enter and stay; exit via 1/2/3). `SetReadinessADS()` is the shared discrete "enter ADS" path.
- Key C++ in `Source/TacticalMovement/TacticalMovementCharacter.*`: `EnterADSHold()`, `ExitADSHold()`, `PreviousReadinessBeforeADS` (seeded LowReady), `ADSDevLatchAction`. `CombatReadinessState` is `UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)` → readable in Blueprints via a Get node; the inline `GetCombatReadinessState()` accessor is **not** a `UFUNCTION` (not a BP node). `ECombatReadinessState` is `UENUM(BlueprintType)` with `Sul/LowReady/MovementReady/ADS`.

## Repo / project
- **UE working repo (ACTIVE):** `~/UnrealEngine/TacticalMovement_UE58` — UE 5.8. Remote `origin` = https://github.com/jteck/TacticalMovement.
- **Original UE 5.7 project — UNTOUCHED:** `~/UnrealEngine/TacticalMovement` (branch `checkpoint/pre-ue58-upgrade`). Do not upgrade in place.
- **Infima eval project (READ-ONLY, do not modify/save):** `~/UnrealEngine/Infima_TacticalFPS_Test/Infima_TacticalFPS/`.
- **Docs repo:** `~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS project/` — branch `main`, **NO remote configured (local-only, verified 2026-07-11)**. Primary fresh-session handoff file: `CONSOLIDATED_FOR_CHATGPT_2026-07-11.md`. Numbered docs: `01` roadmap, `03A` chronology, `04` code/asset state, `09` change log, `10` Epic-First Gate + Decision Log, `13` Infima FP integration map, `14` FP AnimBP layer design.

## Enhanced Input map (`/Game/Input/`)
- Input Actions (Boolean): `IA_ReadinessSul/LowReady/MovementReady`, `IA_ADS`, `IA_ADS_DevLatch` (+ template `IA_Move/Look/Jump/Sprint`).
- **`IMC_Default` mappings** live under `defaultKeyMappings.mappings` (UE 5.8; legacy top-level `mappings` empty). `RightMouseButton → IA_ADS`, `Four → IA_ADS_DevLatch`, `One/Two/Three → readiness`. Move/Look/Jump/Sprint from template (WASD+arrows+gamepad, LeftShift sprint, SpaceBar jump).
- Bindings in `SetupPlayerInputComponent`: `IA_ADS` Started→`EnterADSHold`, Completed→`ExitADSHold`; `IA_ADS_DevLatch` Started→`SetReadinessADS`; readiness Started→`SetReadiness*`.

## Editor + MCP bridge (macOS, Apple Silicon; UE 5.8 at `/Users/Shared/Epic Games/UE_5.8`; Xcode 26)
```bash
# status
git -C ~/UnrealEngine/TacticalMovement_UE58 status
git -C ~/UnrealEngine/TacticalMovement_UE58 log --oneline --decorate -10

# relaunch editor + MCP bridge — DETACHED so it survives a Claude session restart (see lessons):
nohup "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" \
  ~/UnrealEngine/TacticalMovement_UE58/TacticalMovement.uproject -ModelContextProtocolStartServer \
  > /tmp/ue_editor_launch_$(date +%s).log 2>&1 & disown
# Poll until `lsof -nP -iTCP:8000 -sTCP:LISTEN` shows LISTEN AND the editor finished loading
# (log line "LogModelContextProtocol: Tool search enabled"); GET 127.0.0.1:8000/mcp returns 405 = alive.

# build (editor MUST be closed first — it locks the module dylib):
cd ~/UnrealEngine/TacticalMovement_UE58
"/Users/Shared/Epic Games/UE_5.8/Engine/Build/BatchFiles/Mac/Build.sh" \
  TacticalMovementEditor Mac Development -project="$PWD/TacticalMovement.uproject" -waitmutex
```

## MCP / editor operational lessons
- **Launch the editor DETACHED** (`nohup … & disown`), NOT via a harness-tracked background job: a `run_in_background` launch dies when the Claude session exits (learned when the editor died on `claude --continue`). Detached survives.
- **MCP client binds at Claude-startup.** If the editor bridge isn't up when the session starts, `unreal-mcp` tools won't register. Fix: launch the editor first, then start/continue Claude; or run **`/mcp` to reconnect** once the bridge is up. `unreal-mcp` exposes 3 meta-tools (`list_toolsets`, `describe_toolset`, `call_tool`) fronting ~53 toolsets.
- **On UE crash → "reopen" gets stuck / `CrashReportClient` squats on port 8000:** `kill` the specific `CrashReportClient` PID (SIGKILL if SIGTERM is ignored), confirm port 8000 free, then relaunch detached. Editor cold-start opens the port early but is unresponsive (HTTP 000) until fully loaded.
- **On the "Restore Packages" auto-save prompt after a crash: choose "Skip Restore"** to keep the manually-saved, verified asset (do not overwrite it with an unknown auto-save).
- **Skeletons open dirty in-memory** on load (asterisk) without any edit; **SIGTERM discards dirty packages** (does not save) — safe for read-only inspection. `git status` on disk is the source of truth for whether anything actually changed.
- **MCP cannot read or author AnimGraph pose nodes** (`BlueprintTools.read_graph_dsl` returns empty for the AnimGraph). **EventGraph DSL is readable.** AnimGraph authoring is MANUAL in-editor by the user; MCP verifies indirectly (compile + `get_dependencies` + the user's visual check).
- **MCP/Slate could NOT see the docked Anim Slot Manager** (`CaptureEditorImage` didn't show it; `WaitFor("DefaultSlot")`/`WaitFor("Anim Slot Manager")` false; no floating window) — for skeleton slot groups, **require an OS screenshot from the user.**
- `USkeleton` slot groups (`SlotGroups`) are **not exposed** via `ObjectTools` property reflection.
- `EditorAppToolset.CaptureEditorImage` / `SlateInspectorToolset.Screenshot` return large base64 → decode to a PNG file and Read it.
- `gh` CLI is **not** installed. Use the GitHub REST API with the token from `git credential fill` (host `github.com`); never print the token. Metal Toolchain installed (UE 5.8 + Xcode 26). UE 5.8 logs: `~/Library/Logs/Unreal Engine/TacticalMovementEditor/TacticalMovement.log`.

## PIE / MCP validation techniques
- Tests: `AutomationTestToolset.DiscoverTests` then `RunTestsByFilter("StartsWith:TacticalMovement.Readiness")`.
- The **PIE player pawn is not reachable** via `EditorAppToolset.GetVisibleActors` (returns editor-world actors). Live-instance reads may need `SceneTools.find_actors` or user-driven checks; `Slate PressKey` cannot reach the PIE game viewport → for input-driven checks use `PlayMode_InEditorFloating` + real user input.

## Workflow reminders
- Before any new subsystem: run the **Epic-First Gate** (docs `10`) and log it. Reference Epic / Lyra / Infima **patterns/tech/assets only** — never their feel/values.
- Per-slice: propose → approve → implement on a new `feature/*` branch → verify (compile + 12/12 + deps + git scope) → report → **commit only named files on explicit approval** → **push on separate explicit approval** (report remote/branch/hash + match). No merge/PR without separate approval.
