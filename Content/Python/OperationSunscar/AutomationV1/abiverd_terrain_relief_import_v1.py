"""Dry-run-first import of the reversible Abiverd Terrain Relief V1 heightmap.

Apply mode saves only the map-owned source texture/material, then imports the
heightmap as an *unsaved* Landscape preview. A separate audited save step is
required after foundation and visual checks.
"""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
SOURCE_FILE = (
    "/Users/jasonteck/UnrealEngine/_worktrees/map-development/Documentation/Maps/"
    "OperationSunscar/Source/Heightmaps/Abiverd_TerrainReliefV1_RG16_2017.png"
)
TARGET_FOLDER = "/Game/Maps/Sunscar/Art/Terrain/ReliefV1"
TEXTURE_PATH = TARGET_FOLDER + "/T_ABV_TerrainReliefV1_RG16_2017"
MATERIAL_PATH = TARGET_FOLDER + "/M_ABV_TerrainReliefV1_RG16Import"
LANDSCAPE_BOX = unreal.Box(
    min=unreal.Vector(-130000.0, -130000.0, -100000.0),
    max=unreal.Vector(130000.0, 130000.0, 100000.0),
)
REPORT_NAME = (
    "abiverd_terrain_relief_rg16_import_apply_preview_v1.json"
    if APPLY_CHANGES else "abiverd_terrain_relief_import_dry_run_v1.json"
)


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


def write_report(payload):
    report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
    os.makedirs(report_root, exist_ok=True)
    path = os.path.join(report_root, REPORT_NAME)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return path


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_CONTEXT")
if dirty_packages():
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_DIRTY_BEFORE " + "|".join(dirty_packages()))
if not os.path.isfile(SOURCE_FILE):
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_SOURCE")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
parent = next(
    actor
    for actor in actors
    if isinstance(actor, unreal.Landscape) and actor.get_actor_label() == "Landscape_Sunscar"
)
edit_layers = list(parent.get_edit_layers_bp())
if len(edit_layers) != 1 or str(edit_layers[0].get_name_bp()) != "Layer":
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_LAYER_SCOPE")

if not APPLY_CHANGES:
    path = write_report(
        {
            "schema_version": 1,
            "status": "terrain_relief_import_dry_run_complete",
            "source_file": SOURCE_FILE,
            "source_size_bytes": os.path.getsize(SOURCE_FILE),
            "target_texture": TEXTURE_PATH,
            "target_material": MATERIAL_PATH,
            "landscape": parent.get_path_name(),
            "edit_layer_index": 0,
            "edit_layer_name": str(edit_layers[0].get_name_bp()),
            "planned_render_target": {"resolution": [2017, 2017], "format": "RTF_RGBA8", "height_from_rg": True},
            "height_import_saved": False,
            "dirty_after": dirty_packages(),
        }
    )
    unreal.log("ABIVERD_TERRAIN_RELIEF_IMPORT_DRY_RUN_PASS")
    print("ABIVERD_TERRAIN_RELIEF_IMPORT_DRY_RUN_PASS", path)
    raise SystemExit

