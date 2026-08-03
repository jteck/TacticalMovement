"""Dry-run-first non-traversable rooftop utility accents for Old Town."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownRooftopUtilityV1")
FOLDER = "OldTown_ArtDraft/RooftopUtilityV1"
SITES = ("SS_003", "SS_007", "SS_013", "SS_015", "SS_018")
FAN_PATH = "/Game/Scene_Junkyard/Assets/MS/3D/Ind_Jun_Fan_Metal_Rusty_01/SM_Ind_Jun_Fan_Metal_Rusty_01"
CYLINDER_PATH = "/Engine/BasicShapes/Cylinder.Cylinder"
METAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal"
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_ROOFTOP_UTILITY_DUPLICATE existing=%d" % len(existing))

fan = unreal.EditorAssetLibrary.load_asset(FAN_PATH)
cylinder = unreal.EditorAssetLibrary.load_asset(CYLINDER_PATH)
metal = unreal.EditorAssetLibrary.load_asset(METAL_PATH)
if not isinstance(fan, unreal.StaticMesh) or not isinstance(cylinder, unreal.StaticMesh) or metal is None:
    raise RuntimeError("SUNSCAR_ROOFTOP_UTILITY_REQUIRED_ASSET_MISSING")

roofs = {}
for site in SITES:
    label = "Core_%s_Roof" % site
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    if len(matches) == 1:
        roofs[site] = matches[0]

candidate_ids = {}
for site in SITES:
    matches = sorted(
        [row["candidate_id"] for row in plan if row["site_id"] == site and row["bom_id"] == "OT_UTIL_007"]
    )
    candidate_ids[site] = matches[:2]

ready = []
blockers = []
for site_index, site in enumerate(SITES):
    roof = roofs.get(site)
    ids = candidate_ids.get(site, [])
    if roof is None or len(ids) < 2:
        blockers.append({"site_id": site, "reason": "roof_or_two_candidates_missing"})
        continue
    roof_origin, roof_extent = roof.get_actor_bounds(False)
    roof_top = roof_origin.z + roof_extent.z
    offsets = (
        (-0.28 + 0.03 * (site_index % 2), 0.24),
        (0.30, -0.22 + 0.03 * (site_index % 3)),
    )
    for kind_index, kind in enumerate(("fan_vent", "antenna_mast")):
        x = roof_origin.x + roof_extent.x * offsets[kind_index][0]
        y = roof_origin.y + roof_extent.y * offsets[kind_index][1]
        if kind == "fan_vent":
            bounds = fan.get_bounds()
            base_dims = bounds.box_extent * 2.0
            scale = min(1.0, 120.0 / max(base_dims.x, base_dims.y))
            dimensions = base_dims * scale
            local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
            z = roof_top - local_min_z
            asset = fan
        else:
            scale = 1.0
            dimensions = unreal.Vector(7.0, 7.0, 180.0)
            z = roof_top + 90.0
            asset = cylinder
        edge_clearance_x = roof_extent.x - abs(x - roof_origin.x) - dimensions.x * 0.5
        edge_clearance_y = roof_extent.y - abs(y - roof_origin.y) - dimensions.y * 0.5
        if min(edge_clearance_x, edge_clearance_y) < 150.0:
            blockers.append({
                "site_id": site,
                "candidate_id": ids[kind_index],
                "reason": "roof_edge_clearance_below_150cm",
                "edge_clearance_cm": round(min(edge_clearance_x, edge_clearance_y), 3),
            })
            continue
        ready.append({
            "site_id": site,
            "candidate_id": ids[kind_index],
            "kind": kind,
            "roof_actor": roof.get_actor_label(),
            "roof_top_z_cm": round(roof_top, 3),
            "location_cm": {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3)},
            "dimensions_cm": {"x": round(dimensions.x, 3), "y": round(dimensions.y, 3), "z": round(dimensions.z, 3)},
            "scale": round(scale, 6),
            "asset_path": asset.get_path_name().split(".")[0],
            "edge_clearance_cm": round(min(edge_clearance_x, edge_clearance_y), 3),
            "asset": asset,
        })

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_ROOFTOP_UTILITY_APPLY_BLOCKED blockers=%d" % len(blockers))

created = []
if apply_requested:
    for item in ready:
        location = item["location_cm"]
        actor = actor_system.spawn_actor_from_object(
            item["asset"],
            unreal.Vector(location["x"], location["y"], location["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=float((len(created) * 47) % 360)),
            transient=False,
        )
        if item["kind"] == "fan_vent":
            scale = item["scale"]
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        else:
            actor.set_actor_scale3d(unreal.Vector(0.07, 0.07, 1.8))
            actor.static_mesh_component.set_material(0, metal)
        origin, extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(
            unreal.Vector(0.0, 0.0, item["roof_top_z_cm"] - (origin.z - extent.z)),
            False,
            False,
        )
        actor.static_mesh_component.set_collision_profile_name("NoCollision")
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        actor.set_actor_label("OT_ROOFUTIL_%s" % item["candidate_id"])
        actor.tags = [
            TAG,
            unreal.Name(item["site_id"]),
            unreal.Name("OT_UTIL_007"),
            unreal.Name(item["candidate_id"]),
            unreal.Name("NonTraversableDecorativeUtility"),
            unreal.Name("ReviewedAutomationPlacement"),
        ]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        created.append(actor.get_actor_label())

serial_ready = [{key: value for key, value in item.items() if key != "asset"} for item in ready]
payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "site_count": len(SITES),
    "ready_count": len(ready),
    "blocker_count": len(blockers),
    "blockers": blockers,
    "ready": serial_ready,
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "changes_made": bool(created),
    "level_saved": False,
    "collision_policy": "NoCollision; rooftop silhouette detail only",
    "excluded_site": "SS_006 Water Tower already has four Tower_Utility actors and a protected landmark silhouette",
}
name = "old_town_rooftop_utility_apply_preview_v1.json" if apply_requested else "old_town_rooftop_utility_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_ROOFTOP_UTILITY mode=%s ready=%d blockers=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report)
)
print("SUNSCAR_ROOFTOP_UTILITY", len(ready), len(blockers), len(created), report)
