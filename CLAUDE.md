# CLAUDE.md — TacticalMovement (UE 5.8)

Durable project context, auto-loaded every session. This file is a **self-contained handoff**: a fresh Claude Code session should be able to continue from it without prior chat history.

> **Golden rule: "Borrow the rails, keep our train."** Use Epic UE 5.8 systems / tools / sample patterns for scaffolding and plumbing; keep TacticalMovement's readiness/movement identity custom. **Before any new subsystem, run the Epic-First Gate** (docs `10`, Section 11) and log the decision in the Decision Log (Section 12).
>
> **Do not merge or push anything without the user's explicit approval.** Always verify live state with `git`/GitHub before acting — the status below is a point-in-time snapshot.

---

## HANDOFF — current state (2026-07-04)

### 1. Current repo state
> **Verify live git state before acting** (`git status`, `git log --oneline --decorate`); the hashes below are a point-in-time snapshot and may be stale.
- **Active UE project:** `~/UnrealEngine/TacticalMovement_UE58` (UE 5.8; `.uproject` EngineAssociation = 5.8).
- **GitHub:** https://github.com/jteck/TacticalMovement
- **`main` = `origin/main` = `8ecd2e8`** — "Reconcile Claude handoff with six-slice outlook state" (in sync, pushed).
- **ACTIVE BRANCH: `feature/equipped-weapon-static-attach`** (branched from `main` `8ecd2e8`) — **Slice 1 work in progress, UNCOMMITTED** (see §7). Do not merge/push without approval.
- **PR #5 (hold-to-ADS) MERGED** into `main` (merge commit `b8e706c`; slice commit `c5770d2`).
- **`feature/hold-to-ads` deleted** locally and remotely.
- **Branches** — local: `main`, `feature/equipped-weapon-static-attach`, `checkpoint/pre-ue58-upgrade`; remote: `origin/main`, `origin/checkpoint/pre-ue58-upgrade`.
- **`main` working tree clean; the feature branch has uncommitted Slice 1 changes** (§7).
- **No new baseline tag.** `v0.1.0-ue58-baseline` (→ `78b14f6`) remains unchanged.

