"""Read-only preflight for adding an Abiverd meadow layer to the saved Landscape material."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_PROJECT_SUFFIX = "/UnrealEngine/_worktrees/map-development"
TARGET_MATERIAL = "/Game/Maps/Sunscar/Art/Materials/LandscapeV2/M_OT_Landscape_Performance"
TEXTURES = {
    "grass_base": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/WildGrassGround/Wild_Grass_xbreagf_4K_BaseColor",
    "grass_normal": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/WildGrassGround/Wild_Grass_xbreagf_4K_Normal",
    "grass_roughness": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/WildGrassGround/Wild_Grass_xbreagf_4K_Roughness",
    "grass_ao": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/WildGrassGround/Wild_Grass_xbreagf_4K_AO",
    "soil_base": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/DryTrampledSoil/Dry_Trampled_Soil_wcivbfb_4K_BaseColor",
    "soil_normal": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/DryTrampledSoil/Dry_Trampled_Soil_wcivbfb_4K_Normal",
    "soil_roughness": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/DryTrampledSoil/Dry_Trampled_Soil_wcivbfb_4K_Roughness",
    "soil_ao": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/DryTrampledSoil/Dry_Trampled_Soil_wcivbfb_4K_AO",
}

project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_PROJECT_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_MEADOW_PREFLIGHT_CONTEXT")

dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if dirty:
    raise RuntimeError("ABIVERD_MEADOW_PREFLIGHT_DIRTY " + "|".join(dirty))

material = unreal.EditorAssetLibrary.load_asset(TARGET_MATERIAL)
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_MEADOW_PREFLIGHT_MATERIAL_MISSING")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
landscape_rows = []
for actor in landscapes:
    assigned = actor.get_editor_property("landscape_material")
    landscape_rows.append(
        {
            "label": actor.get_actor_label(),
            "package": actor.get_package().get_name(),
            "material": assigned.get_path_name() if assigned else "",
            "tags": [str(tag) for tag in actor.tags],
        }
    )

texture_rows = {}
for key, asset_path in TEXTURES.items():
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not isinstance(asset, unreal.Texture2D):
        raise RuntimeError("ABIVERD_MEADOW_PREFLIGHT_TEXTURE_MISSING " + asset_path)
    texture_rows[key] = {
        "path": asset.get_path_name(),
        "size_x": asset.blueprint_get_size_x(),
        "size_y": asset.blueprint_get_size_y(),
        "srgb": bool(asset.get_editor_property("srgb")),
        "compression": str(asset.get_editor_property("compression_settings")),
    }

expressions = list(unreal.MaterialEditingLibrary.get_material_expressions(material))
parameters = []
for item in expressions:
    try:
        parameter_name = str(item.get_editor_property("parameter_name"))
    except Exception:
        continue
    if parameter_name and parameter_name != "None":
        parameters.append(parameter_name)

layer_info_assets = []
for asset_path in unreal.EditorAssetLibrary.list_assets("/Game/Maps/Sunscar", recursive=True, include_folder=False):
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if isinstance(asset, unreal.LandscapeLayerInfoObject):
        layer_info_assets.append(asset.get_path_name())

payload = {
    "schema_version": 1,
    "status": "read_only_meadow_preflight_complete",
    "project_directory": project_directory,
    "level": level_path,
    "landscape_material": material.get_path_name(),
    "material_expression_count": len(expressions),
    "material_parameters": sorted(set(parameters)),
    "landscape_actor_count": len(landscapes),
    "landscapes": landscape_rows,
    "textures": texture_rows,
    "existing_layer_info_assets": sorted(layer_info_assets),
    "dirty_packages": dirty,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", "abiverd_landscape_meadow_preflight_v1.json"
)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_MEADOW_PREFLIGHT landscapes=%d expressions=%d" % (len(landscapes), len(expressions)))
print("ABIVERD_MEADOW_PREFLIGHT", report_path)
