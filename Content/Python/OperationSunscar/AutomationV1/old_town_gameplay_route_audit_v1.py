"""Read-only first-draft width and surface audit for the 50 Old Town core routes."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


EXPECTED_ROUTES = 50
MINIMUM_REVIEW_WIDTH_CM = 250.0
PROTOTYPE_TERM = "/Game/LevelPrototyping/Materials/"


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
dirty_content_before = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps_before = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content_before or dirty_maps_before:
    raise RuntimeError("SUNSCAR_GAMEPLAY_ROUTE_AUDIT_REFUSED dirty_scope")

targets = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if actor.get_actor_label().startswith("CoreRoute_")
    ],
    key=lambda actor: actor.get_actor_label(),
)
if len(targets) != EXPECTED_ROUTES:
    raise RuntimeError("SUNSCAR_GAMEPLAY_ROUTE_AUDIT_REFUSED route_count=%d" % len(targets))

records = []
review = []
for actor in targets:
    origin, extent = actor.get_actor_bounds(False)
    horizontal_dimensions = sorted([extent.x * 2.0, extent.y * 2.0])
    width_cm = horizontal_dimensions[0]
    length_cm = horizontal_dimensions[1]
    materials = []
    collision = []
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        materials.extend(material.get_path_name() for material in component.get_materials() if material)
        collision.append(str(component.get_collision_enabled()))
    issues = []
    if width_cm < MINIMUM_REVIEW_WIDTH_CM:
        issues.append("route_width_below_review_minimum")
    if not materials:
        issues.append("route_material_missing")
    if any(PROTOTYPE_TERM in material for material in materials):
        issues.append("prototype_route_material")
    record = {
        "label": actor.get_actor_label(),
        "folder": common.actor_folder(actor),
        "origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "width_cm": round(width_cm, 3),
        "length_cm": round(length_cm, 3),
        "materials": sorted(set(materials)),
        "collision": sorted(set(collision)),
        "issues": issues,
        "package": actor.get_package().get_name(),
    }
    records.append(record)
    if issues:
        review.append(record)

dirty_content_after = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps_after = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content_after or dirty_maps_after:
    raise RuntimeError("SUNSCAR_GAMEPLAY_ROUTE_AUDIT_DIRTIED_PACKAGES")

payload = {
    "schema_version": 1,
    "status": "read_only_gameplay_route_audit_complete",
    "context": context,
    "route_count": len(records),
    "minimum_review_width_cm": MINIMUM_REVIEW_WIDTH_CM,
    "narrowest_route_width_cm": round(min(record["width_cm"] for record in records), 3),
    "widest_route_width_cm": round(max(record["width_cm"] for record in records), 3),
    "review_required_count": len(review),
    "review_required": review,
    "records": records,
    "dirty_content_packages": sorted(dirty_content_after),
    "dirty_map_packages": sorted(dirty_maps_after),
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_gameplay_route_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_GAMEPLAY_ROUTE_AUDIT routes=%d narrowest=%.2f review=%d report=%s"
    % (len(records), payload["narrowest_route_width_cm"], len(review), report)
)
print("SUNSCAR_GAMEPLAY_ROUTE_AUDIT", len(records), payload["narrowest_route_width_cm"], len(review), report)
