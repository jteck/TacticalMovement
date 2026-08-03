"""Discard the four unsaved large-cabinet actors from the utility preview."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownUtilityEnclosuresV1"
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
actors = [
    actor for actor in common.actor_subsystem().get_all_level_actors()
    if TAG in common.actor_tags(actor) and "OT_UTIL_003" in common.actor_tags(actor)
]
labels = sorted(actor.get_actor_label() for actor in actors)
if len(actors) != 4:
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_DISCARD_SCOPE actors=%d" % len(actors))
if apply_requested:
    for actor in actors:
        if not common.actor_subsystem().destroy_actor(actor):
            raise RuntimeError("SUNSCAR_LARGE_UTILITY_DISCARD_FAILED " + actor.get_actor_label())
payload = {
    "schema_version": 1,
    "status": "discard_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(labels),
    "actor_labels": labels,
    "changes_made": apply_requested,
    "level_saved": False,
}
name = "old_town_discard_large_utility_preview_apply_v1.json" if apply_requested else "old_town_discard_large_utility_preview_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_LARGE_UTILITY_DISCARD mode=%s actors=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(labels), report))
print("SUNSCAR_LARGE_UTILITY_DISCARD", len(labels), report)
