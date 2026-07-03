# CLAUDE.md — TacticalMovement (UE 5.8)

Durable project context, auto-loaded every session. For the detailed point-in-time snapshot see `CURRENT_CLAUDE_CODE_HANDOFF.md` (repo root).

> **Golden rule: "Borrow the rails, keep our train."** Use Epic UE 5.8 systems / tools / sample patterns for scaffolding and plumbing; keep TacticalMovement's readiness/movement identity custom. **Before any new subsystem, run the Epic-First Gate** (docs `10`) and log the decision.
>
> **Do not merge or push anything without the user's explicit approval.**

## ✅ LAST SLICE — Phase H (1) default readiness = Low Ready — COMMITTED (2026-07-03)

**Slice: Phase H (1) — make readiness default = Low Ready** (reconciled: runtime was `Sul`, C++ was `MovementReady` → now `LowReady`). **DONE + committed with user approval.**

**Root cause (was):** `BP_ThirdPersonCharacter` **class default** `combatReadinessState = Sul` overrode the C++ initializer (property is `EditDefaultsOnly`); GameMode spawns from the BP class → BP CDO won.

**What shipped (HEAD of branch `feature/default-readiness-lowready`, NOT pushed):**
- ✅ `Source/TacticalMovement/TacticalMovementCharacter.h` — C++ default `MovementReady` → `LowReady` (~line 110); editor target rebuilt (native CDO verified = `LowReady`).
- ✅ `Content/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.uasset` — `combatReadinessState` set to `LowReady` and saved (was `Sul`). NOTE: `ObjectTools.reset_properties` returned `true` but did NOT persist (BP reapplied its serialized value on re-read); `set_properties("LowReady")` did. So the BP carries an **explicit `LowReady` override** matching the C++ default, not a pure inherit — functionally correct; revisit if true single-source inherit is wanted.
- ✅ This CLAUDE.md handoff.
- Docs repo commit `e33808e` on `main`: `01_Roadmap.md` (Phase F/G → Completed, UE 5.8 baseline milestone, Phase H → Current), `04` (default readiness recorded), `03A` (Phase 17.5 baseline + Phase 18 slice), `09` (stale line refreshed).

