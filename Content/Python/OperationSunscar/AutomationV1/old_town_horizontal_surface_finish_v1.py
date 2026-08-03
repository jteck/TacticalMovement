"""Apply reviewed Quixel materials to Old Town floors, masonry roofs, access ramps, and courtyard walls, unsaved."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarHorizontalSurfaceFinishV1")
CONCRETE_PATH = "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/MI_OT_WeatheredConcreteGround_WorldAligned"
STUCCO_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_WorldAligned"
OLD_FLOOR_PATH = "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Concrete.MI_OT_Ground_Concrete"
OLD_STONE_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone.MI_OT_Stone"
OLD_RAMP_PATH = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray_Round.MI_PrototypeGrid_Gray_Round"
OLD_COURTYARD_PATH = "/Game/LevelPrototyping/Materials/MI_DefaultColorway.MI_DefaultColorway"
EXPECTED_COUNTS = {
    "floor": 19,
    "masonry_roof": 7,
    "access": 11,
    "courtyard_wall": 7,
}


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_REFUSED dirty_before=%d" % len(dirty_before))

concrete = common.load_asset_checked(config, CONCRETE_PATH)
stucco = common.load_asset_checked(config, STUCCO_PATH)
targets = []
counts = collections.Counter()
for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        continue
    material = component.get_material(0)
    source_path = material.get_path_name() if material else ""
    treatment = ""
    target = None
    if (
        folder.startswith("Sunscar/CorePlayable/Buildings/SS_")
        and "_F" in label
        and label.endswith("_Floor")
    ):
        treatment, target = "floor", concrete
        if source_path != OLD_FLOOR_PATH:
            raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_FLOOR_SOURCE_REFUSED %s %s" % (label, source_path))
    elif (
        folder.startswith("Sunscar/CorePlayable/Buildings/SS_")
        and label.startswith("Core_SS_")
        and label.endswith("_Roof")
        and source_path == OLD_STONE_PATH
    ):
        treatment, target = "masonry_roof", concrete
    elif (
        folder.startswith("Sunscar/CorePlayable/Buildings/SS_")
        and ("Ramp" in label or "Landing" in label)
    ):
        treatment, target = "access", concrete
        if source_path != OLD_RAMP_PATH:
            raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_ACCESS_SOURCE_REFUSED %s %s" % (label, source_path))
    elif folder == "Sunscar/CorePlayable/Buildings/CentralCourtyard":
        treatment, target = "courtyard_wall", stucco
        if source_path != OLD_COURTYARD_PATH:
            raise RuntimeError("SUNSCAR_HORIZONTAL_FINISH_COURTYARD_SOURCE_REFUSED %s %s" % (label, source_path))
    if treatment:
        counts[treatment] += 1
        targets.append((actor, treatment, target, source_path))

if dict(counts) != EXPECTED_COUNTS or len(targets) != sum(EXPECTED_COUNTS.values()):
    raise RuntimeError(
        "SUNSCAR_HORIZONTAL_FINISH_SCOPE_REFUSED expected=%s actual=%s total=%d"
        % (EXPECTED_COUNTS, dict(counts), len(targets))
    )

records = []
for actor, treatment, target, source_path in sorted(targets, key=lambda item: item[0].get_actor_label()):
    component = actor.static_mesh_component
    actor.modify()
    component.modify()
    component.set_material(0, target)
    if PASS_TAG not in list(actor.tags):
        actor.tags = list(actor.tags) + [PASS_TAG]
    records.append(
        {
            "label": actor.get_actor_label(),
            "folder": common.actor_folder(actor),
            "treatment": treatment,
            "source_material": source_path,
            "target_material": target.get_path_name(),
            "package": actor.get_package().get_name(),
        }
    )

dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
expected_maps = sorted({record["package"] for record in records})
if dirty_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_HORIZONTAL_FINISH_DIRTY_SCOPE_FAILED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_horizontal_surface_finish_ready",
    "context": context,
    "actor_count": len(records),
    "treatment_counts": dict(sorted(counts.items())),
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_horizontal_surface_finish_v1.json", payload)
unreal.log("SUNSCAR_HORIZONTAL_FINISH actors=%d report=%s" % (len(records), report))
print("SUNSCAR_HORIZONTAL_FINISH", len(records), report)
