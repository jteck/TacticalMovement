"""Import the 35 approved standalone Quixel archives into a map-only library.

This script writes assets but never edits or saves the current level. Existing
assets are never replaced. A complete result manifest is written under Saved.
"""

import json
import os
import re
import zipfile
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
INVENTORY = "/Users/jasonteck/Documents/UE FPS Project/MapDesign/Desert_Glory_Inspired/Planning/OldTown_DownloadedAssetInventory_v1.json"
MAP_DESIGN_ROOT = "/Users/jasonteck/Documents/UE FPS Project/MapDesign/Desert_Glory_Inspired"
DESTINATION_ROOT = "/Game/Maps/Sunscar/Art/Quixel/Downloaded"


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT:
    raise RuntimeError("SUNSCAR_IMPORT_WRONG_PROJECT " + project_name)
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("SUNSCAR_IMPORT_WRONG_DIRECTORY " + project_directory)
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("SUNSCAR_IMPORT_WRONG_LEVEL " + level_path)

with open(INVENTORY, "r", encoding="utf-8") as handle:
    inventory = json.load(handle)

staging_root = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "ImportStaging", "QuixelDownloaded"
)
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(staging_root, exist_ok=True)
os.makedirs(report_root, exist_ok=True)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
results = []

for record in inventory["directAssets"]:
    record_id = record["recordId"]
    megascans_id = record["megascansId"]
    archive_path = os.path.join(MAP_DESIGN_ROOT, record["localArchive"])
    if not os.path.isfile(archive_path):
        results.append({
            "record_id": record_id,
            "megascans_id": megascans_id,
            "archive": archive_path,
            "status": "archive_missing",
            "imported_object_paths": [],
        })
        continue

    extract_directory = os.path.join(staging_root, record_id + "_" + megascans_id)
    os.makedirs(extract_directory, exist_ok=True)
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(extract_directory)

    source_files = []
    for root, _directories, files in os.walk(extract_directory):
        for filename in sorted(files):
            if os.path.splitext(filename)[1].lower() in {".fbx", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
                source_files.append(os.path.join(root, filename))

    destination = "%s/%s_%s" % (DESTINATION_ROOT, record_id, megascans_id)
    tasks = []
    for source_file in source_files:
        task = unreal.AssetImportTask()
        task.filename = source_file
        task.destination_path = destination
        task.automated = True
        task.replace_existing = False
        task.save = True
        tasks.append(task)

    imported_paths = []
    errors = []
    if tasks:
        try:
            asset_tools.import_asset_tasks(tasks)
            for task in tasks:
                imported_paths.extend(str(path) for path in task.imported_object_paths)
        except Exception as exc:
            errors.append(repr(exc))

    status = "imported" if imported_paths and not errors else "import_failed"
    results.append({
        "record_id": record_id,
        "megascans_id": megascans_id,
        "listing_name": record["listingName"],
        "archive": archive_path,
        "destination": destination,
        "source_file_count": len(source_files),
        "imported_object_count": len(imported_paths),
        "imported_object_paths": imported_paths,
        "errors": errors,
        "status": status,
    })
    unreal.log(
        "SUNSCAR_QUX_LIBRARY_ITEM %s %s imported=%d errors=%d"
        % (record_id, megascans_id, len(imported_paths), len(errors))
    )

summary = {}
for result in results:
    summary[result["status"]] = summary.get(result["status"], 0) + 1

payload = {
    "schema_version": 1,
    "status": "quixel_downloaded_library_import_complete",
    "verified_context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "inventory": INVENTORY,
    "destination_root": DESTINATION_ROOT,
    "archive_count": len(results),
    "summary": summary,
    "results": results,
    "level_changed": False,
    "level_saved": False,
    "replace_existing": False,
}
report_path = os.path.join(report_root, "old_town_quixel_downloaded_library_import.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("SUNSCAR_QUX_LIBRARY_COMPLETE " + repr(summary) + " report=" + report_path)
print("SUNSCAR_QUX_LIBRARY_COMPLETE", summary, report_path)
