"""Export three owned facade base-color textures to /private/tmp for visual audit."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
TEXTURES = {
    "wall_paint": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_BaseColor",
    "stucco": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_016_vigrejf/Stucco_Wall_vigrejf_4K_BaseColor",
    "flaked_paint": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_017_vhqkeff/Flaked_Paint_Wall_vhqkeff_4K_BaseColor",
}
OUTPUT_DIR = "/private/tmp/abiverd_facade_reference_textures"


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_EXPORT_FACADE_TEXTURES_WRONG_PROJECT")
if unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages() or unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
    raise RuntimeError("ABIVERD_EXPORT_FACADE_TEXTURES_DIRTY_BEFORE")
os.makedirs(OUTPUT_DIR, exist_ok=True)
rows = []
for key, path in sorted(TEXTURES.items()):
    texture = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("ABIVERD_EXPORT_FACADE_TEXTURES_MISSING " + path)
    output = os.path.join(OUTPUT_DIR, key + ".png")
    task = unreal.AssetExportTask()
    task.object = texture
    task.filename = output
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    task.exporter = unreal.TextureExporterPNG()
    if not unreal.Exporter.run_asset_export_task(task):
        raise RuntimeError("ABIVERD_EXPORT_FACADE_TEXTURES_FAILED " + key)
    rows.append({"key": key, "asset": path, "output": output})
report = {"status": "read_only_export_complete", "textures": rows, "dirty_after": []}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_export_facade_reference_textures_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_EXPORT_FACADE_TEXTURES_COMPLETE count=3")
print("ABIVERD_EXPORT_FACADE_TEXTURES_COMPLETE", report_path)
