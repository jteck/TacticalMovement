"""Promote the approved Quixel ruin-floor textures into map-owned content.

Fab imports live below /Game/Fab, which this repository intentionally ignores.
This dry-run-first pass duplicates the four texture dependencies into the
Operation Sunscar art tree and repoints only the existing RoadsideSilt/Farm
Landscape inputs.  It does not alter Landscape layers, masks or actors.
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
TARGET_ROOT = (
    "/Game/Maps/Sunscar/Art/Heritage/Surfaces/"
    "HistoricDesertRuinFloorSandCoarse01/Textures/"
)
NAMES = {
    "BaseColor": "T_xbohccs_4k_B",
    "Height": "T_xbohccs_4k_H",
    "Normal": "T_xbohccs_4k_N",
    "ORM": "T_xbohccs_4k_ORM",
}
CAPS = {"BaseColor": 2048, "Height": 1024, "Normal": 2048, "ORM": 2048}
REPORT_NAME = (
    "abiverd_floor_sand_map_owned_apply_v1.json"
    if APPLY_CHANGES else "abiverd_floor_sand_map_owned_dry_run_v1.json"
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
    raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_DIRTY_BEFORE " + "|".join(dirty_packages()))

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
sources = {
    role: unreal.EditorAssetLibrary.load_asset(SOURCE_ROOT + name)
    for role, name in NAMES.items()
}
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_MATERIAL")
if any(not isinstance(texture, unreal.Texture2D) for texture in sources.values()):
    raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_SOURCE")

target_paths = {role: TARGET_ROOT + name for role, name in NAMES.items()}
existing_targets = {
    role: unreal.EditorAssetLibrary.load_asset(path) for role, path in target_paths.items()
}
for role, texture in existing_targets.items():
    if texture is not None and not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_TARGET_TYPE " + role)

parameters = {"Farm_BaseColor": [], "Farm_Normal": [], "Farm_TileCm": []}
for expression in unreal.MaterialEditingLibrary.get_material_expressions(material):
    try:
        name = str(expression.get_editor_property("parameter_name"))
    except Exception:
        continue
    if name in parameters:
        parameters[name].append(expression)
if {name: len(nodes) for name, nodes in parameters.items()} != {
    "Farm_BaseColor": 2,
    "Farm_Normal": 1,
    "Farm_TileCm": 2,
}:
    raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_PARAMETER_COUNTS")

created = []
targets = dict(existing_targets)
saved_packages = []
if APPLY_CHANGES:
    for role, source in sources.items():
        if targets[role] is None:
            targets[role] = unreal.EditorAssetLibrary.duplicate_asset(
                SOURCE_ROOT + NAMES[role], target_paths[role]
            )
            if not isinstance(targets[role], unreal.Texture2D):
                raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_DUPLICATE " + role)
            created.append(target_paths[role])
        targets[role].set_editor_property("max_texture_size", CAPS[role])

    for node in parameters["Farm_BaseColor"]:
        node.set_editor_property("texture", targets["BaseColor"])
    for node in parameters["Farm_Normal"]:
        node.set_editor_property("texture", targets["Normal"])
    for node in parameters["Farm_TileCm"]:
        node.set_editor_property("default_value", 120.0)

    compiler_errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
    if compiler_errors:
        raise RuntimeError(
            "ABIVERD_FLOOR_SAND_MAP_OWNED_COMPILE "
            + "|".join(str(item) for item in compiler_errors)
        )
    allowed = {MATERIAL_PATH} | set(target_paths.values())
    unexpected = [name for name in dirty_packages() if name not in allowed]
    if unexpected:
        raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    saved_packages = sorted(package_name(package) for package in packages)
    if packages and not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_FLOOR_SAND_MAP_OWNED_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "material": MATERIAL_PATH,
    "source_paths": {role: SOURCE_ROOT + name for role, name in NAMES.items()},
    "target_paths": target_paths,
    "targets_existing_before": sorted(role for role, value in existing_targets.items() if value is not None),
    "created": created,
    "caps": CAPS,
    "semantic_layer": "RoadsideSilt / Farm",
    "tile_cm": 120.0,
    "landscape_layers_changed": 0,
    "weightmaps_changed": 0,
    "saved_packages": saved_packages,
    "dirty_after": dirty_packages(),
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_FLOOR_SAND_MAP_OWNED_COMPLETE apply=%s" % APPLY_CHANGES)
print("ABIVERD_FLOOR_SAND_MAP_OWNED_COMPLETE", report_path)
