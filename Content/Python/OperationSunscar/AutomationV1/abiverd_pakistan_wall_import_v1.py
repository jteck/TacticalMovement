"""Import and configure Pakistan Street Wall Brick Modular 16 map assets only.

The script does not load, edit, or save the production map. It imports the
verified High glTF source into the dedicated Abiverd architecture folder,
reuses the map-owned lightweight scan material master, enables Nanite, caps
runtime texture resolution, and saves only the intentionally created assets.
"""

import json
import os
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
SOURCE_FILE = (
    "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/"
    "Historic_Pakistan_Street_Wall_Brick_Modular_16-9ecd80c7/gltf/high/"
    "historic_pakistan_street_extracted/SM_wkzfbht_tier_1.gltf"
)
DESTINATION = "/Game/Maps/Sunscar/Art/Heritage/Architecture/PakistanWallModular16"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/M_ABV_HeritageScan_PBR"
PACKED_MASTER_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/M_ABV_HeritageScan_ORM"
MATERIAL_PATH = DESTINATION + "/MI_ABV_PakistanWallModular16"
REPORT_NAME = "abiverd_pakistan_wall_import_v1.json"


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


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_PAK_WALL_WRONG_PROJECT %s %s" % (project_name, project_directory))
if not os.path.isfile(SOURCE_FILE):
    raise RuntimeError("ABIVERD_PAK_WALL_SOURCE_MISSING " + SOURCE_FILE)
if dirty_packages():
    raise RuntimeError("ABIVERD_PAK_WALL_DIRTY_BEFORE " + "|".join(dirty_packages()))

existing = (
    unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True)
    if unreal.EditorAssetLibrary.does_directory_exist(DESTINATION)
    else []
)
if existing:
    raise RuntimeError("ABIVERD_PAK_WALL_DESTINATION_NOT_EMPTY " + repr(existing))

task = unreal.AssetImportTask()
task.filename = SOURCE_FILE
task.destination_path = DESTINATION
task.automated = True
task.replace_existing = False
task.save = False
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

assets = [
    unreal.EditorAssetLibrary.load_asset(path)
    for path in unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True)
]
meshes = [item for item in assets if isinstance(item, unreal.StaticMesh)]
textures = [item for item in assets if isinstance(item, unreal.Texture2D)]
source_materials = [item for item in assets if isinstance(item, unreal.MaterialInstanceConstant)]
if len(meshes) != 1 or len(textures) != 4 or len(source_materials) != 1:
    raise RuntimeError(
        "ABIVERD_PAK_WALL_IMPORT_SCOPE meshes=%d textures=%d materials=%d"
        % (len(meshes), len(textures), len(source_materials))
    )

roles = {}
for texture in textures:
    lower = texture.get_name().lower()
    if lower.endswith("_b"):
        roles["BaseColor"] = texture
    elif lower.endswith("_n"):
        roles["Normal"] = texture
    elif lower.endswith("_orm"):
        roles["ORM"] = texture
    elif lower.endswith("_h"):
        roles["Height"] = texture
if set(roles) != {"BaseColor", "Normal", "ORM", "Height"}:
    raise RuntimeError("ABIVERD_PAK_WALL_TEXTURE_ROLES " + repr(sorted(roles)))

# Interchange imports the packed ORM image as generic color data. Correct its
# color space before the map-owned material graph is compiled.
roles["ORM"].modify()
roles["ORM"].set_editor_properties(
    {
        "srgb": False,
        "compression_settings": unreal.TextureCompressionSettings.TC_MASKS,
        "max_texture_size": 2048,
    }
)
roles["Normal"].modify()
roles["Normal"].set_editor_properties(
    {
        "srgb": False,
        "compression_settings": unreal.TextureCompressionSettings.TC_NORMALMAP,
        "max_texture_size": 2048,
    }
)
roles["BaseColor"].modify()
roles["BaseColor"].set_editor_property("max_texture_size", 2048)

reference_master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
if not isinstance(reference_master, unreal.Material):
    raise RuntimeError("ABIVERD_PAK_WALL_MASTER_MISSING " + MASTER_PATH)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
master = unreal.EditorAssetLibrary.load_asset(PACKED_MASTER_PATH)
if master is None:
    master = asset_tools.create_asset(
        PACKED_MASTER_PATH.rsplit("/", 1)[1],
        PACKED_MASTER_PATH.rsplit("/", 1)[0],
        unreal.Material,
        unreal.MaterialFactoryNew(),
    )
if not isinstance(master, unreal.Material):
    raise RuntimeError("ABIVERD_PAK_WALL_PACKED_MASTER")
master.modify()
unreal.MaterialEditingLibrary.delete_all_material_expressions(master)
master.set_editor_properties(
    {"blend_mode": unreal.BlendMode.BLEND_OPAQUE, "two_sided": False, "tangent_space_normal": True}
)

