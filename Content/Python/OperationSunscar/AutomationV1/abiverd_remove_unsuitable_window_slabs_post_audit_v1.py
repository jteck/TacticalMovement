"""Read-only post-audit for removal of unsuitable window scan slabs."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_OldTown_PakistanWindowFacade_HISM_V1"
COMPONENT_NAME = "HISM_PakistanWindowModular04"
SELECTED_PAIR_KEYS = {
    "tea_window_01", "tea_window_02", "tea_window_03",
    "clinic_f1_win_01", "clinic_f1_win_02", "clinic_f1_win_03", "clinic_f1_win_04",
    "detention_f1_win_01", "detention_f1_win_03", "detention_f1_win_05",
    "consulate_f1_win_01", "consulate_f1_win_02", "consulate_f1_win_03", "consulate_f1_win_04",
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


def role_and_key(label):
    lowered = label.lower()
    for suffix, role in (("_frame", "frame"), ("_glass", "glass")):
        if lowered.endswith(suffix):
            return role, lowered[:-len(suffix)]
    return "", ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
matches = [actor for actor in actors if actor.get_actor_label() == ACTOR_LABEL]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_ACTORS %d" % len(matches))
components = list(matches[0].get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
target = [component for component in components if component.get_name() == COMPONENT_NAME]
if len(target) != 1 or target[0].get_instance_count() != 0:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_COMPONENT")

rows = []
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    role, key = role_and_key(actor.get_actor_label())
    if key not in SELECTED_PAIR_KEYS:
        continue
    component = actor.static_mesh_component
    row = {
        "key": key,
        "role": role,
        "label": actor.get_actor_label(),
        "visible": component.is_visible(),
        "hidden_in_game": bool(component.get_editor_property("hidden_in_game")),
        "collision": str(component.get_collision_enabled()),
    }
    if not row["visible"] or row["hidden_in_game"]:
        raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_VISIBILITY " + repr(row))
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_COLLISION " + repr(row))
    rows.append(row)
rows.sort(key=lambda item: (item["key"], item["role"]))
if len(rows) != 28:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_SOURCE_COUNT %d" % len(rows))

dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))
report = {
    "schema_version": 1,
    "status": "post_apply_audit_passed",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "incorrect_hism_instances": target[0].get_instance_count(),
    "restored_source_visuals": rows,
    "restored_source_visual_count": len(rows),
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_remove_unsuitable_window_slabs_post_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_REMOVE_WINDOW_SLABS_POST_AUDIT_PASS instances=0 restored=28")
print("ABIVERD_REMOVE_WINDOW_SLABS_POST_AUDIT_PASS", report_path)
