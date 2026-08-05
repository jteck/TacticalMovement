"""Import and configure the five approved Abiverd surface sources, unsaved."""

import json
import os
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ROOT = "/Game/Maps/Sunscar/Art/Heritage/Surfaces"

DEFINITIONS = (
    ("ABV_ASSET_004", "Wild Grass Ground", "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Wild_Grass-1a4cd0a2/texture-set/wild_grass_xbreagf_4k_extracted", ROOT + "/WildGrassGround"),
    ("ABV_ASSET_005", "Dry Trampled Soil", "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Dry_Trampled_Soil-e9c8521d/texture-set/dry_trampled_soil_wcivbf_extracted", ROOT + "/DryTrampledSoil"),
    ("ABV_ASSET_006", "Cracked Mud Wall", "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Cracked_Mud_Wall-381158fe/texture-set/cracked_mud_wall_th5kcij_extracted", ROOT + "/CrackedMudWall"),
    ("ABV_ASSET_008", "Historic Desert Ruin Wall Brick 03", "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Historic_Desert_Ruin_Wall_Brick_03-9d643c9c/texture-set/historic_desert_ruin_wal_extracted", ROOT + "/RuinWallBrick03"),
    ("ABV_ASSET_012", "Historic Pakistan Street Wall Brick White 01", "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Historic_Pakistan_Street_Wall_Brick_White_01-f372a8f7/texture-set/historic_pakistan_street_extracted", ROOT + "/BrickWhite01"),
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
    raise RuntimeError("ABIVERD_SURFACE_IMPORT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_SURFACE_IMPORT_WRONG_LEVEL " + level_path)

dirty_before = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
if dirty_before:
    raise RuntimeError("ABIVERD_SURFACE_IMPORT_PREEXISTING_DIRTY " + repr(dirty_before))

for record_id, name, source_root, destination in DEFINITIONS:
    if not os.path.isdir(source_root):
        raise RuntimeError("ABIVERD_SURFACE_IMPORT_SOURCE_MISSING " + source_root)
    if unreal.EditorAssetLibrary.does_directory_exist(destination):
        existing = unreal.EditorAssetLibrary.list_assets(destination, recursive=True)
        if existing:
            raise RuntimeError("ABIVERD_SURFACE_IMPORT_DESTINATION_NOT_EMPTY %s %s" % (destination, repr(existing)))

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
records = []
for record_id, name, source_root, destination in DEFINITIONS:
    selected = []
    for filename in sorted(os.listdir(source_root)):
        lower = filename.lower()
        if not lower.endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
            continue
        if any(token in lower for token in ("basecolor", "_normal", "roughness", "_ao")):
            selected.append(os.path.join(source_root, filename))
    if len(selected) != 4:
        raise RuntimeError("ABIVERD_SURFACE_IMPORT_SOURCE_SCOPE %s %s" % (record_id, repr(selected)))

    tasks = []
    for source in selected:
        task = unreal.AssetImportTask()
        task.filename = source
        task.destination_path = destination
        task.automated = True
        task.replace_existing = False
        task.save = False
        tasks.append(task)
    asset_tools.import_asset_tasks(tasks)
    imported_paths = [str(path) for task in tasks for path in task.imported_object_paths]
    if len(imported_paths) != 4:
        raise RuntimeError("ABIVERD_SURFACE_IMPORT_RESULT_SCOPE %s %s" % (record_id, repr(imported_paths)))

    role_paths = {}
    for path in imported_paths:
        texture = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(texture, unreal.Texture2D):
            raise RuntimeError("ABIVERD_SURFACE_IMPORT_NON_TEXTURE " + path)
        lower = texture.get_name().lower()
        if "basecolor" in lower:
            role = "BaseColor"
            texture.modify()
            texture.set_editor_property("srgb", True)
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
        elif "_normal" in lower:
            role = "Normal"
            texture.modify()
            texture.set_editor_property("srgb", False)
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        elif "roughness" in lower:
            role = "Roughness"
            texture.modify()
            texture.set_editor_property("srgb", False)
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        elif "_ao" in lower:
            role = "AO"
            texture.modify()
            texture.set_editor_property("srgb", False)
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        else:
            raise RuntimeError("ABIVERD_SURFACE_IMPORT_ROLE_UNKNOWN " + path)
        role_paths[role] = path
    if set(role_paths) != {"BaseColor", "Normal", "Roughness", "AO"}:
        raise RuntimeError("ABIVERD_SURFACE_IMPORT_ROLE_SCOPE %s %s" % (record_id, repr(role_paths)))
    records.append(
        {
            "record_id": record_id,
            "name": name,
            "source_root": source_root,
            "destination": destination,
            "textures": role_paths,
        }
    )

dirty_after = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
unexpected_dirty = [name for name in dirty_after if not name.startswith(ROOT + "/")]
if len(dirty_after) != 20 or unexpected_dirty:
    raise RuntimeError("ABIVERD_SURFACE_IMPORT_DIRTY_SCOPE count=%d unexpected=%s" % (len(dirty_after), repr(unexpected_dirty)))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_heritage_surfaces_stage_import_v1.json")
payload = {
    "schema_version": 1,
    "status": "surface_stage_import_unsaved_complete",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "records": records,
    "dirty_packages_before": dirty_before,
    "dirty_packages_after": dirty_after,
    "unexpected_dirty_packages": unexpected_dirty,
    "level_changed": False,
    "level_saved": False,
    "asset_packages_saved": False,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_SURFACE_IMPORT_COMPLETE assets=20 report=" + report_path)
print("ABIVERD_SURFACE_IMPORT_COMPLETE", report_path)
