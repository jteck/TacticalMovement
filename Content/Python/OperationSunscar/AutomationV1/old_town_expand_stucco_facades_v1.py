"""Dry-run-first expansion of the approved Quixel stucco facade standard."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarFacadeExpansionV1")
TARGET_SITES = {"SS_004", "SS_007", "SS_012"}
EXPECTED_COUNTS = {"SS_004": 12, "SS_007": 22, "SS_012": 16}
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_Quixel"
ALLOWED_PREFIXES = (
    "/Game/LevelPrototyping/Materials/",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_PaleStucco.",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_WarmStucco.",
    TARGET_PATH + ".MI_OT_Stucco_Quixel",
)


def site_from_label(label):
    marker = label.find("SS_")
    return label[marker:marker + 6] if marker >= 0 else ""


def is_exterior(actor):
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    tags = common.actor_tags(actor)
    core = (
        folder.startswith("Sunscar/CorePlayable/Buildings/")
        and "CoreCategory_Building" in tags
        and "Floor" not in label
        and "Roof" not in label
    )
    parapet = folder.startswith("OldTown_ArtDraft/") and "Parapet" in label
    return core or parapet


config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_STUCCO_EXPANSION_REFUSED dirty_before=%d" % len(dirty_before))
target = common.load_asset_checked(config, TARGET_PATH)
actors = []
for actor in common.actor_subsystem().get_all_level_actors():
    site_id = site_from_label(actor.get_actor_label())
    if site_id in TARGET_SITES and is_exterior(actor):
        actors.append((actor, site_id))
actors.sort(key=lambda item: item[0].get_actor_label())
counts = collections.Counter(site_id for _, site_id in actors)
if len(actors) != 50 or dict(counts) != EXPECTED_COUNTS:
    raise RuntimeError(
        "SUNSCAR_STUCCO_EXPANSION_SCOPE_REFUSED actors=%d counts=%s"
        % (len(actors), dict(counts))
    )

records = []
for actor, site_id in actors:
    label = actor.get_actor_label()
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        raise RuntimeError("SUNSCAR_STUCCO_EXPANSION_COMPONENT_REFUSED " + label)
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    if not current_path.startswith(ALLOWED_PREFIXES):
        raise RuntimeError(
            "SUNSCAR_STUCCO_EXPANSION_SOURCE_REFUSED %s %s" % (label, current_path)
        )
    if apply_requested:
        actor.modify()
        component.modify()
        component.set_material(0, target)
        if PASS_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [PASS_TAG]
    records.append({
        "site_id": site_id,
        "label": label,
        "source_material": current_path,
        "target_material": TARGET_PATH,
        "package": actor.get_package().get_name(),
    })

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "site_counts": dict(sorted(counts.items())),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_expand_stucco_facades_apply_v1.json"
    if apply_requested
    else "old_town_expand_stucco_facades_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_STUCCO_EXPANSION mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report)
)
print("SUNSCAR_STUCCO_EXPANSION", len(records), report)
