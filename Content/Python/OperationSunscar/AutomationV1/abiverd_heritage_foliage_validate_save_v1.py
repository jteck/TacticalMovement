"""Validate and save exactly the optimized Abiverd Field Poppy/Wild Grass assets."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ROOT = "/Game/Maps/Sunscar/Art/Heritage/Foliage"
MASTER_PATH = "/Game/Fab/Materials/Standard/M_MS_Foliage"
MASTER_OBJECT_PATH = "/Game/Fab/Materials/Standard/M_MS_Foliage.M_MS_Foliage"
EXPECTED_SCREEN_SIZES = [1.0, 0.48, 0.20, 0.07]
EXPECTED_COUNT = 24


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_FOLIAGE_SAVE_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_FOLIAGE_SAVE_WRONG_LEVEL " + level_path)

paths = sorted(unreal.EditorAssetLibrary.list_assets(ROOT, recursive=True, include_folder=False))
assets = [unreal.EditorAssetLibrary.load_asset(path) for path in paths]
if len(assets) != EXPECTED_COUNT or any(asset is None for asset in assets):
    raise RuntimeError("ABIVERD_FOLIAGE_SAVE_ASSET_SCOPE expected=24 actual=%d" % len(assets))

class_counts = {}
for asset in assets:
    class_name = asset.get_class().get_name()
    class_counts[class_name] = class_counts.get(class_name, 0) + 1
if class_counts != {"StaticMesh": 16, "Texture2D": 6, "MaterialInstanceConstant": 2}:
    raise RuntimeError("ABIVERD_FOLIAGE_SAVE_CLASS_SCOPE " + repr(class_counts))

mesh_subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
records = []
for asset in assets:
    path = asset.get_path_name()
    row = {"path": path, "class": asset.get_class().get_name()}
    if isinstance(asset, unreal.Texture2D):
        name = asset.get_name()
        size = [int(asset.blueprint_get_size_x()), int(asset.blueprint_get_size_y())]
        srgb = bool(asset.get_editor_property("srgb"))
        compression = asset.get_editor_property("compression_settings")
        lod_group = asset.get_editor_property("lod_group")
        if name.endswith("_BaseColor"):
            role = "BaseColor"
            expected_srgb = True
            expected_compression = unreal.TextureCompressionSettings.TC_DEFAULT
            expected_group = unreal.TextureGroup.TEXTUREGROUP_WORLD
        elif name.endswith("_Normal"):
            role = "Normal"
            expected_srgb = False
            expected_compression = unreal.TextureCompressionSettings.TC_NORMALMAP
            expected_group = unreal.TextureGroup.TEXTUREGROUP_WORLD_NORMAL_MAP
        elif name.endswith("_Mask"):
            role = "Mask"
            expected_srgb = False
            expected_compression = unreal.TextureCompressionSettings.TC_MASKS
            expected_group = unreal.TextureGroup.TEXTUREGROUP_WORLD
        else:
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_TEXTURE_ROLE " + path)
        if size != [4096, 4096]:
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_TEXTURE_SIZE %s %s" % (path, repr(size)))
        if srgb != expected_srgb or compression != expected_compression or lod_group != expected_group:
            raise RuntimeError(
                "ABIVERD_FOLIAGE_SAVE_TEXTURE_SETTINGS %s srgb=%s compression=%s group=%s"
                % (path, srgb, str(compression), str(lod_group))
            )
        if bool(asset.get_editor_property("virtual_texture_streaming")):
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_TEXTURE_VT_ENABLED " + path)
        row.update(
            {
                "role": role,
                "size": size,
                "srgb": srgb,
                "compression": str(compression),
                "lod_group": str(lod_group),
                "virtual_texture_streaming": False,
            }
        )
    elif isinstance(asset, unreal.MaterialInstanceConstant):
        parent = asset.get_editor_property("parent")
        parent_path = parent.get_path_name() if parent else None
        if parent_path != MASTER_OBJECT_PATH:
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_MATERIAL_PARENT %s %s" % (path, parent_path))
        expected_slug = "FieldPoppy" if "FieldPoppy" in path else "WildGrass"
        expected_textures = {
            "BaseColorTexture": ROOT + "/%s/T_%s_BaseColor.T_%s_BaseColor" % (expected_slug, expected_slug, expected_slug),
            "NormalTexture": ROOT + "/%s/T_%s_Normal.T_%s_Normal" % (expected_slug, expected_slug, expected_slug),
            "Mask": ROOT + "/%s/T_%s_Mask.T_%s_Mask" % (expected_slug, expected_slug, expected_slug),
        }
        resolved = {}
        for parameter, expected_path in expected_textures.items():
            texture = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(asset, parameter)
            actual_path = texture.get_path_name() if texture else None
            resolved[parameter] = actual_path
            if actual_path != expected_path:
                raise RuntimeError(
                    "ABIVERD_FOLIAGE_SAVE_MATERIAL_TEXTURE %s %s expected=%s actual=%s"
                    % (path, parameter, expected_path, actual_path)
                )
        row.update({"parent": parent_path, "textures": resolved})
    elif isinstance(asset, unreal.StaticMesh):
        lod_count = mesh_subsystem.get_lod_count(asset)
        if lod_count != 4:
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_LOD_COUNT %s %d" % (path, lod_count))
        screen_sizes = [float(value) for value in mesh_subsystem.get_lod_screen_sizes(asset)]
        if len(screen_sizes) != 4 or any(
            abs(actual - expected) > 0.0001
            for actual, expected in zip(screen_sizes, EXPECTED_SCREEN_SIZES)
        ):
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_SCREEN_SIZES %s %s" % (path, repr(screen_sizes)))
        vertices = [mesh_subsystem.get_number_verts(asset, lod_index) for lod_index in range(4)]
        if any(value <= 0 for value in vertices) or any(
            vertices[index] > vertices[index - 1] for index in range(1, len(vertices))
        ) or vertices[-1] >= vertices[0]:
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_LOD_VERTICES %s %s" % (path, repr(vertices)))
        if mesh_subsystem.get_simple_collision_count(asset) != 0:
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_COLLISION " + path)
        if bool(asset.get_editor_property("nanite_settings").enabled):
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_NANITE_ENABLED " + path)
        expected_slug = "FieldPoppy" if "FieldPoppy" in path else "WildGrass"
        expected_material = ROOT + "/%s/MI_%s.MI_%s" % (expected_slug, expected_slug, expected_slug)
        materials = [
            value.material_interface.get_path_name() if value.material_interface else None
            for value in asset.get_editor_property("static_materials")
        ]
        if not materials or any(value != expected_material for value in materials):
            raise RuntimeError("ABIVERD_FOLIAGE_SAVE_MESH_MATERIAL %s %s" % (path, repr(materials)))
        bounds = asset.get_bounds()
        dimensions = [
            bounds.box_extent.x * 2.0,
            bounds.box_extent.y * 2.0,
            bounds.box_extent.z * 2.0,
        ]
        bottom = bounds.origin.z - bounds.box_extent.z
        height_limits = (30.0, 100.0) if expected_slug == "FieldPoppy" else (8.0, 60.0)
        if not (height_limits[0] <= dimensions[2] <= height_limits[1]) or not (-6.0 <= bottom <= 1.0):
            raise RuntimeError(
                "ABIVERD_FOLIAGE_SAVE_BOUNDS %s dims=%s bottom=%s"
                % (path, repr(dimensions), str(bottom))
            )
        row.update(
            {
                "lod_count": lod_count,
                "lod_screen_sizes": screen_sizes,
                "vertices_by_lod": vertices,
                "nanite_enabled": False,
                "simple_collision_count": 0,
                "materials": materials,
                "dimensions_cm": dimensions,
                "bottom_cm": bottom,
            }
        )
    records.append(row)

packages = [asset.get_package() for asset in assets]
target_names = {package.get_name() for package in packages}
dirty_content = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content != target_names or dirty_maps:
    raise RuntimeError(
        "ABIVERD_FOLIAGE_SAVE_DIRTY_SCOPE content=%s maps=%s targets=%s"
        % (repr(sorted(dirty_content)), repr(sorted(dirty_maps)), repr(sorted(target_names)))
    )

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
preflight_path = os.path.join(report_root, "abiverd_heritage_foliage_validate_save_preflight_v1.json")
with open(preflight_path, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "status": "save_preflight_passed",
            "asset_count": len(records),
            "class_counts": class_counts,
            "dirty_content": sorted(dirty_content),
            "dirty_maps": sorted(dirty_maps),
            "target_packages": sorted(target_names),
        },
        handle,
        indent=2,
    )
    handle.write("\n")

if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_FOLIAGE_SAVE_FAILED")

remaining = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
if remaining:
    raise RuntimeError("ABIVERD_FOLIAGE_SAVE_DIRTY_AFTER " + repr(remaining))

report_path = os.path.join(report_root, "abiverd_heritage_foliage_validate_save_v1.json")
payload = {
    "schema_version": 1,
    "status": "validated_and_saved",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "asset_count": len(records),
    "class_counts": class_counts,
    "records": records,
    "saved_packages": sorted(target_names),
    "dirty_packages_after": remaining,
    "level_changed": False,
    "level_saved": False,
    "mask_channel_packing": {"R": "Opacity", "G": "Roughness", "B": "Translucency"},
    "performance_policy": {
        "nanite": "disabled pending masked-overdraw benchmark",
        "lods": "four source-authored LODs per mesh",
        "collision": "disabled",
        "material": MASTER_PATH,
    },
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_FOLIAGE_SAVE_COMPLETE assets=%d report=%s" % (len(records), report_path))
print("ABIVERD_FOLIAGE_SAVE_COMPLETE", len(records), report_path)
