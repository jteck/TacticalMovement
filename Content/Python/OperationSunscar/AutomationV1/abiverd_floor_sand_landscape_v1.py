"""Dry-run-first use of Historic Desert Ruin Floor Sand Coarse in Landscape V3.

The pass swaps the existing RoadsideSilt/Farm texture inputs.  It creates no
new Landscape target layer, weightmap, texture sample, actor or collision.
"""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
SOURCE_ROOT = (
    "/Game/Fab/Megascans/Surfaces/Historic_Desert_Ruin_Floor_Sand_Coarse_01_xbohccs/"
    "High/xbohccs_tier_1/Textures/"
)
TEXTURES = {
    "BaseColor": SOURCE_ROOT + "T_xbohccs_4k_B",
    "Height": SOURCE_ROOT + "T_xbohccs_4k_H",
    "Normal": SOURCE_ROOT + "T_xbohccs_4k_N",
    "ORM": SOURCE_ROOT + "T_xbohccs_4k_ORM",
}
EXPECTED_CURRENT = {
    "Farm_BaseColor": (
        "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Fine_02/"
        "Textures/T_Mil_Trench_Ground_Dirt_Fine_02_B"
    ),
    "Farm_Normal": (
        "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Fine_02/"
        "Textures/T_Mil_Trench_Ground_Dirt_Fine_02_N"
    ),
}
REPORT_NAME = (
    "abiverd_floor_sand_landscape_apply_v1.json"
    if APPLY_CHANGES else "abiverd_floor_sand_landscape_dry_run_v1.json"
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


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_DIRTY_BEFORE " + "|".join(dirty_packages()))

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
textures = {role: unreal.EditorAssetLibrary.load_asset(path) for role, path in TEXTURES.items()}
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_MATERIAL")
if any(not isinstance(texture, unreal.Texture2D) for texture in textures.values()):
    raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_TEXTURES")

parameter_nodes = {}
for expression in unreal.MaterialEditingLibrary.get_material_expressions(material):
    try:
        name = str(expression.get_editor_property("parameter_name"))
    except Exception:
        continue
    if name:
        parameter_nodes.setdefault(name, []).append(expression)

resolved = {}
for parameter in ("Farm_BaseColor", "Farm_Normal", "Farm_TileCm"):
    nodes = parameter_nodes.get(parameter, [])
    if not nodes:
        raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_PARAMETER %s count=%d" % (parameter, len(nodes)))
    resolved[parameter] = nodes

current_paths = {}
for parameter in ("Farm_BaseColor", "Farm_Normal"):
    current_paths[parameter] = []
    expected_asset = unreal.EditorAssetLibrary.load_asset(EXPECTED_CURRENT[parameter])
    expected_path = expected_asset.get_path_name() if expected_asset else ""
    target_path = textures["BaseColor" if parameter.endswith("BaseColor") else "Normal"].get_path_name()
    for node in resolved[parameter]:
        texture = node.get_editor_property("texture")
        path = texture.get_path_name() if texture else ""
        current_paths[parameter].append(path)
        if path not in (expected_path, target_path):
            raise RuntimeError(
                "ABIVERD_FLOOR_SAND_LANDSCAPE_UNEXPECTED_CURRENT %s %s" % (parameter, path)
            )

tile_nodes = resolved["Farm_TileCm"]
current_tile_cm = [float(node.get_editor_property("default_value")) for node in tile_nodes]
target_tile_cm = 120.0
expression_count_before = len(unreal.MaterialEditingLibrary.get_material_expressions(material))

saved_packages = []
if APPLY_CHANGES:
    textures["BaseColor"].set_editor_property("max_texture_size", 2048)
    textures["Normal"].set_editor_property("max_texture_size", 2048)
    textures["ORM"].set_editor_property("max_texture_size", 2048)
    textures["Height"].set_editor_property("max_texture_size", 1024)
    for node in resolved["Farm_BaseColor"]:
        node.set_editor_property("texture", textures["BaseColor"])
    for node in resolved["Farm_Normal"]:
        node.set_editor_property("texture", textures["Normal"])
    for node in tile_nodes:
        node.set_editor_property("default_value", target_tile_cm)
    compiler_errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
    if compiler_errors:
        raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_COMPILE " + "|".join(str(item) for item in compiler_errors))
    if len(unreal.MaterialEditingLibrary.get_material_expressions(material)) != expression_count_before:
        raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_EXPRESSION_COUNT_CHANGED")
    dirty_after_change = dirty_packages()
    allowed = {MATERIAL_PATH} | set(TEXTURES.values())
    unexpected = [name for name in dirty_after_change if name not in allowed]
    if unexpected:
        raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    saved_packages = sorted(package_name(package) for package in packages)
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_FLOOR_SAND_LANDSCAPE_DIRTY_AFTER_SAVE " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "landscape_material": MATERIAL_PATH,
    "semantic_layer": "RoadsideSilt / heritage courtyards, dry canal sediment and ruin floors",
    "target_layer_internal_name": "Farm",
    "current_texture_paths": current_paths,
    "target_texture_paths": {
        "Farm_BaseColor": textures["BaseColor"].get_path_name(),
        "Farm_Normal": textures["Normal"].get_path_name(),
    },
    "current_tile_cm": current_tile_cm,
    "target_tile_cm": target_tile_cm,
    "parameter_node_counts": {parameter: len(nodes) for parameter, nodes in resolved.items()},
    "texture_caps": {"BaseColor": 2048, "Normal": 2048, "ORM": 2048, "Height": 1024},
    "material_expression_count": expression_count_before,
    "saved_packages": saved_packages,
    "policies": {
        "performance": "existing layer substitution; zero added target layers, weightmaps or texture samples",
        "scope": "uses the existing deterministic Farm/RoadsideSilt mask; broad desert Sand layer remains unchanged",
        "source": "original Fab material remains intact; Landscape reads only the verified BaseColor and Normal textures",
    },
    "dirty_after": dirty_packages(),
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_FLOOR_SAND_LANDSCAPE_COMPLETE apply=%s expressions=%d tile=%.1f"
    % (APPLY_CHANGES, expression_count_before, target_tile_cm)
)
print("ABIVERD_FLOOR_SAND_LANDSCAPE_COMPLETE", report_path)