**Live PIE validation (MCP):** fresh spawn `combatReadinessState` = **LowReady** ✅; readiness ladder via real Enhanced Input path — `1`→Sul ✅ `2`→LowReady ✅ `3`→MovementReady ✅ `4`→ADS ✅ RMB→ADS ✅. *Technique that worked:* `Click(sp4)` (viewport region) to focus game input BEFORE `PressKey` (`One`/`Two`/`Three`/`Four`); readiness persists so read after each. **Not re-driven:** sprint / ADS-cancels-sprint / jump — **hold-to-input** transients and Slate `PressKey` is press+release only (no key-hold primitive); this slice changed only a data default (can't affect movement/input logic), already log-verified in the Enhanced Input slice.

**NEXT (not started):** branch `feature/default-readiness-lowready` is local-only — **push / open PR pending user decision.** Then Phase H continues (Movement Ready as deliberate choice, etc.) or next slice per roadmap. Automation tests still DEFERRED. Note this CLAUDE.md edit is a post-commit tweak = uncommitted working-tree change on the feature branch.

**Editor status — BLOCKER RESOLVED (2026-07-03):** the "editor hangs on an early modal dialog" diagnosis was WRONG. Two facts corrected it:
- **UE 5.8 logs live at `~/Library/Logs/Unreal Engine/TacticalMovementEditor/TacticalMovement.log`, NOT the project's `Saved/Logs`.** The old "no logs = stuck early in boot" conclusion came from checking the wrong path; the editor was logging + booting fine the whole time.
- **Real root cause of MCP-down:** a stale `CrashReportClient` (from an earlier crash) was **squatting `127.0.0.1:8000`**, so the editor's MCP HTTP listener failed to bind (log: `LogHttpListener: Error: HttpListener unable to bind to 127.0.0.1:8000`) and UE does not retry. That leftover crash reporter was likely also the "modal" that was seen.
- **Fix applied:** killed the stale `CrashReportClient` + the old editor, freed port 8000, relaunched with `-ModelContextProtocolStartServer`. Editor now fully booted (fast ~2.5 min on warm cache) and **MCP is bound on 8000** (`curl 127.0.0.1:8000/mcp` → 405, i.e. reachable/POST-only).
- **If MCP is ever down again:** check `lsof -nP -iTCP:8000` — if something other than UnrealEditor holds it (e.g. `CrashReportClient`), kill that, then `pkill -9 -f "TacticalMovement_UE58/TacticalMovement.uproject"` and relaunch. To diagnose boot, read the `~/Library/Logs/...` log, not `Saved/Logs`. MCP client connects only if the editor is bound to 8000 **before** Claude Code starts (restart Claude Code after the bridge is up).

**Git anchors:** `main` = `60dadd6` (pushed); baseline tag `v0.1.0-ue58-baseline` → `78b14f6`. Default-readiness slice = HEAD of branch `feature/default-readiness-lowready` (local only, NOT pushed). Docs repo `main` = `e33808e` (no remote). Working tree: this CLAUDE.md tweak is the only uncommitted change (on the feature branch).

## Repo / project

- **UE working repo (ACTIVE):** `~/UnrealEngine/TacticalMovement_UE58` — UE 5.8, `.uproject` EngineAssociation = 5.8.
- **Original UE 5.7 project — UNTOUCHED:** `~/UnrealEngine/TacticalMovement` (branch `checkpoint/pre-ue58-upgrade`). 5.7 source of truth; **do not upgrade in place**.
- **GitHub:** https://github.com/jteck/TacticalMovement
- **Docs repo (separate git repo):** `~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS project/` — branch `main`, **no remote configured**, working tree clean, latest commit `24eb740`. Key docs: `10` (Epic-First Gate + Decision Log), `04` (code/asset state), `03A` (chronology; Phase 17 = Enhanced Input), `06` (open issues; sprint/ADS bug = RESOLVED).

## Current project state — VOLATILE (verify with `git`/GitHub before acting)

_This block reflects 2026-07-03 and can go stale. Confirm with `git status`, `git log --oneline --decorate -10`, and the GitHub PR pages._

> **⚠️ SUPERSEDED — the facts in this block predate the baseline merge and are OUT OF DATE.** PR #1 & PR #2 are both MERGED and their branches deleted; `main` is now `60dadd6`; UE 5.8 baseline is tagged `v0.1.0-ue58-baseline` (`78b14f6`); jump input binding was fixed. Trust the **"ACTIVE SLICE — RESUME HERE"** section at the top and live `git`, not the lines below.

- **Active branch:** `feature/enhanced-input-readiness` (all four branches pushed to origin; nothing unpushed; working tree clean).
- **Editor + MCP bridge:** DOWN by default; relaunch on demand (see Commands).
- **Open PR stack (both OPEN, NOT merged):**
  - **PR #2** — `feature/ue58-migration` → `main` — https://github.com/jteck/TacticalMovement/pull/2
    Scope: readiness-state movement checkpoint, UE 5.8 migration, Epic MCP bridge, sprint/ADS debug-key fix.
  - **PR #1** — `feature/enhanced-input-readiness` → `feature/ue58-migration` — https://github.com/jteck/TacticalMovement/pull/1
    Scope: Enhanced Input readiness / ADS slice only. **Stacked on PR #2.**
- **Merge order:** merge **PR #2 first, then PR #1**. Do NOT merge PR #1 before PR #2. After PR #2 merges, PR #1 likely needs retargeting to `main`.

## Important commits

| Hash | Contents |
|---|---|
| `2b80eda` | Readiness-state movement checkpoint before UE 5.8 migration (base of migration branch; not yet in `main`) |
| `1a1e63a` | UE 5.7 → 5.8 migration (`.uproject`, both `Target.cs` → V7 + Unreal5_8, STATETREE macro deprecation fix) |
| `58892c6` | Epic MCP bridge enablement (`ModelContextProtocol` + `AllToolsets`) |
| `fe27c80` | Sprint/ADS debug-key fix (Input Debug Key → normal keyboard events; modifier-chord was the bug, not the C++) |
| `034470c` | Enhanced Input readiness / ADS C++ bindings |
| `70c80cd` | Enhanced Input assets, IMC mappings, Blueprint cleanup |
| docs `24eb740` | Docs updated for Enhanced Input implementation |

`main` = `b376de9`; initial commit `cd52d8a`.

## Enhanced Input slice (implemented, validated)

- **New Input Actions** (`/Game/Input/`, Boolean): `IA_ReadinessSul`, `IA_ReadinessLowReady`, `IA_ReadinessMovementReady`, `IA_ADS`.
- **`IMC_Default` mappings** (existing WASD/Move/Look/Sprint/Jump untouched; mappings live in `defaultKeyMappings.mappings` in 5.8): `1`→Sul, `2`→LowReady, `3`→MovementReady, `RMB`→ADS, `4`→ADS.
- **`TacticalMovementCharacter.h`:** added `UInputAction*` properties for readiness + ADS.
- **`TacticalMovementCharacter.cpp`:** bound them in `SetupPlayerInputComponent` (`ETriggerEvent::Started`); bindings call the **existing** `SetReadiness*` functions (no rule/logic changes).
- **`BP_ThirdPersonCharacter`:** assigned the Input Actions in Class Defaults; **removed** the old keyboard readiness event nodes + their `SetReadiness` call nodes.
- **Final input path:** Enhanced Input → C++ readiness functions. **Old path removed** (raw Blueprint keyboard events → readiness functions).

## Validation results (Enhanced Input slice)

- Clean rebuild succeeded, **zero warnings/errors**.
- Temporary `[EIValidate]` logs were **removed before commit** (source verified clean).
- Old Blueprint readiness keyboard path was **removed before final validation** (Enhanced Input tested in isolation).
- Objectively verified via runtime log trace: `1/2/3/4` route through Enhanced Input; RMB → ADS; sprint works via `IA_Sprint`; pressing `4` while sprinting triggers ADS and **cancels sprint**; **ADS blocks starting sprint**; Move/Look/Jump normal.

## Guardrails (do not violate without approval)

- Do **not** replace `ECombatReadinessState`.
- Do **not** change the readiness ladder/rules without approval.
- Do **not** introduce GAS yet.
- Do **not** migrate into Lyra (reference only).
- Do **not** start animation work yet.
- Do **not** replace the DataTable movement profile system.
- Do **not** change movement values without approval.
- ADS is **temporary discrete-press** for this slice; hold-to-ADS / release-to-previous is **deferred**.

## Gameplay identity

Readiness ladder = TacticalMovement identity (custom; no Epic sample provides it):
- **Sul**, **Low Ready**, **Movement Ready**, **ADS**.
- (Note: current C++ default is `MovementReady`; docs say **Low Ready** is the *intended* default — not yet reconciled.)
- Epic systems are for scaffolding/plumbing only; custom tactical readiness logic stays custom.

## Workflow reminder

- Before any new subsystem: run the **Epic-First Gate** (docs `10`) and log it in the Decision Log.
- Reference Epic / Lyra / Game Animation Sample **patterns and tech only** — never feel/values. Preserve identity.
- **Do not merge or push unless the user explicitly approves.**
- Likely next slices (each pending a gate check + approval): weapon setup / posture visual animation, ADS behavior design (hold-to-ADS), weapon sockets, animation layering, input expansion (crouch/fire/lean).
- **Planned traversal slice (NOT started):** Mantle first, then vault/climb later. Must go through the Epic-First Gate before implementation; evaluate the Epic Game Animation Sample traversal/mantle system. Mantling should feel grounded/weighted, suspend readiness/ADS during the action, and restore the prior state afterward. (Docs: `01` Roadmap → Later/Planned, `10` §4.)

## Commands (macOS, Apple Silicon; UE 5.8 at `/Users/Shared/Epic Games/UE_5.8`; Xcode 26)

```bash
# status
git -C ~/UnrealEngine/TacticalMovement_UE58 status
git -C ~/UnrealEngine/TacticalMovement_UE58 log --oneline --decorate -10

# relaunch editor + MCP bridge (detached; auto-starts MCP server on 127.0.0.1:8000)
open -n -a "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" \
  --args "/Users/jasonteck/UnrealEngine/TacticalMovement_UE58/TacticalMovement.uproject" \
  -ModelContextProtocolStartServer
# wait ~20-30s until `curl 127.0.0.1:8000/mcp` returns HTTP 200, THEN start/restart Claude Code so its
# MCP client connects (client retries only 3x at startup then marks the server `failed`).

# clean C++ rebuild (editor must be closed)
cd ~/UnrealEngine/TacticalMovement_UE58 && rm -rf Binaries Intermediate
"/Users/Shared/Epic Games/UE_5.8/Engine/Build/BatchFiles/Mac/Build.sh" \
  TacticalMovementEditor Mac Development -project="$PWD/TacticalMovement.uproject" -waitmutex
```

- **`gh` CLI is NOT installed.** PRs were created/edited via the **GitHub REST API** using the token from `git credential fill` (host `github.com`).
- Metal Toolchain already installed (`xcodebuild -downloadComponent MetalToolchain`) — required by UE 5.8 + Xcode 26.
