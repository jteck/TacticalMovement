"""Read-only transform, collision and support audit for remaining-site scatter."""

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
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in common.actor_tags(actor)]
if len(targets) != 84:
    raise RuntimeError("SUNSCAR_REMAINING_SCATTER_AUDIT_SCOPE actor_count=%d" % len(targets))

records = []
review_required = []
for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(origin.x, origin.y, bottom_z + 50.0),
        unreal.Vector(origin.x, origin.y, bottom_z - 500.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        targets,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    support_z = result["location"].z if result.get("blocking_hit") else None
    support_actor = result.get("hit_actor") if result.get("blocking_hit") else None
    gap = bottom_z - support_z if support_z is not None else None
    rotation = actor.get_actor_rotation()
    component = getattr(actor, "static_mesh_component", None)
    collision = str(component.get_collision_enabled()) if component is not None else ""
    reasons = []
    if support_z is None:
        reasons.append("support_trace_failed")
    elif gap < -3.0 or gap > 3.0:
        reasons.append("support_gap_out_of_tolerance")
    if abs(rotation.pitch) > 0.01 or abs(rotation.roll) > 0.01:
        reasons.append("unexpected_pitch_or_roll")
    if "NO_COLLISION" not in collision:
        reasons.append("collision_not_disabled")
    record = {
        "label": actor.get_actor_label(),
        "site_tags": [tag for tag in common.actor_tags(actor) if tag.startswith("SS_")],
        "mesh_path": common.actor_mesh_path(actor),
        "bottom_z_cm": round(bottom_z, 3),
        "support_z_cm": round(support_z, 3) if support_z is not None else None,
        "support_gap_cm": round(gap, 3) if gap is not None else None,
        "support_actor": support_actor.get_actor_label() if support_actor else "",
        "rotation": {
            "pitch": round(rotation.pitch, 3),
            "yaw": round(rotation.yaw, 3),
            "roll": round(rotation.roll, 3),
        },
        "collision": collision,
        "review_reasons": reasons,
    }
    records.append(record)
    if reasons:
        review_required.append(record)

gaps = [record["support_gap_cm"] for record in records if record["support_gap_cm"] is not None]
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "review_required_count": len(review_required),
    "minimum_support_gap_cm": min(gaps) if gaps else None,
    "maximum_support_gap_cm": max(gaps) if gaps else None,
    "review_required": review_required,
    "records": records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_remaining_scatter_geometry_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_REMAINING_SCATTER_GEOMETRY actors=%d review=%d report=%s"
    % (len(records), len(review_required), report)
)
print("SUNSCAR_REMAINING_SCATTER_GEOMETRY", len(records), len(review_required), report)
