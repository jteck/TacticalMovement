# CLAUDE.md — TacticalMovement (UE 5.8)

Durable project context, auto-loaded every session. For the detailed point-in-time snapshot see `CURRENT_CLAUDE_CODE_HANDOFF.md` (repo root).

> **Golden rule: "Borrow the rails, keep our train."** Use Epic UE 5.8 systems / tools / sample patterns for scaffolding and plumbing; keep TacticalMovement's readiness/movement identity custom. **Before any new subsystem, run the Epic-First Gate** (docs `10`) and log the decision.
>
> **Do not merge or push anything without the user's explicit approval.**

## Repo / project

- **UE working repo (ACTIVE):** `~/UnrealEngine/TacticalMovement_UE58` — UE 5.8, `.uproject` EngineAssociation = 5.8.
- **Original UE 5.7 project — UNTOUCHED:** `~/UnrealEngine/TacticalMovement` (branch `checkpoint/pre-ue58-upgrade`). 5.7 source of truth; **do not upgrade in place**.
- **GitHub:** https://github.com/jteck/TacticalMovement
- **Docs repo (separate git repo):** `~/Library/Mobile Documents/com~apple~CloudDocs/Coding/UE FPS project/` — branch `main`, **no remote configured**, working tree clean, latest commit `24eb740`. Key docs: `10` (Epic-First Gate + Decision Log), `04` (code/asset state), `03A` (chronology; Phase 17 = Enhanced Input), `06` (open issues; sprint/ADS bug = RESOLVED).

## Current project state — VOLATILE (verify with `git`/GitHub before acting)

_This block reflects 2026-07-03 and can go stale. Confirm with `git status`, `git log --oneline --decorate -10`, and the GitHub PR pages._

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
