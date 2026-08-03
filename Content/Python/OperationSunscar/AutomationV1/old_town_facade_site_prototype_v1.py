"""Dry-run-first Quixel stucco prototype on the six SS_005 wall actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarFacadePrototypeV1")
SOURCE_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_PaleStucco"
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_Quixel"
EXPECTED_LABELS = [
    "Core_SS_005_F1_N_Wall",
    "Core_SS_005_F1_W_Wall",
    "Core_SS_005_F2_E_Wall",
    "Core_SS_005_F2_N_Wall",
    "Core_SS_005_F2_S_Wall",
    "Core_SS_005_F2_W_Wall",
]


config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if apply_requested and dirty_before:
    raise RuntimeError("SUNSCAR_FACADE_SITE_APPLY_REFUSED dirty_before=%d" % len(dirty_before))
target = common.load_asset_checked(config, TARGET_PATH)
actors_by_label = {
    actor.get_actor_label(): actor for actor in common.actor_subsystem().get_all_level_actors()
}
missing = sorted(set(EXPECTED_LABELS) - set(actors_by_label))
if missing:
    raise RuntimeError("SUNSCAR_FACADE_SITE_SCOPE_REFUSED missing=%s" % "|".join(missing))

records = []
for label in EXPECTED_LABELS:
    actor = actors_by_label[label]
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        raise RuntimeError("SUNSCAR_FACADE_SITE_COMPONENT_REFUSED " + label)
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    if current_path not in (SOURCE_PATH + ".MI_OT_PaleStucco", TARGET_PATH + ".MI_OT_Stucco_Quixel"):
        raise RuntimeError(
            "SUNSCAR_FACADE_SITE_SOURCE_REFUSED %s %s" % (label, current_path)
        )
    record = {
        "label": label,
        "source_material": current_path,
        "target_material": TARGET_PATH,
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
    "site_id": "SS_005",
    "actor_count": len(records),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_facade_site_prototype_apply_v1.json"
    if apply_requested
    else "old_town_facade_site_prototype_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_FACADE_SITE_PROTOTYPE mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report)
)
print("SUNSCAR_FACADE_SITE_PROTOTYPE", len(records), report)
