"""Save exactly the accepted Abiverd HISM vegetation actor and its external objects."""

import json
import os

import unreal


TAG = unreal.Name("SunscarAbiverdVegetationHISMV1")
EXPECTED_LABEL = "ABV_SS025_PoppyMeadow_HISM"
EXPECTED_COMPONENTS = 16
EXPECTED_INSTANCES = 1415
ACTOR_PREFIX = "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/"
OBJECT_PREFIX = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"
MATERIALS = {
    "/Game/Maps/Sunscar/Art/Heritage/Foliage/FieldPoppy/MI_FieldPoppy",
    "/Game/Maps/Sunscar/Art/Heritage/Foliage/WildGrass/MI_WildGrass",
}

actors = [
    actor for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    if TAG in list(actor.tags)
]
if len(actors) != 1 or actors[0].get_actor_label() != EXPECTED_LABEL:
    raise RuntimeError("ABIVERD_VEGETATION_SAVE_ACTOR_SCOPE count=%d" % len(actors))
actor = actors[0]
components = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
if len(components) != EXPECTED_COMPONENTS or sum(item.get_instance_count() for item in components) != EXPECTED_INSTANCES:
    raise RuntimeError("ABIVERD_VEGETATION_SAVE_COMPONENT_SCOPE")

actor_package = actor.get_package().get_name()
if not actor_package.startswith(ACTOR_PREFIX):
    raise RuntimeError("ABIVERD_VEGETATION_SAVE_ACTOR_PACKAGE")
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
names = {package.get_name() for package in packages}
unexpected = sorted(
    name for name in names
    if name != actor_package and name not in MATERIALS and not name.startswith(OBJECT_PREFIX)
)
if unexpected or actor_package not in names:
    raise RuntimeError("ABIVERD_VEGETATION_SAVE_DIRTY_SCOPE " + "|".join(unexpected))
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_VEGETATION_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("ABIVERD_VEGETATION_SAVE_DIRTY_AFTER " + "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_hism_vegetation_scope_saved",
    "actor_label": actor.get_actor_label(),
    "component_count": len(components),
    "total_instance_count": sum(item.get_instance_count() for item in components),
    "saved_package_count": len(packages),
    "saved_packages": sorted(names),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
path = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", "abiverd_save_heritage_vegetation_v1.json"
)
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_VEGETATION_SAVE packages=%d" % len(packages))
print("ABIVERD_VEGETATION_SAVE", len(packages), path)
