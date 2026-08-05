"""Stage Field Poppy and Wild Grass as optimized UE 5.8 foliage assets.

This script imports eight source variations per plant, assembles LOD0-LOD3
into each final Static Mesh, uses Epic's M_MS_Foliage master, disables Nanite
and collision, and leaves every new package unsaved for a separate audit.
It does not place foliage or modify the current level.
"""

import json
import os
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ROOT = "/Game/Maps/Sunscar/Art/Heritage/Foliage"
MASTER_PATH = "/Game/Fab/Materials/Standard/M_MS_Foliage"
REPORT_NAME = "abiverd_heritage_foliage_stage_import_v1.json"

PLANTS = (
    {
        "record_id": "ABV_ASSET_001",
        "label": "Field Poppy",
        "slug": "FieldPoppy",
        "source_root": "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Field_Poppy-66cb2706/fbx/high/field_poppy_vmcobd0ja_hi_extracted",
        "mesh_prefix": "Field_Poppy_vmcobd0ja_High_vmcobd0ja",
        "texture_prefix": "Field_Poppy_vmcobd0ja_High_4K",
        "generated_mask": "/private/tmp/T_FieldPoppy_Mask.png",
        "wind_strength": 0.08,
    },
    {
        "record_id": "ABV_ASSET_002",
        "label": "Wild Grass",
        "slug": "WildGrass",
        "source_root": "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Wild_Grass-50d9a417/fbx/high/wild_grass_vlkhcbxia_hig_extracted",
        "mesh_prefix": "Wild_Grass_vlkhcbxia_High_vlkhcbxia",
        "texture_prefix": "Wild_Grass_vlkhcbxia_High_4K",
        "generated_mask": "/private/tmp/T_WildGrass_Mask.png",
        "wind_strength": 0.12,
    },
)

VARIATIONS = tuple("ABCDEFGH")
LOD_SCREEN_SIZES = [1.0, 0.48, 0.20, 0.07]


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


def import_texture(asset_tools, source, destination, destination_name):
    existing_path = destination + "/" + destination_name
    if unreal.EditorAssetLibrary.does_asset_exist(existing_path):
        texture = unreal.EditorAssetLibrary.load_asset(existing_path)
        if not isinstance(texture, unreal.Texture2D):
            raise RuntimeError("ABIVERD_FOLIAGE_TEXTURE_EXISTING_TYPE " + existing_path)
        return texture, texture.get_path_name()
    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = destination
    task.destination_name = destination_name
    task.automated = True
    task.replace_existing = False
    task.save = False
    asset_tools.import_asset_tasks([task])
    imported = [str(value) for value in task.imported_object_paths]
    if len(imported) != 1:
        raise RuntimeError("ABIVERD_FOLIAGE_TEXTURE_IMPORT_RESULT %s %s" % (destination_name, repr(imported)))
    texture = unreal.EditorAssetLibrary.load_asset(imported[0])
    if not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("ABIVERD_FOLIAGE_TEXTURE_IMPORT_TYPE " + imported[0])
    return texture, imported[0]


def import_mesh_lod0(asset_tools, source, destination, destination_name):
    existing_path = destination + "/" + destination_name
    if unreal.EditorAssetLibrary.does_asset_exist(existing_path):
        mesh = unreal.EditorAssetLibrary.load_asset(existing_path)
        if not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError("ABIVERD_FOLIAGE_MESH_EXISTING_TYPE " + existing_path)
        return mesh, mesh.get_path_name()
    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = destination
    task.destination_name = destination_name
    task.automated = True
    task.replace_existing = False
    task.save = False
    options = unreal.FbxImportUI()
    options.import_as_skeletal = False
    options.import_mesh = True
    options.import_materials = False
    options.import_textures = False
    options.automated_import_should_detect_type = False
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    options.static_mesh_import_data.combine_meshes = True
    options.static_mesh_import_data.generate_lightmap_u_vs = False
    options.static_mesh_import_data.auto_generate_collision = False
    task.options = options
    asset_tools.import_asset_tasks([task])
    imported = [str(value) for value in task.imported_object_paths]
    if len(imported) != 1:
        raise RuntimeError("ABIVERD_FOLIAGE_MESH_IMPORT_RESULT %s %s" % (destination_name, repr(imported)))
    mesh = unreal.EditorAssetLibrary.load_asset(imported[0])
    if not isinstance(mesh, unreal.StaticMesh):
        raise RuntimeError("ABIVERD_FOLIAGE_MESH_IMPORT_TYPE " + imported[0])
    return mesh, imported[0]


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT:
    raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_WRONG_PROJECT " + project_name)
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_WRONG_DIRECTORY " + project_directory)
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_WRONG_LEVEL " + level_path)

