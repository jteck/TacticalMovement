"""Read-only Hotel/Bazaar opening inventory for the Abiverd facade pass."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TARGET_SITES = {"SS_007": "Municipal Hotel", "SS_017": "Covered Bazaar"}


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


def actor_site(actor):
    for tag in actor.tags:
        value = str(tag)
        if value.startswith("Building_"):
            return value[len("Building_"):]
        if value in TARGET_SITES:
            return value
    label = actor.get_actor_label()
    for site in TARGET_SITES:
        if site in label:
            return site
    return ""


def classify(label):
    value = label.lower()
    if "door" in value:
        return "door"
    if "window" in value or "_win_" in value:
        if value.endswith("_frame"):
            return "window_frame"
        if value.endswith("_glass"):
            return "window_glass"
        return "window_other"
    if "lintel" in value:
        return "lintel"
    if "wall" in value:
        return "wall"
    if "parapet" in value:
        return "parapet"
    if "balcony" in value:
        return "balcony"
    if "shade" in value or "awning" in value or "canopy" in value:
        return "shade"
    return "supporting"


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_HOTEL_BAZAAR_AUDIT_WRONG_PROJECT")

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_HOTEL_BAZAAR_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_HOTEL_BAZAAR_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_HOTEL_BAZAAR_AUDIT_LOAD_DIRTY")

rows = []
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in actor_subsystem.get_all_level_actors():
    site = actor_site(actor)
    if site not in TARGET_SITES:
        continue
    label = actor.get_actor_label()
    origin, extent = actor.get_actor_bounds(False)
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    component = actor.static_mesh_component if isinstance(actor, unreal.StaticMeshActor) else None
    mesh = component.get_editor_property("static_mesh") if component else None
    rows.append(
        {
            "site": site,
            "site_name": TARGET_SITES[site],
            "label": label,
            "class": actor.get_class().get_name(),
            "category": classify(label),
            "tags": sorted(str(tag) for tag in actor.tags),
            "location_cm": [round(location.x, 3), round(location.y, 3), round(location.z, 3)],
            "rotation_deg": [round(rotation.roll, 3), round(rotation.pitch, 3), round(rotation.yaw, 3)],
            "bounds_origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
            "bounds_size_cm": [round(extent.x * 2.0, 3), round(extent.y * 2.0, 3), round(extent.z * 2.0, 3)],
            "mesh": mesh.get_path_name() if mesh else "",
            "visible": bool(component.is_visible()) if component else None,
            "hidden_in_game": bool(component.get_editor_property("hidden_in_game")) if component else None,
            "collision_enabled": str(component.get_collision_enabled()) if component else "",
        }
    )

rows.sort(key=lambda item: (item["site"], item["category"], item["label"]))
by_site = {}
for site in sorted(TARGET_SITES):
    site_rows = [row for row in rows if row["site"] == site]
    category_counts = {}
    for row in site_rows:
        category_counts[row["category"]] = category_counts.get(row["category"], 0) + 1
    by_site[site] = {
        "site_name": TARGET_SITES[site],
        "actor_count": len(site_rows),
        "category_counts": dict(sorted(category_counts.items())),
        "door_labels": [row["label"] for row in site_rows if row["category"] == "door"],
        "window_frame_labels": [row["label"] for row in site_rows if row["category"] == "window_frame"],
        "window_glass_labels": [row["label"] for row in site_rows if row["category"] == "window_glass"],
        "lintel_labels": [row["label"] for row in site_rows if row["category"] == "lintel"],
        "wall_labels": [row["label"] for row in site_rows if row["category"] == "wall"],
    }

dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_HOTEL_BAZAAR_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))

report = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "target_sites": by_site,
    "actors": rows,
    "dirty_after": dirty_after,
    "policies": {
        "mutation": "none",
        "opening_authority": "existing gameplay shells, doors and windows remain authoritative",
        "decision_gate": "inventory first; only compatible assemblies may be extended in a later dry-run-first pass",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_hotel_bazaar_opening_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_HOTEL_BAZAAR_OPENING_AUDIT_COMPLETE hotel=%d bazaar=%d"
    % (by_site["SS_007"]["actor_count"], by_site["SS_017"]["actor_count"])
)
print("ABIVERD_HOTEL_BAZAAR_OPENING_AUDIT_COMPLETE", report_path)
