"""Read-only validation of the unsaved Old Town exterior completion preview."""

import collections
import json
import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownExteriorCompletionV1"
EXPECTED_COUNTS = {
    "ground_debris_decal": 18,
    "worn_route_decal": 24,
    "drainpipe": 10,
    "drain_outlet": 10,
    "utility_meter": 10,
    "wall_weathering_decal": 12,
    "door_threshold": 8,
    "roof_mast_base": 6,
    "roof_mast": 6,
    "roadside_post": 8,
}

config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in common.actor_tags(actor)]
by_label = {actor.get_actor_label(): actor for actor in actors}
counts = collections.Counter()
records = []
review = []

for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    tags = common.actor_tags(actor)
    kind = next((value for value in EXPECTED_COUNTS if value in tags), "")
    counts[kind] += 1
    origin, extent = actor.get_actor_bounds(False)
    issues = []
    if not kind:
        issues.append("missing_kind_tag")
    if isinstance(actor, unreal.DecalActor):
        component = actor.get_editor_property("decal")
        material = component.get_editor_property("decal_material")
        material_path = material.get_path_name() if material else ""
        if not material_path.startswith(("/Game/MilitaryTrench/", "/Game/Scene_Junkyard/")):
            issues.append("unexpected_decal_material")
    else:
        component = getattr(actor, "static_mesh_component", None)
        material_path = ""
        if component is None:
            issues.append("missing_static_mesh_component")
        else:
            if "NO_COLLISION" not in str(component.get_collision_enabled()):
                issues.append("decorative_mesh_collision_enabled")
            material = component.get_material(0) if component.get_num_materials() else None
            material_path = material.get_path_name() if material else ""
    if kind in ("drainpipe", "drain_outlet", "utility_meter", "door_threshold", "roof_mast", "roof_mast_base", "roadside_post"):
        if max(extent.x, extent.y, extent.z) > 300.0:
            issues.append("unexpected_large_detail")
    package = actor.get_package().get_name()
    if not package.startswith(("/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/", "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")):
        issues.append("unexpected_package")
    record = {
        "label": actor.get_actor_label(),
        "kind": kind,
        "class": actor.get_class().get_name(),
        "location_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "material_path": material_path,
        "package": package,
        "issues": issues,
    }
    records.append(record)
    if issues:
        review.append(record)

apply_path = os.path.join(common.report_directory(config), "old_town_exterior_completion_apply_preview_v1.json")
with open(apply_path, "r", encoding="utf-8") as handle:
    apply_report = json.load(handle)
support_checks = []
for item in apply_report["planned"]:
    support = item.get("support", "")
    if not support or support in ("roofline",):
        continue
    target = by_label.get(item["label"])
    support_actor = by_label.get(support)
    if target is None or support_actor is None:
        support_checks.append({"label": item["label"], "support": support, "status": "missing_actor"})
        continue
    target_location = target.get_actor_location()
    support_origin, support_extent = support_actor.get_actor_bounds(False)
    horizontal_distance = math.hypot(target_location.x - support_origin.x, target_location.y - support_origin.y)
    maximum = math.hypot(support_extent.x, support_extent.y) + 260.0
    status = "pass" if horizontal_distance <= maximum else "too_far_from_support"
    support_checks.append({
        "label": item["label"],
        "support": support,
        "horizontal_distance_cm": round(horizontal_distance, 3),
        "allowed_distance_cm": round(maximum, 3),
        "status": status,
    })
    if status != "pass":
        review.append(support_checks[-1])

dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
unexpected_dirty = [
    name for name in dirty_content + dirty_maps
    if not name.startswith((
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/Maps/Blockout/Lvl_Blockout_01",
    ))
]
if dict(counts) != EXPECTED_COUNTS:
    review.append({"status": "count_mismatch", "actual": dict(counts), "expected": EXPECTED_COUNTS})
if unexpected_dirty:
    review.append({"status": "unexpected_dirty_scope", "packages": unexpected_dirty})

payload = {
    "schema_version": 2,
    "status": "read_only_exterior_completion_audit_complete",
    "context": context,
    "actor_count": len(targets),
    "counts": dict(sorted(counts.items())),
    "review_required_count": len(review),
    "review": review,
    "support_checks": support_checks,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "unexpected_dirty_packages": unexpected_dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_exterior_completion_audit_v2.json", payload)
unreal.log("SUNSCAR_EXTERIOR_COMPLETION_AUDIT_V2 actors=%d review=%d dirty_maps=%d report=%s" % (len(targets), len(review), len(dirty_maps), report))
print("SUNSCAR_EXTERIOR_COMPLETION_AUDIT_V2", len(targets), len(review), len(dirty_maps), report)
