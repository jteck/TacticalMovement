"""Replace the final 40 prototype-grid Old Town facade pieces, without saving."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarCompletePrototypeFacadesV1")
PROTOTYPE_PREFIX = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_"
SITE_TARGETS = {
    "SS_003": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone",
    "SS_010": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Detention",
    "SS_013": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone",
    "SS_015": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal",
    "SS_016": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal",
    "SS_018": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone",
}
EXPECTED_COUNTS = {
    "SS_003": 6,
    "SS_010": 9,
    "SS_013": 5,
    "SS_015": 5,
    "SS_016": 6,
    "SS_018": 9,
}


def site_from_label(label):
    marker = label.find("SS_")
    return label[marker:marker + 6] if marker >= 0 else ""


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError(
        "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_REFUSED dirty_before=%d" % len(dirty_before)
    )

materials = {
    site_id: common.load_asset_checked(config, path)
    for site_id, path in SITE_TARGETS.items()
}
targets_by_site = {site_id: [] for site_id in SITE_TARGETS}
for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    site_id = site_from_label(label)
    if site_id not in targets_by_site:
        continue
    folder = common.actor_folder(actor)
    tags = common.actor_tags(actor)
    core_exterior = (
        folder.startswith("Sunscar/CorePlayable/Buildings/")
        and "CoreCategory_Building" in tags
        and "Floor" not in label
        and "Roof" not in label
    )
    art_parapet = folder.startswith("OldTown_ArtDraft/") and "Parapet" in label
    if not (core_exterior or art_parapet):
        continue
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component and component.get_num_materials() == 1 else None
    material_path = material.get_path_name() if material else ""
    if material_path.startswith(PROTOTYPE_PREFIX):
        targets_by_site[site_id].append(actor)

actual_counts = {site_id: len(actors) for site_id, actors in targets_by_site.items()}
if actual_counts != EXPECTED_COUNTS:
    raise RuntimeError(
        "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SCOPE_REFUSED expected=%s actual=%s"
        % (EXPECTED_COUNTS, actual_counts)
    )

records = []
for site_id in sorted(targets_by_site):
    target_material = materials[site_id]
    for actor in sorted(targets_by_site[site_id], key=lambda item: item.get_actor_label()):
        component = actor.static_mesh_component
        source_material = component.get_material(0)
        source_path = source_material.get_path_name() if source_material else ""
        if not source_path.startswith(PROTOTYPE_PREFIX):
            raise RuntimeError(
                "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SOURCE_REFUSED %s %s"
                % (actor.get_actor_label(), source_path)
            )
        actor.modify()
        component.modify()
        component.set_material(0, target_material)
        if PASS_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [PASS_TAG]
        records.append(
            {
                "site_id": site_id,
                "label": actor.get_actor_label(),
                "source_material": source_path,
                "target_material": target_material.get_path_name(),
                "package": actor.get_package().get_name(),
            }
        )

dirty_content = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
expected_maps = sorted({record["package"] for record in records})
if dirty_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_DIRTY_SCOPE_FAILED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_complete_prototype_facades_ready",
    "context": context,
    "actor_count": len(records),
    "counts_by_site": actual_counts,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(
    config, "old_town_complete_prototype_facades_v1.json", payload
)
unreal.log(
    "SUNSCAR_COMPLETE_PROTOTYPE_FACADES actors=%d report=%s" % (len(records), report)
)
print("SUNSCAR_COMPLETE_PROTOTYPE_FACADES", len(records), report)
