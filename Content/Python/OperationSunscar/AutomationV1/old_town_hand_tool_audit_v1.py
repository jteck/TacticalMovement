"""Read-only support, orientation, collision and overlap audit for Salvage Yard tools."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownHandToolV1"
EXPECTED_ACTORS = 9
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
world = common.editor_world()
all_actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in all_actors if TAG in common.actor_tags(actor)]
visual_overlays = [actor for actor in all_actors if "VisualGroundOverlay" in common.actor_tags(actor)]
if len(targets) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_HAND_TOOL_AUDIT_SCOPE actor_count=%d" % len(targets))


def overlap_3d(actor_a, actor_b, shrink=0.88):
    origin_a, extent_a = actor_a.get_actor_bounds(False)
    origin_b, extent_b = actor_b.get_actor_bounds(False)
    return (
        abs(origin_a.x - origin_b.x) < (extent_a.x + extent_b.x) * shrink
        and abs(origin_a.y - origin_b.y) < (extent_a.y + extent_b.y) * shrink
        and abs(origin_a.z - origin_b.z) < (extent_a.z + extent_b.z) * shrink
    )


def visual_overlay_support(x, y, bottom_z):
    candidates = []
    for overlay in visual_overlays:
        overlay_origin, overlay_extent = overlay.get_actor_bounds(False)
        if abs(x - overlay_origin.x) > overlay_extent.x or abs(y - overlay_origin.y) > overlay_extent.y:
            continue
        top_z = overlay_origin.z + overlay_extent.z
        gap = bottom_z - top_z
        if -3.0 <= gap <= 30.0:
            candidates.append((top_z, overlay))
    return max(candidates, key=lambda item: item[0]) if candidates else (None, None)


pair_overlaps = []
for index, actor_a in enumerate(targets):
    for actor_b in targets[index + 1:]:
        if overlap_3d(actor_a, actor_b):
            pair_overlaps.append([actor_a.get_actor_label(), actor_b.get_actor_label()])

records = []
review_required = []
for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(origin.x, origin.y, bottom_z + 35.0),
        unreal.Vector(origin.x, origin.y, bottom_z - 300.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        targets,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    support_z = result["location"].z if result.get("blocking_hit") else None
    support_actor = result.get("hit_actor") if result.get("blocking_hit") else None
    overlay_z, overlay_actor = visual_overlay_support(origin.x, origin.y, bottom_z)
    if overlay_z is not None and (support_z is None or overlay_z > support_z):
        support_z = overlay_z
        support_actor = overlay_actor
    gap = bottom_z - support_z if support_z is not None else None
    component = actor.static_mesh_component
    collision = str(component.get_collision_enabled())
    rotation = actor.get_actor_rotation()
    tags = common.actor_tags(actor)
    kind = "shovel_flat" if "shovel_flat" in tags else "support_stand_upright"
    reasons = []
    if support_z is None:
        reasons.append("support_trace_failed")
    elif gap < -3.0 or gap > 3.0:
        reasons.append("support_gap_out_of_tolerance")
    if "NO_COLLISION" not in collision:
        reasons.append("collision_not_disabled")
    if abs(rotation.roll) > 0.05 or abs(rotation.pitch) > 0.05:
        reasons.append("unexpected_pitch_or_roll")
    if kind == "shovel_flat" and (extent.z * 2.0 > 30.0 or max(extent.x, extent.y) * 2.0 < 70.0):
        reasons.append("shovel_orientation_not_flat")
    if kind == "support_stand_upright" and (extent.z * 2.0 < 90.0 or max(extent.x, extent.y) * 2.0 < 180.0):
        reasons.append("support_stand_orientation_unexpected")
    record = {
        "label": actor.get_actor_label(),
        "asset_kind": kind,
        "mesh_path": common.actor_mesh_path(actor),
        "dimensions_cm": {"x": round(extent.x * 2.0, 3), "y": round(extent.y * 2.0, 3), "z": round(extent.z * 2.0, 3)},
        "rotation_deg": {"pitch": round(rotation.pitch, 3), "yaw": round(rotation.yaw, 3), "roll": round(rotation.roll, 3)},
        "bottom_z_cm": round(bottom_z, 3),
        "support_z_cm": round(support_z, 3) if support_z is not None else None,
        "support_gap_cm": round(gap, 3) if gap is not None else None,
        "support_actor": support_actor.get_actor_label() if support_actor else "",
        "collision": collision,
        "review_reasons": reasons,
    }
    records.append(record)
    if reasons:
        review_required.append(record)

dirty_content = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
dirty_maps = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "review_required_count": len(review_required),
    "pair_overlap_count": len(pair_overlaps),
    "pair_overlaps": pair_overlaps,
    "review_required": review_required,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_hand_tool_audit_v1.json", payload)
unreal.log("SUNSCAR_HAND_TOOL_AUDIT actors=%d review=%d overlaps=%d dirty_maps=%d report=%s" % (len(records), len(review_required), len(pair_overlaps), len(dirty_maps), report))
print("SUNSCAR_HAND_TOOL_AUDIT", len(records), len(review_required), len(pair_overlaps), len(dirty_maps), report)
