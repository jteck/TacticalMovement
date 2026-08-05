"""Read-only terrain, actor, spawn, and clearance audit for the Abiverd precinct."""

import json
import os
from collections import Counter

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
REPORT_NAME = "abiverd_heritage_site_preflight_v1.json"

HERITAGE_BOUNDS_CM = {
    "min_x": -6000.0,
    "max_x": 6500.0,
    "min_y": 12000.0,
    "max_y": 24000.0,
}

SITES_M = {
    "SS_021_Juma_Mosque": {"center": [10.0, 165.0], "size": [18.0, 16.0]},
    "SS_022_Ruins_Field": {"center": [5.0, 178.0], "size": [105.0, 100.0]},
    "SS_023_Well_Court": {"center": [-20.0, 154.0], "size": [12.0, 10.0]},
    "SS_024_Fortification_Ditch": {"center": [-5.0, 218.0], "size": [90.0, 12.0]},
}


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def vector_dict(value):
    return {"x": value.x, "y": value.y, "z": value.z}


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_SITE_PREFLIGHT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_SITE_PREFLIGHT_WRONG_LEVEL " + level_path)

dirty = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
if dirty:
    raise RuntimeError("ABIVERD_SITE_PREFLIGHT_DIRTY_SCOPE " + repr(dirty))

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = list(actor_subsystem.get_all_level_actors())
landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
non_landscapes = [actor for actor in actors if actor not in landscapes]

nearby = []
spawns = []
for actor in actors:
    location = actor.get_actor_location()
    label = actor.get_actor_label()
    class_name = actor.get_class().get_name()
    origin, extent = actor.get_actor_bounds(False)
    row = {
        "label": label,
        "class": class_name,
        "path": actor.get_path_name(),
        "location_cm": vector_dict(location),
        "bounds_origin_cm": vector_dict(origin),
        "bounds_extent_cm": vector_dict(extent),
        "folder": str(actor.get_folder_path()) if hasattr(actor, "get_folder_path") else "",
        "tags": [str(value) for value in actor.tags],
    }
    components = actor.get_components_by_class(unreal.StaticMeshComponent)
    row["static_meshes"] = []
    for component in components:
        mesh = component.get_editor_property("static_mesh")
        if mesh:
            row["static_meshes"].append(mesh.get_path_name())
    if (
        HERITAGE_BOUNDS_CM["min_x"] <= origin.x <= HERITAGE_BOUNDS_CM["max_x"]
        and HERITAGE_BOUNDS_CM["min_y"] <= origin.y <= HERITAGE_BOUNDS_CM["max_y"]
    ):
        nearby.append(row)
    lowered = (label + " " + class_name + " " + " ".join(row["tags"])).lower()
    if any(token in lowered for token in ("spawn", "insertion", "playerstart")):
        spawns.append(row)

sample_points = []
for site_id, site in SITES_M.items():
    center_x_cm = site["center"][0] * 100.0
    center_y_cm = site["center"][1] * 100.0
    half_x_cm = site["size"][0] * 50.0
    half_y_cm = site["size"][1] * 50.0
    offsets = ((0.0, 0.0), (-0.8, -0.8), (0.8, -0.8), (-0.8, 0.8), (0.8, 0.8))
    for sample_index, (fx, fy) in enumerate(offsets):
        sample_points.append(
            {
                "site": site_id,
                "sample_index": sample_index,
                "x_cm": center_x_cm + half_x_cm * fx,
                "y_cm": center_y_cm + half_y_cm * fy,
            }
        )

terrain_samples = []
for sample in sample_points:
    result_row = dict(sample)
    result_row["channels"] = []
    selected_hit = None
    for index in (1, 2):
        trace_type = getattr(unreal.TraceTypeQuery, "TRACE_TYPE_QUERY%d" % index)
        hit = unreal.SystemLibrary.line_trace_single(
            world,
            unreal.Vector(sample["x_cm"], sample["y_cm"], 100000.0),
            unreal.Vector(sample["x_cm"], sample["y_cm"], -100000.0),
            trace_type,
            True,
            non_landscapes,
            unreal.DrawDebugTrace.NONE,
            True,
        )
        channel = {"trace_type_query": index, "hit": hit is not None}
        if hit is not None:
            data = hit.to_dict()
            hit_actor = data.get("hit_actor")
            location = data.get("location")
            channel.update(
                {
                    "blocking_hit": bool(data.get("blocking_hit")),
                    "actor": hit_actor.get_path_name() if hit_actor else None,
                    "location_cm": vector_dict(location) if location else None,
                }
            )
            if selected_hit is None and location is not None:
                selected_hit = channel
        result_row["channels"].append(channel)
    result_row["selected_landscape_hit"] = selected_hit
    terrain_samples.append(result_row)

landscape_rows = []
for landscape in landscapes:
    origin, extent = landscape.get_actor_bounds(False)
    material = landscape.get_editor_property("landscape_material")
    landscape_rows.append(
        {
            "label": landscape.get_actor_label(),
            "class": landscape.get_class().get_name(),
            "path": landscape.get_path_name(),
            "location_cm": vector_dict(landscape.get_actor_location()),
            "bounds_origin_cm": vector_dict(origin),
            "bounds_extent_cm": vector_dict(extent),
            "landscape_material": material.get_path_name() if material else None,
        }
    )

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
payload = {
    "schema_version": 1,
    "status": "read_only_site_preflight_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "changes_made": False,
    "actor_count": len(actors),
    "class_counts": dict(Counter(actor.get_class().get_name() for actor in actors).most_common()),
    "heritage_bounds_cm": HERITAGE_BOUNDS_CM,
    "nearby_actor_count": len(nearby),
    "nearby_actors": sorted(nearby, key=lambda value: value["label"]),
    "spawn_candidate_count": len(spawns),
    "spawn_candidates": sorted(spawns, key=lambda value: value["label"]),
    "landscapes": landscape_rows,
    "terrain_samples": terrain_samples,
    "dirty_packages": dirty,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_SITE_PREFLIGHT_COMPLETE actors=%d nearby=%d report=%s" % (len(actors), len(nearby), report_path))
print("ABIVERD_SITE_PREFLIGHT_COMPLETE", len(actors), len(nearby), report_path)
