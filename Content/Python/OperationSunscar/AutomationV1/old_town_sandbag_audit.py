"""Read-only sandbag transform, attachment and support audit for Old Town."""

import os
import statistics
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
audit = config["sandbag_audit"]
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
world = common.editor_world()


def is_sandbag_actor(actor):
    label = actor.get_actor_label()
    mesh_path = common.actor_mesh_path(actor)
    tags = common.actor_tags(actor)
    return (
        common.has_any_term(label, audit["label_terms"])
        or common.has_any_term(mesh_path, audit["mesh_path_terms"])
        or any(tag in audit["tag_terms"] for tag in tags)
    )


def trace(start, end, ignored):
    result = unreal.SystemLibrary.line_trace_single(
        world,
        start,
        end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        ignored,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    return result.to_dict()


sandbags = [actor for actor in actors if is_sandbag_actor(actor)]
records = []

landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscape_actors = [actor for actor in actors if actor not in landscapes]

for actor in sandbags:
    label = actor.get_actor_label()
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    origin, extent = actor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    parent = actor.get_attach_parent_actor()
    parent_label = parent.get_actor_label() if parent else ""
    parent_class = parent.get_class().get_name() if parent else ""
    mesh_path = common.actor_mesh_path(actor)
    tags = common.actor_tags(actor)

    support_result = trace(
        unreal.Vector(origin.x, origin.y, bottom_z + audit["trace_above_cm"]),
        unreal.Vector(origin.x, origin.y, bottom_z - audit["trace_below_cm"]),
        [actor],
    )
    support_actor = support_result.get("hit_actor")
    support_label = support_actor.get_actor_label() if support_actor else ""
    support_class = support_actor.get_class().get_name() if support_actor else ""
    support_z = support_result.get("location").z if support_result.get("blocking_hit") else None
    support_gap_cm = bottom_z - support_z if support_z is not None else None

    terrain_result = trace(
        unreal.Vector(origin.x, origin.y, bottom_z + audit["trace_above_cm"]),
        unreal.Vector(origin.x, origin.y, bottom_z - audit["trace_below_cm"]),
        non_landscape_actors,
    )
    terrain_z = terrain_result.get("location").z if terrain_result.get("blocking_hit") else None
    above_terrain_cm = bottom_z - terrain_z if terrain_z is not None else None

    flags = []
    if parent:
        flags.append("attached_to_actor")
    if support_gap_cm is None:
        flags.append("no_support_hit")
    elif support_gap_cm > audit["support_tolerance_cm"]:
        flags.append("support_gap")
    if above_terrain_cm is not None and above_terrain_cm > audit["upper_elevation_review_cm"]:
        flags.append("upper_elevation_review")
    if support_actor and support_actor != parent and parent:
        flags.append("attachment_support_mismatch")
    if any(tag in audit["tag_terms"] for tag in tags):
        flags.append("created_by_known_sandbag_script")

    records.append(
        {
            "label": label,
            "class": actor.get_class().get_name(),
            "mesh_path": mesh_path,
            "folder": common.actor_folder(actor),
            "tags": ";".join(tags),
            "location_x_cm": round(location.x, 3),
            "location_y_cm": round(location.y, 3),
            "location_z_cm": round(location.z, 3),
            "bottom_z_cm": round(bottom_z, 3),
            "rotation_pitch": round(rotation.pitch, 3),
            "rotation_yaw": round(rotation.yaw, 3),
            "rotation_roll": round(rotation.roll, 3),
            "scale_x": round(scale.x, 5),
            "scale_y": round(scale.y, 5),
            "scale_z": round(scale.z, 5),
            "parent_label": parent_label,
            "parent_class": parent_class,
            "support_label": support_label,
            "support_class": support_class,
            "support_z_cm": round(support_z, 3) if support_z is not None else "",
            "support_gap_cm": round(support_gap_cm, 3) if support_gap_cm is not None else "",
            "terrain_z_cm": round(terrain_z, 3) if terrain_z is not None else "",
            "above_terrain_cm": round(above_terrain_cm, 3) if above_terrain_cm is not None else "",
            "flags": ";".join(flags),
            "review_required": bool(flags),
        }
    )

bottom_values = [record["bottom_z_cm"] for record in records]
median_bottom = statistics.median(bottom_values) if bottom_values else None
if median_bottom is not None:
    for record in records:
        if record["bottom_z_cm"] > median_bottom + audit["upper_elevation_review_cm"]:
            existing = [flag for flag in record["flags"].split(";") if flag]
            if "global_z_outlier" not in existing:
                existing.append("global_z_outlier")
            record["flags"] = ";".join(existing)
            record["review_required"] = True

headers = [
    "label", "class", "mesh_path", "folder", "tags",
    "location_x_cm", "location_y_cm", "location_z_cm", "bottom_z_cm",
    "rotation_pitch", "rotation_yaw", "rotation_roll", "scale_x", "scale_y", "scale_z",
    "parent_label", "parent_class", "support_label", "support_class",
    "support_z_cm", "support_gap_cm", "terrain_z_cm", "above_terrain_cm",
    "flags", "review_required",
]

json_payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "sandbag_actor_count": len(records),
    "review_required_count": sum(1 for record in records if record["review_required"]),
    "median_bottom_z_cm": median_bottom,
    "thresholds": audit,
    "known_risk": "Earlier scripts derive site base from the first actor whose label starts with a site ID; this must not be trusted as a ground datum without tracing.",
    "records": records,
    "changes_made": False,
}

json_path = common.write_json_report(config, "old_town_sandbag_audit.json", json_payload)
csv_path = common.write_csv_report(config, "old_town_sandbag_audit.csv", records, headers)
unreal.log(
    "SUNSCAR_SANDBAG_AUDIT actors=%d review=%d json=%s csv=%s"
    % (len(records), json_payload["review_required_count"], json_path, csv_path)
)
print("SUNSCAR_SANDBAG_AUDIT", len(records), json_payload["review_required_count"], json_path, csv_path)
