"""Read-only mount, opening, material and collision audit for Old Town shutters."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownWindowShutterV1"
EXPECTED_ACTORS = 19
METAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal"
TIMBER_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Timber"
METAL_SITES = {"SS_010", "SS_011", "SS_018"}
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
all_actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in all_actors if TAG in common.actor_tags(actor)]
if len(targets) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_WINDOW_SHUTTER_AUDIT_SCOPE actor_count=%d" % len(targets))


def overlaps(origin_a, extent_a, origin_b, extent_b, margin=0.0):
    return (
        abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x + margin
        and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y + margin
        and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z + margin
    )


pair_overlaps = []
for index, actor_a in enumerate(targets):
    origin_a, extent_a = actor_a.get_actor_bounds(False)
    for actor_b in targets[index + 1:]:
        origin_b, extent_b = actor_b.get_actor_bounds(False)
        if overlaps(origin_a, extent_a, origin_b, extent_b, margin=-1.0):
            pair_overlaps.append([actor_a.get_actor_label(), actor_b.get_actor_label()])

records = []
review_required = []
for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    tags = common.actor_tags(actor)
    site = next((tag for tag in tags if tag.startswith("SS_") and len(tag) == 6), "")
    source_label = next((tag for tag in tags if tag.endswith("_Frame")), "")
    origin, extent = actor.get_actor_bounds(False)
    component = actor.static_mesh_component
    material = component.get_material(0)
    material_path = material.get_path_name().split(".")[0] if material else ""
    expected_material = METAL_PATH if site in METAL_SITES else TIMBER_PATH
    reasons = []
    if material_path != expected_material:
        reasons.append("unexpected_material")
    if "NO_COLLISION" not in str(component.get_collision_enabled()):
        reasons.append("collision_not_disabled")
    source_matches = [other for other in all_actors if other.get_actor_label() == source_label]
    if len(source_matches) != 1:
        reasons.append("source_frame_not_unique")
    else:
        frame_origin, frame_extent = source_matches[0].get_actor_bounds(False)
        if overlaps(origin, extent, frame_origin, frame_extent, margin=1.0):
            reasons.append("frame_overlap")
    opening_overlaps = []
    mount_candidates = []
    for other in all_actors:
        label = other.get_actor_label()
        if site not in " ".join([label, common.actor_folder(other), *common.actor_tags(other)]):
            continue
        other_origin, other_extent = other.get_actor_bounds(False)
        lowered = label.lower()
        if "wall" in lowered:
            dx = max(abs(origin.x - other_origin.x) - extent.x - other_extent.x, 0.0)
            dy = max(abs(origin.y - other_origin.y) - extent.y - other_extent.y, 0.0)
            mount_candidates.append((math.hypot(dx, dy), label))
        if ("door" in lowered or "glass" in lowered) and label != source_label:
            if overlaps(origin, extent, other_origin, other_extent, margin=2.0):
                opening_overlaps.append(label)
    mount_candidates.sort()
    mount_gap = mount_candidates[0][0] if mount_candidates else None
    mount_actor = mount_candidates[0][1] if mount_candidates else ""
    if mount_gap is None or mount_gap > 3.0:
        reasons.append("mount_gap")
    if opening_overlaps:
        reasons.append("opening_overlap")
    record = {
        "label": actor.get_actor_label(),
        "site_id": site,
        "source_frame": source_label,
        "mount_actor": mount_actor,
        "mount_gap_cm": round(mount_gap, 3) if mount_gap is not None else None,
        "opening_overlaps": opening_overlaps,
        "dimensions_cm": {"x": round(extent.x * 2.0, 3), "y": round(extent.y * 2.0, 3), "z": round(extent.z * 2.0, 3)},
        "material_path": material_path,
        "collision": str(component.get_collision_enabled()),
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
report = common.write_json_report(config, "old_town_window_shutter_audit_v1.json", payload)
unreal.log("SUNSCAR_WINDOW_SHUTTER_AUDIT actors=%d review=%d overlaps=%d dirty_maps=%d report=%s" % (len(records), len(review_required), len(pair_overlaps), len(dirty_maps), report))
print("SUNSCAR_WINDOW_SHUTTER_AUDIT", len(records), len(review_required), len(pair_overlaps), len(dirty_maps), report)
