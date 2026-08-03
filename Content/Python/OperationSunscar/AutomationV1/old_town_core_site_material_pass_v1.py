"""Dry-run-first material pass for the 20 Old Town site proxy actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarCoreSiteMaterialPassV1")
PROTOTYPE_PREFIX = "/Game/LevelPrototyping/Materials/"
MATERIAL_ROOT = "/Game/Maps/Sunscar/Art/Materials"
SITE_MATERIALS = {
    "SS_001": MATERIAL_ROOT + "/Ground/MI_OT_Ground_Earth",
    "SS_002": MATERIAL_ROOT + "/Ground/MI_OT_Ground_Silt",
    "SS_003": MATERIAL_ROOT + "/Instances/MI_OT_Stone",
    "SS_004": MATERIAL_ROOT + "/Instances/MI_OT_WarmStucco",
    "SS_005": MATERIAL_ROOT + "/Instances/MI_OT_PaleStucco",
    "SS_006": MATERIAL_ROOT + "/Instances/MI_OT_Stone",
    "SS_007": MATERIAL_ROOT + "/Instances/MI_OT_PaleStucco",
    "SS_008": MATERIAL_ROOT + "/Ground/MI_OT_Ground_Concrete",
    "SS_009": MATERIAL_ROOT + "/Ground/MI_OT_Ground_Asphalt",
    "SS_010": MATERIAL_ROOT + "/Instances/MI_OT_Detention",
    "SS_011": MATERIAL_ROOT + "/Instances/MI_OT_WarmStucco",
    "SS_012": MATERIAL_ROOT + "/Instances/MI_OT_PaleStucco",
    "SS_013": MATERIAL_ROOT + "/Instances/MI_OT_Stone",
    "SS_014": MATERIAL_ROOT + "/Ground/MI_OT_Ground_Earth",
    "SS_015": MATERIAL_ROOT + "/Instances/MI_OT_Metal",
    "SS_016": MATERIAL_ROOT + "/Instances/MI_OT_Metal",
    "SS_017": MATERIAL_ROOT + "/Instances/MI_OT_WarmStucco",
    "SS_018": MATERIAL_ROOT + "/Instances/MI_OT_Stone",
    "SS_019": MATERIAL_ROOT + "/Ground/MI_OT_Ground_Earth",
    "SS_020": MATERIAL_ROOT + "/Ground/MI_OT_Ground_Earth",
}

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if apply_requested and (dirty_content or dirty_maps):
    raise RuntimeError(
        "SUNSCAR_CORE_SITE_MATERIAL_APPLY_REFUSED preexisting_dirty_content=%d preexisting_dirty_maps=%d"
        % (len(dirty_content), len(dirty_maps))
    )

materials = {
    site_id: common.load_asset_checked(config, path)
    for site_id, path in SITE_MATERIALS.items()
}
actors = []
for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    if not label.startswith("SS_"):
        continue
    if common.actor_folder(actor) != "Sunscar/Blockout/Landmarks/Old Town Core":
        continue
    actors.append(actor)
if len(actors) != 20:
    raise RuntimeError("SUNSCAR_CORE_SITE_MATERIAL_SCOPE_REFUSED actor_count=%d" % len(actors))

records = []
for actor in sorted(actors, key=lambda value: value.get_actor_label()):
    site_id = actor.get_actor_label()[:6]
    if site_id not in materials:
        raise RuntimeError("SUNSCAR_CORE_SITE_MATERIAL_UNCLASSIFIED " + actor.get_actor_label())
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        raise RuntimeError("SUNSCAR_CORE_SITE_MATERIAL_NO_COMPONENT " + actor.get_actor_label())
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    target = materials[site_id]
    target_path = target.get_path_name()
    if not (current_path.startswith(PROTOTYPE_PREFIX) or current_path == target_path):
        raise RuntimeError(
            "SUNSCAR_CORE_SITE_MATERIAL_UNEXPECTED_SOURCE %s %s"
            % (actor.get_actor_label(), current_path)
        )
    origin, extent = actor.get_actor_bounds(False)
    record = {
        "site_id": site_id,
        "label": actor.get_actor_label(),
        "source_material": current_path,
        "target_material": target_path,
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
    "old_town_core_site_material_apply_v1.json"
    if apply_requested
    else "old_town_core_site_material_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_CORE_SITE_MATERIAL mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report)
)
print("SUNSCAR_CORE_SITE_MATERIAL", len(records), report)
