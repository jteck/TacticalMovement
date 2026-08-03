"""Dry-run-first readability correction for existing Old Town landmark signs."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownLandmarkSignV1"
SITE_NORMAL = {
    "SS_004": (0.0, -1.0),
    "SS_005": (0.0, -1.0),
    "SS_007": (0.0, -1.0),
    "SS_010": (0.0, -1.0),
    "SS_011": (0.0, -1.0),
    "SS_013": (0.0, -1.0),
    "SS_014": (0.0, 1.0),
    "SS_017": (0.0, -1.0),
    "SS_018": (0.0, -1.0),
}
WORLD_SIZE_CM = 28.0
FACE_CLEARANCE_CM = 7.0

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in common.actor_tags(actor)]

ready = []
blockers = []
for site, normal in SITE_NORMAL.items():
    boards = [actor for actor in targets if actor.get_actor_label() == "OT_SIGNBOARD_%s" % site]
    texts = [actor for actor in targets if actor.get_actor_label() == "OT_SIGNTEXT_%s" % site]
    if len(boards) != 1 or len(texts) != 1:
        blockers.append({"site_id": site, "reason": "board_or_text_not_unique"})
        continue
    board, text_actor = boards[0], texts[0]
    origin = board.get_actor_location()
    nx, ny = normal
    ready.append({
        "site_id": site,
        "board_label": board.get_actor_label(),
        "text_label": text_actor.get_actor_label(),
        "location_cm": {
            "x": round(origin.x + nx * FACE_CLEARANCE_CM, 3),
            "y": round(origin.y + ny * FACE_CLEARANCE_CM, 3),
            "z": round(origin.z, 3),
        },
        "yaw_deg": round(math.degrees(math.atan2(ny, nx)), 3),
        "world_size_cm": WORLD_SIZE_CM,
        "horizontal_alignment": "center",
        "vertical_alignment": "text_center",
    })

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_LANDMARK_SIGN_TEXT_FINISH_BLOCKED blockers=%d" % len(blockers))

changed = []
if apply_requested:
    for item in ready:
        text_actor = next(actor for actor in targets if actor.get_actor_label() == item["text_label"])
        loc = item["location_cm"]
        text_actor.set_actor_location(unreal.Vector(loc["x"], loc["y"], loc["z"]), False, False)
        text_actor.set_actor_rotation(
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=item["yaw_deg"]),
            False,
        )
        component = text_actor.text_render
        component.set_world_size(WORLD_SIZE_CM)
        component.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
        component.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        changed.append(text_actor.get_actor_label())

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "ready_count": len(ready),
    "blocker_count": len(blockers),
    "blockers": blockers,
    "ready": ready,
    "changed_actor_count": len(changed),
    "changed_actor_labels": changed,
    "changes_made": bool(changed),
    "level_saved": False,
}
name = "old_town_landmark_sign_text_finish_apply_preview_v1.json" if apply_requested else "old_town_landmark_sign_text_finish_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_LANDMARK_SIGN_TEXT_FINISH mode=%s ready=%d blockers=%d changed=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(changed), report)
)
print("SUNSCAR_LANDMARK_SIGN_TEXT_FINISH", len(ready), len(blockers), len(changed), report)
