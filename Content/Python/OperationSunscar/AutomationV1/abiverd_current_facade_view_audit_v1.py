"""Read-only identification of the building currently framed in the viewport."""

import json
import math
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
        if value.startswith("SS_") and len(value) == 6:
            return value
    return ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_CURRENT_FACADE_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_CURRENT_FACADE_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_CURRENT_FACADE_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
camera_location, camera_rotation = editor.get_level_viewport_camera_info()
forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
rows = []
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    site = actor_site(actor)
    if not site:
        continue
    origin, extent = actor.get_actor_bounds(False)
    dx = origin.x - camera_location.x
    dy = origin.y - camera_location.y
    dz = origin.z - camera_location.z
    distance = math.sqrt(dx * dx + dy * dy + dz * dz)
    if distance < 1.0:
        continue
    facing = (dx * forward.x + dy * forward.y + dz * forward.z) / distance
    if facing < 0.72 or distance > 12000.0:
        continue
    component = actor.static_mesh_component
    materials = []
    for index in range(component.get_num_materials()):
        material = component.get_material(index)
        materials.append(material.get_outermost().get_name() if material else "")
    rows.append(
        {
            "site": site,
            "label": actor.get_actor_label(),
            "distance_cm": round(distance, 2),
            "facing_dot": round(facing, 5),
            "bounds_origin_cm": [round(origin.x, 2), round(origin.y, 2), round(origin.z, 2)],
            "bounds_size_cm": [round(extent.x * 2.0, 2), round(extent.y * 2.0, 2), round(extent.z * 2.0, 2)],
            "materials": materials,
            "collision": str(component.get_collision_enabled()),
            "visible": component.is_visible(),
        }
    )
rows.sort(key=lambda row: (-row["facing_dot"], row["distance_cm"]))
site_scores = {}
for row in rows:
    site_scores.setdefault(row["site"], 0.0)
    site_scores[row["site"]] += max(0.0, row["facing_dot"] - 0.72) / max(row["distance_cm"], 1.0)
site_ranking = sorted(site_scores.items(), key=lambda item: item[1], reverse=True)
dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_CURRENT_FACADE_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))
report = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "camera_location_cm": [round(camera_location.x, 2), round(camera_location.y, 2), round(camera_location.z, 2)],
    "camera_rotation_deg": [round(camera_rotation.roll, 2), round(camera_rotation.pitch, 2), round(camera_rotation.yaw, 2)],
    "site_ranking": [{"site": site, "score": score} for site, score in site_ranking],
    "visible_building_actors": rows,
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_current_facade_view_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_CURRENT_FACADE_AUDIT_COMPLETE top_site=%s actors=%d"
    % (site_ranking[0][0] if site_ranking else "none", len(rows))
)
print("ABIVERD_CURRENT_FACADE_AUDIT_COMPLETE", report_path)
