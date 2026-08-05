"""Diagnostic wrapper for the guarded Abiverd World Partition region load."""

import json
import os
import traceback

import unreal


target = "/Users/jasonteck/UnrealEngine/_worktrees/map-development/Content/Python/OperationSunscar/AutomationV1/abiverd_world_partition_load_region_v1.py"
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
diagnostic = os.path.join(report_root, "abiverd_world_partition_load_diagnostic_v1.json")
try:
    with open(target, "r", encoding="utf-8") as handle:
        source = handle.read()
    exec(compile(source, target, "exec"), {"__name__": "__main__", "__file__": target})
except Exception as exc:
    with open(diagnostic, "w", encoding="utf-8") as handle:
        json.dump(
            {"status": "failed", "exception": repr(exc), "traceback": traceback.format_exc()},
            handle,
            indent=2,
        )
        handle.write("\n")
    unreal.log_error("ABIVERD_WP_LOAD_DIAGNOSTIC " + repr(exc))
else:
    with open(diagnostic, "w", encoding="utf-8") as handle:
        json.dump({"status": "complete"}, handle, indent=2)
        handle.write("\n")
