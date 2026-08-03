"""Save exactly the three reviewed Quixel facade material instances."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TARGET_PATHS = [
    "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_WallPaint_Quixel",
    "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_Quixel",
    "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_Quixel",
]
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
assets = [unreal.EditorAssetLibrary.load_asset(path) for path in TARGET_PATHS]
if any(asset is None for asset in assets):
    raise RuntimeError("SUNSCAR_FACADE_MATERIAL_SAVE_REFUSED missing_asset")
packages = [asset.get_package() for asset in assets]
target_names = {package.get_name() for package in packages}
dirty_content = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content != target_names or dirty_maps:
    raise RuntimeError(
        "SUNSCAR_FACADE_MATERIAL_SAVE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps)))
    )
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("SUNSCAR_FACADE_MATERIAL_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
if remaining:
    raise RuntimeError("SUNSCAR_FACADE_MATERIAL_SAVE_DIRTY_AFTER %s" % "|".join(remaining))
payload = {
    "schema_version": 1,
    "status": "exact_facade_material_packages_saved",
    "context": context,
    "saved_packages": sorted(target_names),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_facade_materials_v1.json", payload)
unreal.log("SUNSCAR_FACADE_MATERIAL_SAVE packages=3 report=%s" % report)
print("SUNSCAR_FACADE_MATERIAL_SAVE", report)
