"""Save exactly the reviewed SS_010 west support plinth actor package."""

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
    os.path.join(common.report_directory(config), "old_town_ss010_foundation_support_v1.json")
)
if source_report.get("status") != "unsaved_ss010_foundation_support_ready":
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_SAVE_REPORT_STATUS_REFUSED")

actors = [
    actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if PASS_TAG in common.actor_tags(actor)
]
if len(actors) != 1 or actors[0].get_actor_label() != source_report.get("label"):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_SAVE_ACTOR_REFUSED count=%d" % len(actors))
actor = actors[0]
actor_package = actor.get_package()
if actor_package.get_name() != source_report.get("actor_package"):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_SAVE_PACKAGE_REFUSED")
component = getattr(actor, "static_mesh_component", None)
material = component.get_material(0) if component else None
if material is None or material.get_path_name() != source_report.get("material"):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_SAVE_MATERIAL_REFUSED")
origin, extent = actor.get_actor_bounds(False)
expected_origin = source_report["location_cm"]
expected_extent = source_report["extent_cm"]
actual = [origin.x, origin.y, origin.z, extent.x, extent.y, extent.z]
expected = expected_origin + expected_extent
if any(abs(a - b) > 0.1 for a, b in zip(actual, expected)):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_SAVE_BOUNDS_REFUSED")

dirty_content = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_content or dirty_maps != sorted(source_report.get("dirty_map_packages", [])):
    raise RuntimeError(
        "SUNSCAR_SS010_SUPPORT_SAVE_DIRTY_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )
if not unreal.EditorLoadingAndSavingUtils.save_packages([actor_package], True):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_SAVE_FAILED")

remaining_content = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
remaining_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
expected_remaining = sorted(
    package for package in source_report["dirty_map_packages"] if package != actor_package.get_name()
)
if remaining_content or remaining_maps != expected_remaining or len(remaining_maps) != 44:
    raise RuntimeError(
        "SUNSCAR_SS010_SUPPORT_SAVE_DIRTY_AFTER_REFUSED content=%s maps=%s"
        % ("|".join(remaining_content), "|".join(remaining_maps))
    )

payload = {
    "schema_version": 1,
    "status": "exact_ss010_foundation_support_saved",
    "context": context,
    "actor_count": 1,
    "saved_package_count": 1,
    "saved_package": actor_package.get_name(),
    "remaining_dirty_map_packages": remaining_maps,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_ss010_foundation_support_v1.json", payload)
unreal.log("SUNSCAR_SS010_SUPPORT_SAVE package=%s report=%s" % (actor_package.get_name(), report))
print("SUNSCAR_SS010_SUPPORT_SAVE", actor_package.get_name(), report)
