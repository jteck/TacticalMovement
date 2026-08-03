"""Dry-run-first Quixel flaked-paint prototype on all ten SS_017 exterior pieces."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarFlakedFacadePrototypeV1")
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_Quixel"
EXPECTED_LABELS = [
    "Core_SS_017_F1_E_Left",
    "Core_SS_017_F1_E_Lintel",
    "Core_SS_017_F1_E_Right",
    "Core_SS_017_F1_N_Left",
    "Core_SS_017_F1_N_Lintel",
    "Core_SS_017_F1_N_Right",
    "Core_SS_017_F1_S_Wall",
    "Core_SS_017_F1_W_Left",
    "Core_SS_017_F1_W_Lintel",
    "Core_SS_017_F1_W_Right",
]
ALLOWED_PREFIXES = (
    "/Game/LevelPrototyping/Materials/",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_WarmStucco.",
    TARGET_PATH + ".MI_OT_FlakedPaint_Quixel",
)


config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_FLAKED_FACADE_REFUSED dirty_before=%d" % len(dirty_before))
target = common.load_asset_checked(config, TARGET_PATH)
actors_by_label = {
    actor.get_actor_label(): actor for actor in common.actor_subsystem().get_all_level_actors()
}
missing = sorted(set(EXPECTED_LABELS) - set(actors_by_label))
if missing:
    raise RuntimeError("SUNSCAR_FLAKED_FACADE_SCOPE_REFUSED missing=%s" % "|".join(missing))
records = []
for label in EXPECTED_LABELS:
    actor = actors_by_label[label]
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        raise RuntimeError("SUNSCAR_FLAKED_FACADE_COMPONENT_REFUSED " + label)
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    if not current_path.startswith(ALLOWED_PREFIXES):
        raise RuntimeError("SUNSCAR_FLAKED_FACADE_SOURCE_REFUSED %s %s" % (label, current_path))
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
payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "site_id": "SS_017",
    "actor_count": len(records),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_flaked_facade_prototype_apply_v1.json"
    if apply_requested
    else "old_town_flaked_facade_prototype_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log("SUNSCAR_FLAKED_FACADE mode=%s actors=10 report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", report))
print("SUNSCAR_FLAKED_FACADE", report)
