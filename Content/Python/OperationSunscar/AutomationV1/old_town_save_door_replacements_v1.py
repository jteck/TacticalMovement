"""Save exactly the 16 existing actor packages used for door replacement."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownDoorReplacementV1"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = [actor for actor in common.actor_subsystem().get_all_level_actors() if TAG in common.actor_tags(actor)]
if len(actors) != 16:
    raise RuntimeError("SUNSCAR_DOOR_REPLACE_SAVE_REFUSED actor_count=%d" % len(actors))
target_packages = {actor.get_package() for actor in actors}
target_names = {package.get_name() for package in target_packages}
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
dirty_names = {package.get_name() for package in dirty_maps}
unexpected = sorted(dirty_names - target_names)
missing = sorted(target_names - dirty_names)
if dirty_content or unexpected or missing:
    raise RuntimeError(
        "SUNSCAR_DOOR_REPLACE_SAVE_REFUSED content=%d unexpected=%s missing=%s"
        % (len(dirty_content), "|".join(unexpected), "|".join(missing))
    )
if not unreal.EditorLoadingAndSavingUtils.save_packages(list(target_packages), True):
    raise RuntimeError("SUNSCAR_DOOR_REPLACE_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package.get_name() in target_names
)
if remaining:
    raise RuntimeError("SUNSCAR_DOOR_REPLACE_SAVE_INCOMPLETE " + " | ".join(remaining))
payload = {
    "schema_version": 1,
    "status": "exact_packages_saved",
    "context": context,
    "actor_count": len(actors),
    "package_count": len(target_packages),
    "saved_packages": sorted(target_names),
    "remaining_target_dirty_packages": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_door_replacements_v1.json", payload)
unreal.log("SUNSCAR_DOOR_REPLACE_SAVE packages=%d remaining=%d report=%s" % (len(target_packages), len(remaining), report))
print("SUNSCAR_DOOR_REPLACE_SAVE", len(target_packages), report)
