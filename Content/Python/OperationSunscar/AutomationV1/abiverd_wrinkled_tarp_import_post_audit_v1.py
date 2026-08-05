"""Independent read-only audit for the map-owned Quixel Wrinkled Tarp import."""

import json
import math
import os
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
DESTINATION = "/Game/Maps/Sunscar/Art/Heritage/Props/WrinkledTarp"
MESH_PATH = DESTINATION + "/vieldbo_tier_1/StaticMeshes/vieldbo_tier_1"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/M_ABV_Cloth_ORM"
MATERIAL_PATH = DESTINATION + "/MI_ABV_WrinkledTarp"
TEXTURE_ROOT = DESTINATION + "/vieldbo_tier_1/Textures/"
TEXTURE_PATHS = {
    "BaseColor": TEXTURE_ROOT + "T_vieldbo_4K_B",
    "Height": TEXTURE_ROOT + "T_vieldbo_4K_H",
    "Normal": TEXTURE_ROOT + "T_vieldbo_4K_N",
    "ORM": TEXTURE_ROOT + "T_vieldbo_4K_ORM",
}
REPORT_NAME = "abiverd_wrinkled_tarp_import_post_audit_v1.json"


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
    raise RuntimeError("ABIVERD_TARP_AUDIT_WRONG_PROJECT %s %s" % (project_name, project_directory))

dirty_before = dirty_packages()
if dirty_before:
    raise RuntimeError("ABIVERD_TARP_AUDIT_DIRTY_BEFORE " + "|".join(dirty_before))

mesh = unreal.EditorAssetLibrary.load_asset(MESH_PATH)
master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
textures = {role: unreal.EditorAssetLibrary.load_asset(path) for role, path in TEXTURE_PATHS.items()}

if not isinstance(mesh, unreal.StaticMesh):
    raise RuntimeError("ABIVERD_TARP_AUDIT_MESH")
if not isinstance(master, unreal.Material):
    raise RuntimeError("ABIVERD_TARP_AUDIT_MASTER")
if not isinstance(material, unreal.MaterialInstanceConstant):
    raise RuntimeError("ABIVERD_TARP_AUDIT_MATERIAL")
if any(not isinstance(texture, unreal.Texture2D) for texture in textures.values()):
    raise RuntimeError("ABIVERD_TARP_AUDIT_TEXTURES")

bounds = mesh.get_bounds()
extent = bounds.box_extent
bounds_size_cm = [
    round(float(extent.x) * 2.0, 3),
    round(float(extent.y) * 2.0, 3),
    round(float(extent.z) * 2.0, 3),
]
if not all(math.isfinite(value) for value in bounds_size_cm):
    raise RuntimeError("ABIVERD_TARP_AUDIT_BOUNDS_NONFINITE")
expected_sorted = sorted([276.886, 151.093, 10.339])
if any(abs(actual - expected) > 0.5 for actual, expected in zip(sorted(bounds_size_cm), expected_sorted)):
    raise RuntimeError("ABIVERD_TARP_AUDIT_BOUNDS " + repr(bounds_size_cm))

if not bool(mesh.get_editor_property("nanite_settings").enabled):
    raise RuntimeError("ABIVERD_TARP_AUDIT_NANITE")
assigned_material = mesh.get_material(0)
if assigned_material is None or assigned_material.get_path_name() != material.get_path_name():
    raise RuntimeError("ABIVERD_TARP_AUDIT_MESH_MATERIAL")
parent = material.get_editor_property("parent")
if parent is None or parent.get_path_name() != master.get_path_name():
    raise RuntimeError("ABIVERD_TARP_AUDIT_PARENT")
if master.get_editor_property("blend_mode") != unreal.BlendMode.BLEND_OPAQUE:
    raise RuntimeError("ABIVERD_TARP_AUDIT_BLEND")
if not bool(master.get_editor_property("two_sided")):
    raise RuntimeError("ABIVERD_TARP_AUDIT_TWO_SIDED")

texture_state = {}
for role, texture in textures.items():
    max_size = int(texture.get_editor_property("max_texture_size"))
    expected_max = 1024 if role == "Height" else 2048
    if max_size != expected_max:
        raise RuntimeError("ABIVERD_TARP_AUDIT_TEXTURE_CAP %s %d" % (role, max_size))
    texture_state[role] = {
        "path": texture.get_path_name(),
        "max_texture_size": max_size,
        "srgb": bool(texture.get_editor_property("srgb")),
        "compression_settings": str(texture.get_editor_property("compression_settings")),
    }

dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_TARP_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))

assets = unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True)
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
payload = {
    "schema_version": 1,
    "status": "post_import_audit_passed",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level_changed": False,
    },
    "mesh": mesh.get_path_name(),
    "bounds_size_cm": bounds_size_cm,
    "lod0_vertices": int(mesh.get_num_vertices(0)),
    "nanite_enabled": True,
    "mesh_material": assigned_material.get_path_name(),
    "material_parent": parent.get_path_name(),
    "master_opaque": True,
    "master_two_sided": True,
    "textures": texture_state,
    "asset_count": len(assets),
    "assets": sorted(assets),
    "dirty_before": dirty_before,
    "dirty_after": dirty_after,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_TARP_IMPORT_POST_AUDIT_PASS " + report_path)
print("ABIVERD_TARP_IMPORT_POST_AUDIT_PASS", report_path)
