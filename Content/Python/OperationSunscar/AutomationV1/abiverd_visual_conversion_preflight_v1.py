"""Read-only inventory for the Abiverd/Old Town visual-conversion pass."""

import collections
import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def actor_tags(actor):
    return [str(tag) for tag in list(actor.tags)]


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_VISUAL_PREFLIGHT_WRONG_PROJECT")
if level_path.startswith("/Temp/Untitled_"):
    if not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_VISUAL_PREFLIGHT_COMMANDLET_LOAD_FAILED")
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_VISUAL_PREFLIGHT_WRONG_LEVEL " + level_path)

# Command-line editor sessions start with only always-loaded actors.  Load and
# pin the full Old Town plus northern Abiverd heritage working area so the
# inventory is equivalent to the interactive editor review scope.
working_box = unreal.Box(
    min=unreal.Vector(-20000.0, -16000.0, -100000.0),
    max=unreal.Vector(20000.0, 25000.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([descriptor.guid for descriptor in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([descriptor.guid for descriptor in descriptors])

dirty_content = sorted(
    package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
rows = []
tag_counts = collections.Counter()
folder_counts = collections.Counter()
mesh_counts = collections.Counter()
material_counts = collections.Counter()
for actor in actors:
    tags = actor_tags(actor)
    for tag in tags:
        tag_counts[tag] += 1
    folder = str(actor.get_folder_path())
    folder_counts[folder] += 1
    mesh_path = ""
    materials = []
    component = getattr(actor, "static_mesh_component", None)
    if component is not None:
        mesh = component.get_editor_property("static_mesh")
        if mesh is not None:
            mesh_path = mesh.get_path_name()
            mesh_counts[mesh_path] += 1
        for index in range(component.get_num_materials()):
            material = component.get_material(index)
            path = material.get_path_name() if material else ""
            materials.append(path)
            if path:
                material_counts[path] += 1
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    origin, extent = actor.get_actor_bounds(False, False)
    row = {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_name(),
        "folder": folder,
        "tags": tags,
        "location_cm": [round(location.x, 2), round(location.y, 2), round(location.z, 2)],
        "rotation_deg": [round(rotation.roll, 3), round(rotation.pitch, 3), round(rotation.yaw, 3)],
        "scale": [round(scale.x, 4), round(scale.y, 4), round(scale.z, 4)],
        "bounds_origin_cm": [round(origin.x, 2), round(origin.y, 2), round(origin.z, 2)],
        "bounds_extent_cm": [round(extent.x, 2), round(extent.y, 2), round(extent.z, 2)],
        "mesh": mesh_path,
        "materials": materials,
        "package": package_name(actor.get_package()),
    }
    if (
        "Abiverd" in row["label"]
        or row["label"].startswith("ABV_")
        or folder.startswith("OperationSunscar/Abiverd")
        or folder.startswith("Sunscar/CorePlayable")
        or folder.startswith("OldTown_")
        or "CoreCategory_Building" in tags
        or "VisualGroundOverlay" in tags
    ):
        rows.append(row)

payload = {
    "schema_version": 1,
    "status": "read_only_preflight_complete",
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "actor_count_loaded": len(actors),
    "working_region_descriptor_count": len(descriptors),
    "scoped_actor_count": len(rows),
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "tag_counts": dict(sorted(tag_counts.items())),
    "folder_counts": dict(sorted(folder_counts.items())),
    "mesh_counts": dict(sorted(mesh_counts.items())),
    "material_counts": dict(sorted(material_counts.items())),
    "scoped_actors": sorted(rows, key=lambda row: row["label"]),
    "changes_made": False,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_visual_conversion_preflight_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_VISUAL_PREFLIGHT loaded=%d scoped=%d dirty_content=%d dirty_maps=%d report=%s"
    % (len(actors), len(rows), len(dirty_content), len(dirty_maps), report_path)
)
print("ABIVERD_VISUAL_PREFLIGHT", len(actors), len(rows), report_path)
