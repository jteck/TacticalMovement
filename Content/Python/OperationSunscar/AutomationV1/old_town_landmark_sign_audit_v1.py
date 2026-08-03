"""Read-only mount, text, collision and opening audit for landmark signs."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownLandmarkSignV1"
EXPECTED_ACTORS = 18
EXPECTED_MATERIAL = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Accent"
EXPECTED_TEXT = {
    "SS_004": "TEA HOUSE",
    "SS_005": "CLINIC",
    "SS_007": "HOTEL",
    "SS_010": "DETENTION",
    "SS_011": "CHECKPOINT",
    "SS_013": "FREIGHT",
    "SS_014": "SALVAGE",
    "SS_017": "BAZAAR",
    "SS_018": "TELECOM",
}
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
all_actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in all_actors if TAG in common.actor_tags(actor)]
if len(targets) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_LANDMARK_SIGN_AUDIT_SCOPE actor_count=%d" % len(targets))


def site_for(actor):
    return next((tag for tag in common.actor_tags(actor) if tag in EXPECTED_TEXT), "")


def overlaps(origin_a, extent_a, origin_b, extent_b, margin=0.0):
    return (
        abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x + margin
        and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y + margin
        and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z + margin
    )


records = []
review_required = []
for site, expected_text in EXPECTED_TEXT.items():
    boards = [actor for actor in targets if actor.get_actor_label() == "OT_SIGNBOARD_%s" % site]
    texts = [actor for actor in targets if actor.get_actor_label() == "OT_SIGNTEXT_%s" % site]
    reasons = []
    if len(boards) != 1 or len(texts) != 1:
        records.append({"site_id": site, "review_reasons": ["board_or_text_not_unique"]})
        review_required.append(records[-1])
        continue
    board, text_actor = boards[0], texts[0]
    board_origin, board_extent = board.get_actor_bounds(False)
    board_component = board.static_mesh_component
    collision = str(board_component.get_collision_enabled())
    material = board_component.get_material(0)
    material_path = material.get_path_name().split(".")[0] if material else ""
    text_value = str(text_actor.text_render.get_editor_property("text"))
    if text_value != expected_text:
        reasons.append("unexpected_text")
    if material_path != EXPECTED_MATERIAL:
        reasons.append("unexpected_board_material")
    if "NO_COLLISION" not in collision:
        reasons.append("board_collision_not_disabled")
    mount_candidates = []
    opening_overlaps = []
    for other in all_actors:
        label = other.get_actor_label()
        search = " ".join([label, common.actor_folder(other), *common.actor_tags(other)])
        if site not in search:
            continue
        lowered = label.lower()
        other_origin, other_extent = other.get_actor_bounds(False)
        if "wall" in lowered or "fence" in lowered:
            dx = max(abs(board_origin.x - other_origin.x) - board_extent.x - other_extent.x, 0.0)
            dy = max(abs(board_origin.y - other_origin.y) - board_extent.y - other_extent.y, 0.0)
            mount_candidates.append((math.hypot(dx, dy), label))
        if "door" in lowered or "window" in lowered or "gate" in lowered:
            if overlaps(board_origin, board_extent, other_origin, other_extent, margin=3.0):
                opening_overlaps.append(label)
    mount_candidates.sort()
    mount_gap = mount_candidates[0][0] if mount_candidates else None
    mount_actor = mount_candidates[0][1] if mount_candidates else ""
    if mount_gap is None or mount_gap > 3.0:
        reasons.append("mount_gap")
    if opening_overlaps:
        reasons.append("opening_overlap")
    record = {
        "site_id": site,
        "board_label": board.get_actor_label(),
        "text_label": text_actor.get_actor_label(),
        "text": text_value,
        "mount_actor": mount_actor,
        "mount_gap_cm": round(mount_gap, 3) if mount_gap is not None else None,
        "opening_overlaps": opening_overlaps,
        "board_material": material_path,
        "board_collision": collision,
        "board_dimensions_cm": {"x": round(board_extent.x * 2.0, 3), "y": round(board_extent.y * 2.0, 3), "z": round(board_extent.z * 2.0, 3)},
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
    "actor_count": len(targets),
    "site_count": len(records),
    "review_required_count": len(review_required),
    "review_required": review_required,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_landmark_sign_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_LANDMARK_SIGN_AUDIT actors=%d sites=%d review=%d dirty_maps=%d report=%s"
    % (len(targets), len(records), len(review_required), len(dirty_maps), report)
)
print("SUNSCAR_LANDMARK_SIGN_AUDIT", len(targets), len(records), len(review_required), len(dirty_maps), report)
