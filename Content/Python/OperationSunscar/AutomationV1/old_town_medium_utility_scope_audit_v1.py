"""Read-only ownership audit for the ten accepted medium utility enclosures."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownUtilityEnclosuresV1"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
targets = [actor for actor in common.actor_subsystem().get_all_level_actors() if TAG in common.actor_tags(actor)]
target_packages = {actor.get_package().get_name(): actor.get_actor_label() for actor in targets}
dirty_content = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
dirty_maps = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
extra_packages = sorted(set(dirty_maps) - set(target_packages))
registry = unreal.AssetRegistryHelpers.get_asset_registry()
extra_records = []
for package_name in extra_packages:
    assets = registry.get_assets_by_package_name(unreal.Name(package_name), False, False)
    classes = sorted(str(data.asset_class_path) for data in assets)
    extra_records.append({"package": package_name, "asset_classes": classes})
folders_valid = all(
    record["package"].startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")
    and len(record["asset_classes"]) == 1
    and "ActorFolder" in record["asset_classes"][0]
    for record in extra_records
)
safe_scope = (
    len(targets) == 10
    and not dirty_content
    and len(target_packages) == 10
    and len(extra_records) == 5
    and folders_valid
    and len(dirty_maps) == 15
)
payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "target_actor_count": len(targets),
    "target_actor_packages": target_packages,
    "dirty_content_packages": sorted(dirty_content),
    "dirty_map_package_count": len(dirty_maps),
    "external_folder_package_count": len(extra_records),
    "external_folder_packages": extra_records,
    "folders_valid": folders_valid,
    "safe_scope": safe_scope,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_medium_utility_scope_audit_v1.json", payload)
unreal.log("SUNSCAR_MEDIUM_UTILITY_SCOPE actors=%d dirty=%d folders=%d safe=%s report=%s" % (len(targets), len(dirty_maps), len(extra_records), safe_scope, report))
print("SUNSCAR_MEDIUM_UTILITY_SCOPE", len(targets), len(dirty_maps), len(extra_records), safe_scope, report)