### 2. Completed systems now in `main`
- **UE 5.7 → 5.8 migration** complete.
- **Enhanced Input** readiness/ADS/sprint mappings complete (readiness moved off the old Blueprint keyboard debug events onto real Input Actions).
- **Low Ready is the default readiness** (C++ default + BP CDO both `LowReady`; guarded by the `BPDefaultIsLowReady` test).
- **Sprint / readiness / ADS rules are stable.**
- **Readiness automation tests** are in `main` (was PR #4).
- **Hold-to-ADS** is merged into `main` (PR #5).

### 3. Current readiness behavior
Readiness enum `ECombatReadinessState` = **Sul / LowReady / MovementReady / ADS** (identity — do not replace).
- **`1`** → Sul · **`2`** → LowReady · **`3`** → MovementReady (Enhanced Input → existing `SetReadiness*` C++ functions).
- **RMB / `IA_ADS` = hold-to-ADS:**
  - Press (`Started` → `EnterADSHold`) captures the previous **non-ADS** readiness, then enters ADS.
  - Release (`Completed` → `ExitADSHold`) **restores the previous readiness**.
  - Invalid/unclear previous state → fallback **LowReady**.
  - A manual readiness change (1/2/3) made **while holding RMB** leaves ADS; the subsequent release is a **no-op** and must **not** clobber that choice.
  - ADS **cancels** an active sprint and **blocks** starting one; sprint does **not** auto-resume after ADS exits.
- **`4` / `IA_ADS_DevLatch` = discrete ADS dev latch** for testing (enters ADS and stays; exit via 1/2/3). Separate action from `IA_ADS` so RMB can be true hold while key 4 stays a hold-independent latch.
- **`SetReadinessADS()` is unchanged** — it remains the discrete "enter ADS" path (cancel sprint + set ADS), called by both the dev latch and internally by `EnterADSHold()`.
- Sprint = `LeftShift` / `IA_Sprint` (hold). Move/Look/Jump unchanged.

Key C++ (in `Source/TacticalMovement/TacticalMovementCharacter.*`): `EnterADSHold()`, `ExitADSHold()`, transient `PreviousReadinessBeforeADS` (seeded `LowReady`), `UInputAction* ADSDevLatchAction`. Read-only test accessors `GetCombatReadinessState()`, `IsSprinting()`.

### 4. Validation already completed (hold-to-ADS slice)
- **Clean build** passed (0 warnings/errors).
- **`TacticalMovement.Readiness` automation suite: 12/12 pass** (4 prior + 8 hold-to-ADS).
- **Live PIE / MCP validation passed:** key-4 ADS latch; 1/2/3 exit from the latch; RMB hold/release restore from LowReady, MovementReady, and Sul; sprint → RMB ADS cancels sprint; ADS blocks sprint; manual readiness change during RMB hold not clobbered on release.

### 5. Important Unreal asset-workflow lesson
After adding a **new C++ `UPROPERTY`** and assigning it on `BP_ThirdPersonCharacter` (e.g. `ADSDevLatchAction`), **save-only was NOT enough** — the property spawned as `None` in PIE. The Blueprint had to be **`compile_blueprint` + saved** before the live PIE instance carried the value. **For any future newly-added C++ `UPROPERTY` assigned on a BP: compile the BP, and verify on the live PIE instance (`find_actors` → `get_properties`), not just a saved-asset read-back.**

### 6. Docs repo state
- **Path:** `~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS project/`
- **No remote configured**; `main` is local-only.
- **Latest local docs commit:** `786a902` — "Correct Slice 1 equipped rifle gate after static attach failure" (docs `10` Slice 1 Gate; see §7).
- Docs remain **local-only** for now. Key docs: `10` (Epic-First Gate + Decision Log), `01` (Roadmap), `04` (code/asset state), `05` (gameplay design decisions), `03A` (chronology), `06` (open issues/risks), `08` (AI project context).

### 7. Slice 1 — IN PROGRESS (paused mid-implementation, 2026-07-04)
**Branch `feature/equipped-weapon-static-attach`. Uncommitted. Corrected goal: "Externally reviewable equipped rifle baseline" — the character must VISIBLY and BELIEVABLY hold one rifle.** Full Gate + history in docs `10` (commit `786a902`).

**Six-slice outlook** (`01_Roadmap.md`): 1) equipped weapon → 2) weapon posture → 3) weapon data → 4) Gameplay Tags → 5) pickup/drop → 6) GAS eval. Slices 1–5 GAS-free; Tags enter at Slice 4; GAS first considered at Slice 6. Each slice needs its own Gate + explicit approval.

**KEY LESSON that reshaped Slice 1:** a **static** rifle mesh bolted to a hand socket **FAILS the alpha visual bar** — with the character in its unarmed animation the arms hang and the rifle dangles/clips. **A believable hold is an ANIMATION POSE, not a mesh transform.** New project-wide **alpha standard: a slice is not complete if it looks broken to an external reviewer.** (The first static-attach attempt + `HandGrip_R` socket + rotation guessing was reverted.)

