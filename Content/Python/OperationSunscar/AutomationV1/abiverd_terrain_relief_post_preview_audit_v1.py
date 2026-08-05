"""Read-only audit of the unsaved Abiverd terrain-relief preview."""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
IMPORT_REPORT_NAME = "abiverd_terrain_relief_rg16_import_apply_preview_v1.json"
OUTPUT_REPORT_NAME = "abiverd_terrain_relief_post_preview_audit_v1.json"
OLD_TOWN_BOX = unreal.Box(
    min=unreal.Vector(-40000.0, -35000.0, -100000.0),
    max=unreal.Vector(40000.0, 35000.0, 100000.0),
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


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_AUDIT_CONTEXT")

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
with open(os.path.join(report_root, IMPORT_REPORT_NAME), "r", encoding="utf-8") as handle:
    import_report = json.load(handle)

expected_dirty = sorted(import_report["dirty_landscape_packages"])
actual_dirty = dirty_packages()
if actual_dirty != expected_dirty:
    raise RuntimeError(
        "ABIVERD_TERRAIN_RELIEF_AUDIT_SCOPE expected=%s actual=%s"
        % ("|".join(expected_dirty), "|".join(actual_dirty))
    )

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(OLD_TOWN_BOX))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
landscape_actors = [
    actor for actor in actors if isinstance(actor, (unreal.Landscape, unreal.LandscapeStreamingProxy))
]
ignored_actors = [actor for actor in actors if actor not in landscape_actors]
floors = sorted(
    [
        actor
        for actor in actors
        if actor.get_actor_label().startswith("Core_SS_")
        and actor.get_actor_label().endswith("_F1_Floor")
    ],
    key=lambda actor: actor.get_actor_label(),
)


def landscape_height(x, y):
    hits = unreal.SystemLibrary.line_trace_multi(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        ignored_actors,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    for hit in hits or []:
        data = hit.to_dict()
        actor = data.get("hit_actor")
        location = data.get("location")
        if data.get("blocking_hit") and actor in landscape_actors and location:
            return location.z, actor.get_actor_label()
    return None, ""


foundation_records = []
for floor in floors:
    origin, extent = floor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    inset_x = extent.x * 0.60
    inset_y = extent.y * 0.60
    points = [
        ("center", origin.x, origin.y),
        ("north_east", origin.x + inset_x, origin.y + inset_y),
        ("north_west", origin.x - inset_x, origin.y + inset_y),
        ("south_east", origin.x + inset_x, origin.y - inset_y),
        ("south_west", origin.x - inset_x, origin.y - inset_y),
    ]
    samples = []
    for name, x, y in points:
        support_z, support_actor = landscape_height(x, y)
        samples.append(
            {
                "sample": name,
                "landscape_actor": support_actor,
                "landscape_z_cm": round(support_z, 3) if support_z is not None else None,
                "floor_bottom_z_cm": round(bottom_z, 3),
                "gap_cm": round(bottom_z - support_z, 3) if support_z is not None else None,
            }
        )
    gaps = [sample["gap_cm"] for sample in samples if sample["gap_cm"] is not None]
    foundation_records.append(
        {
            "label": floor.get_actor_label(),
            "samples_found": len(gaps),
            "minimum_gap_cm": min(gaps) if gaps else None,
            "maximum_gap_cm": max(gaps) if gaps else None,
            "samples": samples,
        }
    )

terrain_samples = []
for y in range(-30000, 30001, 5000):
    for x in range(-35000, 35001, 5000):
        height, actor_label = landscape_height(float(x), float(y))
        if height is not None:
            terrain_samples.append({"x_cm": x, "y_cm": y, "z_cm": round(height, 3), "actor": actor_label})

heights = [sample["z_cm"] for sample in terrain_samples]
source_texture = unreal.load_asset(import_report["source_texture"].split(".")[0])
payload = {
    "schema_version": 1,
    "status": "terrain_relief_unsaved_preview_audited",
    "context": {"project_directory": project_directory, "level": level_path},
    "scope": {
        "expected_dirty_packages": expected_dirty,
        "actual_dirty_packages": actual_dirty,
        "scope_exact": actual_dirty == expected_dirty,
    },
    "landscape": {
        "actor_count": len(landscape_actors),
        "terrain_sample_count": len(heights),
        "sample_min_z_cm": min(heights) if heights else None,
        "sample_max_z_cm": max(heights) if heights else None,
        "sample_range_cm": round(max(heights) - min(heights), 3) if heights else None,
        "samples": terrain_samples,
    },
    "foundations": {
        "floor_count": len(foundation_records),
        "complete_trace_count": sum(item["samples_found"] == 5 for item in foundation_records),
        "records": foundation_records,
    },
    "source_asset": {
        "path": import_report["source_texture"],
        "loaded": source_texture is not None,
        "size": import_report["source_texture_size"],
        "srgb": import_report["source_texture_srgb"],
    },
    "changes_made": False,
}
os.makedirs(report_root, exist_ok=True)
output_path = os.path.join(report_root, OUTPUT_REPORT_NAME)
with open(output_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_TERRAIN_RELIEF_POST_PREVIEW_AUDIT_PASS terrain_range_cm=%.3f floors=%d dirty=%d"
    % (payload["landscape"]["sample_range_cm"] or 0.0, len(foundation_records), len(actual_dirty))
)
print("ABIVERD_TERRAIN_RELIEF_POST_PREVIEW_AUDIT_PASS", output_path)
