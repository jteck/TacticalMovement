"""Read-only grounding and occlusion audit for connected-slice preview actors."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
execution = config["execution"]
placement_tag = unreal.Name(execution["placement_tag"])
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
preview = [actor for actor in actors if placement_tag in list(actor.tags)]
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]


def trace(start, end, ignored):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        start,
        end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        ignored,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return None
    result = hit.to_dict()
    return result if result.get("blocking_hit") else None


rows = []
for actor in preview:
    origin, extent = actor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    top_z = origin.z + extent.z
    location = actor.get_actor_location()
    terrain_hit = trace(
        unreal.Vector(location.x, location.y, bottom_z + 100000.0),
        unreal.Vector(location.x, location.y, bottom_z - 100000.0),
        non_landscapes,
    )
    surface_hit = trace(
        unreal.Vector(location.x, location.y, top_z + 5000.0),
        unreal.Vector(location.x, location.y, bottom_z - 5000.0),
        [actor],
    )
    terrain_z = terrain_hit["location"].z if terrain_hit else None
    surface_z = surface_hit["location"].z if surface_hit else None
    surface_actor = surface_hit.get("hit_actor") if surface_hit else None
    surface_label = surface_actor.get_actor_label() if surface_actor else ""
    surface_class = surface_actor.get_class().get_name() if surface_actor else ""
    landscape_gap = None if terrain_z is None else bottom_z - terrain_z
    cover_above_bottom = None if surface_z is None else surface_z - bottom_z
    buried_or_occluded = bool(
        surface_hit
        and surface_actor not in landscapes
        and cover_above_bottom is not None
        and cover_above_bottom > 8.0
    )
    rows.append(
        {
            "actor_label": actor.get_actor_label(),
            "location_cm": {"x": location.x, "y": location.y, "z": location.z},
            "bounds_bottom_z_cm": bottom_z,
            "bounds_top_z_cm": top_z,
            "terrain_z_cm": terrain_z,
            "landscape_gap_cm": landscape_gap,
            "first_surface_z_cm": surface_z,
            "first_surface_actor": surface_label,
            "first_surface_class": surface_class,
            "surface_above_actor_bottom_cm": cover_above_bottom,
            "buried_or_occluded": buried_or_occluded,
        }
    )

buried = [row for row in rows if row["buried_or_occluded"]]
grounded = [
    row
    for row in rows
    if row["landscape_gap_cm"] is not None and abs(row["landscape_gap_cm"]) <= 3.0
]
payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "preview_actor_count": len(preview),
    "terrain_grounded_count": len(grounded),
    "buried_or_occluded_count": len(buried),
    "visible_candidate_count": len(preview) - len(buried),
    "rows": rows,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(
    config, "old_town_connected_slice_visibility_audit.json", payload
)
unreal.log(
    "SUNSCAR_CONNECTED_SLICE_VISIBILITY actors=%d grounded=%d occluded=%d report=%s"
    % (len(preview), len(grounded), len(buried), report)
)
print(
    "SUNSCAR_CONNECTED_SLICE_VISIBILITY",
    len(preview),
    len(grounded),
    len(buried),
    report,
)
