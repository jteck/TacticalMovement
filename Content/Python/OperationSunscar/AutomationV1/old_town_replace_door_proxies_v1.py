"""Dry-run-first in-place replacement of 16 pedestrian door proxies."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownDoorReplacementV1")
PROXY_MESH = "/Game/LevelPrototyping/Meshes/SM_Cube.SM_Cube"
ASSET_REF = "source://FAB_P1B_001/old_wooden_door_wbmgdcpdw_high"
EXCLUDED_LABELS = {"Depot_LoadingDoor"}
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
if apply_requested:
    dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    if dirty_content or dirty_maps:
        raise RuntimeError(
            "SUNSCAR_DOOR_REPLACE_APPLY_REFUSED preexisting_content=%d preexisting_maps=%d"
            % (len(dirty_content), len(dirty_maps))
        )

registry = common.read_json(common.planning_file(config, "final_registry_file"))
target_path = common.safe_asset_ref_to_path(ASSET_REF, registry)
target_mesh = common.load_asset_checked(config, target_path)
if not isinstance(target_mesh, unreal.StaticMesh):
    raise RuntimeError("SUNSCAR_DOOR_REPLACE_TARGET_NOT_MESH " + str(target_path))
box = target_mesh.get_bounding_box()
mesh_size = box.max - box.min
all_actors = list(common.actor_subsystem().get_all_level_actors())
targets = sorted(
    [
        actor for actor in all_actors
        if isinstance(actor, unreal.StaticMeshActor)
        and "door" in actor.get_actor_label().lower()
        and actor.get_actor_label() not in EXCLUDED_LABELS
    ],
    key=lambda actor: actor.get_actor_label(),
)
if len(targets) != 16:
    raise RuntimeError("SUNSCAR_DOOR_REPLACE_SCOPE actor_count=%d" % len(targets))

records = []
for actor in targets:
    component = actor.static_mesh_component
    source_path = common.actor_mesh_path(actor)
    if source_path not in (PROXY_MESH, target_mesh.get_path_name()):
        raise RuntimeError("SUNSCAR_DOOR_REPLACE_UNEXPECTED_SOURCE %s %s" % (actor.get_actor_label(), source_path))
    before_origin, before_extent = actor.get_actor_bounds(False)
    before_bottom = before_origin.z - before_extent.z
    before_rotation = actor.get_actor_rotation()
    target_scale = unreal.Vector(
        before_extent.x * 2.0 / mesh_size.x,
        before_extent.y * 2.0 / mesh_size.y,
        before_extent.z * 2.0 / mesh_size.z,
    )
    record = {
        "label": actor.get_actor_label(),
        "source_mesh": source_path,
        "target_mesh": target_mesh.get_path_name(),
        "before_origin_cm": [round(before_origin.x, 3), round(before_origin.y, 3), round(before_origin.z, 3)],
        "before_bottom_z_cm": round(before_bottom, 3),
        "before_dimensions_cm": [round(before_extent.x * 2.0, 3), round(before_extent.y * 2.0, 3), round(before_extent.z * 2.0, 3)],
        "target_scale": [round(target_scale.x, 6), round(target_scale.y, 6), round(target_scale.z, 6)],
        "rotation": {"pitch": round(before_rotation.pitch, 3), "yaw": round(before_rotation.yaw, 3), "roll": round(before_rotation.roll, 3)},
        "package": actor.get_package().get_name(),
    }
    if apply_requested:
        actor.modify()
        component.modify()
        component.set_editor_property("override_materials", [])
        component.set_editor_property("static_mesh", target_mesh)
        actor.set_actor_scale3d(target_scale)
        actor.set_actor_rotation(before_rotation, False)
        after_origin, after_extent = actor.get_actor_bounds(False)
        after_bottom = after_origin.z - after_extent.z
        actor.add_actor_world_offset(
            unreal.Vector(
                before_origin.x - after_origin.x,
                before_origin.y - after_origin.y,
                before_bottom - after_bottom,
            ),
            False,
            False,
        )
        component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        if TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [TAG, unreal.Name("QuixelPedestrianDoor")]
        final_origin, final_extent = actor.get_actor_bounds(False)
        record["after_origin_cm"] = [round(final_origin.x, 3), round(final_origin.y, 3), round(final_origin.z, 3)]
        record["after_bottom_z_cm"] = round(final_origin.z - final_extent.z, 3)
        record["after_dimensions_cm"] = [round(final_extent.x * 2.0, 3), round(final_extent.y * 2.0, 3), round(final_extent.z * 2.0, 3)]
        record["after_materials"] = [
            component.get_material(index).get_path_name() if component.get_material(index) else ""
            for index in range(component.get_num_materials())
        ]
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "excluded_labels": sorted(EXCLUDED_LABELS),
    "target_mesh": target_mesh.get_path_name(),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = "old_town_replace_door_proxies_apply_preview_v1.json" if apply_requested else "old_town_replace_door_proxies_dry_run_v1.json"
report = common.write_json_report(config, filename, payload)
unreal.log("SUNSCAR_DOOR_REPLACE mode=%s actors=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report))
print("SUNSCAR_DOOR_REPLACE", len(records), report)
