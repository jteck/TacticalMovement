"""Save only the landscape material and five Landscape actor packages."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarLandscapeMaterialPassV1"
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Landscape/MI_OT_Landscape_Sandstone"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if PASS_TAG in common.actor_tags(actor)
    ],
    key=lambda actor: actor.get_actor_label(),
)
if len(actors) != 5:
    raise RuntimeError("SUNSCAR_LANDSCAPE_MATERIAL_SAVE_REFUSED actor_count=%d" % len(actors))
material = unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
if material is None:
    raise RuntimeError("SUNSCAR_LANDSCAPE_MATERIAL_SAVE_REFUSED missing_material")

actor_packages = {actor.get_package() for actor in actors}
material_package = material.get_package()
target_packages = actor_packages | {material_package}
target_names = {package.get_name() for package in target_packages}
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
dirty_names = {package.get_name() for package in dirty_content + dirty_maps}
unexpected = sorted(dirty_names - target_names)
missing = sorted(target_names - dirty_names)
if unexpected or missing:
    raise RuntimeError(
        "SUNSCAR_LANDSCAPE_MATERIAL_SAVE_REFUSED unexpected=%s missing=%s"
        % ("|".join(unexpected), "|".join(missing))
    )

if not unreal.EditorLoadingAndSavingUtils.save_packages(list(target_packages), True):
    raise RuntimeError("SUNSCAR_LANDSCAPE_MATERIAL_SAVE_FAILED")

remaining = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
    if package.get_name() in target_names
)
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
report = common.write_json_report(config, "old_town_save_landscape_material_v1.json", payload)
unreal.log(
    "SUNSCAR_LANDSCAPE_MATERIAL_SAVE packages=%d remaining=%d report=%s"
    % (len(target_packages), len(remaining), report)
)
print("SUNSCAR_LANDSCAPE_MATERIAL_SAVE", len(target_packages), report)
