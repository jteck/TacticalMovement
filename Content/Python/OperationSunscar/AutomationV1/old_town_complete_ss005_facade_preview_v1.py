"""Complete the unsaved Quixel stucco preview across all SS_005 exterior pieces."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarFacadePrototypeV1")
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_Quixel"
INITIAL_DIRTY_LABELS = {
    "Core_SS_005_F1_N_Wall",
    "Core_SS_005_F1_W_Wall",
    "Core_SS_005_F2_E_Wall",
    "Core_SS_005_F2_N_Wall",
    "Core_SS_005_F2_S_Wall",
    "Core_SS_005_F2_W_Wall",
}
TARGET_LABELS = sorted(INITIAL_DIRTY_LABELS | {
    "Core_SS_005_F1_E_Left",
    "Core_SS_005_F1_E_Lintel",
    "Core_SS_005_F1_E_Right",
    "Core_SS_005_F1_S_Left",
    "Core_SS_005_F1_S_Lintel",
    "Core_SS_005_F1_S_Right",
    "SS_005_Parapet_E",
    "SS_005_Parapet_N",
    "SS_005_Parapet_S",
    "SS_005_Parapet_W",
})
ALLOWED_SOURCE_PREFIXES = (
    "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_PaleStucco.",
    TARGET_PATH + ".MI_OT_Stucco_Quixel",
)


def dirty_names():
    return {
        package.get_name()
        for package in (
            list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
            + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
        )
    }


config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
target = common.load_asset_checked(config, TARGET_PATH)
actors_by_label = {
    actor.get_actor_label(): actor for actor in common.actor_subsystem().get_all_level_actors()
}
missing = sorted(set(TARGET_LABELS) - set(actors_by_label))
if missing:
    raise RuntimeError("SUNSCAR_SS005_FACADE_COMPLETE_SCOPE_REFUSED missing=%s" % "|".join(missing))

initial_dirty_packages = {
    actors_by_label[label].get_package().get_name() for label in INITIAL_DIRTY_LABELS
}
before = dirty_names()
if before != initial_dirty_packages:
    raise RuntimeError(
        "SUNSCAR_SS005_FACADE_COMPLETE_REFUSED dirty_before=%s" % "|".join(sorted(before))
    )

records = []
for label in TARGET_LABELS:
    actor = actors_by_label[label]
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        raise RuntimeError("SUNSCAR_SS005_FACADE_COMPLETE_COMPONENT_REFUSED " + label)
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    if not current_path.startswith(ALLOWED_SOURCE_PREFIXES):
        raise RuntimeError(
            "SUNSCAR_SS005_FACADE_COMPLETE_SOURCE_REFUSED %s %s" % (label, current_path)
        )
    if apply_requested:
        actor.modify()
        component.modify()
        component.set_material(0, target)
        if PASS_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [PASS_TAG]
    records.append({
        "label": label,
        "source_material": current_path,
        "target_material": TARGET_PATH,
        "package": actor.get_package().get_name(),
    })

expected_after = {actors_by_label[label].get_package().get_name() for label in TARGET_LABELS}
after = dirty_names()
if apply_requested and after != expected_after:
    raise RuntimeError(
        "SUNSCAR_SS005_FACADE_COMPLETE_SCOPE_FAILED dirty_after=%s" % "|".join(sorted(after))
    )

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "site_id": "SS_005",
    "actor_count": len(records),
    "records": records,
    "dirty_packages_after": sorted(after),
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_complete_ss005_facade_apply_v1.json"
    if apply_requested
    else "old_town_complete_ss005_facade_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_SS005_FACADE_COMPLETE mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report)
)
print("SUNSCAR_SS005_FACADE_COMPLETE", len(records), report)
