"""Save exactly the reviewed 20 named-compound facade actor packages."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarNamedCompoundFacadesV1"
FOLDER_TARGETS = {
    "Sunscar/CorePlayable/Buildings/DetentionYard": (6, "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Detention"),
    "Sunscar/CorePlayable/Buildings/SalvageYard": (6, "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_WorldAligned"),
    "Sunscar/CorePlayable/Buildings/WaterTowerCompound": (8, "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_WorldAligned"),
}


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
materials = {
    folder: common.load_asset_checked(config, definition[1])
    for folder, definition in FOLDER_TARGETS.items()
}
actors = sorted(
    [actor for actor in common.actor_subsystem().get_all_level_actors() if PASS_TAG in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
counts = {folder: 0 for folder in FOLDER_TARGETS}
for actor in actors:
    folder = common.actor_folder(actor)
    if folder not in counts:
        raise RuntimeError("SUNSCAR_NAMED_COMPOUND_FACADES_SAVE_FOLDER_REFUSED " + folder)
    counts[folder] += 1
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    if material != materials[folder]:
        raise RuntimeError("SUNSCAR_NAMED_COMPOUND_FACADES_SAVE_MATERIAL_REFUSED " + actor.get_actor_label())
expected_counts = {folder: definition[0] for folder, definition in FOLDER_TARGETS.items()}
if counts != expected_counts or len(actors) != 20:
    raise RuntimeError("SUNSCAR_NAMED_COMPOUND_FACADES_SAVE_SCOPE_REFUSED counts=%s" % counts)

packages = {actor.get_package() for actor in actors}
expected_maps = {package.get_name() for package in packages}
dirty_content = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_NAMED_COMPOUND_FACADES_SAVE_DIRTY_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps)))
    )
ordered_packages = sorted(packages, key=lambda package: package.get_name())
if not unreal.EditorLoadingAndSavingUtils.save_packages(ordered_packages, True):
    raise RuntimeError("SUNSCAR_NAMED_COMPOUND_FACADES_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("SUNSCAR_NAMED_COMPOUND_FACADES_SAVE_DIRTY_AFTER %s" % "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_named_compound_facades_saved",
    "context": context,
    "actor_count": len(actors),
    "counts_by_folder": counts,
    "saved_packages": [package.get_name() for package in ordered_packages],
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_named_compound_facades_v1.json", payload)
unreal.log("SUNSCAR_NAMED_COMPOUND_FACADES_SAVE packages=%d report=%s" % (len(ordered_packages), report))
print("SUNSCAR_NAMED_COMPOUND_FACADES_SAVE", len(ordered_packages), report)
