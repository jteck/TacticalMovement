"""Dry-run-first stone material pass for the 12 Old Town perimeter walls."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarPerimeterWallMaterialPassV1")
PROTOTYPE_PREFIX = "/Game/LevelPrototyping/Materials/"
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone"

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if apply_requested and (dirty_content or dirty_maps):
    raise RuntimeError(
        "SUNSCAR_PERIMETER_MATERIAL_APPLY_REFUSED preexisting_dirty_content=%d preexisting_dirty_maps=%d"
        % (len(dirty_content), len(dirty_maps))
    )

target = common.load_asset_checked(config, TARGET_PATH)
actors = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if actor.get_actor_label().startswith("CoreWall_")
        and common.actor_folder(actor) == "Sunscar/CorePlayable/Walls/Perimeter"
    ],
    key=lambda actor: actor.get_actor_label(),
)
if len(actors) != 12:
    raise RuntimeError("SUNSCAR_PERIMETER_MATERIAL_SCOPE_REFUSED actor_count=%d" % len(actors))

records = []
for actor in actors:
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        raise RuntimeError("SUNSCAR_PERIMETER_MATERIAL_COMPONENT_REFUSED " + actor.get_actor_label())
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    if not (current_path.startswith(PROTOTYPE_PREFIX) or current_path == target.get_path_name()):
        raise RuntimeError(
            "SUNSCAR_PERIMETER_MATERIAL_UNEXPECTED_SOURCE %s %s"
            % (actor.get_actor_label(), current_path)
        )
    origin, extent = actor.get_actor_bounds(False)
    record = {
        "label": actor.get_actor_label(),
        "source_material": current_path,
        "target_material": target.get_path_name(),
        "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "package": actor.get_package().get_name(),
    }
    if apply_requested:
        actor.modify()
        component.modify()
        component.set_material(0, target)
        if PASS_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [PASS_TAG]
        record["applied_material"] = component.get_material(0).get_path_name()
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_perimeter_wall_material_apply_v1.json"
    if apply_requested
    else "old_town_perimeter_wall_material_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_PERIMETER_MATERIAL mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report)
)
print("SUNSCAR_PERIMETER_MATERIAL", len(records), report)
