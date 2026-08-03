"""Apply reviewed materials to three unsurfaced Old Town compound facades, unsaved."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarNamedCompoundFacadesV1")
PROTOTYPE_PREFIX = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_"
FOLDER_TARGETS = {
    "Sunscar/CorePlayable/Buildings/DetentionYard": (
        6,
        "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Detention",
        "detention_masonry",
    ),
    "Sunscar/CorePlayable/Buildings/SalvageYard": (
        6,
        "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_WorldAligned",
        "weathered_flaked_paint",
    ),
    "Sunscar/CorePlayable/Buildings/WaterTowerCompound": (
        8,
        "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_WorldAligned",
        "world_aligned_stucco",
    ),
}


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_NAMED_COMPOUND_FACADES_REFUSED dirty_before=%d" % len(dirty_before))

materials = {
    folder: common.load_asset_checked(config, definition[1])
    for folder, definition in FOLDER_TARGETS.items()
}
targets = {folder: [] for folder in FOLDER_TARGETS}
for actor in common.actor_subsystem().get_all_level_actors():
    folder = common.actor_folder(actor)
    if folder not in targets:
        continue
    if "CoreCategory_Building" not in common.actor_tags(actor):
        raise RuntimeError("SUNSCAR_NAMED_COMPOUND_FACADES_TAG_REFUSED " + actor.get_actor_label())
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component and component.get_num_materials() == 1 else None
    material_path = material.get_path_name() if material else ""
    if not material_path.startswith(PROTOTYPE_PREFIX):
        raise RuntimeError(
            "SUNSCAR_NAMED_COMPOUND_FACADES_SOURCE_REFUSED %s %s"
            % (actor.get_actor_label(), material_path)
        )
    targets[folder].append(actor)

actual_counts = {folder: len(actors) for folder, actors in targets.items()}
expected_counts = {folder: definition[0] for folder, definition in FOLDER_TARGETS.items()}
if actual_counts != expected_counts:
    raise RuntimeError(
        "SUNSCAR_NAMED_COMPOUND_FACADES_SCOPE_REFUSED expected=%s actual=%s"
        % (expected_counts, actual_counts)
    )

records = []
for folder in sorted(targets):
    target = materials[folder]
    treatment = FOLDER_TARGETS[folder][2]
    for actor in sorted(targets[folder], key=lambda item: item.get_actor_label()):
        component = actor.static_mesh_component
        source = component.get_material(0)
        actor.modify()
        component.modify()
        component.set_material(0, target)
        if PASS_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [PASS_TAG]
        records.append(
            {
                "folder": folder,
                "label": actor.get_actor_label(),
                "treatment": treatment,
                "source_material": source.get_path_name() if source else "",
                "target_material": target.get_path_name(),
                "package": actor.get_package().get_name(),
            }
        )

dirty_content = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
expected_maps = sorted({record["package"] for record in records})
if dirty_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_NAMED_COMPOUND_FACADES_DIRTY_SCOPE_FAILED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_named_compound_facades_ready",
    "context": context,
    "actor_count": len(records),
    "counts_by_folder": actual_counts,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_named_compound_facades_v1.json", payload)
unreal.log("SUNSCAR_NAMED_COMPOUND_FACADES actors=%d report=%s" % (len(records), report))
print("SUNSCAR_NAMED_COMPOUND_FACADES", len(records), report)
