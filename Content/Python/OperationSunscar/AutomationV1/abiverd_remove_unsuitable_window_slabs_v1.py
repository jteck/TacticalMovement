"""Dry-run-first removal of unsuitable Pakistan full-wall window slabs.

The purchased scan is a complete storey wall module, not a window insert. This
pass clears its 14 incorrect HISM placements and restores the original map-owned
frame/glass visuals. Gameplay shells are not modified.
"""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_OldTown_PakistanWindowFacade_HISM_V1"
PASS_TAG = unreal.Name("SunscarAbiverdPakistanWindowFacadeV1")
COMPONENT_NAME = "HISM_PakistanWindowModular04"
SELECTED_PAIR_KEYS = {
    "tea_window_01",
    "tea_window_02",
    "tea_window_03",
    "clinic_f1_win_01",
    "clinic_f1_win_02",
    "clinic_f1_win_03",
    "clinic_f1_win_04",
    "detention_f1_win_01",
    "detention_f1_win_03",
    "detention_f1_win_05",
    "consulate_f1_win_01",
    "consulate_f1_win_02",
    "consulate_f1_win_03",
    "consulate_f1_win_04",
}
REPORT_NAME = (
    "abiverd_remove_unsuitable_window_slabs_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_remove_unsuitable_window_slabs_dry_run_v1.json"
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


def role_and_key(label):
    lowered = label.lower()
    for suffix, role in (("_frame", "frame"), ("_glass", "glass")):
        if lowered.endswith(suffix):
            return role, lowered[:-len(suffix)]
    return "", ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_WRONG_PROJECT")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_LOAD_DIRTY")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
matches = [actor for actor in actors if actor.get_actor_label() == ACTOR_LABEL or PASS_TAG in list(actor.tags)]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_ACTOR_COUNT %d" % len(matches))
facade_actor = matches[0]
components = list(facade_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
target_components = [component for component in components if component.get_name() == COMPONENT_NAME]
if len(target_components) != 1:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_COMPONENT_COUNT %d" % len(target_components))
component = target_components[0]
if component.get_instance_count() != 14:
    raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_INSTANCE_COUNT %d" % component.get_instance_count())

pair_actors = {}
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    role, key = role_and_key(actor.get_actor_label())
    if key in SELECTED_PAIR_KEYS:
        pair_actors.setdefault(key, {})[role] = actor
if set(pair_actors) != SELECTED_PAIR_KEYS:
    raise RuntimeError(
        "ABIVERD_REMOVE_WINDOW_SLABS_MISSING_PAIRS "
        + repr(sorted(SELECTED_PAIR_KEYS - set(pair_actors)))
    )
for key, roles in pair_actors.items():
    if set(roles) != {"frame", "glass"}:
        raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_PAIR_ROLES %s %s" % (key, sorted(roles)))

source_rows = []
for key in sorted(pair_actors):
    for role in ("frame", "glass"):
        actor = pair_actors[key][role]
        source = actor.static_mesh_component
        source_rows.append(
            {
                "key": key,
                "role": role,
                "label": actor.get_actor_label(),
                "visible_before": source.is_visible(),
                "hidden_in_game_before": bool(source.get_editor_property("hidden_in_game")),
                "collision_before": str(source.get_collision_enabled()),
                "action": "restore_visual_keep_no_collision" if APPLY_CHANGES else "planned",
            }
        )

saved_packages = []
if APPLY_CHANGES:
    facade_actor.modify()
    component.modify()
    component.clear_instances()
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    for roles in pair_actors.values():
        for actor in roles.values():
            actor.modify()
            source = actor.static_mesh_component
            source.modify()
            source.set_visibility(True, True)
            source.set_hidden_in_game(False)
            source.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    if component.get_instance_count() != 0:
        raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_CLEAR_FAILED")
    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_REMOVE_WINDOW_SLABS_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "incorrect_instance_count_before": 14,
    "incorrect_instance_count_after": 0 if APPLY_CHANGES else 14,
    "restored_source_visual_count": 28 if APPLY_CHANGES else 0,
    "source_visuals": source_rows,
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "gameplay_shells": "unchanged",
        "source_scan": "retained in project library but removed from unsuitable insert usage",
        "restored_visuals": "map-owned frame/glass visuals visible and non-colliding",
        "future_usage": "Pakistan Window Modular 04 may only be used inside a complete compatible modular facade assembly",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_REMOVE_WINDOW_SLABS_COMPLETE apply=%s cleared=%d restored=%d"
    % (APPLY_CHANGES, 14 if APPLY_CHANGES else 0, 28 if APPLY_CHANGES else 0)
)
print("ABIVERD_REMOVE_WINDOW_SLABS_COMPLETE", report_path)
