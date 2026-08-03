"""Discard only unsaved Landscape V2 preview actor edits and restore overlays."""

import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development/"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"

project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/")
if not project_directory.endswith("/"):
    project_directory += "/"
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("SUNSCAR_ROLLBACK_UNSAFE_PROJECT " + project_directory)

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
level_path = world.get_path_name().split(":", 1)[0].split(".", 1)[0]
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("SUNSCAR_ROLLBACK_UNSAFE_LEVEL " + level_path)

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
overlays = [
    actor
    for actor in actors
    if "VisualGroundOverlay" in [str(tag) for tag in actor.tags]
]
if len(landscapes) != 5 or len(overlays) != 288:
    raise RuntimeError(
        "SUNSCAR_ROLLBACK_SCOPE_REFUSED landscapes=%d overlays=%d"
        % (len(landscapes), len(overlays))
    )

for actor in overlays:
    actor.set_is_temporarily_hidden_in_editor(False)

landscape_packages = [actor.get_package() for actor in landscapes]
reloaded, error = unreal.EditorLoadingAndSavingUtils.reload_packages(
    landscape_packages,
    unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE,
)
if not reloaded:
    raise RuntimeError("SUNSCAR_ROLLBACK_RELOAD_FAILED " + str(error))

unreal.log(
    "SUNSCAR_LANDSCAPE_V2_ROLLBACK landscapes=%d overlays=%d"
    % (len(landscapes), len(overlays))
)
print("SUNSCAR_LANDSCAPE_V2_ROLLBACK", len(landscapes), len(overlays))
