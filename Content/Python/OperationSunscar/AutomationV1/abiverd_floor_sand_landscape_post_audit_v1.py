"""Independent read-only audit of the heritage-sand Landscape substitution."""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
ROOT = (
    "/Game/Maps/Sunscar/Art/Heritage/Surfaces/"
    "HistoricDesertRuinFloorSandCoarse01/Textures/"
)
TEXTURES = {
    "BaseColor": ROOT + "T_xbohccs_4k_B",
    "Height": ROOT + "T_xbohccs_4k_H",
    "Normal": ROOT + "T_xbohccs_4k_N",
    "ORM": ROOT + "T_xbohccs_4k_ORM",
}


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


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_CONTEXT")
if dirty_packages():
    raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
textures = {role: unreal.EditorAssetLibrary.load_asset(path) for role, path in TEXTURES.items()}
if not isinstance(material, unreal.Material) or any(not isinstance(value, unreal.Texture2D) for value in textures.values()):
    raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_ASSETS")

expected_caps = {"BaseColor": 2048, "Normal": 2048, "ORM": 2048, "Height": 1024}
texture_state = {}
for role, texture in textures.items():
    cap = int(texture.get_editor_property("max_texture_size"))
    if cap != expected_caps[role]:
        raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_CAP %s %d" % (role, cap))
    texture_state[role] = {"path": texture.get_path_name(), "max_texture_size": cap}

parameters = {"Farm_BaseColor": [], "Farm_Normal": [], "Farm_TileCm": []}
for expression in unreal.MaterialEditingLibrary.get_material_expressions(material):
    try:
        name = str(expression.get_editor_property("parameter_name"))
    except Exception:
        continue
    if name in parameters:
        parameters[name].append(expression)

if {name: len(nodes) for name, nodes in parameters.items()} != {
    "Farm_BaseColor": 2, "Farm_Normal": 1, "Farm_TileCm": 2
}:
    raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_COUNTS")
for node in parameters["Farm_BaseColor"]:
    if node.get_editor_property("texture").get_path_name() != textures["BaseColor"].get_path_name():
        raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_BASE")
for node in parameters["Farm_Normal"]:
    if node.get_editor_property("texture").get_path_name() != textures["Normal"].get_path_name():
        raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_NORMAL")
for node in parameters["Farm_TileCm"]:
    if abs(float(node.get_editor_property("default_value")) - 120.0) > 0.001:
        raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_TILE")

expression_count = len(unreal.MaterialEditingLibrary.get_material_expressions(material))
if expression_count != 130:
    raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_EXPRESSIONS %d" % expression_count)
if dirty_packages():
    raise RuntimeError("ABIVERD_FLOOR_SAND_POST_AUDIT_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "post_conversion_audit_passed",
    "level": level_path,
    "material": material.get_path_name(),
    "semantic_layer": "RoadsideSilt / heritage sand",
    "parameter_node_counts": {name: len(nodes) for name, nodes in parameters.items()},
    "tile_cm": 120.0,
    "material_expression_count": expression_count,
    "texture_state": texture_state,
    "added_target_layers": 0,
    "added_texture_samples": 0,
    "dirty_after": dirty_packages(),
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_floor_sand_landscape_post_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_FLOOR_SAND_LANDSCAPE_POST_AUDIT_PASS")
print("ABIVERD_FLOOR_SAND_LANDSCAPE_POST_AUDIT_PASS", report_path)
