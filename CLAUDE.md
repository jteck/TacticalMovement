# CLAUDE.md — TacticalMovement (UE 5.8)

Durable project context, auto-loaded every session. This file is a **self-contained handoff**: a fresh Claude Code session should be able to continue from it without prior chat history.

> **Golden rule: "Borrow the rails, keep our train."** Use Epic UE 5.8 systems / tools / sample patterns (and Infima FP animation assets) for scaffolding and plumbing; keep TacticalMovement's readiness/movement identity custom. **Before any new subsystem, run the Epic-First Gate** (docs `10`, Section 11) and log the decision in the Decision Log.
>
> **Do not merge or push anything without the user's explicit approval.** Commit and push are **separate** approval gates, per slice. Always verify live state with `git`/GitHub before acting — the status below is a point-in-time snapshot.

---

## HANDOFF — current state (2026-07-12)

> **Verify live git state before acting** (`git status`, `git log --oneline --decorate`). Hashes below were verified on 2026-07-12 but re-check.

### 1. Current repo state (verified 2026-07-12)
- **Active UE project:** `~/UnrealEngine/TacticalMovement_UE58` (UE 5.8; `.uproject` EngineAssociation = 5.8).
- **GitHub:** https://github.com/jteck/TacticalMovement (remote `origin`).
- **ACTIVE BRANCH:** `feature/fp4-tactical-fp-montage-slots` @ **`e9bac570c18998e637418872ecd579cc1ffef51f`** ("Add Tactical FP montage slot plumbing", FP-4). Parent = **`c27d2ce`** (FP-3 branch tip: a CLAUDE.md refresh atop FP-3 impl `6910085`).
  - **Pushed; local == `origin/feature/fp4-tactical-fp-montage-slots`** (upstream set, verified 2026-07-12).
- **`origin/main` = `acae9cb`** — unchanged (FP work never touched `main`).
- **FP commit chain (newest first):** `e9bac57` FP-4 → `c27d2ce` (CLAUDE.md refresh) → `6910085` FP-3 → `2314dbf` FP-2 (`origin/feature/fp2-tactical-fp-idle-animbp`, pushed) → `df2367e` FP-1 → `deed772` FP-0 → `cebdf56` (Slice-2 handoff) → …
- **Local branches:** `main`, `checkpoint/pre-ue58-upgrade`, `feature/fp0-infima-viewmodel-assets`, `feature/fp1-first-person-viewmodel-component`, `feature/fp2-tactical-fp-idle-animbp`, `feature/fp3-tactical-fp-ads-blend`, `feature/fp4-tactical-fp-montage-slots` (current), `feature/weapon-posture-visualization`.
- **Working tree clean.** Readiness suite **12/12**.

### 2. First-person (Infima) slices — FP-0 … FP-4 COMPLETE
TacticalMovement is a **first-person (FPS)** game. The **Infima "Tactical FPS Animation Pack – Assault Rifle"** is used **only** as an authored FP arms/weapon animation source — **not Lyra, no MoCap, no GAS, no Gameplay Tags.**
- **FP-0 (`deed772`)** — copied the minimal Infima FP viewmodel asset closure (13 `.uasset`) into `/Game/InfimaGames/TacticalFPSAnimations/…`: 2 poses (`A_TFA_FP_AR_Idle_Pose_Standing`, `A_TFA_FP_AR_Aim_Pose`), skeleton `SKEL_TFA_Mannequin`, mesh `SKM_FP_Manny_Simple`, `M_Mannequin` + `MI_Manny_01/02` + 6 `T_Manny` textures. Excluded full-body preview meshes. No demo/TP/Lyra deps.
- **FP-1 (`df2367e`)** — added to `BP_ThirdPersonCharacter` (Blueprint-only): `FirstPersonCamera` (`UCameraComponent`, `bAutoActivate=FALSE` — NOT the gameplay view) on the capsule; `FirstPersonArms` (`USkeletalMeshComponent`) under it, mesh `SKM_FP_Manny_Simple`, `bOnlyOwnerSee=true`. `FollowCamera`/`CameraBoom` remain the active TP gameplay view.
- **FP-2 (`2314dbf`)** — created `/Game/FirstPerson/Animations/ABP_TacticalFP` (skeleton `SKEL_TFA_Mannequin`, AnimGraph = idle pose Sequence Player → Output). `FirstPersonArms.animClass = ABP_TacticalFP_C`.
- **FP-3 (`6910085`)** — MovementReady↔ADS pose blend on `ABP_TacticalFP`. Verified: **compile 0/0**; EventGraph logic confirmed via DSL read (`bIsADS = OwningCharacter.CombatReadinessState == ADS`, cast to the **C++ class** `TacticalMovementCharacter` — not `BP_ThirdPersonCharacter`; resilient owner reacquire; `bIsADS` set only when owner valid); AnimGraph `Blend Poses by Bool` (Active=`bIsADS`, True=Aim pose, False=Idle pose, **0.2s** both blend times); **deps clean** (no `BP_ThirdPersonCharacter`/demo/TP/Lyra); **12/12**; git scope = only `ABP_TacticalFP.uasset`; **user visual verification passed** (RMB-hold→aim, release→idle; key `4` latch, `1/2/3` exit; smooth 0.2s blend).
- **FP-4 (`e9bac57`)** — `DefaultSlot` + `Aiming` **montage slot plumbing** spliced into `ABP_TacticalFP` AnimGraph: `Idle Sequence Player → Slot 'DefaultSlot' (DefaultGroup) → Blend Poses by Bool [False]`; `Aim Sequence Player → Slot 'Aiming' (DefaultGroup) → Blend [True]`. Existing `bIsADS` Active Value, **0.2s** blend times, EventGraph, and Output Pose all preserved; empty slots pass base poses through → **FP-3 behavior unchanged**. **No montage created or played.** Authored **entirely via MCP** `BlueprintTools` (`create_node` + `set_properties` `Node.slotName` + `break_pins`/`connect_pins`) — no manual editing. Verified: **compile 0/0**; both slots resolve `DefaultSlot`/`Aiming` in `DefaultGroup`; **deps clean** (no montage/`BP_ThirdPersonCharacter`/demo/TP/Lyra — Slot nodes add zero content deps); **12/12**; PIE smoke clean; git scope = only `ABP_TacticalFP.uasset`; **user visual regression passed** (RMB hold/release + `4` then `1/2/3` → same smooth idle↔aim as FP-3). Preflight confirmed against the Infima reference (read-only): `AM_TFA_FP_AR_Reload` targets **both** slots (`DefaultSlot`=hip reload `A_TFA_FP_AR_Reload`, `Aiming`=aimed reload `A_TFA_FP_AR_Reload_Aimed`); `ABP_TFA_FP_BaseCharacter` wires `Aiming`→True / `DefaultSlot`→False into a bool blend, both slots in `DefaultGroup`.

