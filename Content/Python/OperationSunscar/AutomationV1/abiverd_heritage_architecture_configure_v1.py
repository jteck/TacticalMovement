"""Configure the unsaved Abiverd architecture batch using the existing map master.

Reuses M_OT_QuixelOpaqueCompat, enables Nanite on the three visual meshes,
corrects linear texture settings, and assigns one map-owned material instance
per scan. Collision remains map-owned and is not generated on the scan meshes.
Nothing is saved and the current level is not modified.
"""

import json
import os
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ROOT = "/Game/Maps/Sunscar/Art/Heritage/Architecture"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Materials/M_OT_QuixelOpaqueCompat"

DEFINITIONS = (
    {
        "folder": ROOT + "/ArchStoneCarved08",
        "mesh_token": "_High",
        "material_name": "MI_ABV_ArchStoneCarved08",
    },
    {
        "folder": ROOT + "/WallModularSet04",
        "mesh_token": "_High",
        "material_name": "MI_ABV_WallModularSet04",
    },
    {
        "folder": ROOT + "/StructureStoneS06",
        "mesh_token": "_High",
        "material_name": "MI_ABV_StructureStoneS06",
    },
)


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_ARCH_CONFIG_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_ARCH_CONFIG_WRONG_LEVEL " + level_path)

dirty_before = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
unexpected_before = [name for name in dirty_before if not name.startswith(ROOT + "/")]
if unexpected_before:
    raise RuntimeError("ABIVERD_ARCH_CONFIG_UNEXPECTED_DIRTY_BEFORE " + repr(unexpected_before))

master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
if master is None or not isinstance(master, unreal.Material):
    raise RuntimeError("ABIVERD_ARCH_CONFIG_MASTER_MISSING " + MASTER_PATH)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
records = []
for definition in DEFINITIONS:
    paths = sorted(unreal.EditorAssetLibrary.list_assets(definition["folder"], recursive=False, include_folder=False))
    loaded = [unreal.EditorAssetLibrary.load_asset(path) for path in paths]
    meshes = [asset for asset in loaded if isinstance(asset, unreal.StaticMesh)]
    textures = [asset for asset in loaded if isinstance(asset, unreal.Texture2D)]
    if len(meshes) != 1 or len(textures) != 4:
        raise RuntimeError(
            "ABIVERD_ARCH_CONFIG_SCOPE %s meshes=%d textures=%d" % (definition["folder"], len(meshes), len(textures))
        )
    mesh = meshes[0]
    by_role = {}
    for texture in textures:
        name = texture.get_name().lower()
        if "basecolor" in name:
            by_role["BaseColor"] = texture
        elif "_normal" in name:
            by_role["Normal"] = texture
        elif "roughness" in name:
            by_role["Roughness"] = texture
        elif "_ao" in name:
            by_role["AO"] = texture
    if set(by_role) != {"BaseColor", "Normal", "Roughness", "AO"}:
        raise RuntimeError("ABIVERD_ARCH_CONFIG_TEXTURE_ROLES %s %s" % (definition["folder"], repr(by_role)))

    by_role["BaseColor"].modify()
    by_role["BaseColor"].set_editor_property("srgb", True)
    by_role["Normal"].modify()
    by_role["Normal"].set_editor_property("srgb", False)
    by_role["Normal"].set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    for role in ("Roughness", "AO"):
        by_role[role].modify()
        by_role[role].set_editor_property("srgb", False)
        by_role[role].set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)

    material_path = definition["folder"] + "/" + definition["material_name"]
    if unreal.EditorAssetLibrary.does_asset_exist(material_path):
        material = unreal.EditorAssetLibrary.load_asset(material_path)
        if not isinstance(material, unreal.MaterialInstanceConstant):
            raise RuntimeError("ABIVERD_ARCH_CONFIG_UNEXPECTED_EXISTING_MATERIAL " + material_path)
        existing_parent = material.get_editor_property("parent")
        if existing_parent is not None and existing_parent.get_path_name() != master.get_path_name():
            raise RuntimeError("ABIVERD_ARCH_CONFIG_UNEXPECTED_EXISTING_PARENT " + material_path)
    else:
        material = asset_tools.create_asset(
            definition["material_name"],
            definition["folder"],
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew(),
        )
    if material is None:
        raise RuntimeError("ABIVERD_ARCH_CONFIG_MATERIAL_CREATE_FAILED " + material_path)
    material.set_editor_property("parent", master)
    for parameter in ("BaseColor", "Normal", "Roughness"):
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
            material, parameter, by_role[parameter]
        )
    unreal.MaterialEditingLibrary.update_material_instance(material)

    mesh.modify()
    nanite_settings = mesh.get_editor_property("nanite_settings")
    nanite_settings.enabled = True
    mesh.set_editor_property("nanite_settings", nanite_settings)
    mesh.set_material(0, material)
    records.append(
        {
            "folder": definition["folder"],
            "mesh": mesh.get_path_name(),
            "material": material.get_path_name(),
            "master": MASTER_PATH,
            "base_color": by_role["BaseColor"].get_path_name(),
            "normal": by_role["Normal"].get_path_name(),
            "roughness": by_role["Roughness"].get_path_name(),
            "ao_imported_not_sampled": by_role["AO"].get_path_name(),
            "nanite_enabled": bool(mesh.get_editor_property("nanite_settings").enabled),
            "collision_policy": "visual_scan_only; map-owned simple collision during placement",
        }
    )

dirty_after = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
unexpected_after = [name for name in dirty_after if not name.startswith(ROOT + "/")]
if unexpected_after:
    raise RuntimeError("ABIVERD_ARCH_CONFIG_UNEXPECTED_DIRTY_AFTER " + repr(unexpected_after))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_heritage_architecture_configure_v1.json")
payload = {
    "schema_version": 1,
    "status": "configured_unsaved_complete",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "records": records,
    "dirty_packages_before": dirty_before,
    "dirty_packages_after": dirty_after,
    "unexpected_dirty_packages": unexpected_after,
    "level_changed": False,
    "level_saved": False,
    "asset_packages_saved": False,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_ARCH_CONFIG_COMPLETE assets=%d report=%s" % (len(records), report_path))
print("ABIVERD_ARCH_CONFIG_COMPLETE", len(records), report_path)
