"""Read-only facade contact and opening-clearance audit for conduit accents."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownFacadeConduitV1"
EXPECTED_ACTORS = 16
EXPECTED_MATERIAL = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
all_actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in all_actors if TAG in common.actor_tags(actor)]
if len(targets) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_AUDIT_SCOPE actor_count=%d" % len(targets))


def actor_site(actor):
    return next((tag for tag in common.actor_tags(actor) if tag.startswith("SS_") and len(tag) == 6), "")


def overlaps_3d(origin_a, extent_a, origin_b, extent_b, margin=0.0):
    return (
        abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x + margin
        and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y + margin
        and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z + margin
    )


records = []
review_required = []
for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    site = actor_site(actor)
    origin, extent = actor.get_actor_bounds(False)
    walls = []
    openings = []
    for other in all_actors:
        label = other.get_actor_label()
        if site not in label:
            continue
        lowered = label.lower()
        other_origin, other_extent = other.get_actor_bounds(False)
        if "wall" in lowered:
            dx = max(abs(origin.x - other_origin.x) - extent.x - other_extent.x, 0.0)
            dy = max(abs(origin.y - other_origin.y) - extent.y - other_extent.y, 0.0)
            walls.append((math.hypot(dx, dy), label))
        if "door" in lowered or "window" in lowered or "gate" in lowered:
            if overlaps_3d(origin, extent, other_origin, other_extent, margin=10.0):
                openings.append(label)
    walls.sort()
    wall_gap = walls[0][0] if walls else None
    wall_label = walls[0][1] if walls else ""
    component = actor.static_mesh_component
    collision = str(component.get_collision_enabled())
    assigned = component.get_material(0)
    assigned_path = assigned.get_path_name().split(".")[0] if assigned else ""
    reasons = []
    if wall_gap is None or wall_gap > 3.0:
        reasons.append("facade_contact_gap")
    if openings:
        reasons.append("opening_overlap")
    if "NO_COLLISION" not in collision:
        reasons.append("collision_not_disabled")
    if assigned_path != EXPECTED_MATERIAL:
        reasons.append("unexpected_material")
    record = {
        "label": actor.get_actor_label(),
        "site_id": site,
        "nearest_wall": wall_label,
        "facade_gap_cm": round(wall_gap, 3) if wall_gap is not None else None,
        "opening_overlaps": openings,
        "material": assigned_path,
        "collision": collision,
        "dimensions_cm": {"x": round(extent.x * 2.0, 3), "y": round(extent.y * 2.0, 3), "z": round(extent.z * 2.0, 3)},
        "review_reasons": reasons,
    }
    records.append(record)
    if reasons:
        review_required.append(record)

pair_overlaps = []
for index, actor_a in enumerate(targets):
    origin_a, extent_a = actor_a.get_actor_bounds(False)
    for actor_b in targets[index + 1:]:
        origin_b, extent_b = actor_b.get_actor_bounds(False)
        if overlaps_3d(origin_a, extent_a, origin_b, extent_b):
            pair_overlaps.append([actor_a.get_actor_label(), actor_b.get_actor_label()])

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
report = common.write_json_report(config, "old_town_facade_conduit_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_FACADE_CONDUIT_AUDIT actors=%d review=%d overlaps=%d dirty_maps=%d report=%s"
    % (len(records), len(review_required), len(pair_overlaps), len(dirty_maps), report)
)
print("SUNSCAR_FACADE_CONDUIT_AUDIT", len(records), len(review_required), len(pair_overlaps), len(dirty_maps), report)