**Expected visual caveat (normal, not a bug):** from the TP view the FP arms look wrong (posed for a rifle, no FP weapon attached, TP body still visible). The FP arms only "make sense" through `FirstPersonCamera` with the TP body hidden + an FP weapon — all deferred.

### 3. FP-5 — NOT YET SCOPED
FP-4 (montage slot plumbing) is complete/pushed (see §2). The `DefaultSlot`/`Aiming` slots on `ABP_TacticalFP` are now in place and pass base poses through until a montage drives them. **FP-5 is the next presentation-layer slice but has no defined scope yet — await user direction.** (Resolved during FP-4 preflight: the `Aiming` slot DID survive FP-0 on the TacticalMovement `SKEL_TFA_Mannequin`, sitting in `DefaultGroup` — so no FP-0 Infima-asset edit was ever needed.) Same gated pattern: propose → approve → implement on a new `feature/*` branch → verify → commit gate → push gate.

### 4. NEXT ACTION (resume here)
FP-4 is complete, committed (`e9bac57`), and pushed; **no FP work is in flight** and the working tree is clean. To continue: verify live git state, then pick a direction —
1. **Scope/approve FP-5** (§3) — next presentation-layer slice, same gated pattern; or
2. **Integrate** the pushed FP branch(es) toward `main` (PR / merge) — needs separate explicit approval (**no merge/PR without it**).
Reopen the editor (detached launch + MCP bridge) per the Editor section when hands-on work resumes.

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
- **Docs repo:** `~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS project/` — branch `main`, **private GitHub mirror `origin` = https://github.com/jteck/TacticalMovement-Docs (upstream `origin/main`; added 2026-07-12)**. Local-only reference dirs (`FPS shooter UE ideas/`, `tactical positions/`) are excluded via `.gitignore`. Commit hashes here are point-in-time snapshots — **verify live** with `git`. Primary fresh-session handoff file: `CONSOLIDATED_FOR_CHATGPT_2026-07-11.md`. Numbered docs: `01` roadmap, `03A` chronology, `04` code/asset state, `09` change log, `10` Epic-First Gate + Decision Log, `13` Infima FP integration map, `14` FP AnimBP layer design.

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
- **MCP CAN read AND author AnimGraph pose nodes** (corrected in FP-4 — the earlier "manual only" belief was wrong for UE 5.8 `BlueprintTools`). `read_graph_dsl` returns **empty** for an AnimGraph, BUT `find_nodes(graph, title="")` enumerates the pose nodes and `get_node_infos` returns full pin/link detail; `create_node` + `ObjectTools.set_properties` (SlotName is `Node.slotName`) + `break_pins`/`connect_pins` + `compile_blueprint` author and compile them. Slot node `type_id` = `Animation|Montage|Slot'DefaultSlot'` (only the DefaultSlot spawn exists — create it, then set `Node.slotName` for other slot names). **FP-4 added both Slot nodes entirely via MCP, zero manual editing.** EventGraph DSL is also readable. Still verify with compile 0/0 + `get_dependencies` + the user's visual check.
- **Editor shutdown/relaunch — use `kill -9` (SIGKILL), not SIGTERM, then wait ~8s before relaunching.** The MCP HTTP server does a **one-shot** bind of port 8000 at startup; if the port isn't fully released it logs `LogHttpListener: Error: HttpListener unable to bind to 127.0.0.1:8000`, gives up, and runs with **no bridge** (tools never register). SIGTERM makes it worse — it spawns a `CrashReportClient` that re-grabs port 8000. So: SIGKILL the editor, confirm `lsof -nP -iTCP:8000` shows nothing, wait for the socket to release, then relaunch detached. Readiness = port 8000 LISTEN **and** `GET 127.0.0.1:8000/mcp` → 405.
- **Never call MCP `OpenEditorForAsset` on macOS** — opening an asset-editor window from the HTTP-server tick deadlocks the game+UI thread in `FSlateApplication::MakeWindow` (editor freezes, dock "not responding", MCP HTTP → 000). Have the **user double-click** assets to open them (normal UI path is safe). `sample <pid>` diagnoses: MakeWindow/semaphore = deadlock; `UpdateTimeAndHandleMaxTickRate → nanosleep` = healthy idle; high CPU + `LogShaderCompilers` = benign first-launch shader compile (intermittent spinners — wait it out).
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
