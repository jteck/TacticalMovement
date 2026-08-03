"""Save exactly the persistent NoCollision changes for 460 Old Town decoration actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
source = common.read_json(
    os.path.join(common.report_directory(config), "old_town_persistent_decorative_collision_v1.json")
)
if not source.get("apply_changes") or source.get("target_package_count") != 460:
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_SAVE_REFUSED source_report")
if source.get("no_collision_after_count") != 460:
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_SAVE_REFUSED collision_count")

expected_names = set(source.get("dirty_map_packages", []))
if len(expected_names) != 460:
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_SAVE_REFUSED package_count")
if any(
    not name.startswith("/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/")
    for name in expected_names
):
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_SAVE_REFUSED package_prefix")

dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
dirty_content_names = {package.get_name() for package in dirty_content}
dirty_map_names = {package.get_name() for package in dirty_maps}
if dirty_content_names or dirty_map_names != expected_names:
    raise RuntimeError(
        "SUNSCAR_PERSISTENT_COLLISION_SAVE_REFUSED content=%d maps=%d"
        % (len(dirty_content_names), len(dirty_map_names))
    )

package_by_name = {package.get_name(): package for package in dirty_maps}
packages = [package_by_name[name] for name in sorted(expected_names)]
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_SAVE_FAILED")

remaining_content = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
remaining_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if remaining_content or remaining_maps:
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_SAVE_DIRTY_AFTER")

payload = {
    "schema_version": 1,
    "status": "persistent_decorative_collision_saved",
    "context": context,
    "saved_package_count": len(packages),
    "saved_packages": sorted(expected_names),
    "dirty_content_packages_after": remaining_content,
    "dirty_map_packages_after": remaining_maps,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_persistent_decorative_collision_v1.json", payload)
unreal.log("SUNSCAR_PERSISTENT_COLLISION_SAVE packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_PERSISTENT_COLLISION_SAVE", len(packages), report)
