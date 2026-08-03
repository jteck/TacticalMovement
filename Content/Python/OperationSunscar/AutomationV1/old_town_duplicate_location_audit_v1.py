"""Read-only audit of StaticMeshActor transform-location duplicates reported by Map Check."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
groups = collections.defaultdict(list)
for actor in common.actor_subsystem().get_all_level_actors():
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    location = actor.get_actor_location()
    key = (round(location.x, 3), round(location.y, 3), round(location.z, 3))
    component = actor.static_mesh_component
    bounds_origin, bounds_extent = actor.get_actor_bounds(False)
    groups[key].append(
        {
            "label": actor.get_actor_label(),
            "folder": common.actor_folder(actor),
            "tags": common.actor_tags(actor),
            "location_cm": list(key),
            "bounds_origin_cm": [round(bounds_origin.x, 3), round(bounds_origin.y, 3), round(bounds_origin.z, 3)],
            "bounds_extent_cm": [round(bounds_extent.x, 3), round(bounds_extent.y, 3), round(bounds_extent.z, 3)],
            "mesh_path": common.actor_mesh_path(actor),
            "visible": bool(component.get_editor_property("visible")),
            "collision": str(component.get_collision_enabled()),
            "package": actor.get_package().get_name(),
        }
    )
duplicate_groups = [
    {"location_cm": list(key), "actor_count": len(records), "actors": sorted(records, key=lambda row: row["label"])}
    for key, records in groups.items()
    if len(records) > 1
]
duplicate_groups.sort(key=lambda group: tuple(group["location_cm"]))
dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "schema_version": 1,
    "status": "read_only_duplicate_location_audit_complete",
    "context": context,
    "duplicate_group_count": len(duplicate_groups),
    "duplicate_actor_count": sum(group["actor_count"] for group in duplicate_groups),
    "groups": duplicate_groups,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_duplicate_location_audit_v1.json", payload)
unreal.log("SUNSCAR_DUPLICATE_LOCATION_AUDIT groups=%d actors=%d report=%s" % (len(duplicate_groups), payload["duplicate_actor_count"], report))
print("SUNSCAR_DUPLICATE_LOCATION_AUDIT", len(duplicate_groups), report)
