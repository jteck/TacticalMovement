"""Read-only Landscape bounds and editor collision probe for Old Town."""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development/"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"

project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/")
if not project_directory.endswith("/"):
    project_directory += "/"
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("SUNSCAR_UNSAFE_PROJECT_DIRECTORY " + project_directory)

world = unreal.UnrealEditorSubsystem().get_editor_world()
level_path = world.get_path_name().split(":", 1)[0].split(".", 1)[0]
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("SUNSCAR_UNSAFE_LEVEL " + level_path)

actors = list(unreal.EditorActorSubsystem().get_all_level_actors())
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
sample_xy_cm = [
    (-13820.7, -9962.7),
    (0.0, 0.0),
    (13820.7, 9962.7),
]

payload = {
    "schema_version": 1,
    "status": "read_only_landscape_probe_complete",
    "project_directory": project_directory,
    "level": level_path,
    "landscape_count": len(landscapes),
    "landscapes": [],
    "trace_samples": [],
    "changes_made": False,
    "level_saved": False,
}

for actor in landscapes:
    origin, extent = actor.get_actor_bounds(False)
    actor_data = {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_name(),
        "path": actor.get_path_name(),
        "location_cm": actor.get_actor_location().to_dict(),
        "bounds_origin_cm": origin.to_dict(),
        "bounds_extent_cm": extent.to_dict(),
        "component_count": len(actor.get_components_by_class(unreal.PrimitiveComponent)),
        "components": [],
    }
    for component in actor.get_components_by_class(unreal.PrimitiveComponent):
        component_data = {
            "name": component.get_name(),
            "class": component.get_class().get_name(),
        }
        for property_name in ("collision_profile_name", "collision_enabled", "generate_overlap_events"):
            try:
                value = component.get_editor_property(property_name)
                component_data[property_name] = str(value)
            except Exception:
                component_data[property_name] = "unavailable"
        actor_data["components"].append(component_data)
    payload["landscapes"].append(actor_data)

ignored = [actor for actor in actors if actor not in landscapes]
for x_cm, y_cm in sample_xy_cm:
    sample = {"x_cm": x_cm, "y_cm": y_cm, "channels": []}
    for index in range(1, 3):
        trace_type = getattr(unreal.TraceTypeQuery, "TRACE_TYPE_QUERY%d" % index)
        hit = unreal.SystemLibrary.line_trace_single(
            world,
            unreal.Vector(x_cm, y_cm, 100000.0),
            unreal.Vector(x_cm, y_cm, -100000.0),
            trace_type,
            True,
            ignored,
            unreal.DrawDebugTrace.NONE,
            True,
        )
        hit_data = {"trace_type_query": index, "hit": hit is not None}
        if hit is not None:
            result = hit.to_dict()
            hit_data["blocking_hit"] = bool(result.get("blocking_hit"))
            location = result.get("location")
            hit_actor = result.get("hit_actor")
            hit_data["location_cm"] = location.to_dict() if location else None
            hit_data["actor"] = hit_actor.get_path_name() if hit_actor else None
        sample["channels"].append(hit_data)
    payload["trace_samples"].append(sample)

report_directory = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_directory, exist_ok=True)
report_path = os.path.join(report_directory, "old_town_landscape_probe.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, default=str)
    handle.write("\n")

unreal.log("SUNSCAR_LANDSCAPE_PROBE landscapes=%d report=%s" % (len(landscapes), report_path))
print("SUNSCAR_LANDSCAPE_PROBE", len(landscapes), report_path)
