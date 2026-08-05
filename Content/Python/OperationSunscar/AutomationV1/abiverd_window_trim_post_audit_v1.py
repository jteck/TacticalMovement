"""Read-only post-audit for the Old Town window trim HISM pass."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_OldTown_WindowTrim_HISM_V1"
PASS_TAG = unreal.Name("SunscarAbiverdWindowTrimV1")
EXPECTED_COMPONENTS = {
    "HISM_WindowTrim_Brick": {
        "material": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
        "instances": 70,
    },
    "HISM_WindowTrim_Mud": {
        "material": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
        "instances": 10,
    },
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


def asset_path(asset):
    return asset.get_outermost().get_name() if asset else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
matches = [actor for actor in actors if actor.get_actor_label() == ACTOR_LABEL or PASS_TAG in list(actor.tags)]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_ACTOR_COUNT %d" % len(matches))
actor = matches[0]
if bool(actor.get_editor_property("replicates")):
    raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_REPLICATES")
components = list(actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
components_by_name = {component.get_name(): component for component in components}
if set(components_by_name) != set(EXPECTED_COMPONENTS):
    raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_COMPONENTS " + repr(sorted(components_by_name)))

records = []
for name, expected in sorted(EXPECTED_COMPONENTS.items()):
    component = components_by_name[name]
    row = {
        "component": name,
        "instances": component.get_instance_count(),
        "material": asset_path(component.get_material(0)),
        "mesh": asset_path(component.get_editor_property("static_mesh")),
        "collision": str(component.get_collision_enabled()),
        "start_cull_cm": int(component.get_editor_property("instance_start_cull_distance")),
        "end_cull_cm": int(component.get_editor_property("instance_end_cull_distance")),
    }
    if row["instances"] != expected["instances"] or row["material"] != expected["material"]:
        raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_CONTENT " + repr(row))
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_COLLISION " + repr(row))
    if row["start_cull_cm"] != 12000 or row["end_cull_cm"] != 30000:
        raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_CULL " + repr(row))
    records.append(row)

dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_WINDOW_TRIM_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))
report = {
    "schema_version": 1,
    "status": "post_apply_audit_passed",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "actor": ACTOR_LABEL,
    "replicates": bool(actor.get_editor_property("replicates")),
    "component_count": len(records),
    "piece_count": sum(item["instances"] for item in records),
    "components": records,
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_window_trim_post_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_WINDOW_TRIM_POST_AUDIT_PASS pieces=80 components=2")
print("ABIVERD_WINDOW_TRIM_POST_AUDIT_PASS", report_path)
