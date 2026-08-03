"""Read-only support, edge, collision and overlap audit for rooftop utilities."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownRooftopUtilityV1"
EXPECTED_ACTORS = 10
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in common.actor_tags(actor)]
if len(targets) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_ROOFTOP_UTILITY_AUDIT_SCOPE actor_count=%d" % len(targets))


def actor_site(actor):
    return next((tag for tag in common.actor_tags(actor) if tag.startswith("SS_") and len(tag) == 6), "")


def overlaps(origin_a, extent_a, origin_b, extent_b):
    return (
        abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x
        and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y
        and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z
    )


records = []
review_required = []
for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    site = actor_site(actor)
    roof_label = "Core_%s_Roof" % site
    roof_matches = [other for other in actors if other.get_actor_label() == roof_label]
    origin, extent = actor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    reasons = []
    roof_top = None
    edge_clearance = None
    if len(roof_matches) != 1:
        reasons.append("roof_not_unique")
    else:
        roof_origin, roof_extent = roof_matches[0].get_actor_bounds(False)
        roof_top = roof_origin.z + roof_extent.z
        edge_clearance = min(
            roof_extent.x - abs(origin.x - roof_origin.x) - extent.x,
            roof_extent.y - abs(origin.y - roof_origin.y) - extent.y,
        )
        if abs(bottom_z - roof_top) > 0.05:
            reasons.append("roof_support_gap")
        if edge_clearance < 150.0:
            reasons.append("roof_edge_clearance")
    component = actor.static_mesh_component
    collision = str(component.get_collision_enabled())
    if "NO_COLLISION" not in collision:
        reasons.append("collision_not_disabled")
    record = {
        "label": actor.get_actor_label(),
        "site_id": site,
        "mesh_path": common.actor_mesh_path(actor),
        "roof_actor": roof_label,
        "bottom_z_cm": round(bottom_z, 3),
        "roof_top_z_cm": round(roof_top, 3) if roof_top is not None else None,
        "support_gap_cm": round(bottom_z - roof_top, 3) if roof_top is not None else None,
        "edge_clearance_cm": round(edge_clearance, 3) if edge_clearance is not None else None,
        "dimensions_cm": {"x": round(extent.x * 2.0, 3), "y": round(extent.y * 2.0, 3), "z": round(extent.z * 2.0, 3)},
        "collision": collision,
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
        if overlaps(origin_a, extent_a, origin_b, extent_b):
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
report = common.write_json_report(config, "old_town_rooftop_utility_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_ROOFTOP_UTILITY_AUDIT actors=%d review=%d overlaps=%d dirty_maps=%d report=%s"
    % (len(records), len(review_required), len(pair_overlaps), len(dirty_maps), report)
)
print("SUNSCAR_ROOFTOP_UTILITY_AUDIT", len(records), len(review_required), len(pair_overlaps), len(dirty_maps), report)