**Approved corrected approach (adapt Epic's rifle Anim Blueprint):**
- Epic's `ABP_TP_Rifle` (UE 5.8 FirstPerson → `Variant_Shooter`) depends ONLY on assets this project already owns (`MF_Rifle_Idle_ADS`, `AIM/AO_Rifle`, and the same `BS_Idle_Walk_Run`/`MM_Idle`/jump base as `ABP_Unarmed`). No shooter-state/GAS/Lyra/C++ deps. It = `ABP_Unarmed` + a rifle upper-body pose.
- Duplicated it into project as **`ABP_TacticalRifle`** (`/Game/Characters/Mannequins/Anims/Rifle/ABP_TacticalRifle`); the template copy was deleted (clean, self-contained).
- Character mesh (`CharacterMesh0` = `SKM_Quinn_Simple`, skeleton `SK_Mannequin`) `AnimClass` set to `ABP_TacticalRifle`. (`ABP_Unarmed` kept intact as rollback.)
- Attach target = the **`weapon_r` bone** (evidence: rifle anims drive `weapon_r_CONTROL`). **NOT** `HandGrip_R` (that's on `hand_r`), **NOT** `weapon_r_muzzle` (muzzle tip). Rifle mesh = **`SM_Rifle`** (`/Game/Weapons/Rifle/Meshes/SM_Rifle`), attached with **identity** transform (the pose does the placement).

**DONE so far (uncommitted on the branch):**
- `?? Content/Weapons/Rifle/…` — imported `SM_Rifle` + `M_Rifle` + `M_Weapon` + `T_Rifle_BC`/`T_Rifle_N` (license-safe UE 5.8 template resource).
- `?? Content/Characters/Mannequins/Anims/Rifle/ABP_TacticalRifle.uasset` — the adapted Anim BP.
- `M  Content/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.uasset` — mesh `AnimClass`→`ABP_TacticalRifle`; `WeaponMesh` (StaticMeshComponent, `SM_Rifle`, identity, parented to `CharacterMesh0`) added — **Parent Socket still UNSET.**

**BLOCKER / NEXT STEP (needs the two in-editor user actions below):**
The `weapon_r` socket + the SCS "Parent Socket" **cannot be set via the MCP tools** — two known limitations: (a) MCP has no skeleton-socket API and `add_socket` on the reduced `SKM_Quinn_Simple` mesh falls back to `root` for `weapon_r` (it works for `hand_r`/`ik_hand_gun`); `weapon_r` sockets must live on the **skeleton** `SK_Mannequin` (where `weapon_r_muzzle` already is). (b) MCP cannot write a component's SCS **Parent Socket**. So the user must, in-editor:
1. Open `SKM_Quinn_Simple`/`SK_Mannequin` → Skeleton Tree → right-click **`weapon_r`** → Add Socket → rename **`weapon_r_hold`** (identity transform) → Save.
2. `BP_ThirdPersonCharacter` → select `WeaponMesh` → **Parent Socket = `weapon_r_hold`** (leave component transform identity) → Compile + Save.

**THEN (Claude resumes):** relaunch floating PIE (`PlayMode_InEditorFloating`) for the user's alpha-bar visual check (rifle believably held, no clipping, no dangling, barrel believable, through move + all readiness states 1/2/3/4/RMB); re-run `TacticalMovement.Readiness` → expect **12/12**. **If the rifle is held-but-rotated, fix with a PRINCIPLED rotation on the `weapon_r_hold` SOCKET (derived from the axis mismatch), NOT component-offset guessing** (`SM_Rifle` barrel is local +Y). Then report changed files/attach target/mesh/PIE result/tests/git status and await commit approval. **Nothing may be committed without explicit user approval.**

### 8. Standing guardrails (do not violate without explicit approval)
- Do **not** migrate to Lyra (reference only).
- Do **not** introduce **GAS** without explicit approval.
- Do **not** replace `ECombatReadinessState`.
- Do **not** replace the DataTable movement-profile system (`DT_MovementProfiles`).
- Do **not** change movement values without approval.
- Do **not** start weapon visuals, firing, inventory, pickup/drop, mantle, AI, or GAS until approved **as a slice**.
- **Do** use Epic / Lyra / built-in Unreal systems when they speed up beta development (borrow the rails).
- Keep TacticalMovement's **custom readiness/movement identity**.
- **Never merge or push without explicit user approval.** Work on a `feature/*` branch, not `main`.

---

## Repo / project

- **UE working repo (ACTIVE):** `~/UnrealEngine/TacticalMovement_UE58` — UE 5.8.
- **Original UE 5.7 project — UNTOUCHED:** `~/UnrealEngine/TacticalMovement` (branch `checkpoint/pre-ue58-upgrade`). 5.7 source of truth; **do not upgrade in place**.
- **GitHub:** https://github.com/jteck/TacticalMovement
- **Docs repo:** `~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS project/` — branch `main`, **no remote**.

## Enhanced Input map (`/Game/Input/`)

- Input Actions (Boolean): `IA_ReadinessSul`, `IA_ReadinessLowReady`, `IA_ReadinessMovementReady`, `IA_ADS`, `IA_ADS_DevLatch` (+ template `IA_Move`, `IA_Look`, `IA_Jump`, `IA_Sprint`).
- **`IMC_Default` mappings** live under `defaultKeyMappings.mappings` (UE 5.8; the legacy top-level `mappings` array is empty). Current ADS-relevant rows: `RightMouseButton → IA_ADS`, `Four → IA_ADS_DevLatch`. Readiness: `One/Two/Three → Sul/LowReady/MovementReady`. Move/Look/Jump/Sprint from the template (WASD+arrows+gamepad, LeftShift sprint, SpaceBar jump) — all intact.
- Bindings live in `SetupPlayerInputComponent`: `IA_ADS` Started→`EnterADSHold`, Completed→`ExitADSHold`; `IA_ADS_DevLatch` Started→`SetReadinessADS`; readiness actions Started→`SetReadiness*`.

## Gameplay identity (custom — never flatten to a sample's feel)

Readiness ladder = **Sul / Low Ready / Movement Ready / ADS**. Low Ready is the default firearm posture; Movement Ready is deliberate; ADS is most committed; Sul is lower-readiness but mobile. Mobility-vs-readiness tradeoff + directional movement (distinct fwd/strafe/back speeds, readiness multipliers) are the product. Epic systems express the model; they do not define it.

## Editor + MCP bridge (macOS, Apple Silicon; UE 5.8 at `/Users/Shared/Epic Games/UE_5.8`; Xcode 26)

```bash
# status
git -C ~/UnrealEngine/TacticalMovement_UE58 status
git -C ~/UnrealEngine/TacticalMovement_UE58 log --oneline --decorate -10

# relaunch editor + MCP bridge (detached; MCP server on 127.0.0.1:8000)
open -n -a "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" \
  --args "/Users/jasonteck/UnrealEngine/TacticalMovement_UE58/TacticalMovement.uproject" \
  -ModelContextProtocolStartServer
# wait until `curl -s -o /dev/null -w '%{http_code}' 127.0.0.1:8000/mcp` is reachable (405/200), then use MCP.

# build (editor MUST be closed first — it locks the module dylib)
#   incremental (fast, ~20s) — preferred for small C++ changes:
cd ~/UnrealEngine/TacticalMovement_UE58
"/Users/Shared/Epic Games/UE_5.8/Engine/Build/BatchFiles/Mac/Build.sh" \
  TacticalMovementEditor Mac Development -project="$PWD/TacticalMovement.uproject" -waitmutex
#   full clean rebuild (only if needed): prepend `rm -rf Binaries Intermediate`
```

**MCP / editor operational notes (learned in the hold-to-ADS slice):**
- Adding a new `UPROPERTY` needs a full editor-closed build (Live Coding won't add reflected properties); a new plain C++ method (non-`UFUNCTION`) can bind via `BindAction` without reflection.
- After closing the editor to build and relaunching, the MCP client **may reconnect automatically**; if tools error, restart Claude Code (client retries only ~3× at startup; the editor must be bound to `:8000` first).
- If MCP is down: check `lsof -nP -iTCP:8000`. If a stale `CrashReportClient` (not `UnrealEditor`) holds the port, kill it, then `pkill -9 -f "TacticalMovement_UE58/TacticalMovement.uproject"` and relaunch. UE 5.8 logs are at `~/Library/Logs/Unreal Engine/TacticalMovementEditor/TacticalMovement.log` (NOT the project's `Saved/Logs`).
- **`gh` CLI is NOT installed.** Create/merge PRs via the **GitHub REST API** with the token from `git credential fill` (host `github.com`); never print the token.
- Metal Toolchain installed (required by UE 5.8 + Xcode 26).

**PIE / MCP validation techniques (how the live checks were driven):**
- Run tests: `AutomationTestToolset` → `DiscoverTests(bForceRediscover=true)` after a rebuild, then `RunTestsByFilter("StartsWith:TacticalMovement.Readiness")`.
- Read live pawn state: start PIE (`EditorAppToolset.StartPIE`), then `SceneTools.find_actors(name="ThirdPersonCharacter")` returns the PIE pawn (`…UEDPIE_0_…BP_ThirdPersonCharacter_C_0`); read with `ObjectTools.get_properties` (`CombatReadinessState`, `bIsSprinting`).
- **Slate `PressKey` cannot reach the PIE game viewport** (input goes to the focused Slate widget, not the game) — synthetic keypress routing is effectively unavailable. **Use `PlayMode_InEditorFloating`** and have the **user provide real keyboard/mouse input**; the floating window captures it reliably.
- For **hold** inputs (RMB, Shift) the user can't type while the mouse is captured: use a **timed read** — user sends "go" then holds; run a `ProgrammaticToolset.execute_tool_script` that `time.sleep(4)` then reads the pawn (sample twice, e.g. t≈4s and t≈6s, to be robust to timing). Key 4 (discrete latch) is the only ADS state settable by a single tap and is directly readable after the press.

## Workflow reminders
- Before any new subsystem: run the **Epic-First Gate** (docs `10` §11) and log it (§12).
- Reference Epic / Lyra / Game Animation Sample **patterns and tech only** — never feel/values.
- Vertical-slice discipline: one Epic-backed layer, prove it in runtime + tests, then the next.
- **Do not merge or push unless the user explicitly approves.**
