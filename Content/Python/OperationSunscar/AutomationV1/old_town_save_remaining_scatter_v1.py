"""Save exactly the remaining-site scatter actor packages."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownRemainingScatterV1"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = [
    actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if TAG in common.actor_tags(actor)
]
if len(actors) < 40 or len(actors) > 180:
    raise RuntimeError("SUNSCAR_REMAINING_SCATTER_SAVE_REFUSED actor_count=%d" % len(actors))

target_packages = {actor.get_package() for actor in actors}
target_names = {package.get_name() for package in target_packages}
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
dirty_names = {package.get_name() for package in dirty_maps}
external_object_packages = []
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
for package in dirty_maps:
    name = package.get_name()
    if name in target_names:
        continue
    if not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"):
        continue
    assets = asset_registry.get_assets_by_package_name(unreal.Name(name), False, False)
    if len(assets) != 1 or str(assets[0].asset_class_path.asset_name) != "ActorFolder":
        continue
    external_object_packages.append(package)
external_object_names = {package.get_name() for package in external_object_packages}
allowed_names = target_names | external_object_names
unexpected = sorted(dirty_names - allowed_names)
missing = sorted(target_names - dirty_names)
if len(external_object_packages) != 8 or dirty_content or unexpected or missing:
    raise RuntimeError(
        "SUNSCAR_REMAINING_SCATTER_SAVE_REFUSED content=%d folders=%d unexpected=%s missing=%s"
        % (len(dirty_content), len(external_object_packages), "|".join(unexpected), "|".join(missing))
    )
packages_to_save = target_packages | set(external_object_packages)
if not unreal.EditorLoadingAndSavingUtils.save_packages(list(packages_to_save), True):
    raise RuntimeError("SUNSCAR_REMAINING_SCATTER_SAVE_FAILED")

remaining = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package.get_name() in target_names
)
payload = {
    "schema_version": 1,
    "status": "exact_packages_saved",
    "context": context,
    "actor_count": len(actors),
    "actor_package_count": len(target_packages),
    "actor_folder_package_count": len(external_object_packages),
    "package_count": len(packages_to_save),
    "saved_actor_packages": sorted(target_names),
    "saved_actor_folder_packages": sorted(external_object_names),
    "saved_packages": sorted(allowed_names),
    "remaining_target_dirty_packages": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_remaining_scatter_v1.json", payload)
unreal.log(
    "SUNSCAR_REMAINING_SCATTER_SAVE packages=%d remaining=%d report=%s"
    % (len(target_packages), len(remaining), report)
)
print("SUNSCAR_REMAINING_SCATTER_SAVE", len(target_packages), report)