# Load and pin all 16 Landscape proxies so the 2017x2017 edit-layer merge is complete.
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(LANDSCAPE_BOX))
landscape_descriptors = [
    descriptor for descriptor in descriptors if str(descriptor.label).startswith("LandscapeStreamingProxy_")
]
if len(landscape_descriptors) != 16:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_PROXY_DESCRIPTORS %d" % len(landscape_descriptors))
unreal.WorldPartitionBlueprintLibrary.load_actors([descriptor.guid for descriptor in landscape_descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([descriptor.guid for descriptor in landscape_descriptors])

unreal.EditorAssetLibrary.make_directory(TARGET_FOLDER)
texture = unreal.EditorAssetLibrary.load_asset(TEXTURE_PATH)
texture_existed = texture is not None
created_assets = []
task = unreal.AssetImportTask()
task.set_editor_properties(
    {
        "filename": SOURCE_FILE,
        "destination_path": TARGET_FOLDER,
        "destination_name": "T_ABV_TerrainReliefV1_RG16_2017",
        "automated": True,
        "replace_existing": texture_existed,
        "replace_existing_settings": texture_existed,
        "save": False,
    }
)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
texture = unreal.EditorAssetLibrary.load_asset(TEXTURE_PATH)
if not texture_existed:
    created_assets.append(TEXTURE_PATH)
if not isinstance(texture, unreal.Texture2D):
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_TEXTURE")
texture.set_editor_property("srgb", False)
texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
if material is None:
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_ABV_TerrainReliefV1_RG16Import",
        TARGET_FOLDER,
        unreal.Material,
        unreal.MaterialFactoryNew(),
    )
    created_assets.append(MATERIAL_PATH)
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_MATERIAL")
unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
sample = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionTextureSample, -300, 0
)
sample.set_editor_property("texture", texture)
sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
if not unreal.MaterialEditingLibrary.connect_material_property(
    sample, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR
):
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_MATERIAL_CONNECT")
errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
if errors:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_MATERIAL_COMPILE " + "|".join(str(item) for item in errors))

content_dirty = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
allowed_content = {TEXTURE_PATH, MATERIAL_PATH}
unexpected_content = [package_name(package) for package in content_dirty if package_name(package) not in allowed_content]
if unexpected_content:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_SOURCE_DIRTY " + "|".join(unexpected_content))
if content_dirty and not unreal.EditorLoadingAndSavingUtils.save_packages(content_dirty, True):
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_SOURCE_SAVE")
if dirty_packages():
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_DIRTY_AFTER_SOURCE_SAVE " + "|".join(dirty_packages()))

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
render_target = unreal.RenderingLibrary.create_render_target2d(
    world,
    2017,
    2017,
    unreal.TextureRenderTargetFormat.RTF_RGBA8,
    unreal.LinearColor(0.0, 0.0, 0.0, 1.0),
    False,
    False,
)
unreal.RenderingLibrary.draw_material_to_render_target(world, render_target, material)
imported = parent.landscape_import_heightmap_from_render_target(render_target, True, 0)
if not imported:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_HEIGHT_FAILED")
parent.force_layers_full_update()

dirty_after = dirty_packages()
if not dirty_after:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_NO_LANDSCAPE_DIRTY")
content_after = [name for name in dirty_after if not name.startswith("/Game/__External")]
if content_after:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_IMPORT_UNEXPECTED_CONTENT " + "|".join(content_after))

path = write_report(
    {
        "schema_version": 1,
        "status": "terrain_relief_imported_unsaved_preview",
        "source_file": SOURCE_FILE,
        "source_texture": texture.get_path_name(),
        "source_texture_size": [int(texture.blueprint_get_size_x()), int(texture.blueprint_get_size_y())],
        "source_texture_compression": str(texture.get_editor_property("compression_settings")),
        "source_texture_srgb": bool(texture.get_editor_property("srgb")),
        "source_material": material.get_path_name(),
        "created_assets": created_assets,
        "landscape": parent.get_path_name(),
        "edit_layer_index": 0,
        "landscape_proxy_count": len(landscape_descriptors),
        "dirty_landscape_packages": dirty_after,
        "height_import_saved": False,
        "rollback_source": (
            "/Users/jasonteck/UnrealEngine/_worktrees/map-development/Documentation/Maps/"
            "OperationSunscar/Source/Heightmaps/Sunscar_Height_2017_BaseBackup.png"
        ),
    }
)
unreal.log("ABIVERD_TERRAIN_RELIEF_IMPORT_PREVIEW_PASS dirty=%d" % len(dirty_after))
print("ABIVERD_TERRAIN_RELIEF_IMPORT_PREVIEW_PASS", path)
