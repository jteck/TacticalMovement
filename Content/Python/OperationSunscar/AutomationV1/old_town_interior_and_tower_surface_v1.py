"""Apply reviewed materials to 14 Old Town interior partitions and two tower pieces, unsaved."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarInteriorAndTowerSurfaceV1")
INTERIOR_SOURCE = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray_02.MI_PrototypeGrid_Gray_02"
PILLAR_SOURCE = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark.MI_PrototypeGrid_TopDark"
PLATFORM_SOURCE = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray_Round.MI_PrototypeGrid_Gray_Round"
MATERIALS = {
    "interior": "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_WorldAligned",
    "tower_pillar": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal",
    "tower_platform": "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/MI_OT_WeatheredConcreteGround_WorldAligned",
}
EXPECTED_COUNTS = {"interior": 14, "tower_pillar": 1, "tower_platform": 1}


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if dirty_before:
    raise RuntimeError("SUNSCAR_INTERIOR_TOWER_REFUSED dirty_before=%s" % "|".join(dirty_before))
loaded_materials = {role: common.load_asset_checked(config, path) for role, path in MATERIALS.items()}
targets = []
counts = collections.Counter()
for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    if not folder.startswith("Sunscar/CorePlayable/Buildings/SS_"):
        continue
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        continue
    material = component.get_material(0)
    source = material.get_path_name() if material else ""
    role = ""
    expected_source = ""
    if "_Interior_" in label:
        role, expected_source = "interior", INTERIOR_SOURCE
    elif label == "Core_SS_006_TowerPillar":
        role, expected_source = "tower_pillar", PILLAR_SOURCE
    elif label == "Core_SS_006_TowerPlatform":
        role, expected_source = "tower_platform", PLATFORM_SOURCE
    if role:
        if source != expected_source:
            raise RuntimeError("SUNSCAR_INTERIOR_TOWER_SOURCE_REFUSED %s %s" % (label, source))
        counts[role] += 1
        targets.append((actor, role, source))
if dict(counts) != EXPECTED_COUNTS or len(targets) != 16:
    raise RuntimeError("SUNSCAR_INTERIOR_TOWER_SCOPE_REFUSED expected=%s actual=%s" % (EXPECTED_COUNTS, dict(counts)))

records = []
for actor, role, source in sorted(targets, key=lambda item: item[0].get_actor_label()):
    target = loaded_materials[role]
    actor.modify()
    actor.static_mesh_component.modify()
    actor.static_mesh_component.set_material(0, target)
    actor.tags = list(actor.tags) + [PASS_TAG]
    records.append(
        {
            "label": actor.get_actor_label(),
            "folder": common.actor_folder(actor),
            "treatment": role,
            "source_material": source,
            "target_material": target.get_path_name(),
            "package": actor.get_package().get_name(),
        }
    )
dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
expected_maps = sorted(record["package"] for record in records)
if dirty_content or dirty_maps != expected_maps:
    raise RuntimeError("SUNSCAR_INTERIOR_TOWER_DIRTY_SCOPE_REFUSED content=%s maps=%s" % ("|".join(dirty_content), "|".join(dirty_maps)))
payload = {
    "schema_version": 1,
    "status": "unsaved_interior_and_tower_surface_ready",
    "context": context,
    "actor_count": len(records),
    "treatment_counts": dict(sorted(counts.items())),
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_interior_and_tower_surface_v1.json", payload)
unreal.log("SUNSCAR_INTERIOR_TOWER actors=%d report=%s" % (len(records), report))
print("SUNSCAR_INTERIOR_TOWER", len(records), report)
