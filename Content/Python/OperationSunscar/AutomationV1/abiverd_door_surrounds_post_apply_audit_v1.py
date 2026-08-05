"""Read-only validation of Abiverd door surrounds after placement."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_OldTown_DoorSurrounds_HISM_V1"
PASS_TAG = unreal.Name("SunscarAbiverdDoorSurroundsV1")
EXPECTED_DOORS = {
    "Tea_MainDoor",
    "Clinic_MainDoor",
    "Clinic_ServiceDoor",
    "Detention_Door_12",
    "Detention_Door_22",
    "Detention_Door_32",
    "Consulate_Door_A",
    "Consulate_Door_B",
}
EXPECTED_DOOR_MESH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_001_wbmgdcpdw/"
    "Old_Wooden_Door_wbmgdcpdw_High.Old_Wooden_Door_wbmgdcpdw_High"
)
EXPECTED_COMPONENTS = {
    "HISM_DoorSurround_Brick": 15,
    "HISM_DoorSurround_Mud": 9,
}


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_WRONG_PROJECT")

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_WRONG_LEVEL " + level_path)

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
matches = [
    actor
    for actor in actors
    if actor.get_actor_label() == ACTOR_LABEL or PASS_TAG in list(actor.tags)
]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_ACTORS %d" % len(matches))
surround_actor = matches[0]
components = list(
    surround_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
)
component_rows = []
for component in sorted(components, key=lambda item: item.get_name()):
    material = component.get_material(0)
    component_rows.append(
        {
            "name": component.get_name(),
            "instance_count": component.get_instance_count(),
            "collision": str(component.get_collision_enabled()),
            "material": material.get_path_name() if material else "",
            "start_cull_distance": component.get_editor_property("instance_start_cull_distance"),
            "end_cull_distance": component.get_editor_property("instance_end_cull_distance"),
        }
    )

component_counts = {row["name"]: row["instance_count"] for row in component_rows}
if component_counts != EXPECTED_COMPONENTS:
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_COMPONENT_COUNTS " + repr(component_counts))
for row in component_rows:
    if "NO_COLLISION" not in row["collision"]:
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_COLLISION " + row["name"])
    if row["start_cull_distance"] != 12000 or row["end_cull_distance"] != 30000:
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_CULL " + row["name"])
if surround_actor.get_editor_property("replicates"):
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_REPLICATION")

door_rows = []
for label in sorted(EXPECTED_DOORS):
    matches = [
        actor
        for actor in actors
        if isinstance(actor, unreal.StaticMeshActor) and actor.get_actor_label() == label
    ]
    if len(matches) != 1:
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_DOOR %s %d" % (label, len(matches)))
    door = matches[0]
    mesh = door.static_mesh_component.get_editor_property("static_mesh")
    mesh_path = mesh.get_path_name() if mesh else ""
    collision = str(door.static_mesh_component.get_collision_enabled())
    if mesh_path != EXPECTED_DOOR_MESH or "QUERY_AND_PHYSICS" not in collision:
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_AUDIT_DOOR_STATE " + label)
    door_rows.append({"label": label, "mesh": mesh_path, "collision": collision})

dirty = sorted(
    {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "actor": surround_actor.get_path_name(),
    "actor_package": surround_actor.get_package().get_name(),
    "replicates": bool(surround_actor.get_editor_property("replicates")),
    "components": component_rows,
    "doors": door_rows,
    "dirty_packages": dirty,
    "changes_made": False,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_door_surrounds_post_apply_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_DOOR_SURROUNDS_AUDIT_COMPLETE components=%d doors=%d dirty=%d"
    % (len(component_rows), len(door_rows), len(dirty))
)
print("ABIVERD_DOOR_SURROUNDS_AUDIT_COMPLETE", report_path)
