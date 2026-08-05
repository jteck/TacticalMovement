"""Read-only post-audit for removal of superseded prototype parapets."""

import json
import os
import re

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_SITES = {"SS_004", "SS_005", "SS_007", "SS_010", "SS_011", "SS_012", "SS_018"}
SIDES = {"N": "North", "S": "South", "E": "East", "W": "West"}
PROTOTYPE_PATTERN = re.compile(r"^(SS_\d{3})_Parapet_([NSEW])$")


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
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_PARAPET_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_PARAPET_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_PARAPET_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
rows = []
site_counts = {}
for label, actor in sorted(by_label.items()):
    match = PROTOTYPE_PATTERN.match(label)
    if not match:
        continue
    site, side_key = match.groups()
    if site not in EXPECTED_SITES:
        continue
    replacement_label = "ABV_%s_RoofParapet_%s" % (site, SIDES[side_key])
    replacement = by_label.get(replacement_label)
    if not isinstance(actor, unreal.StaticMeshActor) or not isinstance(replacement, unreal.StaticMeshActor):
        raise RuntimeError("ABIVERD_PARAPET_AUDIT_PAIR " + label)
    source_component = actor.static_mesh_component
    replacement_component = replacement.static_mesh_component
    row = {
        "site": site,
        "side": SIDES[side_key],
        "prototype_label": label,
        "prototype_visible": source_component.is_visible(),
        "prototype_hidden_in_game": bool(source_component.get_editor_property("hidden_in_game")),
        "prototype_collision": str(source_component.get_collision_enabled()),
        "replacement_label": replacement_label,
        "replacement_visible": replacement_component.is_visible(),
        "replacement_hidden_in_game": bool(replacement_component.get_editor_property("hidden_in_game")),
        "replacement_collision": str(replacement_component.get_collision_enabled()),
    }
    if row["prototype_visible"] or not row["prototype_hidden_in_game"]:
        raise RuntimeError("ABIVERD_PARAPET_AUDIT_PROTOTYPE_VISIBILITY " + repr(row))
    if source_component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_PARAPET_AUDIT_PROTOTYPE_COLLISION " + repr(row))
    if not row["replacement_visible"] or row["replacement_hidden_in_game"]:
        raise RuntimeError("ABIVERD_PARAPET_AUDIT_REPLACEMENT_VISIBILITY " + repr(row))
    if replacement_component.get_collision_enabled() != unreal.CollisionEnabled.QUERY_AND_PHYSICS:
        raise RuntimeError("ABIVERD_PARAPET_AUDIT_REPLACEMENT_COLLISION " + repr(row))
    rows.append(row)
    site_counts[site] = site_counts.get(site, 0) + 1

if len(rows) != 28:
    raise RuntimeError("ABIVERD_PARAPET_AUDIT_COUNT %d" % len(rows))
if set(site_counts) != EXPECTED_SITES or any(count != 4 for count in site_counts.values()):
    raise RuntimeError("ABIVERD_PARAPET_AUDIT_SITES " + repr(site_counts))
dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_PARAPET_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))

report = {
    "schema_version": 1,
    "status": "post_apply_audit_passed",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "prototype_count": len(rows),
    "replacement_count": len(rows),
    "site_counts": dict(sorted(site_counts.items())),
    "records": rows,
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_remove_duplicate_parapets_post_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_REMOVE_DUPLICATE_PARAPETS_POST_AUDIT_PASS prototypes=28 replacements=28")
print("ABIVERD_REMOVE_DUPLICATE_PARAPETS_POST_AUDIT_PASS", report_path)
