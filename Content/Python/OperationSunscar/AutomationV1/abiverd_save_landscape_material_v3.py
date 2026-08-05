"""Save exactly the accepted Abiverd V3 material and three Landscape actors."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_MEADOW_SAVE_CONTEXT")

material = unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_MEADOW_SAVE_TARGET")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
if len(landscapes) != 3:
    raise RuntimeError("ABIVERD_MEADOW_SAVE_LANDSCAPE_SCOPE")

expected = {TARGET_PATH} | {actor.get_package().get_name() for actor in landscapes}
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
actual = {package_name(package) for package in packages}
if actual != expected:
    raise RuntimeError(
        "ABIVERD_MEADOW_SAVE_DIRTY expected=%s actual=%s"
        % ("|".join(sorted(expected)), "|".join(sorted(actual)))
    )

if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_MEADOW_SAVE_FAILED")

remaining = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
if remaining:
    raise RuntimeError("ABIVERD_MEADOW_SAVE_DIRTY_AFTER " + "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_landscape_material_scope_saved",
    "level": level_path,
    "material": material.get_path_name(),
    "landscape_labels": [actor.get_actor_label() for actor in landscapes],
    "saved_packages": sorted(actual),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_save_landscape_material_v3.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_MEADOW_SAVE_COMPLETE packages=%d" % len(actual))
