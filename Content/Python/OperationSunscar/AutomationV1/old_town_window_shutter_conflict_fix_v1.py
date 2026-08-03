"""Dry-run-first removal of the one Detention shutter that conflicts with a door."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownWindowShutterV1"
TARGET_LABEL = "OT_SHUTTER_Detention_F1_Win_01_R"
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
actor_system = common.actor_subsystem()
targets = [actor for actor in actor_system.get_all_level_actors() if TAG in common.actor_tags(actor)]
matches = [actor for actor in targets if actor.get_actor_label() == TARGET_LABEL]
if len(targets) != 20 or len(matches) != 1:
    raise RuntimeError("SUNSCAR_WINDOW_SHUTTER_FIX_SCOPE actors=%d matches=%d" % (len(targets), len(matches)))

removed = []
if apply_requested:
    if not actor_system.destroy_actor(matches[0]):
        raise RuntimeError("SUNSCAR_WINDOW_SHUTTER_FIX_DESTROY_FAILED")
    removed.append(TARGET_LABEL)

payload = {
    "schema_version": 1,
    "status": "conflict_fix_unsaved_complete" if apply_requested else "conflict_fix_dry_run_complete",
    "context": context,
    "target_label": TARGET_LABEL,
    "reason": "doorway_overlap_with_Detention_Door_12",
    "removed_actor_count": len(removed),
    "removed_actor_labels": removed,
    "changes_made": bool(removed),
    "level_saved": False,
}
name = "old_town_window_shutter_conflict_fix_apply_v1.json" if apply_requested else "old_town_window_shutter_conflict_fix_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_WINDOW_SHUTTER_FIX mode=%s removed=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(removed), report))
print("SUNSCAR_WINDOW_SHUTTER_FIX", len(removed), report)