dirty_before = dirty_packages()
unexpected_dirty_before = [name for name in dirty_before if not name.startswith(ROOT + "/")]
if unexpected_dirty_before:
    raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_PREEXISTING_UNEXPECTED_DIRTY " + repr(unexpected_dirty_before))

master = unreal.load_asset(MASTER_PATH)
if not isinstance(master, unreal.Material):
    raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_MASTER_MISSING " + MASTER_PATH)

for plant in PLANTS:
    destination = ROOT + "/" + plant["slug"]
    if not os.path.isdir(plant["source_root"]):
        raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_SOURCE_MISSING " + plant["source_root"])
    if not os.path.isfile(plant["generated_mask"]):
        raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_MASK_MISSING " + plant["generated_mask"])
    if unreal.EditorAssetLibrary.does_directory_exist(destination):
        existing = unreal.EditorAssetLibrary.list_assets(destination, recursive=True)
        allowed_names = {
            destination + "/T_%s_BaseColor.T_%s_BaseColor" % (plant["slug"], plant["slug"]),
            destination + "/T_%s_Normal.T_%s_Normal" % (plant["slug"], plant["slug"]),
            destination + "/T_%s_Mask.T_%s_Mask" % (plant["slug"], plant["slug"]),
            destination + "/MI_%s.MI_%s" % (plant["slug"], plant["slug"]),
        } | {
            destination + "/SM_%s_Var%s.SM_%s_Var%s" % (plant["slug"], variation, plant["slug"], variation)
            for variation in VARIATIONS
        }
        unexpected_existing = [path for path in existing if str(path) not in allowed_names]
        if unexpected_existing:
            raise RuntimeError(
                "ABIVERD_FOLIAGE_IMPORT_DESTINATION_UNEXPECTED %s %s"
                % (destination, repr(unexpected_existing))
            )
    for variation in VARIATIONS:
        for lod_index in range(4):
            source = os.path.join(
                plant["source_root"],
                "%s_Var%s_LOD%d.fbx" % (plant["mesh_prefix"], variation, lod_index),
            )
            if not os.path.isfile(source):
                raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_LOD_SOURCE_MISSING " + source)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
static_mesh_subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
records = []

