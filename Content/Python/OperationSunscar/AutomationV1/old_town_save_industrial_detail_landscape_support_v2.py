"""Save exactly the two final SS_014 Landscape support corrections."""

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
    os.path.join(common.report_directory(config), "old_town_industrial_detail_landscape_support_fix_v2.json")
)
if not source.get("apply_changes") or source.get("actor_count") != 2:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_SAVE_REFUSED source")
expected_names = set(source.get("dirty_map_packages", []))
if len(expected_names) != 2:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_SAVE_REFUSED count")

dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if dirty_content or {package.get_name() for package in dirty_maps} != expected_names:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_SAVE_REFUSED dirty_scope")
package_by_name = {package.get_name(): package for package in dirty_maps}
packages = [package_by_name[name] for name in sorted(expected_names)]
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_SAVE_FAILED")

remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_SAVE_DIRTY_AFTER")
payload = {
    "schema_version": 1,
    "status": "industrial_landscape_support_saved",
    "context": context,
    "saved_package_count": len(packages),
    "saved_packages": sorted(expected_names),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_industrial_detail_landscape_support_v2.json", payload)
unreal.log("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_SAVE packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_SAVE", len(packages), report)
