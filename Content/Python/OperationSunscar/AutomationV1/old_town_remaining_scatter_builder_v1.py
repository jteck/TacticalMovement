"""Dry-run-first bounded ground/vegetation dressing for the 15 non-slice sites."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownRemainingScatterV1")
FOLDER = "OldTown_AutomationPreview/RemainingScatterV1"
ALL_SITES = {"SS_%03d" % index for index in range(1, 21)}
LIMITS = {"ground": 8, "vegetation": 4}
SUPPORTED_POLICIES = {"seeded_scatter", "seeded_pcg"}

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
sites = ALL_SITES - set(config["connected_slice_sites"])
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
records = [
    row
    for row in plan
    if row["site_id"] in sites
    and row["class"] in LIMITS
    and row["placement_policy"] in SUPPORTED_POLICIES
]

actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]
existing = [actor for actor in actors if TAG in list(actor.tags)]
support_ignore = landscapes + [
    actor for actor in actors if actor.get_actor_label().startswith("OT_")
]


def landscape_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        non_landscapes,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    return result["location"].z if result.get("blocking_hit") else None


def visible_support(x, y, terrain):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        support_ignore,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    if not result.get("blocking_hit"):
        return terrain, "Landscape", ""
    support_z = result["location"].z
    support_actor = result.get("hit_actor")
    support_label = support_actor.get_actor_label() if support_actor else "Unknown"
    if support_z - terrain > 80.0:
        return None, support_label, "coordinate_covered_by_existing_geometry"
    if support_z < terrain - 10.0:
        return terrain, "Landscape", ""
    return max(terrain, support_z), support_label, ""


eligible = []
manual = []
blockers = []
for row in records:
    item = dict(row)
    path = common.safe_asset_ref_to_path(item["planned_asset_ref"], registry)
    item["resolved_asset_path"] = path
    if not path or not common.asset_path_allowed(config, path):
        item["reason"] = "unresolved_or_disallowed_asset"
        blockers.append(item)
        continue
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        item["reason"] = "remaining_scatter_requires_static_mesh"
        blockers.append(item)
        continue
    x = float(item["x_m"]) * 100.0
    y = float(item["y_m"]) * 100.0
    terrain = landscape_z(x, y)
    if terrain is None:
        item["reason"] = "landscape_trace_failed"
        blockers.append(item)
        continue
    support_z, support_label, reason = visible_support(x, y, terrain)
    item["terrain_z_cm"] = round(terrain, 3)
    item["support_actor"] = support_label
    if support_z is None:
        item["reason"] = reason
        manual.append(item)
        continue
    scale = float(item["scale"])
    bounds = asset.get_bounds()
    local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
    item["support_z_cm"] = round(support_z, 3)
    item["planned_location_cm"] = {
        "x": round(x, 3),
        "y": round(y, 3),
        "z": round(support_z - local_min_z, 3),
    }
    item["reason"] = ""
    eligible.append((item, asset))

# Deterministic first-round limits prevent a blind full-plan scatter.
selected = []
counts = {}
for item, asset in eligible:
    key = (item["site_id"], item["class"])
    count = counts.get(key, 0)
    if count >= LIMITS[item["class"]]:
        item["reason"] = "held_by_first_round_site_class_limit"
        manual.append(item)
        continue
    counts[key] = count + 1
    selected.append((item, asset))

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_REMAINING_SCATTER_APPLY_BLOCKED blockers=%d" % len(blockers))
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_REMAINING_SCATTER_DUPLICATE existing=%d" % len(existing))
if apply_requested and (len(selected) < 40 or len(selected) > 180):
    raise RuntimeError("SUNSCAR_REMAINING_SCATTER_COUNT_REFUSED selected=%d" % len(selected))

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
        actor.set_actor_label("OT_REMAIN_%s" % item["candidate_id"])
        actor.tags = [
            TAG,
            unreal.Name(item["site_id"]),
            unreal.Name(item["bom_id"]),
            unreal.Name("UnreviewedAutomationPlacement"),
        ]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "sites": sorted(sites),
    "source_record_count": len(records),
    "eligible_count": len(eligible),
    "selected_count": len(selected),
    "manual_count": len(manual),
    "blocker_count": len(blockers),
    "selected_counts": {"%s_%s" % key: value for key, value in sorted(counts.items())},
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "selected": [item for item, _asset in selected],
    "manual": manual,
    "blockers": blockers,
    "changes_made": bool(created),
    "level_saved": False,
}
filename = (
    "old_town_remaining_scatter_apply_preview_v1.json"
    if apply_requested
    else "old_town_remaining_scatter_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_REMAINING_SCATTER mode=%s selected=%d manual=%d blockers=%d created=%d report=%s"
    % (
        "APPLY_UNSAVED" if apply_requested else "DRY_RUN",
        len(selected),
        len(manual),
        len(blockers),
        len(created),
        report,
    )
)
print("SUNSCAR_REMAINING_SCATTER", len(selected), len(manual), len(blockers), len(created), report)
