"""Read-only post-apply audit for Old Town visual ground-overlay conformance."""

import collections
import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarGroundOverlayConformanceV1"
TARGET_COUNT = 288
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
targets = sorted([actor for actor in actors if TAG in common.actor_tags(actor)], key=lambda actor: actor.get_actor_label())
trace_ignore = [actor for actor in actors if "Landscape" not in actor.get_class().get_name()]


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x, y, 100000.0), unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, trace_ignore,
        unreal.DrawDebugTrace.NONE, True,
    )
    result = hit.to_dict() if hit is not None else {}
    return result["location"].z if result.get("blocking_hit") else None


records = []
review = []
for actor in targets:
    component = actor.static_mesh_component
    mesh = component.get_editor_property("static_mesh")
    scale = actor.get_actor_scale3d()
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    bounds = mesh.get_bounds()
    half_x = bounds.box_extent.x * abs(scale.x)
    half_y = bounds.box_extent.y * abs(scale.y)
    thickness = bounds.box_extent.z * abs(scale.z) * 2.0
    yaw = math.radians(rotation.yaw)
    fx, fy = math.cos(yaw), math.sin(yaw)
    rx, ry = -math.sin(yaw), math.cos(yaw)
    sample_x, sample_y = half_x * 0.82, half_y * 0.82
    terrain = {
        "back": terrain_z(location.x - fx * sample_x, location.y - fy * sample_x),
        "front": terrain_z(location.x + fx * sample_x, location.y + fy * sample_x),
        "left": terrain_z(location.x - rx * sample_y, location.y - ry * sample_y),
        "right": terrain_z(location.x + rx * sample_y, location.y + ry * sample_y),
        "center": terrain_z(location.x, location.y),
    }
    half_z = thickness * 0.5
    pitch_delta = math.tan(math.radians(rotation.pitch)) * sample_x
    roll_delta = math.tan(math.radians(rotation.roll)) * sample_y
    surface = {
        "back": location.z - pitch_delta + half_z,
        "front": location.z + pitch_delta + half_z,
        "left": location.z - roll_delta + half_z,
        "right": location.z + roll_delta + half_z,
        "center": location.z + half_z,
    }
    gaps = {name: surface[name] - terrain[name] for name in terrain if terrain[name] is not None}
    issues = []
    if "NO_COLLISION" not in str(component.get_collision_enabled()):
        issues.append("collision_not_disabled")
    if abs(thickness - 0.8) > 0.05:
        issues.append("unexpected_thickness")
    maximum_gap = max(abs(value) for value in gaps.values()) if gaps else 100000.0
    if maximum_gap > 18.0:
        issues.append("surface_gap_over_18cm")
    record = {
        "label": actor.get_actor_label(),
        "folder": common.actor_folder(actor),
        "collision": str(component.get_collision_enabled()),
        "thickness_cm": round(thickness, 3),
        "rotation_deg": {"pitch": round(rotation.pitch, 3), "roll": round(rotation.roll, 3), "yaw": round(rotation.yaw, 3)},
        "gaps_cm": {name: round(value, 3) for name, value in gaps.items()},
        "maximum_abs_gap_cm": round(maximum_gap, 3),
        "issues": issues,
        "package": actor.get_package().get_name(),
    }
    records.append(record)
    if issues:
        review.append(record)

dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
unexpected_dirty = [name for name in dirty_content + dirty_maps if not name.startswith((
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/Maps/Blockout/Lvl_Blockout_01",
))]
if len(targets) != TARGET_COUNT:
    review.append({"issue": "actor_count", "actual": len(targets), "expected": TARGET_COUNT})
if unexpected_dirty:
    review.append({"issue": "unexpected_dirty_scope", "packages": unexpected_dirty})

bands = collections.Counter()
for record in records:
    gap = record["maximum_abs_gap_cm"]
    bands["over_18cm" if gap > 18.0 else "10_to_18cm" if gap > 10.0 else "5_to_10cm" if gap > 5.0 else "under_5cm"] += 1
payload = {
    "schema_version": 1,
    "status": "read_only_ground_overlay_conformance_audit_complete",
    "context": context,
    "actor_count": len(targets),
    "collision_disabled_count": sum("NO_COLLISION" in record["collision"] for record in records),
    "gap_bands_after": dict(sorted(bands.items())),
    "maximum_abs_gap_cm": max(record["maximum_abs_gap_cm"] for record in records),
    "review_required_count": len(review),
    "review": review,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "unexpected_dirty_packages": unexpected_dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_ground_overlay_conformance_audit_v1.json", payload)
unreal.log("SUNSCAR_GROUND_CONFORMANCE_AUDIT actors=%d collision_off=%d review=%d max_gap=%.2f report=%s" % (len(targets), payload["collision_disabled_count"], len(review), payload["maximum_abs_gap_cm"], report))
print("SUNSCAR_GROUND_CONFORMANCE_AUDIT", len(targets), payload["collision_disabled_count"], len(review), payload["maximum_abs_gap_cm"], report)