base_sample = unreal.MaterialEditingLibrary.create_material_expression(
    master, unreal.MaterialExpressionTextureSampleParameter2D, -600, -180
)
normal_sample = unreal.MaterialEditingLibrary.create_material_expression(
    master, unreal.MaterialExpressionTextureSampleParameter2D, -600, 40
)
orm_sample = unreal.MaterialEditingLibrary.create_material_expression(
    master, unreal.MaterialExpressionTextureSampleParameter2D, -600, 260
)
if base_sample is None or normal_sample is None or orm_sample is None:
    raise RuntimeError("ABIVERD_PAK_WALL_MASTER_EXPRESSIONS")
base_sample.set_editor_properties(
    {
        "parameter_name": unreal.Name("BaseColor"),
        "texture": roles["BaseColor"],
        "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
    }
)
normal_sample.set_editor_properties(
    {
        "parameter_name": unreal.Name("Normal"),
        "texture": roles["Normal"],
        "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
    }
)
orm_sample.set_editor_properties(
    {
        "parameter_name": unreal.Name("ORM"),
        "texture": roles["ORM"],
        "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_MASKS,
    }
)
connections = (
    (base_sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR),
    (normal_sample, "RGB", unreal.MaterialProperty.MP_NORMAL),
    (orm_sample, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),
    (orm_sample, "G", unreal.MaterialProperty.MP_ROUGHNESS),
    (orm_sample, "B", unreal.MaterialProperty.MP_METALLIC),
)
for expression, output_name, material_property in connections:
    if not unreal.MaterialEditingLibrary.connect_material_property(
        expression, output_name, material_property
    ):
        raise RuntimeError("ABIVERD_PAK_WALL_MASTER_CONNECT " + str(material_property))
compile_errors = list(unreal.MaterialEditingLibrary.recompile_material(master))
if compile_errors:
    raise RuntimeError("ABIVERD_PAK_WALL_MASTER_COMPILE " + "|".join(str(item) for item in compile_errors))

material = asset_tools.create_asset(
    MATERIAL_PATH.rsplit("/", 1)[1],
    DESTINATION,
    unreal.MaterialInstanceConstant,
    unreal.MaterialInstanceConstantFactoryNew(),
)
if not isinstance(material, unreal.MaterialInstanceConstant):
    raise RuntimeError("ABIVERD_PAK_WALL_MATERIAL_CREATE")
material.modify()
material.set_editor_property("parent", master)
for parameter, texture in (
    ("BaseColor", roles["BaseColor"]),
    ("Normal", roles["Normal"]),
    ("ORM", roles["ORM"]),
):
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
        material, parameter, texture
    )
unreal.MaterialEditingLibrary.update_material_instance(material)

mesh = meshes[0]
mesh.modify()
nanite = mesh.get_editor_property("nanite_settings")
nanite.enabled = True
mesh.set_editor_property("nanite_settings", nanite)
mesh.set_material(0, material)

bounds = mesh.get_bounds()
extent = bounds.box_extent
bounds_size_cm = [
    round(float(extent.x) * 2.0, 3),
    round(float(extent.y) * 2.0, 3),
    round(float(extent.z) * 2.0, 3),
]
expected = [200.603, 30.578, 350.016]
if any(abs(actual - target) > 2.0 for actual, target in zip(bounds_size_cm, expected)):
    raise RuntimeError("ABIVERD_PAK_WALL_BOUNDS " + repr(bounds_size_cm))

dirty_before_save = dirty_packages()
unexpected = [name for name in dirty_before_save if not name.startswith(DESTINATION + "/")]
unexpected = [
    name for name in unexpected
    if not name.startswith(PACKED_MASTER_PATH.rsplit("/", 1)[0] + "/")
]
if unexpected:
    raise RuntimeError("ABIVERD_PAK_WALL_UNEXPECTED_DIRTY " + "|".join(unexpected))
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_PAK_WALL_SAVE_FAILED")
remaining = dirty_packages()
if remaining:
    raise RuntimeError("ABIVERD_PAK_WALL_DIRTY_AFTER " + "|".join(remaining))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
payload = {
    "schema_version": 1,
    "status": "imported_configured_and_saved",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "context": {"project": project_name, "project_directory": project_directory},
    "source_file": SOURCE_FILE,
    "destination": DESTINATION,
    "mesh": mesh.get_path_name(),
    "bounds_size_cm": bounds_size_cm,
    "lod0_vertices": int(mesh.get_num_vertices(0)),
    "nanite_enabled": bool(mesh.get_editor_property("nanite_settings").enabled),
    "assets": sorted(item.get_path_name() for item in assets),
    "created_material": material.get_path_name(),
    "packed_orm_master": master.get_path_name(),
    "runtime_texture_max_size": 2048,
    "dirty_before_save": dirty_before_save,
    "dirty_after_save": remaining,
    "map_changed": False,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_PAK_WALL_IMPORT_COMPLETE " + report_path)
print("ABIVERD_PAK_WALL_IMPORT_COMPLETE", report_path)
