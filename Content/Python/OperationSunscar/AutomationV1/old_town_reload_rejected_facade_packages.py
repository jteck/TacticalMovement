"""Reload exactly four dirty external-object packages left by rejected preview removal."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


EXPECTED_PACKAGES = 4
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
rejected = [actor.get_actor_label() for actor in common.actor_subsystem().get_all_level_actors() if actor.get_actor_label().startswith("OT_DAMAGE_")]
if rejected:
    raise RuntimeError("SUNSCAR_FACADE_RELOAD_REFUSED rejected_actors=" + " | ".join(rejected))
content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if content:
    raise RuntimeError("SUNSCAR_FACADE_RELOAD_REFUSED dirty_content=%d" % len(content))


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


names = sorted(package_name(package) for package in maps)
prefix = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"
if len(names) != EXPECTED_PACKAGES or any(not name.startswith(prefix) for name in names):
    raise RuntimeError("SUNSCAR_FACADE_RELOAD_REFUSED packages=" + " | ".join(names))
reloaded, error = unreal.EditorLoadingAndSavingUtils.reload_packages(
    maps, unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE
)
if not reloaded:
    raise RuntimeError("SUNSCAR_FACADE_RELOAD_FAILED error=%s" % error)
remaining = [
    package_name(package)
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package_name(package) in set(names)
]
restored_rejected = [actor.get_actor_label() for actor in common.actor_subsystem().get_all_level_actors() if actor.get_actor_label().startswith("OT_DAMAGE_")]
if remaining or restored_rejected:
    raise RuntimeError("SUNSCAR_FACADE_RELOAD_INCOMPLETE remaining=%s actors=%s" % (" | ".join(remaining), " | ".join(restored_rejected)))
payload = {
    "schema_version": 1, "status": "rejected_preview_packages_reloaded", "context": context,
    "reloaded_package_count": len(names), "reloaded_packages": names,
    "remaining_target_dirty_packages": remaining, "restored_rejected_actor_count": len(restored_rejected),
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_reload_rejected_facade_packages.json", payload)
unreal.log("SUNSCAR_FACADE_RELOAD packages=%d report=%s" % (len(names), report))
print("SUNSCAR_FACADE_RELOAD", len(names), report)
