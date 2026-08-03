"""Read-only support, collision and overlap audit for resolved large cabinets."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownLargeUtilityResolvedV1"
FLOORS = {
    "SS_003": "Core_SS_003_F1_Floor",
    "SS_016": "Core_SS_016_F1_Floor",
}


def overlaps(origin_a, extent_a, origin_b, extent_b):
    return (
        abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x
        and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y
        and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z
    )


def ignored(actor):
    label = actor.get_actor_label()
    tags = common.actor_tags(actor)
    if isinstance(actor, (unreal.LandscapeProxy, unreal.TextRenderActor, unreal.Volume)):
        return True
    if "SunscarCoreSourceFootprint" in tags:
        return True
    if "Floor" in label or "Roof" in label:
        return True
    return label.startswith(("Ground_", "Route_", "District_", "CoreRoute_"))


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
actors_by_label = {actor.get_actor_label(): actor for actor in actors}
targets = sorted(
    [actor for actor in actors if TAG in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
if len(targets) != 4:
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_AUDIT_SCOPE actors=%d" % len(targets))

records = []
review = []
for actor in targets:
    tags = common.actor_tags(actor)
    site_tags = [tag for tag in tags if tag in FLOORS]
    if len(site_tags) != 1:
        raise RuntimeError("SUNSCAR_LARGE_UTILITY_AUDIT_SITE " + actor.get_actor_label())
    site_id = site_tags[0]
    floor = actors_by_label[FLOORS[site_id]]
    floor_origin, floor_extent = floor.get_actor_bounds(False, False)
    floor_top = floor_origin.z + floor_extent.z
    origin, extent = actor.get_actor_bounds(False, False)
    bottom = origin.z - extent.z
    rotation = actor.get_actor_rotation()
    component = actor.static_mesh_component
    overlap_labels = []
    for other in actors:
        if other == actor or other in targets or ignored(other):
            continue
        other_origin, other_extent = other.get_actor_bounds(False, False)
        if other_extent.z <= 20.0:
            continue
        if overlaps(origin, extent, other_origin, other_extent):
            overlap_labels.append(other.get_actor_label())
    reasons = []
    if abs(bottom - floor_top) > 3.0:
        reasons.append("support_height")
    if abs(rotation.pitch) > 0.01 or abs(rotation.roll) > 0.01:
        reasons.append("unexpected_pitch_or_roll")
    collision = str(component.get_collision_enabled())
    if "QUERY_AND_PHYSICS" not in collision:
        reasons.append("collision_mode")
    materials = [
        component.get_material(index).get_path_name()
        if component.get_material(index)
        else ""
        for index in range(component.get_num_materials())
    ]
    if not materials or any(not value for value in materials):
        reasons.append("missing_material")
    if overlap_labels:
        reasons.append("actor_overlap")
    record = {
        "label": actor.get_actor_label(),
        "site_id": site_id,
        "floor_actor": floor.get_actor_label(),
        "support_gap_cm": round(bottom - floor_top, 3),
        "location_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "dimensions_cm": [round(extent.x * 2.0, 3), round(extent.y * 2.0, 3), round(extent.z * 2.0, 3)],
        "rotation_deg": [rotation.pitch, rotation.yaw, rotation.roll],
        "collision": collision,
        "materials": materials,
        "overlap_labels": sorted(set(overlap_labels)),
        "review_reasons": reasons,
        "package": actor.get_package().get_name(),
    }
    records.append(record)
    if reasons:
        review.append(record)

pair_overlaps = []
for index, actor_a in enumerate(targets):
    origin_a, extent_a = actor_a.get_actor_bounds(False, False)
    for actor_b in targets[index + 1:]:
        origin_b, extent_b = actor_b.get_actor_bounds(False, False)
        if overlaps(origin_a, extent_a, origin_b, extent_b):
            pair_overlaps.append([actor_a.get_actor_label(), actor_b.get_actor_label()])
if pair_overlaps:
    for record in records:
        if any(record["label"] in pair for pair in pair_overlaps):
            record["review_reasons"].append("pair_overlap")
            if record not in review:
                review.append(record)

dirty_content = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "review_required_count": len(review),
    "pair_overlap_count": len(pair_overlaps),
    "pair_overlaps": pair_overlaps,
    "review_required": review,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_large_utility_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_LARGE_UTILITY_AUDIT actors=%d review=%d pairs=%d report=%s"
    % (len(records), len(review), len(pair_overlaps), report)
)
print("SUNSCAR_LARGE_UTILITY_AUDIT", report)
