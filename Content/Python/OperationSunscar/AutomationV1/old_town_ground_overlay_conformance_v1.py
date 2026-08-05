"""Dry-run-first conformance of visual ground overlays to the underlying Landscape."""

import collections
import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarGroundOverlayConformanceV1")
TARGET_COUNT = 288
MAX_TILT_DEG = 6.0
TARGET_THICKNESS_CM = 0.8
APPLY_CHANGES = False

config = common.load_config()
apply_requested = APPLY_CHANGES
context = common.require_safe_context(config, write_requested=False)
context["write_requested"] = apply_requested
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
targets = sorted(
    [actor for actor in actors if "VisualGroundOverlay" in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
if len(targets) != TARGET_COUNT:
    raise RuntimeError("SUNSCAR_GROUND_CONFORMANCE_SCOPE_REFUSED actors=%d" % len(targets))

trace_ignore = [actor for actor in actors if "Landscape" not in actor.get_class().get_name()]


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        trace_ignore,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    return result["location"].z if result.get("blocking_hit") else None


records = []
blockers = []
for actor in targets:
    component = actor.static_mesh_component
    mesh = component.get_editor_property("static_mesh")
    if not isinstance(mesh, unreal.StaticMesh):
        blockers.append({"label": actor.get_actor_label(), "reason": "visual_static_mesh_required", "mesh_class": mesh.get_class().get_name() if mesh else ""})
        continue
    mesh_bounds = mesh.get_bounds()
    scale = actor.get_actor_scale3d()
    half_x = mesh_bounds.box_extent.x * abs(scale.x)
    half_y = mesh_bounds.box_extent.y * abs(scale.y)
    if half_x < 20.0 or half_y < 20.0:
        blockers.append({"label": actor.get_actor_label(), "reason": "unexpected_overlay_dimensions"})
        continue
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    yaw = rotation.yaw
    radians = math.radians(yaw)
    fx, fy = math.cos(radians), math.sin(radians)
    rx, ry = -math.sin(radians), math.cos(radians)
    sample_x = half_x * 0.82
    sample_y = half_y * 0.82
    back = terrain_z(location.x - fx * sample_x, location.y - fy * sample_x)
    front = terrain_z(location.x + fx * sample_x, location.y + fy * sample_x)
    left = terrain_z(location.x - rx * sample_y, location.y - ry * sample_y)
    right = terrain_z(location.x + rx * sample_y, location.y + ry * sample_y)
    center = terrain_z(location.x, location.y)
    if None in (back, front, left, right, center):
        blockers.append({"label": actor.get_actor_label(), "reason": "landscape_sample_failed"})
        continue
    pitch = math.degrees(math.atan2(front - back, sample_x * 2.0))
    roll = math.degrees(math.atan2(right - left, sample_y * 2.0))
    raw_pitch, raw_roll = pitch, roll
    pitch = max(-MAX_TILT_DEG, min(MAX_TILT_DEG, pitch))
    roll = max(-MAX_TILT_DEG, min(MAX_TILT_DEG, roll))
    new_scale_z = scale.z * (TARGET_THICKNESS_CM / max(mesh_bounds.box_extent.z * abs(scale.z) * 2.0, 0.001))
    half_z = TARGET_THICKNESS_CM * 0.5
    support_average = (back + front + left + right + center * 2.0) / 6.0
    new_z = support_average + half_z
    current_top = location.z + mesh_bounds.box_extent.z * abs(scale.z)
    samples = {"back": back, "front": front, "left": left, "right": right, "center": center}
    current_gaps = {name: current_top - value for name, value in samples.items()}
    item = {
        "label": actor.get_actor_label(),
        "folder": common.actor_folder(actor),
        "package": actor.get_package().get_name(),
        "before_location_z_cm": round(location.z, 3),
        "after_location_z_cm": round(new_z, 3),
        "delta_z_cm": round(new_z - location.z, 3),
        "before_rotation_deg": {"pitch": round(rotation.pitch, 3), "roll": round(rotation.roll, 3), "yaw": round(rotation.yaw, 3)},
        "after_rotation_deg": {"pitch": round(pitch, 3), "roll": round(roll, 3), "yaw": round(yaw, 3)},
        "raw_fit_rotation_deg": {"pitch": round(raw_pitch, 3), "roll": round(raw_roll, 3)},
        "tilt_clamped": abs(raw_pitch) > MAX_TILT_DEG or abs(raw_roll) > MAX_TILT_DEG,
        "before_thickness_cm": round(mesh_bounds.box_extent.z * abs(scale.z) * 2.0, 3),
        "after_thickness_cm": TARGET_THICKNESS_CM,
        "before_collision": str(component.get_collision_enabled()),
        "after_collision": "NO_COLLISION",
        "new_scale_z": new_scale_z,
        "current_max_abs_gap_cm": round(max(abs(value) for value in current_gaps.values()), 3),
        "terrain_samples_cm": {name: round(value, 3) for name, value in samples.items()},
    }
    records.append(item)

if blockers:
    blocker_counts = collections.Counter(item["reason"] for item in blockers)
    raise RuntimeError("SUNSCAR_GROUND_CONFORMANCE_BLOCKED blockers=%d reasons=%s first=%s" % (len(blockers), dict(blocker_counts), blockers[0]))
if len(records) != TARGET_COUNT:
    raise RuntimeError("SUNSCAR_GROUND_CONFORMANCE_RECORD_REFUSED records=%d" % len(records))

originals = []
if apply_requested:
    try:
        for actor, item in zip(targets, records):
            originals.append((actor, actor.get_actor_location(), actor.get_actor_rotation(), actor.get_actor_scale3d(), list(actor.tags)))
            actor.modify()
            location = actor.get_actor_location()
            actor.set_actor_location(unreal.Vector(location.x, location.y, item["after_location_z_cm"]), False, False)
            actor.set_actor_rotation(
                unreal.Rotator(
                    roll=item["after_rotation_deg"]["roll"],
                    pitch=item["after_rotation_deg"]["pitch"],
                    yaw=item["after_rotation_deg"]["yaw"],
                ),
                False,
            )
            scale = actor.get_actor_scale3d()
            actor.set_actor_scale3d(unreal.Vector(scale.x, scale.y, item["new_scale_z"]))
            actor.static_mesh_component.set_collision_profile_name("NoCollision")
            actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            if TAG not in list(actor.tags):
                actor.tags = list(actor.tags) + [TAG]
    except Exception:
        for actor, location, rotation, scale, tags in reversed(originals):
            actor.set_actor_location(location, False, False)
            actor.set_actor_rotation(rotation, False)
            actor.set_actor_scale3d(scale)
            actor.tags = tags
        raise

gap_bands = collections.Counter()
for item in records:
    gap = item["current_max_abs_gap_cm"]
    band = "over_20cm" if gap > 20.0 else "10_to_20cm" if gap > 10.0 else "5_to_10cm" if gap > 5.0 else "under_5cm"
    gap_bands[band] += 1
payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "gap_bands_before": dict(sorted(gap_bands.items())),
    "maximum_existing_gap_cm": max(item["current_max_abs_gap_cm"] for item in records),
    "maximum_abs_delta_z_cm": max(abs(item["delta_z_cm"]) for item in records),
    "maximum_abs_pitch_deg": max(abs(item["after_rotation_deg"]["pitch"]) for item in records),
    "maximum_abs_roll_deg": max(abs(item["after_rotation_deg"]["roll"]) for item in records),
    "target_thickness_cm": TARGET_THICKNESS_CM,
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
    "collision_policy": "All 288 visual overlays remain NoCollision.",
}
filename = "old_town_ground_overlay_conformance_apply_preview_v1.json" if apply_requested else "old_town_ground_overlay_conformance_dry_run_v1.json"
report = common.write_json_report(config, filename, payload)
unreal.log("SUNSCAR_GROUND_CONFORMANCE mode=%s actors=%d max_gap=%.2f report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), payload["maximum_existing_gap_cm"], report))
print("SUNSCAR_GROUND_CONFORMANCE", len(records), payload["maximum_existing_gap_cm"], report)
