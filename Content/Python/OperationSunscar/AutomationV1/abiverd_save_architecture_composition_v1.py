"""Save exactly the accepted Abiverd architecture preview packages."""

import json
import os

import unreal


TAG = unreal.Name("SunscarAbiverdHeritageCompositionV1")
EXPECTED_COUNT = 65
MATERIALS = {
    "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
    "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
}
ACTOR_PREFIX = "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/"
OBJECT_PREFIX = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"

actors = [
    actor for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    if TAG in list(actor.tags)
]
if len(actors) != EXPECTED_COUNT or len({actor.get_actor_label() for actor in actors}) != EXPECTED_COUNT:
    raise RuntimeError("ABIVERD_ARCH_SAVE_ACTOR_SCOPE count=%d" % len(actors))
actor_packages = {actor.get_package().get_name() for actor in actors}
if any(not name.startswith(ACTOR_PREFIX) for name in actor_packages):
    raise RuntimeError("ABIVERD_ARCH_SAVE_ACTOR_PACKAGE_SCOPE")

packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
names = {package.get_name() for package in packages}
unexpected = sorted(
    name for name in names
    if name not in MATERIALS and name not in actor_packages and not name.startswith(OBJECT_PREFIX)
)
if unexpected:
    raise RuntimeError("ABIVERD_ARCH_SAVE_UNEXPECTED_DIRTY " + "|".join(unexpected))
if not MATERIALS.issubset(names) or actor_packages != {name for name in names if name.startswith(ACTOR_PREFIX)}:
    raise RuntimeError("ABIVERD_ARCH_SAVE_INCOMPLETE_SCOPE")
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_ARCH_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("ABIVERD_ARCH_SAVE_DIRTY_AFTER " + "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_architecture_composition_scope_saved",
    "actor_count": len(actors),
    "saved_package_count": len(packages),
    "saved_packages": sorted(names),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
path = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", "abiverd_save_architecture_composition_v1.json"
)
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_ARCH_SAVE packages=%d" % len(packages))
print("ABIVERD_ARCH_SAVE", len(packages), path)
