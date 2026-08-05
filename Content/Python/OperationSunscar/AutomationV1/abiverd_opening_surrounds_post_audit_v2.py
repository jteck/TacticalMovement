"""Read-only post-apply audit for Abiverd opening surrounds V2."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_OldTown_DoorSurrounds_HISM_V1"
PASS_TAG = unreal.Name("SunscarAbiverdDoorSurroundsV1")
EXPECTED_COMPONENTS = {
    "HISM_DoorSurround_Brick": {
        "instances": 24,
        "material": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
    },
    "HISM_DoorSurround_Mud": {
        "instances": 18,
        "material": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
    },
}
REAL_DOORS = {
    "Tea_MainDoor",
    "Clinic_MainDoor",
    "Clinic_ServiceDoor",
    "Hotel_Door_-20",
    "Detention_Door_12",
    "Detention_Door_22",
    "Detention_Door_32",
    "Consulate_Door_A",
    "Consulate_Door_B",
}
FALSE_DOORS = {"Hotel_Door_-14", "Hotel_Door_-8"}
PASSAGE_LINTELS = {
    "Core_SS_007_F1_E_Lintel",
    "Core_SS_007_F2_W_Lintel",
    "Core_SS_017_F1_E_Lintel",
    "Core_SS_017_F1_N_Lintel",
    "Core_SS_017_F1_W_Lintel",
}


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
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_WRONG_PROJECT")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_WRONG_LEVEL " + level_path)
dirty_before = dirty_packages()
if dirty_before:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_DIRTY_BEFORE " + "|".join(dirty_before))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_LOAD_DIRTY")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
required = REAL_DOORS | FALSE_DOORS | PASSAGE_LINTELS
missing = sorted(required - set(by_label))
if missing:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_MISSING " + repr(missing))

matches = [actor for actor in actors if PASS_TAG in list(actor.tags) or actor.get_actor_label() == ACTOR_LABEL]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_ACTOR_COUNT %d" % len(matches))
surround_actor = matches[0]
surround_replicated = bool(surround_actor.get_editor_property("replicates"))
if surround_replicated:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_REPLICATED")
components = list(surround_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
components_by_name = {component.get_name(): component for component in components}
if set(components_by_name) != set(EXPECTED_COMPONENTS):
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_COMPONENTS " + repr(sorted(components_by_name)))

component_rows = []
for name, expected in sorted(EXPECTED_COMPONENTS.items()):
    component = components_by_name[name]
    material = component.get_material(0)
    material_path = material.get_outermost().get_name() if material else ""
    row = {
        "name": name,
        "instances": component.get_instance_count(),
        "material": material_path,
        "collision": str(component.get_collision_enabled()),
        "start_cull_cm": component.get_editor_property("instance_start_cull_distance"),
        "end_cull_cm": component.get_editor_property("instance_end_cull_distance"),
    }
    if row["instances"] != expected["instances"]:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_INSTANCES " + repr(row))
    if row["material"] != expected["material"]:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_MATERIAL " + repr(row))
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_COLLISION " + repr(row))
    if row["start_cull_cm"] != 12000 or row["end_cull_cm"] != 30000:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_CULL " + repr(row))
    component_rows.append(row)

real_door_rows = []
for label in sorted(REAL_DOORS):
    actor = by_label[label]
    component = actor.static_mesh_component
    row = {
        "label": label,
        "actor_hidden": actor.is_hidden_ed(),
        "component_visible": component.is_visible(),
        "hidden_in_game": component.get_editor_property("hidden_in_game"),
        "collision": str(component.get_collision_enabled()),
    }
    if row["actor_hidden"] or not row["component_visible"] or row["hidden_in_game"]:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_REAL_DOOR_VISIBILITY " + repr(row))
    if component.get_collision_enabled() != unreal.CollisionEnabled.QUERY_AND_PHYSICS:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_REAL_DOOR_COLLISION " + repr(row))
    real_door_rows.append(row)

false_door_rows = []
for label in sorted(FALSE_DOORS):
    actor = by_label[label]
    component = actor.static_mesh_component
    row = {
        "label": label,
        "component_visible": component.is_visible(),
        "hidden_in_game": component.get_editor_property("hidden_in_game"),
        "collision": str(component.get_collision_enabled()),
    }
    if row["component_visible"] or not row["hidden_in_game"]:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_FALSE_DOOR_VISIBILITY " + repr(row))
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_FALSE_DOOR_COLLISION " + repr(row))
    false_door_rows.append(row)

passage_rows = []
for label in sorted(PASSAGE_LINTELS):
    actor = by_label[label]
    component = actor.static_mesh_component
    row = {
        "label": label,
        "component_visible": component.is_visible(),
        "collision": str(component.get_collision_enabled()),
    }
    if not row["component_visible"]:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_PASSAGE_VISIBILITY " + repr(row))
    passage_rows.append(row)

dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_DIRTY_AFTER " + "|".join(dirty_after))

report = {
    "schema_version": 2,
    "status": "post_apply_audit_passed",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "surround_actor": {
        "label": surround_actor.get_actor_label(),
        "replicated": surround_replicated,
        "components": component_rows,
        "total_instances": sum(row["instances"] for row in component_rows),
    },
    "real_doors": real_door_rows,
    "false_doors": false_door_rows,
    "open_passages": passage_rows,
    "dirty_before": dirty_before,
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_opening_surrounds_post_apply_audit_v2.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_PASS total=42 real_doors=9 false_doors=2 passages=5")
print("ABIVERD_OPENING_SURROUNDS_POST_AUDIT_V2_PASS", report_path)
