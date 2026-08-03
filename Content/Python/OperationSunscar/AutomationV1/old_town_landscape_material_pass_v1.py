"""Dry-run-first Quixel sandstone material prototype for the Sunscar Landscape."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarLandscapeMaterialPassV1")
MASTER_PATH = "/Game/Fab/Materials/Standard/M_MS_Srf"
SOURCE_ROOT = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv"
BASE_COLOR_PATH = SOURCE_ROOT + "/Sandstone_Rocky_Ground_vmjjfiv_High_4K_BaseColor"
NORMAL_PATH = SOURCE_ROOT + "/Sandstone_Rocky_Ground_vmjjfiv_High_4K_Normal"
MASKS_PATH = "/Game/Fab/Textures/Standard/T_DefaultMasks"
HEIGHT_PATH = "/Game/Fab/Textures/Standard/T_DefaultDisplacement"
TARGET_FOLDER = "/Game/Maps/Sunscar/Art/Materials/Landscape"
TARGET_NAME = "MI_OT_Landscape_Sandstone"
TARGET_PATH = TARGET_FOLDER + "/" + TARGET_NAME

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if apply_requested and (dirty_content or dirty_maps):
    raise RuntimeError(
        "SUNSCAR_LANDSCAPE_MATERIAL_APPLY_REFUSED preexisting_dirty_content=%d preexisting_dirty_maps=%d"
        % (len(dirty_content), len(dirty_maps))
    )

master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
if master is None:
    raise RuntimeError("SUNSCAR_LANDSCAPE_MASTER_MISSING " + MASTER_PATH)
base_color = common.load_asset_checked(config, BASE_COLOR_PATH)
normal = common.load_asset_checked(config, NORMAL_PATH)
masks = unreal.EditorAssetLibrary.load_asset(MASKS_PATH)
height = unreal.EditorAssetLibrary.load_asset(HEIGHT_PATH)
if masks is None or height is None:
    raise RuntimeError("SUNSCAR_LANDSCAPE_FAB_DEFAULT_TEXTURE_MISSING")

actors = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if isinstance(actor, unreal.LandscapeProxy)
    ],
    key=lambda actor: actor.get_actor_label(),
)
labels = [actor.get_actor_label() for actor in actors]
expected_labels = [
    "LandscapeStreamingProxy_1_1_0",
    "LandscapeStreamingProxy_1_2_0",
    "LandscapeStreamingProxy_2_1_0",
    "LandscapeStreamingProxy_2_2_0",
    "Landscape_Sunscar",
]
if labels != expected_labels:
    raise RuntimeError("SUNSCAR_LANDSCAPE_MATERIAL_SCOPE_REFUSED labels=%s" % "|".join(labels))

records = []
for actor in actors:
    current = actor.get_editor_property("landscape_material")
    current_path = current.get_path_name() if current else ""
    if current_path not in ("", TARGET_PATH + "." + TARGET_NAME):
        raise RuntimeError(
            "SUNSCAR_LANDSCAPE_MATERIAL_UNEXPECTED_SOURCE %s %s"
            % (actor.get_actor_label(), current_path)
        )
    records.append({
        "label": actor.get_actor_label(),
        "source_material": current_path,
        "target_material": TARGET_PATH,
        "package": actor.get_package().get_name(),
    })

material = unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
created_material = False
if apply_requested:
    if material is None:
        unreal.EditorAssetLibrary.make_directory(TARGET_FOLDER)
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            TARGET_NAME,
            TARGET_FOLDER,
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew(),
        )
        created_material = True
    if material is None:
        raise RuntimeError("SUNSCAR_LANDSCAPE_MATERIAL_CREATE_FAILED " + TARGET_PATH)
    material.set_editor_property("parent", master)
    for parameter, texture in (
        ("BaseColorTexture", base_color),
        ("NormalTexture", normal),
        ("MetallicRoughnessTexture", masks),
        ("HeightTexture", height),
    ):
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
            material, parameter, texture
        )
    for parameter, value in (
        ("Tiling", 256.0),
        ("Normal Intensity", 0.65),
        ("Specular", 0.25),
        ("Min Roughness", 0.72),
        ("Max Roughness", 1.0),
        ("Saturation", 0.78),
        ("Brightness", 0.82),
        ("Contrast", 0.9),
        ("AO Strength", 0.8),
    ):
        unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
            material, parameter, value
        )
    unreal.MaterialEditingLibrary.update_material_instance(material)
    for actor, record in zip(actors, records):
        actor.modify()
        actor.set_editor_property("landscape_material", material)
        if PASS_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [PASS_TAG]
        applied = actor.get_editor_property("landscape_material")
        record["applied_material"] = applied.get_path_name() if applied else ""

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "material_path": TARGET_PATH,
    "material_created": created_material,
    "material_parent": MASTER_PATH,
    "source_textures": {
        "base_color": BASE_COLOR_PATH,
        "normal": NORMAL_PATH,
        "masks": MASKS_PATH,
        "height": HEIGHT_PATH,
    },
    "tiling": 256.0,
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_landscape_material_apply_preview_v1.json"
    if apply_requested
    else "old_town_landscape_material_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_LANDSCAPE_MATERIAL mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report)
)
print("SUNSCAR_LANDSCAPE_MATERIAL", len(records), report)
