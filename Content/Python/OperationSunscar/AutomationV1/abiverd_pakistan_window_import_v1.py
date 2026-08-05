"""Import and configure Pakistan Street Window Brick Modular 04 map assets.

This bounded pass does not edit or save the level. It imports the verified
High glTF source into the dedicated Abiverd architecture tree, reuses the
existing lightweight packed-ORM material master, enables Nanite, caps runtime
texture resolution, validates plausible architectural bounds, and saves only
the intentionally created asset packages.
"""

import json
import os
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
SOURCE_FILE = (
    "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/"
    "Historic_Pakistan_Street_Window_Brick_Modular_04-e5026e65/gltf/high/"
    "historic_pakistan_street_extracted/SM_wk0hehv_tier_1.gltf"
)
DESTINATION = "/Game/Maps/Sunscar/Art/Heritage/Architecture/PakistanWindowModular04"
PACKED_MASTER_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/M_ABV_HeritageScan_ORM"
MATERIAL_PATH = DESTINATION + "/MI_ABV_PakistanWindowModular04"
REPORT_NAME = "abiverd_pakistan_window_import_v1.json"


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
    raise RuntimeError("ABIVERD_PAK_WINDOW_WRONG_PROJECT %s %s" % (project_name, project_directory))
if not os.path.isfile(SOURCE_FILE):
    raise RuntimeError("ABIVERD_PAK_WINDOW_SOURCE_MISSING " + SOURCE_FILE)
if dirty_packages():
    raise RuntimeError("ABIVERD_PAK_WINDOW_DIRTY_BEFORE " + "|".join(dirty_packages()))

existing = (
    unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True)
    if unreal.EditorAssetLibrary.does_directory_exist(DESTINATION)
    else []
)
if existing:
    raise RuntimeError("ABIVERD_PAK_WINDOW_DESTINATION_NOT_EMPTY " + repr(existing))

master = unreal.EditorAssetLibrary.load_asset(PACKED_MASTER_PATH)
if not isinstance(master, unreal.Material):
    raise RuntimeError("ABIVERD_PAK_WINDOW_MASTER_MISSING " + PACKED_MASTER_PATH)

task = unreal.AssetImportTask()
task.filename = SOURCE_FILE
task.destination_path = DESTINATION
task.automated = True
task.replace_existing = False
task.save = False
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

assets = [
    unreal.EditorAssetLibrary.load_asset(asset_path)
    for asset_path in unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True)
]
meshes = [item for item in assets if isinstance(item, unreal.StaticMesh)]
textures = [item for item in assets if isinstance(item, unreal.Texture2D)]
source_materials = [item for item in assets if isinstance(item, unreal.MaterialInstanceConstant)]
if len(meshes) != 1 or len(textures) != 4 or len(source_materials) != 1:
    raise RuntimeError(
        "ABIVERD_PAK_WINDOW_IMPORT_SCOPE meshes=%d textures=%d materials=%d"
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
    raise RuntimeError("ABIVERD_PAK_WINDOW_TEXTURE_ROLES " + repr(sorted(roles)))

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

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
material = asset_tools.create_asset(
    MATERIAL_PATH.rsplit("/", 1)[1],
    DESTINATION,
    unreal.MaterialInstanceConstant,
    unreal.MaterialInstanceConstantFactoryNew(),
)
if not isinstance(material, unreal.MaterialInstanceConstant):
    raise RuntimeError("ABIVERD_PAK_WINDOW_MATERIAL_CREATE")
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
width, depth, height = bounds_size_cm
if not (100.0 <= width <= 500.0 and 5.0 <= depth <= 120.0 and 200.0 <= height <= 600.0):
    raise RuntimeError("ABIVERD_PAK_WINDOW_IMPLAUSIBLE_BOUNDS " + repr(bounds_size_cm))

dirty_before_save = dirty_packages()
unexpected = [name for name in dirty_before_save if not name.startswith(DESTINATION + "/")]
if unexpected:
    raise RuntimeError("ABIVERD_PAK_WINDOW_UNEXPECTED_DIRTY " + "|".join(unexpected))
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
if not packages or not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_PAK_WINDOW_SAVE_FAILED")
remaining = dirty_packages()
if remaining:
    raise RuntimeError("ABIVERD_PAK_WINDOW_DIRTY_AFTER " + "|".join(remaining))

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
    "bounds_origin_cm": [
        round(float(bounds.origin.x), 3),
        round(float(bounds.origin.y), 3),
        round(float(bounds.origin.z), 3),
    ],
    "lod0_vertices": int(mesh.get_num_vertices(0)),
    "material_slots": len(mesh.get_editor_property("static_materials")),
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

unreal.log("ABIVERD_PAK_WINDOW_IMPORT_COMPLETE " + report_path)
print("ABIVERD_PAK_WINDOW_IMPORT_COMPLETE", report_path)
