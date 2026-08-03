"""Save exactly the reviewed world-aligned facade assets and ten SS_017 actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarWorldAlignedFacadePrototypeV1"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/M_OT_WorldAlignedFacade"
INSTANCE_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_WorldAligned"
EXPECTED_LABELS = {
    "Core_SS_017_F1_E_Left",
    "Core_SS_017_F1_E_Lintel",
    "Core_SS_017_F1_E_Right",
    "Core_SS_017_F1_N_Left",
    "Core_SS_017_F1_N_Lintel",
    "Core_SS_017_F1_N_Right",
    "Core_SS_017_F1_S_Wall",
    "Core_SS_017_F1_W_Left",
    "Core_SS_017_F1_W_Lintel",
    "Core_SS_017_F1_W_Right",
}


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
master = common.load_asset_checked(config, MASTER_PATH)
instance = common.load_asset_checked(config, INSTANCE_PATH)
if instance.get_editor_property("parent") != master:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_SAVE_REFUSED parent_mismatch")

actors = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if PASS_TAG in common.actor_tags(actor)
    ],
    key=lambda actor: actor.get_actor_label(),
)
labels = {actor.get_actor_label() for actor in actors}
if labels != EXPECTED_LABELS:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_SAVE_REFUSED labels=%s" % "|".join(sorted(labels))
    )
for actor in actors:
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    if material != instance:
        raise RuntimeError(
            "SUNSCAR_WORLD_ALIGNED_SAVE_REFUSED material=" + actor.get_actor_label()
        )

actor_packages = {actor.get_package() for actor in actors}
asset_packages = {master.get_package(), instance.get_package()}
expected_content = {MASTER_PATH, INSTANCE_PATH}
expected_maps = {package.get_name() for package in actor_packages}
dirty_content = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content != expected_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_SAVE_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps)))
    )

packages = sorted(asset_packages | actor_packages, key=lambda package: package.get_name())
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_SAVE_DIRTY_AFTER %s" % "|".join(remaining)
    )

payload = {
    "schema_version": 1,
    "status": "exact_world_aligned_facade_scope_saved",
    "context": context,
    "site_id": "SS_017",
    "actor_count": len(actors),
    "material_assets": [MASTER_PATH, INSTANCE_PATH],
    "saved_packages": [package.get_name() for package in packages],
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(
    config, "old_town_save_world_aligned_facade_v1.json", payload
)
unreal.log(
    "SUNSCAR_WORLD_ALIGNED_SAVE packages=%d report=%s" % (len(packages), report)
)
print("SUNSCAR_WORLD_ALIGNED_SAVE", len(packages), report)
