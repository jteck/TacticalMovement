"""Dry-run-first bounded industrial-detail placement for the Old Town art draft."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownIndustrialDetailV1")
FOLDER = "OldTown_ArtDraft/IndustrialDetailV1"
QUOTAS = {
    "OT_SCRAP_001": 14,
    "OT_SCRAP_002": 16,
    "OT_SCRAP_003": 10,
    "OT_SCRAP_005": 11,
}
MIN_SPACING_CM = {
    "OT_SCRAP_001": 120.0,
    "OT_SCRAP_002": 155.0,
    "OT_SCRAP_003": 180.0,
    "OT_SCRAP_005": 260.0,
}
MAX_DIMENSIONS_CM = {
    "OT_SCRAP_001": (450.0, 450.0, 300.0),
    "OT_SCRAP_002": (250.0, 250.0, 250.0),
    "OT_SCRAP_003": (180.0, 180.0, 180.0),
    "OT_SCRAP_005": (400.0, 400.0, 300.0),
}
IGNORED_BLOCKER_TERMS = (
    "landscape",
    "groundoverlay",
    "ground_overlay",
    "groundpatch",
    "ground_patch",
    "debris",
    "rubble",
    "grass",
    "rock",
    "damage",
    "label",
    "marker",
    "spawn",
    "objective",
)

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_DETAIL_DUPLICATE existing=%d" % len(existing))


def collision_enabled(actor):
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        return False
    try:
        return "NO_COLLISION" not in str(component.get_collision_enabled())
    except Exception:
        return False


def should_block(actor):
    search = " ".join(
        [actor.get_actor_label(), common.actor_folder(actor), common.actor_mesh_path(actor)]
    ).lower()
    if any(term in search for term in IGNORED_BLOCKER_TERMS):
        return False
    try:
        _origin, extent = actor.get_actor_bounds(False)
    except Exception:
        return False
    return collision_enabled(actor) and extent.z > 20.0 and (extent.x > 40.0 or extent.y > 40.0)


blockers = []
for actor in actors:
    if should_block(actor):
        origin, extent = actor.get_actor_bounds(False)
        blockers.append((actor.get_actor_label(), origin, extent))


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


def overlaps_blocker(x, y, half_x, half_y):
    clearance = 35.0
    for label, origin, extent in blockers:
        if abs(x - origin.x) <= extent.x + half_x + clearance and abs(y - origin.y) <= extent.y + half_y + clearance:
            return label
    return ""


records = [row for row in plan if row["bom_id"] in QUOTAS]
records.sort(key=lambda row: (row["bom_id"], row["site_id"], row["candidate_id"]))
selected = []
skipped = []
selected_xy = {bom: [] for bom in QUOTAS}
selected_counts = {bom: 0 for bom in QUOTAS}

for row in records:
    item = dict(row)
    bom = item["bom_id"]
    if selected_counts[bom] >= QUOTAS[bom]:
        item["reason"] = "quota_reached"
        skipped.append(item)
        continue
    asset_path = common.safe_asset_ref_to_path(item["planned_asset_ref"], registry)
    item["resolved_asset_path"] = asset_path
    if not asset_path or not common.asset_path_allowed(config, asset_path):
        item["reason"] = "unresolved_or_disallowed_asset"
        skipped.append(item)
        continue
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not isinstance(asset, unreal.StaticMesh):
        item["reason"] = "static_mesh_required"
        skipped.append(item)
        continue
    scale = float(item["scale"])
    bounds = asset.get_bounds()
    dimensions = bounds.box_extent * (2.0 * scale)
    max_dims = MAX_DIMENSIONS_CM[bom]
    item["dimensions_cm"] = {
        "x": round(dimensions.x, 3),
        "y": round(dimensions.y, 3),
        "z": round(dimensions.z, 3),
    }
    if dimensions.x > max_dims[0] or dimensions.y > max_dims[1] or dimensions.z > max_dims[2]:
        item["reason"] = "asset_dimensions_require_review"
        skipped.append(item)
        continue
    x = float(item["x_m"]) * 100.0
    y = float(item["y_m"]) * 100.0
    spacing = MIN_SPACING_CM[bom]
    nearest = min((math.hypot(x - px, y - py) for px, py in selected_xy[bom]), default=1000000.0)
    if nearest < spacing:
        item["reason"] = "candidate_spacing_below_%dcm" % int(spacing)
        skipped.append(item)
        continue
    blocker = overlaps_blocker(x, y, dimensions.x * 0.5, dimensions.y * 0.5)
    if blocker:
        item["reason"] = "overlaps_existing_collision:%s" % blocker
        skipped.append(item)
        continue
    support_z = terrain_z(x, y)
    if support_z is None:
        item["reason"] = "landscape_support_not_found"
        skipped.append(item)
        continue
    local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
    item["support_z_cm"] = round(support_z, 3)
    item["planned_location_cm"] = {
        "x": round(x, 3),
        "y": round(y, 3),
        "z": round(support_z - local_min_z, 3),
    }
    item["reason"] = ""
    selected.append((item, asset))
    selected_xy[bom].append((x, y))
    selected_counts[bom] += 1

unfilled = {bom: QUOTAS[bom] - selected_counts[bom] for bom in QUOTAS if selected_counts[bom] < QUOTAS[bom]}
if apply_requested and unfilled:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_DETAIL_APPLY_BLOCKED unfilled=%s" % unfilled)

created = []
if apply_requested:
    for item, asset in selected:
        location = item["planned_location_cm"]
        scale = float(item["scale"])
        actor = actor_system.spawn_actor_from_object(
            asset,
            unreal.Vector(location["x"], location["y"], location["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(item["yaw_deg"])),
            transient=False,
        )
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        origin, extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(
            unreal.Vector(0.0, 0.0, item["support_z_cm"] - (origin.z - extent.z)),
            False,
            False,
        )
        component = getattr(actor, "static_mesh_component", None)
        if component is not None:
            component.set_collision_profile_name("NoCollision")
            component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        actor.set_actor_label("OT_INDDETAIL_%s" % item["candidate_id"])
        actor.tags = [
            TAG,
            unreal.Name(item["site_id"]),
            unreal.Name(item["bom_id"]),
            unreal.Name(item["candidate_id"]),
            unreal.Name("ReviewedAutomationPlacement"),
        ]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "planned_record_count": len(records),
    "quota_by_bom": QUOTAS,
    "selected_count_by_bom": selected_counts,
    "selected_count": len(selected),
    "unfilled_quota_by_bom": unfilled,
    "skipped_count": len(skipped),
    "existing_tagged_actor_count": len(existing),
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "selected": [item for item, _asset in selected],
    "skipped": skipped,
    "changes_made": bool(created),
    "level_saved": False,
    "collision_policy": "NoCollision; decorative detail only",
    "deferred": ["OT_SCRAP_004 orientation review", "OT_TAC_006 combat-lane playtest", "OT_UTIL_008 existing-placement reconciliation"],
}
name = "old_town_industrial_detail_apply_preview_v1.json" if apply_requested else "old_town_industrial_detail_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_INDUSTRIAL_DETAIL mode=%s selected=%d skipped=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(selected), len(skipped), len(created), report)
)
print("SUNSCAR_INDUSTRIAL_DETAIL", len(selected), len(skipped), len(created), report)
