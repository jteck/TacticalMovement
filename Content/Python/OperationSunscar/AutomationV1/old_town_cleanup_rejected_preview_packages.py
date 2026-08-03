"""Collect garbage after exact removal of unsaved rejected facade actors."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
remaining = [
    actor.get_actor_label()
    for actor in common.actor_subsystem().get_all_level_actors()
    if actor.get_actor_label().startswith("OT_DAMAGE_")
]
if remaining:
    raise RuntimeError("SUNSCAR_REJECTED_CLEANUP_REFUSED actors=" + " | ".join(remaining))
unreal.SystemLibrary.collect_garbage()
dirty_content = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
dirty_maps = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
payload = {
    "schema_version": 1, "status": "garbage_collection_complete", "context": context,
    "remaining_rejected_actor_count": 0,
    "dirty_content_packages_after": sorted(dirty_content),
    "dirty_map_packages_after": sorted(dirty_maps),
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_cleanup_rejected_preview_packages.json", payload)
unreal.log("SUNSCAR_REJECTED_CLEANUP dirty_content=%d dirty_maps=%d report=%s" % (len(dirty_content), len(dirty_maps), report))
print("SUNSCAR_REJECTED_CLEANUP", len(dirty_content), len(dirty_maps), report)
