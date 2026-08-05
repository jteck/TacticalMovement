"""Dry-run-first removal of superseded Old Town prototype parapets.

Structural Skin V3 created terrain/site-correct ABV roof parapets. Older
SS_###_Parapet_* actors remain duplicated and some are offset by half a roof
span, creating floating beams. This pass hides only a prototype parapet when a
complete, colliding ABV replacement exists for the same site and side.
"""

import json
import os
import re

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
SIDES = {"N": "North", "S": "South", "E": "East", "W": "West"}
PROTOTYPE_PATTERN = re.compile(r"^(SS_\d{3})_Parapet_([NSEW])$")
REPORT_NAME = (
    "abiverd_remove_duplicate_parapets_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_remove_duplicate_parapets_dry_run_v1.json"
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


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_LOAD_DIRTY")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
rows = []
targets = []
for label, actor in sorted(by_label.items()):
    match = PROTOTYPE_PATTERN.match(label)
    if not match:
        continue
    site, side_key = match.groups()
    replacement_label = "ABV_%s_RoofParapet_%s" % (site, SIDES[side_key])
    replacement = by_label.get(replacement_label)
    if replacement is None:
        continue
    if not isinstance(actor, unreal.StaticMeshActor) or not isinstance(replacement, unreal.StaticMeshActor):
        raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_CLASS " + label)
    source_origin, source_extent = actor.get_actor_bounds(False)
    replacement_origin, replacement_extent = replacement.get_actor_bounds(False)
    replacement_component = replacement.static_mesh_component
    if not replacement_component.is_visible():
        raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_REPLACEMENT_HIDDEN " + replacement_label)
    if replacement_component.get_collision_enabled() != unreal.CollisionEnabled.QUERY_AND_PHYSICS:
        raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_REPLACEMENT_COLLISION " + replacement_label)
    center_offset = unreal.Vector(
        source_origin.x - replacement_origin.x,
        source_origin.y - replacement_origin.y,
        source_origin.z - replacement_origin.z,
    )
    rows.append(
        {
            "site": site,
            "side": SIDES[side_key],
            "prototype_label": label,
            "replacement_label": replacement_label,
            "prototype_bounds_origin_cm": [round(source_origin.x, 2), round(source_origin.y, 2), round(source_origin.z, 2)],
            "prototype_bounds_size_cm": [round(source_extent.x * 2.0, 2), round(source_extent.y * 2.0, 2), round(source_extent.z * 2.0, 2)],
            "replacement_bounds_origin_cm": [round(replacement_origin.x, 2), round(replacement_origin.y, 2), round(replacement_origin.z, 2)],
            "replacement_bounds_size_cm": [round(replacement_extent.x * 2.0, 2), round(replacement_extent.y * 2.0, 2), round(replacement_extent.z * 2.0, 2)],
            "center_offset_cm": [round(center_offset.x, 2), round(center_offset.y, 2), round(center_offset.z, 2)],
            "prototype_action": "hide_and_disable_collision" if APPLY_CHANGES else "planned",
            "replacement_action": "preserve",
        }
    )
    targets.append(actor)

site_counts = {}
for row in rows:
    site_counts[row["site"]] = site_counts.get(row["site"], 0) + 1
incomplete = {site: count for site, count in site_counts.items() if count != 4}
if incomplete:
    raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_INCOMPLETE " + repr(incomplete))
if not rows:
    raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_NONE")

saved_packages = []
if APPLY_CHANGES:
    for actor in targets:
        actor.modify()
        component = actor.static_mesh_component
        component.modify()
        component.set_visibility(False, True)
        component.set_hidden_in_game(True)
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_REMOVE_DUPLICATE_PARAPETS_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "site_counts": dict(sorted(site_counts.items())),
    "prototype_count": len(rows),
    "records": rows,
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "prototype": "hidden and collision disabled only where complete ABV replacement exists",
        "replacement": "preserved with QueryAndPhysics collision",
        "gameplay_shells": "unchanged",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_REMOVE_DUPLICATE_PARAPETS_COMPLETE apply=%s sites=%d prototypes=%d"
    % (APPLY_CHANGES, len(site_counts), len(rows))
)
print("ABIVERD_REMOVE_DUPLICATE_PARAPETS_COMPLETE", report_path)
