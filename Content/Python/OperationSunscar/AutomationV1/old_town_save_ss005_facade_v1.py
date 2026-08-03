"""Save exactly the 16 reviewed SS_005 exterior facade actor packages."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarFacadePrototypeV1"
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_Quixel.MI_OT_Stucco_Quixel"
TARGET_LABELS = [
    "Core_SS_005_F1_E_Left",
    "Core_SS_005_F1_E_Lintel",
    "Core_SS_005_F1_E_Right",
    "Core_SS_005_F1_N_Wall",
    "Core_SS_005_F1_S_Left",
    "Core_SS_005_F1_S_Lintel",
    "Core_SS_005_F1_S_Right",
    "Core_SS_005_F1_W_Wall",
    "Core_SS_005_F2_E_Wall",
    "Core_SS_005_F2_N_Wall",
    "Core_SS_005_F2_S_Wall",
    "Core_SS_005_F2_W_Wall",
    "SS_005_Parapet_E",
    "SS_005_Parapet_N",
    "SS_005_Parapet_S",
    "SS_005_Parapet_W",
]


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors_by_label = {
    actor.get_actor_label(): actor for actor in common.actor_subsystem().get_all_level_actors()
}
actors = []
for label in TARGET_LABELS:
    actor = actors_by_label.get(label)
    if actor is None:
        raise RuntimeError("SUNSCAR_SS005_FACADE_SAVE_REFUSED missing=" + label)
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    if material is None or material.get_path_name() != TARGET_PATH:
        raise RuntimeError("SUNSCAR_SS005_FACADE_SAVE_REFUSED material=" + label)
    if PASS_TAG not in common.actor_tags(actor):
        raise RuntimeError("SUNSCAR_SS005_FACADE_SAVE_REFUSED tag=" + label)
    actors.append(actor)

packages = {actor.get_package() for actor in actors}
target_names = {package.get_name() for package in packages}
dirty_content = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content or dirty_maps != target_names:
    raise RuntimeError(
        "SUNSCAR_SS005_FACADE_SAVE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps)))
    )
if not unreal.EditorLoadingAndSavingUtils.save_packages(list(packages), True):
    raise RuntimeError("SUNSCAR_SS005_FACADE_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
if remaining:
    raise RuntimeError("SUNSCAR_SS005_FACADE_SAVE_DIRTY_AFTER %s" % "|".join(remaining))
payload = {
    "schema_version": 1,
    "status": "exact_ss005_facade_packages_saved",
    "context": context,
    "actor_count": len(actors),
    "actor_labels": TARGET_LABELS,
    "saved_packages": sorted(target_names),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_ss005_facade_v1.json", payload)
unreal.log("SUNSCAR_SS005_FACADE_SAVE packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_SS005_FACADE_SAVE", len(packages), report)
