# Abiverd — moving work to the second Mac

**Date:** 2026-09-09
**Reason:** continuing Operation Sunscar map work on another machine.

## What has to travel

| Thing | Where it lives | How it moves |
|---|---|---|
| Map work (453 files) | staged, **uncommitted** on `feature/map-development` | commit + push (needs both approval gates) |
| 16 earlier commits | local only, ahead of `origin/feature/map-development` | push |
| Claude Code memory | `~/.claude/projects/-Users-jasonteck/memory/` | copy or sync — see below |
| Bridge + reader scripts | `Planning/bridge_scripts/` (in git) | rides along with the push |
| Ground audit | `Planning/ABIVERD_GROUND_REALISM_AUDIT_2026-09-09.md` | rides along |

## Git route (the repo)

git-lfs **is** configured for `.uasset` / `.umap` / `.ubulk` / `.uexp` / `.uptnl`,
and `origin/feature/map-development` already exists, so binaries transfer cleanly.
Do not try to move the 8.9 GB worktree by hand.

On this Mac, once both gates are approved:

```
git -C ~/UnrealEngine/_worktrees/map-development push origin feature/map-development
```

On the second Mac:

```
git clone https://github.com/jteck/TacticalMovement.git
cd TacticalMovement
git lfs install
git worktree add ../_worktrees/map-development feature/map-development
```

If the clone is already there, just `git fetch origin && git checkout feature/map-development && git pull`.

**Verify LFS actually pulled** — a failed LFS fetch leaves pointer files that
look fine to git but break in the editor:

```
git lfs ls-files | head
head -c 100 Content/Maps/Sunscar/Art/Heightmaps/T_HM_Sunscar_CoreRelief_v2.uasset | xxd | head -2
```

The second command must show binary, not `version https://git-lfs...`.

## Claude Code memory

Memory lives at `~/.claude/projects/<project-key>/memory/`, where `<project-key>`
is the working directory with `/` replaced by `-`. Here that key is
`-Users-jasonteck`, i.e. memory is scoped to the **home directory** as project
root — so Claude Code must be started from `~` on the second Mac for these
memories to load. Starting it from the worktree yields a different key and an
empty memory set.

Ten files, 40 KB total. Three ways to move them, in order of preference:

### 1. iCloud + symlink — **DONE on Mac #1 (2026-09-09)**

Mac #1 is already converted. Its memory directory is now a symlink:

```
~/.claude/projects/-Users-jasonteck/memory
  -> ~/Library/Mobile Documents/com~apple~CloudDocs/ClaudeMemory
```

Verified at setup: 11 files copied, checksum identical before and after
(`6c9a8dd76300d0978abdb5922515937f`), write-through confirmed, 0 `.icloud`
placeholders, `brctl` reported caught-up. The original directory is preserved at
`~/.claude/projects/-Users-jasonteck/memory.bak` — delete it only once Mac #2 has
successfully read the memories.

**CORRECTION 2026-09-10 — do NOT symlink over Mac #2's memory directory.**

The original instruction here said to rename Mac #2's `memory/` to `.bak` and
symlink the iCloud folder in its place. That was wrong and was caught before it
ran. **The two Macs hold different memory sets:**

| | Mac #1 (source) | Mac #2 |
|---|---|---|
| Files | 11 | 34 |
| Subject | Abiverd/Sunscar, BC billing, SEO client | TacticalMovement animation / weapon work |
| Overlap | none found on Abiverd topics | — |

Symlinking would have shadowed all 34 of Mac #2's memories. Nothing is destroyed
(the `.bak` keeps them) but the session would work blind on everything except the
map. **These sets must be MERGED, not replaced.**

Two further facts established 2026-09-10:

- Mac #1's iCloud account is `jasonteck@gmail.com`, iCloud Drive enabled,
  container `caught-up`. The `ClaudeMemory` folder exists there with 11 files.
- Mac #2 reported no `ClaudeMemory` folder and **no `.icloud` placeholder** —
  which means the folder was never advertised to that machine, not that it is
  merely un-downloaded. The likely cause is a **different Apple ID**. Check with
  `defaults read MobileMeAccounts | grep AccountID` on both.

### Correct procedure — merge

Transport the 11 files by any route (a tarball over AirDrop works and is
Apple-ID-independent). Then, on Mac #2:

1. Extract to a staging directory, never straight into `memory/`.
2. For each incoming `.md`: if no file of that name exists, copy it in. If one
   exists and the contents are identical, skip. If one exists and differs, KEEP
   the existing file and save the incoming one as `<name>.mac1.md` for review.
3. `MEMORY.md` collides on both machines — do not overwrite it. Append only the
   index lines that are not already present.
4. Verify the final count is 34 + (new files added), and that
   `~/.claude/projects/<key>/memory` is still a real directory.

Only set up the iCloud symlink afterwards, on the merged set, and only if both
Macs are confirmed on the same Apple ID. If they are not, use a small private git
repo for the memory folder instead — explicit pulls, no silent conflicts.

### 2. Git repo (most robust, explicit)

Best if both machines are often active. Make the memory folder its own small
private repo, commit after a session, pull before one. No silent conflicts —
git makes you resolve them.

### 3. One-time copy (simplest, no ongoing sync)

```
rsync -av ~/.claude/projects/-Users-jasonteck/memory/ \
  jasonteck@<other-mac>.local:~/.claude/projects/-Users-jasonteck/memory/
```

Requires Remote Login on the target (System Settings → General → Sharing).
Good for a one-way handover; memories written afterwards do not come back.

### If the second Mac's username differs

The project key changes with the home path. Check with:

```
ls ~/.claude/projects/
```

and put the memory folder under whatever key that machine actually uses.

## Also worth carrying

- `~/.claude/settings.json` (91 bytes) — small, easy to recreate, but copy it.
- `CLAUDE.md` files travel in the repo already.
- The MCP bridge is a per-machine editor thing; nothing to move. On the second
  Mac, launch the editor detached with `-ModelContextProtocolStartServer` per the
  root `CLAUDE.md`, and confirm `GET 127.0.0.1:8000/mcp` returns 405.

## First command on the second Mac

> Resume Abiverd map work. Read
> `Documentation/Maps/OperationSunscar/Planning/ABIVERD_RESUME_HANDOFF_2026-08-25.md`
> first — it has the bridge-script restore command, current state and the tooling
> traps. Then read `ABIVERD_GROUND_REALISM_AUDIT_2026-09-09.md` for the landscape
> findings. Then continue per `ABIVERD_BUILD_PLAN_V1.md` Sequence.

Note the `/tmp` restore step in the 08-25 handoff: `/tmp` is cleared nightly and
has taken the bridge transport with it twice. `bridge_scripts/` in git is the
master copy — restore from there, never rebuild from memory.
