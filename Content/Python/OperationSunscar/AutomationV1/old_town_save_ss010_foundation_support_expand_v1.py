"""Save exactly the expanded SS_010 support plinth package."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarSS010FoundationSupportV1"


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
source_report = common.read_json(
    os.path.join(common.report_directory(config), "old_town_ss010_foundation_support_expand_v1.json")
)
if source_report.get("status") != "unsaved_ss010_foundation_support_expanded":
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE_REPORT_REFUSED")
actors = [
    actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if PASS_TAG in common.actor_tags(actor)
]
if len(actors) != 1 or actors[0].get_actor_label() != source_report.get("label"):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE_ACTOR_REFUSED")
actor = actors[0]
package = actor.get_package()
if package.get_name() != source_report.get("actor_package"):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE_PACKAGE_REFUSED")
origin, extent = actor.get_actor_bounds(False)
actual = [origin.x, origin.y, origin.z, extent.x, extent.y, extent.z]
expected = source_report["target_origin_cm"] + source_report["target_extent_cm"]
if any(abs(a - b) > 0.1 for a, b in zip(actual, expected)):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE_BOUNDS_REFUSED")
dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if dirty_content or dirty_maps != [package.get_name()]:
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE_DIRTY_SCOPE_REFUSED")
if not unreal.EditorLoadingAndSavingUtils.save_packages([package], True):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE_DIRTY_AFTER %s" % "|".join(remaining))
payload = {
    "schema_version": 1,
    "status": "exact_ss010_foundation_support_expansion_saved",
    "context": context,
    "actor_count": 1,
    "saved_package_count": 1,
    "saved_package": package.get_name(),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_ss010_foundation_support_expand_v1.json", payload)
unreal.log("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE package=%s report=%s" % (package.get_name(), report))
print("SUNSCAR_SS010_SUPPORT_EXPAND_SAVE", package.get_name(), report)
