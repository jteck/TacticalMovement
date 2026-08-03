"""Save exactly the reviewed 44-actor Old Town horizontal-surface finish pass."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarHorizontalSurfaceFinishV1"
EXPECTED_COUNT = 44


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
source_report = common.read_json(
    os.path.join(common.report_directory(config), "old_town_horizontal_surface_finish_v1.json")
)
if source_report.get("status") != "unsaved_horizontal_surface_finish_ready":
    raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_SAVE_REPORT_STATUS_REFUSED")
if source_report.get("actor_count") != EXPECTED_COUNT:
    raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_SAVE_REPORT_COUNT_REFUSED")

record_by_package = {record["package"]: record for record in source_report["records"]}
if len(record_by_package) != EXPECTED_COUNT:
    raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_SAVE_PACKAGE_SCOPE_REFUSED")
actors = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if PASS_TAG in common.actor_tags(actor)
    ],
    key=lambda actor: actor.get_actor_label(),
)
if len(actors) != EXPECTED_COUNT:
    raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_SAVE_ACTOR_COUNT_REFUSED count=%d" % len(actors))

packages = set()
for actor in actors:
    package = actor.get_package()
    record = record_by_package.get(package.get_name())
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    material_path = material.get_path_name() if material else ""
    if record is None or record["label"] != actor.get_actor_label():
        raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_SAVE_ACTOR_REFUSED " + actor.get_actor_label())
    if material_path != record["target_material"]:
        raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_SAVE_MATERIAL_REFUSED " + actor.get_actor_label())
    packages.add(package)

dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
expected_maps = sorted(record_by_package)
if dirty_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_HORIZONTAL_FINISH_SAVE_DIRTY_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )
if len(packages) != EXPECTED_COUNT or not unreal.EditorLoadingAndSavingUtils.save_packages(list(packages), True):
    raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_SAVE_FAILED")

remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_SAVE_DIRTY_AFTER %s" % "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_horizontal_surface_finish_saved",
    "context": context,
    "actor_count": len(actors),
    "saved_package_count": len(packages),
    "saved_packages": sorted(package.get_name() for package in packages),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_horizontal_surface_finish_v1.json", payload)
unreal.log("SUNSCAR_HORIZONTAL_FINISH_SAVE packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_HORIZONTAL_FINISH_SAVE", len(packages), report)
