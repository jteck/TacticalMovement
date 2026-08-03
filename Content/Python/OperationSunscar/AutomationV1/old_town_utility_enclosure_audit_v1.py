"""Read-only geometry, material and overlap audit for utility enclosures."""

import math
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
actors = list(common.actor_subsystem().get_all_level_actors())
targets = sorted([actor for actor in actors if TAG in common.actor_tags(actor)], key=lambda actor: actor.get_actor_label())


def tagged_site(actor):
    values = [tag for tag in common.actor_tags(actor) if tag.startswith("SS_")]
    return values[0] if values else ""


def site_geometry(site_id):
    floors = []
    walls = []
    for actor in actors:
        label = actor.get_actor_label()
        if site_id not in label:
            continue
        origin, extent = actor.get_actor_bounds(False)
        if "Floor" in label:
            floors.append((origin.z + extent.z, label, origin, extent))
        if "Wall" in label:
            walls.append((label, origin, extent))
    return floors, walls


def containing_floor(floors, x, y):
    matches = []
    for top_z, label, origin, extent in floors:
        if abs(x - origin.x) <= extent.x + 10.0 and abs(y - origin.y) <= extent.y + 10.0:
            matches.append((top_z, label))
    matches.sort()
    return matches[0] if matches else (None, "")


def nearest_wall_face_clearance(walls, origin, extent):
    values = []
    for label, wall_origin, wall_extent in walls:
        dx = max(abs(origin.x - wall_origin.x) - wall_extent.x, 0.0)
        dy = max(abs(origin.y - wall_origin.y) - wall_extent.y, 0.0)
        center_distance = math.sqrt(dx * dx + dy * dy)
        projected_extent = extent.x if dx >= dy else extent.y
        values.append((center_distance - projected_extent, label))
    values.sort()
    return values[0] if values else (None, "")


def aabb_overlap(origin_a, extent_a, origin_b, extent_b):
    return (
        abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x
        and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y
        and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z
    )


records = []
review = []
target_bounds = []
for actor in targets:
    tags = common.actor_tags(actor)
    site_id = tagged_site(actor)
    bom_id = "OT_UTIL_003" if "OT_UTIL_003" in tags else "OT_UTIL_002"
    mode = "ground_standing" if bom_id == "OT_UTIL_003" else "wall_mounted"
    floors, walls = site_geometry(site_id)
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    floor_z, floor_label = containing_floor(floors, origin.x, origin.y)
    rotation = actor.get_actor_rotation()
    component = actor.static_mesh_component
    materials = [component.get_material(index).get_path_name() if component.get_material(index) else "" for index in range(component.get_num_materials())]
    reasons = []
    expected_offset = 0.0 if mode == "ground_standing" else 40.0
    support_gap = bottom - floor_z if floor_z is not None else None
    if support_gap is None or abs(support_gap - expected_offset) > 3.0:
        reasons.append("support_height")
    clearance, wall_label = nearest_wall_face_clearance(walls, origin, extent)
    if mode == "wall_mounted" and (clearance is None or clearance < -1.0 or clearance > 10.0):
        reasons.append("facade_clearance")
    if abs(rotation.pitch) > 0.01 or abs(rotation.roll) > 0.01:
        reasons.append("unexpected_pitch_or_roll")
    collision = str(component.get_collision_enabled())
    if mode == "wall_mounted" and "NO_COLLISION" not in collision:
        reasons.append("wall_box_collision")
    if mode == "ground_standing" and "QUERY_AND_PHYSICS" not in collision:
        reasons.append("cabinet_collision")
    if not materials or any(not value for value in materials):
        reasons.append("missing_material")
    overlaps = []
    if mode == "ground_standing":
        for other in actors:
            if other in targets:
                continue
            label = other.get_actor_label()
            if "Floor" in label or label.startswith("Ground_") or label.startswith("District_") or label.startswith("Route_"):
                continue
            other_origin, other_extent = other.get_actor_bounds(False)
            if other_extent.z <= 20.0:
                continue
            if aabb_overlap(origin, extent, other_origin, other_extent):
                overlaps.append(label)
        if overlaps:
            reasons.append("ground_cabinet_overlap")
    record = {
        "label": actor.get_actor_label(),
        "site_id": site_id,
        "bom_id": bom_id,
        "mode": mode,
        "floor_actor": floor_label,
        "support_offset_cm": round(support_gap, 3) if support_gap is not None else None,
        "nearest_wall": wall_label,
        "facade_clearance_cm": round(clearance, 3) if clearance is not None else None,
        "dimensions_cm": [round(extent.x * 2.0, 3), round(extent.y * 2.0, 3), round(extent.z * 2.0, 3)],
        "collision": collision,
        "materials": materials,
        "overlap_labels": sorted(set(overlaps)),
        "review_reasons": reasons,
    }
    records.append(record)
    target_bounds.append((actor.get_actor_label(), origin, extent))
    if reasons:
        review.append(record)

pair_overlaps = []
for index, (label_a, origin_a, extent_a) in enumerate(target_bounds):
    for label_b, origin_b, extent_b in target_bounds[index + 1:]:
        if aabb_overlap(origin_a, extent_a, origin_b, extent_b):
            pair_overlaps.append([label_a, label_b])

payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "actor_count": len(records),
    "expected_actor_count": 10,
    "review_required_count": len(review),
    "pair_overlap_count": len(pair_overlaps),
    "pair_overlaps": pair_overlaps,
    "review_required": review,
    "records": records,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_utility_enclosure_audit_v1.json", payload)
unreal.log("SUNSCAR_UTILITY_ENCLOSURE_AUDIT actors=%d review=%d pairs=%d report=%s" % (len(records), len(review), len(pair_overlaps), report))
print("SUNSCAR_UTILITY_ENCLOSURE_AUDIT", len(records), len(review), len(pair_overlaps), report)
