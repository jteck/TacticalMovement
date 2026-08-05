"""Remove only the exact unsaved partial Abiverd architecture preview."""

import json
import os

import unreal


PASS_TAG = unreal.Name("SunscarAbiverdHeritageCompositionV1")
EXPECTED_LABEL = "ABV_SS021_SouthWall_Left"
MATERIALS = [
    "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
    "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
]
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
matches = [
    actor for actor in actor_subsystem.get_all_level_actors()
    if PASS_TAG in list(actor.tags)
]
if len(matches) != 1 or matches[0].get_actor_label() != EXPECTED_LABEL:
    raise RuntimeError(
        "ABIVERD_ARCH_CLEANUP_REFUSED labels="
        + "|".join(actor.get_actor_label() for actor in matches)
    )

dirty_before = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
allowed_prefixes = (
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
)
unexpected = [
    name for name in dirty_before
    if name not in MATERIALS and not name.startswith(allowed_prefixes)
]
if unexpected:
    raise RuntimeError("ABIVERD_ARCH_CLEANUP_UNEXPECTED_DIRTY " + "|".join(unexpected))

if not actor_subsystem.destroy_actor(matches[0]):
    raise RuntimeError("ABIVERD_ARCH_CLEANUP_ACTOR_DELETE_FAILED")
deleted_materials = []
for path in MATERIALS:
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        if not unreal.EditorAssetLibrary.delete_asset(path):
            raise RuntimeError("ABIVERD_ARCH_CLEANUP_ASSET_DELETE_FAILED " + path)
        deleted_materials.append(path)
unreal.SystemLibrary.collect_garbage()

dirty_after = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "status": "partial_preview_removed",
    "removed_actor": EXPECTED_LABEL,
    "deleted_unsaved_materials": deleted_materials,
    "dirty_before": dirty_before,
    "dirty_after": dirty_after,
    "changes_saved": False,
}
path = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", "abiverd_cleanup_unsaved_architecture_partial_v1.json"
)
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_ARCH_CLEANUP dirty_after=%d" % len(dirty_after))
print("ABIVERD_ARCH_CLEANUP", len(dirty_after), path)
