"""Dry-run-first connected-slice resolver and limited safe scatter builder.

Version 1 never saves the level and never replaces existing actors. Even with
the dual apply gate enabled, it only spawns accepted Static Mesh assets for
explicitly supported non-gameplay scatter policies.
"""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
execution = config["execution"]
apply_requested = bool(execution.get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)

plan_path = common.planning_file(config, "resolved_plan_file")
registry_path = common.planning_file(config, "final_registry_file")
if not os.path.exists(plan_path):
    raise RuntimeError("SUNSCAR_RESOLVED_PLAN_MISSING " + plan_path)
if not os.path.exists(registry_path):
    raise RuntimeError("SUNSCAR_FINAL_REGISTRY_MISSING " + registry_path)

plan = common.read_csv(plan_path)
registry = common.read_json(registry_path)
slice_sites = set(config["connected_slice_sites"])
supported_classes = set(execution["supported_classes"])
supported_policies = {"seeded_scatter", "seeded_pcg"}
slice_records = [record for record in plan if record["site_id"] in slice_sites]

actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
world = common.editor_world()
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]
placement_tag = unreal.Name(execution["placement_tag"])
existing_preview = [actor for actor in actors if placement_tag in list(actor.tags)]


def landscape_z(x_cm, y_cm):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x_cm, y_cm, 100000.0),
        unreal.Vector(x_cm, y_cm, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        non_landscapes,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return None
    result = hit.to_dict()
    return result["location"].z if result.get("blocking_hit") else None


def visible_surface(x_cm, y_cm, terrain_z):
    """Return a safe visible support or explain why the coordinate is covered."""
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x_cm, y_cm, 100000.0),
        unreal.Vector(x_cm, y_cm, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        landscapes + existing_preview,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return terrain_z, "Landscape", ""
    result = hit.to_dict()
    if not result.get("blocking_hit"):
        return terrain_z, "Landscape", ""
    surface_z = result["location"].z
    surface_actor = result.get("hit_actor")
    surface_label = surface_actor.get_actor_label() if surface_actor else "Unknown"
    delta = surface_z - terrain_z
    if delta > 80.0:
        return None, surface_label, "coordinate_covered_by_existing_geometry"
    if delta < -10.0:
        return terrain_z, "Landscape", ""
    return max(terrain_z, surface_z), surface_label, ""


resolved = []
blockers = []
manual_records = []

for record in slice_records:
    item = dict(record)
    item["resolved_asset_path"] = common.safe_asset_ref_to_path(item["planned_asset_ref"], registry)
    item["action"] = "manual_or_specialized_pass"
    item["reason"] = ""
    item["asset_class"] = ""

    if item["class"] not in supported_classes or item["placement_policy"] not in supported_policies:
        item["reason"] = "class_or_policy_not_allowed_for_v1_automatic_spawn"
        manual_records.append(item)
        continue
    if not item["resolved_asset_path"]:
        item["reason"] = "unresolved_asset_reference"
        blockers.append(item)
        continue
    if not common.asset_path_allowed(config, item["resolved_asset_path"]):
        item["reason"] = "asset_path_not_allowed"
        blockers.append(item)
        continue

    asset = unreal.EditorAssetLibrary.load_asset(item["resolved_asset_path"])
    if asset is None:
        item["reason"] = "asset_missing_in_current_project"
        blockers.append(item)
        continue
    item["asset_class"] = asset.get_class().get_name()
    if not isinstance(asset, unreal.StaticMesh):
        item["reason"] = "v1_auto_spawn_requires_static_mesh"
        blockers.append(item)
        continue

    x_cm = float(item["x_m"]) * 100.0
    y_cm = float(item["y_m"]) * 100.0
    terrain_z = landscape_z(x_cm, y_cm)
    if terrain_z is None:
        item["reason"] = "landscape_trace_failed"
        blockers.append(item)
        continue

    support_z, support_actor, support_reason = visible_surface(x_cm, y_cm, terrain_z)
    item["terrain_z_cm"] = round(terrain_z, 3)
    item["support_actor"] = support_actor
    if support_z is None:
        item["reason"] = support_reason
        manual_records.append(item)
        continue
    item["support_z_cm"] = round(support_z, 3)

    bounds = asset.get_bounds()
    scale = float(item["scale"])
    local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
    item["planned_location_cm"] = {
        "x": round(x_cm, 3),
        "y": round(y_cm, 3),
        "z": round(support_z - local_min_z, 3),
    }
    item["action"] = "ready_to_spawn" if apply_requested else "dry_run_ready"
    resolved.append((item, asset))

if apply_requested and blockers:
    payload = {
        "schema_version": 1,
        "status": "apply_blocked",
        "context": context,
        "slice_record_count": len(slice_records),
        "automatic_candidate_count": len(resolved) + len(blockers),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "changes_made": False,
    }
    report = common.write_json_report(config, "old_town_connected_slice_apply_blocked.json", payload)
    raise RuntimeError("SUNSCAR_CONNECTED_SLICE_APPLY_BLOCKED blockers=%d report=%s" % (len(blockers), report))

created = []
if apply_requested:
    if execution.get("destroy_existing_tagged_actors", False):
        raise RuntimeError("SUNSCAR_V1_REFUSES_TAGGED_ACTOR_DESTRUCTION")
    if existing_preview:
        raise RuntimeError(
            "SUNSCAR_V1_REFUSES_DUPLICATE_PREVIEW existing=%d" % len(existing_preview)
        )
    for item, asset in resolved:
        location = item["planned_location_cm"]
        actor = actor_system.spawn_actor_from_object(
            asset,
            unreal.Vector(location["x"], location["y"], location["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(item["yaw_deg"])),
            transient=False,
        )
        actor.set_actor_label("OT_AUTO_%s" % item["candidate_id"])
        actor.tags = [
            unreal.Name(execution["placement_tag"]),
            unreal.Name(item["site_id"]),
            unreal.Name(item["bom_id"]),
            unreal.Name("UnreviewedAutomationPlacement"),
        ]
        actor.set_folder_path(unreal.Name("%s/%s" % (execution["placement_folder"], item["site_id"])))
        actor.set_actor_scale3d(unreal.Vector(float(item["scale"]), float(item["scale"]), float(item["scale"])))
        bounds_origin, bounds_extent = actor.get_actor_bounds(False)
        bottom_z = bounds_origin.z - bounds_extent.z
        grounding_offset = item["support_z_cm"] - bottom_z
        if abs(grounding_offset) > 0.001:
            actor.set_actor_location(
                unreal.Vector(location["x"], location["y"], location["z"] + grounding_offset),
                False,
                False,
            )
        final_location = actor.get_actor_location()
        item["final_location_cm"] = {
            "x": round(final_location.x, 3),
            "y": round(final_location.y, 3),
            "z": round(final_location.z, 3),
        }
        item["grounding_offset_cm"] = round(grounding_offset, 3)
        component = getattr(actor, "static_mesh_component", None)
        if component:
            component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "plan_path": plan_path,
    "registry_path": registry_path,
    "connected_slice_sites": config["connected_slice_sites"],
    "slice_record_count": len(slice_records),
    "automatic_ready_count": len(resolved),
    "manual_or_specialized_count": len(manual_records),
    "blocker_count": len(blockers),
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "blockers": blockers,
    "manual_or_specialized": manual_records,
    "automatic_candidates": [item for item, _asset in resolved],
    "changes_made": bool(created),
    "level_saved": False,
    "warning": "V1 never saves. Review every preview actor before separately authorized Save All.",
}

filename = "old_town_connected_slice_apply_preview.json" if apply_requested else "old_town_connected_slice_dry_run.json"
path = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_CONNECTED_SLICE mode=%s ready=%d manual=%d blockers=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(resolved), len(manual_records), len(blockers), len(created), path)
)
print("SUNSCAR_CONNECTED_SLICE", "APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(resolved), len(manual_records), len(blockers), len(created), path)