for plant in PLANTS:
    destination = ROOT + "/" + plant["slug"]
    base_source = os.path.join(plant["source_root"], plant["texture_prefix"] + "_BaseColor.jpg")
    normal_source = os.path.join(plant["source_root"], plant["texture_prefix"] + "_Normal.jpg")
    for source in (base_source, normal_source, plant["generated_mask"]):
        if not os.path.isfile(source):
            raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_TEXTURE_SOURCE_MISSING " + source)

    base, base_path = import_texture(asset_tools, base_source, destination, "T_%s_BaseColor" % plant["slug"])
    normal, normal_path = import_texture(asset_tools, normal_source, destination, "T_%s_Normal" % plant["slug"])
    mask, mask_path = import_texture(asset_tools, plant["generated_mask"], destination, "T_%s_Mask" % plant["slug"])

    base.modify()
    base.set_editor_property("srgb", True)
    base.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
    base.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_WORLD)
    base.set_editor_property("virtual_texture_streaming", False)
    normal.modify()
    normal.set_editor_property("srgb", False)
    normal.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    normal.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_WORLD_NORMAL_MAP)
    normal.set_editor_property("virtual_texture_streaming", False)
    mask.modify()
    mask.set_editor_property("srgb", False)
    mask.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    mask.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_WORLD)
    mask.set_editor_property("virtual_texture_streaming", False)

    material_name = "MI_%s" % plant["slug"]
    material_path = destination + "/" + material_name
    material = unreal.EditorAssetLibrary.load_asset(material_path)
    if not material:
        material = asset_tools.create_asset(
            material_name,
            destination,
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew(),
        )
    if not material:
        raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_MATERIAL_CREATE_FAILED " + material_name)
    material.set_editor_property("parent", master)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, "BaseColorTexture", base)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, "NormalTexture", normal)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, "Mask", mask)
    switch_values = {
        "disable Wind Animation": False,
        "use simplified Wind": True,
        "primary Animation": True,
        "secondary Animation": False,
        "use Distance Based WPO Fade": True,
        "Use Distance Based Opacity": False,
        "add Translucency Effect": True,
        "use Color Variations": False,
    }
    for parameter, value in switch_values.items():
        unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(
            material, parameter, value
        )
    scalar_values = {
        "Local Primary Wind Strength": plant["wind_strength"],
        "Local Secondary Wind Strength": 0.0,
        "WPO Fade Disable Distance": 5000.0,
        "Opacity Strength": 1.0,
    }
    for parameter, value in scalar_values.items():
        unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
            material, parameter, value
        )
    unreal.MaterialEditingLibrary.update_material_instance(material)

    mesh_records = []
    for variation in VARIATIONS:
        mesh_name = "SM_%s_Var%s" % (plant["slug"], variation)
        lod0_source = os.path.join(
            plant["source_root"],
            "%s_Var%s_LOD0.fbx" % (plant["mesh_prefix"], variation),
        )
        mesh, mesh_path = import_mesh_lod0(asset_tools, lod0_source, destination, mesh_name)
        existing_lod_count = static_mesh_subsystem.get_lod_count(mesh)
        for lod_index in range(max(1, existing_lod_count), 4):
            lod_source = os.path.join(
                plant["source_root"],
                "%s_Var%s_LOD%d.fbx" % (plant["mesh_prefix"], variation, lod_index),
            )
            result_index = static_mesh_subsystem.import_lod(mesh, lod_index, lod_source)
            if result_index != lod_index:
                raise RuntimeError(
                    "ABIVERD_FOLIAGE_IMPORT_LOD_FAILED %s lod=%d result=%s"
                    % (mesh_path, lod_index, str(result_index))
                )
        if not static_mesh_subsystem.set_lod_screen_sizes(mesh, LOD_SCREEN_SIZES):
            raise RuntimeError("ABIVERD_FOLIAGE_IMPORT_SCREEN_SIZES_FAILED " + mesh_path)
        static_mesh_subsystem.remove_collisions(mesh)
        nanite = mesh.get_editor_property("nanite_settings")
        nanite.enabled = False
        mesh.set_editor_property("nanite_settings", nanite)
        for slot_index in range(len(mesh.get_editor_property("static_materials"))):
            mesh.set_material(slot_index, material)
        mesh.modify()
        bounds = mesh.get_bounds()
        mesh_records.append(
            {
                "variation": variation,
                "path": mesh_path,
                "lod_sources": [
                    os.path.join(
                        plant["source_root"],
                        "%s_Var%s_LOD%d.fbx" % (plant["mesh_prefix"], variation, lod_index),
                    ) for lod_index in range(4)
                ],
                "bounds_cm": {
                    "origin": [bounds.origin.x, bounds.origin.y, bounds.origin.z],
                    "extent": [bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z],
                },
            }
        )

    records.append(
        {
            "record_id": plant["record_id"],
            "label": plant["label"],
            "destination": destination,
            "master_material": MASTER_PATH,
            "material": material.get_path_name(),
            "textures": {
                "base_color": base_path,
                "normal": normal_path,
                "mask": mask_path,
            },
            "mask_channel_packing": {
                "R": "Opacity",
                "G": "Roughness",
                "B": "Translucency",
            },
            "meshes": mesh_records,
            "lod_screen_sizes": LOD_SCREEN_SIZES,
            "nanite_enabled": False,
            "collision": "none",
        }
    )

dirty_after = dirty_packages()
unexpected_dirty = [name for name in dirty_after if not name.startswith(ROOT + "/")]
expected_count = len(PLANTS) * (3 + 1 + len(VARIATIONS))
if len(dirty_after) != expected_count or unexpected_dirty:
    raise RuntimeError(
        "ABIVERD_FOLIAGE_IMPORT_DIRTY_SCOPE expected=%d actual=%d unexpected=%s"
        % (expected_count, len(dirty_after), repr(unexpected_dirty))
    )

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
payload = {
    "schema_version": 1,
    "status": "foliage_stage_import_unsaved_complete",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "destination_root": ROOT,
    "records": records,
    "dirty_packages_before": dirty_before,
    "dirty_packages_after": dirty_after,
    "unexpected_dirty_packages": unexpected_dirty,
    "expected_asset_count": expected_count,
    "level_changed": False,
    "level_saved": False,
    "asset_packages_saved": False,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_FOLIAGE_IMPORT_COMPLETE assets=%d report=%s" % (expected_count, report_path))
print("ABIVERD_FOLIAGE_IMPORT_COMPLETE", report_path)
