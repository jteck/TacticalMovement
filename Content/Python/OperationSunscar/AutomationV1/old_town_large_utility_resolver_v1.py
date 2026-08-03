"""Resolve and optionally place four deferred large electrical cabinets safely."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


MESH_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_004_ujzfde2/"
    "Electrical_Cabinet_ujzfde2_High"
)
TAG = unreal.Name("SunscarOldTownLargeUtilityResolvedV1")
BASE_FOLDER = "OldTown_AutomationPreview/LargeUtilityResolvedV1"
DIMENSIONS_CM = (262.0, 87.3, 138.8)
SPECS = [
    {
        "candidate_id": "SS_003_UTILITY_008",
        "site_id": "SS_003",
        "floor_label": "Core_SS_003_F1_Floor",
        "x": -10038.4,
        "y": -6986.4,
        "yaw": 9.18,
    },
    {
        "candidate_id": "SS_003_UTILITY_013",
        "site_id": "SS_003",
        "floor_label": "Core_SS_003_F1_Floor",
        "x": -11372.9,
        "y": -6574.7,
        "yaw": 87.75,
    },
    {
        "candidate_id": "SS_016_UTILITY_020",
        "site_id": "SS_016",
        "floor_label": "Core_SS_016_F1_Floor",
        "x": 4812.5,
        "y": -7663.4,
        "yaw": 99.74,
    },
    {
        "candidate_id": "SS_016_UTILITY_027",
        "site_id": "SS_016",
        "floor_label": "Core_SS_016_F1_Floor",
        "x": 4871.6,
        "y": -6652.9,
        "yaw": 86.63,
    },
]


def projected_extent(yaw_deg):
    radians = math.radians(yaw_deg)
    half_x = DIMENSIONS_CM[0] * 0.5
    half_y = DIMENSIONS_CM[1] * 0.5
    return unreal.Vector(
        abs(math.cos(radians)) * half_x + abs(math.sin(radians)) * half_y,
        abs(math.sin(radians)) * half_x + abs(math.cos(radians)) * half_y,
        DIMENSIONS_CM[2] * 0.5,
    )


def overlaps(origin_a, extent_a, origin_b, extent_b, clearance_xy):
    return (
        abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x + clearance_xy
        and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y + clearance_xy
        and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z + 5.0
    )


def ignore_support_or_editor_actor(actor):
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    tags = common.actor_tags(actor)
    if isinstance(actor, (unreal.LandscapeProxy, unreal.TextRenderActor, unreal.Volume)):
        return True
    if folder.startswith("Sunscar/TemporaryLabels") or "SunscarTemporaryLabel" in tags:
        return True
    if "SunscarCoreSourceFootprint" in tags:
        return True
    if "Floor" in label or "Roof" in label:
        return True
    return label.startswith(("Ground_", "Route_", "District_", "CoreRoute_"))


def clearance_for(label):
    if "Door" in label or "Gate" in label:
        return 100.0
    if "Window" in label:
        return 50.0
    if "Wall" in label or "Interior" in label:
        return 12.0
    return 30.0


def candidate_offsets():
    values = []
    for dx in range(-250, 251, 25):
        for dy in range(-250, 251, 25):
            values.append((dx * dx + dy * dy, abs(dx) + abs(dy), dx, dy))
    values.sort()
    return [(float(dx), float(dy)) for _d2, _d1, dx, dy in values]


config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_REFUSED dirty_before=%d" % len(dirty_before))
mesh = common.load_asset_checked(config, MESH_PATH)
if not isinstance(mesh, unreal.StaticMesh):
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_MESH_INVALID")

actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if str(TAG) in common.actor_tags(actor)]
if existing:
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_DUPLICATE existing=%d" % len(existing))
actors_by_label = {actor.get_actor_label(): actor for actor in actors}
blocker_bounds = []
for actor in actors:
    if ignore_support_or_editor_actor(actor):
        continue
    origin, extent = actor.get_actor_bounds(False, False)
    if extent.z <= 20.0:
        continue
    blocker_bounds.append((actor.get_actor_label(), origin, extent))

resolved = []
reserved = []
for spec in SPECS:
    floor = actors_by_label.get(spec["floor_label"])
    if floor is None:
        raise RuntimeError("SUNSCAR_LARGE_UTILITY_FLOOR_MISSING " + spec["floor_label"])
    floor_origin, floor_extent = floor.get_actor_bounds(False, False)
    floor_top = floor_origin.z + floor_extent.z
    extent = projected_extent(spec["yaw"])
    chosen = None
    rejected = []
    for dx, dy in candidate_offsets():
        origin = unreal.Vector(spec["x"] + dx, spec["y"] + dy, floor_top + extent.z)
        inside_floor = (
            abs(origin.x - floor_origin.x) + extent.x <= floor_extent.x - 20.0
            and abs(origin.y - floor_origin.y) + extent.y <= floor_extent.y - 20.0
        )
        if not inside_floor:
            continue
        collisions = []
        for label, other_origin, other_extent in blocker_bounds + reserved:
            if overlaps(
                origin,
                extent,
                other_origin,
                other_extent,
                clearance_for(label),
            ):
                collisions.append(label)
        if collisions:
            if len(rejected) < 8:
                rejected.append({"offset_cm": [dx, dy], "blockers": sorted(set(collisions))})
            continue
        chosen = origin
        break
    item = dict(spec)
    item["projected_dimensions_cm"] = [extent.x * 2.0, extent.y * 2.0, extent.z * 2.0]
    item["floor_top_z_cm"] = floor_top
    item["sample_rejections"] = rejected
    if chosen is None:
        item["status"] = "deferred_no_safe_floor_position"
        resolved.append(item)
        continue
    item["status"] = "safe_position_resolved"
    item["resolved_center_cm"] = [chosen.x, chosen.y, chosen.z]
    item["offset_from_plan_cm"] = [chosen.x - spec["x"], chosen.y - spec["y"]]
    resolved.append(item)
    reserved.append(("RESERVED_" + spec["candidate_id"], chosen, extent))

ready = [item for item in resolved if item["status"] == "safe_position_resolved"]
if apply_requested and len(ready) != len(SPECS):
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_APPLY_BLOCKED ready=%d" % len(ready))

created = []
if apply_requested:
    for item in ready:
        center = item["resolved_center_cm"]
        actor = actor_system.spawn_actor_from_object(
            mesh,
            unreal.Vector(center[0], center[1], center[2]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=item["yaw"]),
            transient=False,
        )
        actor.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
        actual_origin, actual_extent = actor.get_actor_bounds(False, False)
        actor.add_actor_world_offset(
            unreal.Vector(
                center[0] - actual_origin.x,
                center[1] - actual_origin.y,
                item["floor_top_z_cm"] - (actual_origin.z - actual_extent.z),
            ),
            False,
            False,
        )
        label = "OT_UTIL_" + item["candidate_id"]
        actor.set_actor_label(label)
        actor.tags = [
            TAG,
            unreal.Name(item["site_id"]),
            unreal.Name("OT_UTIL_003"),
            unreal.Name("UnreviewedAutomationPlacement"),
        ]
        actor.set_folder_path(
            unreal.Name("%s/%s" % (BASE_FOLDER, item["site_id"]))
        )
        actor.static_mesh_component.set_collision_enabled(
            unreal.CollisionEnabled.QUERY_AND_PHYSICS
        )
        created.append(label)

dirty_content = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if apply_requested:
    allowed_roots = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    if dirty_content or not dirty_maps or any(
        not package.startswith(allowed_roots) for package in dirty_maps
    ):
        raise RuntimeError(
            "SUNSCAR_LARGE_UTILITY_DIRTY_SCOPE_FAILED content=%s maps=%s"
            % ("|".join(dirty_content), "|".join(dirty_maps))
        )

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "mesh_path": MESH_PATH,
    "planned_count": len(SPECS),
    "ready_count": len(ready),
    "deferred_count": len(SPECS) - len(ready),
    "resolved": resolved,
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": bool(created),
    "level_saved": False,
}
filename = (
    "old_town_large_utility_resolver_apply_v1.json"
    if apply_requested
    else "old_town_large_utility_resolver_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_LARGE_UTILITY mode=%s ready=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(created), report)
)
print("SUNSCAR_LARGE_UTILITY", report)
