"""Read-only validation and close review camera for Pakistan window facade V1."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_OldTown_PakistanWindowFacade_HISM_V1"
PASS_TAG = unreal.Name("SunscarAbiverdPakistanWindowFacadeV1")
EXPECTED_INSTANCE_COUNT = 14
REPORT_NAME = "abiverd_pakistan_window_post_apply_audit_v1.json"


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


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_PAK_WINDOW_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_PAK_WINDOW_AUDIT_WRONG_LEVEL " + level_path)

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
matches = [
    actor for actor in actors
    if actor.get_actor_label() == ACTOR_LABEL or PASS_TAG in list(actor.tags)
]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_PAK_WINDOW_AUDIT_ACTORS %d" % len(matches))
facade_actor = matches[0]
components = list(
    facade_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
)
if len(components) != 1:
    raise RuntimeError("ABIVERD_PAK_WINDOW_AUDIT_COMPONENTS %d" % len(components))
component = components[0]
mesh = component.get_editor_property("static_mesh")
instance_count = component.get_instance_count()
if instance_count != EXPECTED_INSTANCE_COUNT:
    raise RuntimeError("ABIVERD_PAK_WINDOW_AUDIT_INSTANCES %d" % instance_count)

selected_prefixes = ("Tea_Window_", "Clinic_F1_Win_", "Detention_F1_Win_", "Consulate_F1_Win_")
source_rows = []
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    label = actor.get_actor_label()
    if not label.startswith(selected_prefixes):
        continue
    if not (label.endswith("_Frame") or label.endswith("_Glass")):
        continue
    # Detention keeps two prototype pairs visible; audit only the replaced 01/03/05 bays.
    if label.startswith("Detention_F1_Win_") and not any(
        token in label for token in ("_01_", "_03_", "_05_")
    ):
        continue
    source_component = actor.static_mesh_component
    source_rows.append(
        {
            "label": label,
            "visible": bool(source_component.get_editor_property("visible")),
            "hidden_in_game": bool(source_component.get_editor_property("hidden_in_game")),
            "collision": str(source_component.get_collision_enabled()),
            "package": actor.get_package().get_name(),
        }
    )
source_rows.sort(key=lambda item: item["label"])
if len(source_rows) != EXPECTED_INSTANCE_COUNT * 2:
    raise RuntimeError("ABIVERD_PAK_WINDOW_AUDIT_SOURCE_COUNT %d" % len(source_rows))
bad_sources = [
    item for item in source_rows
    if item["visible"] or not item["hidden_in_game"] or "NO_COLLISION" not in item["collision"]
]
if bad_sources:
    raise RuntimeError("ABIVERD_PAK_WINDOW_AUDIT_SOURCE_STATE " + repr(bad_sources))

dirty = dirty_packages()
payload = {
    "schema_version": 1,
    "status": "post_apply_audit_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "actor_label": facade_actor.get_actor_label(),
    "actor_package": facade_actor.get_package().get_name(),
    "mesh": mesh.get_path_name() if mesh else "",
    "instance_count": instance_count,
    "collision": str(component.get_collision_enabled()),
    "replicates": bool(facade_actor.get_editor_property("replicates")),
    "cull_distances_cm": [
        int(component.get_editor_property("instance_start_cull_distance")),
        int(component.get_editor_property("instance_end_cull_distance")),
    ],
    "source_actor_count": len(source_rows),
    "source_actors": source_rows,
    "dirty_packages": dirty,
    "changes_made": False,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(-8700.0, -4850.0, 35080.0),
    unreal.Rotator(roll=0.0, pitch=-2.0, yaw=90.0),
)
unreal.log(
    "ABIVERD_PAK_WINDOW_POST_APPLY_AUDIT instances=%d sources=%d dirty=%d"
    % (instance_count, len(source_rows), len(dirty))
)
print("ABIVERD_PAK_WINDOW_POST_APPLY_AUDIT", report_path)
