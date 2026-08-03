"""Read-only geometry and nearby-visual audit for the 34 Old Town core cover proxies."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
targets = sorted(
    [actor for actor in actors if common.actor_folder(actor).startswith("Sunscar/CorePlayable/Cover/")],
    key=lambda actor: actor.get_actor_label(),
)


def visual_candidate(actor):
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    tags = common.actor_tags(actor)
    if actor in targets or getattr(actor, "static_mesh_component", None) is None:
        return False
    if label.startswith("COL_") or "TemporaryLabel" in tags or "VisualGroundOverlay" in tags:
        return False
    if "Landscape" in actor.get_class().get_name():
        return False
    if folder.startswith("Sunscar/CorePlayable/Routes/") or folder.startswith("OldTown_Ground"):
        return False
    return True


visuals = [actor for actor in actors if visual_candidate(actor)]
records = []
for actor in targets:
    origin, extent = actor.get_actor_bounds(False)
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    component = actor.static_mesh_component
    material = component.get_material(0) if component.get_num_materials() else None
    neighbors = []
    for candidate in visuals:
        candidate_origin, candidate_extent = candidate.get_actor_bounds(False)
        distance = math.hypot(candidate_origin.x - origin.x, candidate_origin.y - origin.y)
        if distance > 800.0:
            continue
        neighbors.append(
            {
                "label": candidate.get_actor_label(),
                "folder": common.actor_folder(candidate),
                "distance_xy_cm": round(distance, 3),
                "location_cm": [round(candidate_origin.x, 3), round(candidate_origin.y, 3), round(candidate_origin.z, 3)],
                "extent_cm": [round(candidate_extent.x, 3), round(candidate_extent.y, 3), round(candidate_extent.z, 3)],
                "mesh_path": common.actor_mesh_path(candidate),
                "tags": common.actor_tags(candidate),
            }
        )
    neighbors.sort(key=lambda row: (row["distance_xy_cm"], row["label"]))
    records.append(
        {
            "label": actor.get_actor_label(),
            "role": "hard_cover" if common.actor_folder(actor).endswith("HardCover") else "vehicle_proxy",
            "folder": common.actor_folder(actor),
            "tags": common.actor_tags(actor),
            "location_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
            "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
            "rotation": {"pitch": round(rotation.pitch, 3), "yaw": round(rotation.yaw, 3), "roll": round(rotation.roll, 3)},
            "scale": [round(scale.x, 4), round(scale.y, 4), round(scale.z, 4)],
            "mesh_path": common.actor_mesh_path(actor),
            "material_path": material.get_path_name() if material else "",
            "collision": str(component.get_collision_enabled()),
            "nearby_visuals": neighbors[:8],
            "package": actor.get_package().get_name(),
        }
    )
dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "schema_version": 1,
    "status": "read_only_core_cover_proxy_audit_complete",
    "context": context,
    "actor_count": len(records),
    "hard_cover_count": sum(record["role"] == "hard_cover" for record in records),
    "vehicle_proxy_count": sum(record["role"] == "vehicle_proxy" for record in records),
    "records": records,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_core_cover_proxy_audit_v1.json", payload)
unreal.log("SUNSCAR_CORE_COVER_AUDIT actors=%d dirty=%d report=%s" % (len(records), len(dirty), report))
print("SUNSCAR_CORE_COVER_AUDIT", len(records), report)
