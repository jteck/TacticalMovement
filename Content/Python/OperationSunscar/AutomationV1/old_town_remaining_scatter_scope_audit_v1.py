"""Read-only comparison of remaining-scatter actor packages and dirty packages."""

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
all_actors = list(common.actor_subsystem().get_all_level_actors())
target_actors = [actor for actor in all_actors if TAG in common.actor_tags(actor)]
target_by_package = {actor.get_package().get_name(): actor.get_actor_label() for actor in target_actors}
all_by_package = {}
for actor in all_actors:
    all_by_package.setdefault(actor.get_package().get_name(), []).append(actor.get_actor_label())

dirty_content = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
dirty_map_objects = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
dirty_maps = [package.get_name() for package in dirty_map_objects]
unexpected = sorted(set(dirty_maps) - set(target_by_package))


def package_objects(package):
    records = []
    try:
        objects = unreal.get_objects_with_outer(package, True)
    except Exception as exc:
        return [{"enumeration_error": str(exc)}]
    for obj in objects:
        chain = []
        current = obj
        owner_actor = ""
        for _index in range(8):
            if current is None:
                break
            chain.append({"class": current.get_class().get_name(), "path": current.get_path_name()})
            if isinstance(current, unreal.Actor):
                owner_actor = current.get_actor_label()
            try:
                current = current.get_outer()
            except Exception:
                break
        records.append({
            "class": obj.get_class().get_name(),
            "path": obj.get_path_name(),
            "owner_actor_label": owner_actor,
            "outer_chain": chain,
        })
    return records


dirty_map_by_name = {package.get_name(): package for package in dirty_map_objects}
try:
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_registry_error = ""
except Exception as exc:
    asset_registry = None
    asset_registry_error = str(exc)


def registry_records(package_name):
    if asset_registry is None:
        return [{"registry_error": asset_registry_error}]
    records = []
    try:
        assets = asset_registry.get_assets_by_package_name(unreal.Name(package_name), False, False)
    except Exception as exc:
        return [{"registry_error": str(exc)}]
    for data in assets:
        try:
            records.append({
                "asset_name": str(data.asset_name),
                "asset_class_path": str(data.asset_class_path),
                "package_name": str(data.package_name),
            })
        except Exception as exc:
            records.append({"asset_record_error": str(exc)})
    return records
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "target_actor_count": len(target_actors),
    "target_package_count": len(target_by_package),
    "dirty_content_packages": sorted(dirty_content),
    "dirty_map_package_count": len(dirty_maps),
    "unexpected_dirty_packages": [
        {
            "package": package,
            "loaded_actor_labels": sorted(all_by_package.get(package, [])),
            "objects": package_objects(dirty_map_by_name[package]),
            "asset_registry": registry_records(package),
        }
        for package in unexpected
    ],
    "missing_dirty_target_packages": sorted(set(target_by_package) - set(dirty_maps)),
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_remaining_scatter_scope_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_REMAINING_SCATTER_SCOPE target=%d dirty=%d unexpected=%d report=%s"
    % (len(target_by_package), len(dirty_maps), len(unexpected), report)
)
print("SUNSCAR_REMAINING_SCATTER_SCOPE", len(target_by_package), len(dirty_maps), len(unexpected), report)
