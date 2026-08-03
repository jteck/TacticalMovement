"""One-shot runner used to reload the Landscape V2 preview implementation from disk."""

SCRIPT = "/Users/jasonteck/UnrealEngine/_worktrees/map-development/Content/Python/OperationSunscar/AutomationV1/old_town_landscape_v2_preview.py"

with open(SCRIPT, "r", encoding="utf-8") as handle:
    exec(compile(handle.read(), SCRIPT, "exec"), {"__file__": SCRIPT, "__name__": "__main__"})
