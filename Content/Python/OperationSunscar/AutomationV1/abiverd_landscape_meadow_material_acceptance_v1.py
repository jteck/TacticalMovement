"""Validate the unsaved Abiverd V3 Landscape material preview and its exact scope."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
REPORT_PATH = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_meadow_material_acceptance_v1.json",
)


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_MEADOW_ACCEPTANCE_CONTEXT")

material = unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_MEADOW_ACCEPTANCE_TARGET")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
if len(landscapes) != 3:
    raise RuntimeError("ABIVERD_MEADOW_ACCEPTANCE_LANDSCAPE_SCOPE")

assignments = {
    actor.get_actor_label(): (
        actor.get_editor_property("landscape_material").get_path_name()
        if actor.get_editor_property("landscape_material") else ""
    )
    for actor in landscapes
}
bad_assignments = [label for label, path in assignments.items() if not path.startswith(TARGET_PATH + ".")]
if bad_assignments:
    raise RuntimeError("ABIVERD_MEADOW_ACCEPTANCE_ASSIGNMENT " + "|".join(bad_assignments))

expected_dirty = {TARGET_PATH} | {actor.get_package().get_name() for actor in landscapes}
dirty = dirty_packages()
if set(dirty) != expected_dirty:
    raise RuntimeError(
        "ABIVERD_MEADOW_ACCEPTANCE_DIRTY expected=%s actual=%s"
        % ("|".join(sorted(expected_dirty)), "|".join(dirty))
    )

payload = {
    "schema_version": 1,
    "status": "accepted_unsaved_preview",
    "level": level_path,
    "target_material": material.get_path_name(),
    "material_expression_count": len(unreal.MaterialEditingLibrary.get_material_expressions(material)),
    "landscape_assignments": assignments,
    "dirty_packages": dirty,
    "changes_saved": False,
}
os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)

unreal.log(
    "ABIVERD_MEADOW_ACCEPTANCE_COMPLETE expressions=%d dirty=%d report=%s"
    % (payload["material_expression_count"], len(dirty), REPORT_PATH)
)
