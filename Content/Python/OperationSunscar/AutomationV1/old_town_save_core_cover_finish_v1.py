"""Save exactly the reviewed 39-actor Old Town core-cover finish pass."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarCoreCoverFinishV1"
EXPECTED_COUNT = 39


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
source_report = common.read_json(os.path.join(common.report_directory(config), "old_town_core_cover_finish_v1.json"))
if source_report.get("status") != "unsaved_core_cover_finish_ready" or source_report.get("actor_count") != EXPECTED_COUNT:
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_REPORT_REFUSED")
record_by_package = {record["package"]: record for record in source_report["records"]}
actors = [actor for actor in common.actor_subsystem().get_all_level_actors() if PASS_TAG in common.actor_tags(actor)]
if len(actors) != EXPECTED_COUNT or len(record_by_package) != EXPECTED_COUNT:
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_SCOPE_REFUSED actors=%d packages=%d" % (len(actors), len(record_by_package)))
packages = set()
for actor in actors:
    package = actor.get_package()
    record = record_by_package.get(package.get_name())
    if record is None or record["label"] != actor.get_actor_label():
        raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_ACTOR_REFUSED " + actor.get_actor_label())
    component = actor.static_mesh_component
    if record["kind"] == "new_visual":
        if common.actor_mesh_path(actor) != record["target_mesh"] or str(component.get_collision_enabled()) != str(unreal.CollisionEnabled.NO_COLLISION):
            raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_VISUAL_REFUSED " + actor.get_actor_label())
    elif record["treatment"].startswith("hidden_"):
        if bool(component.get_editor_property("visible")):
            raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_HIDDEN_REFUSED " + actor.get_actor_label())
    else:
        material = component.get_material(0)
        if material is None or material.get_path_name() != record["target_material"]:
            raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_MATERIAL_REFUSED " + actor.get_actor_label())
    packages.add(package)
dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if dirty_content or dirty_maps != sorted(record_by_package):
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_DIRTY_SCOPE_REFUSED")
if len(packages) != EXPECTED_COUNT or not unreal.EditorLoadingAndSavingUtils.save_packages(list(packages), True):
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SAVE_DIRTY_AFTER %s" % "|".join(remaining))
payload = {
    "schema_version": 1,
    "status": "exact_core_cover_finish_saved",
    "context": context,
    "actor_count": len(actors),
    "saved_package_count": len(packages),
    "saved_packages": sorted(package.get_name() for package in packages),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_core_cover_finish_v1.json", payload)
unreal.log("SUNSCAR_CORE_COVER_FINISH_SAVE packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_CORE_COVER_FINISH_SAVE", len(packages), report)
