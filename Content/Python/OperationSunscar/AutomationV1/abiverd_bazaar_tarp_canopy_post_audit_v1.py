"""Independent read-only audit of the SS_017 Quixel tarp canopy conversion."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TARP_MESH_PATH = (
    "/Game/Maps/Sunscar/Art/Heritage/Props/WrinkledTarp/"
    "vieldbo_tier_1/StaticMeshes/vieldbo_tier_1"
)
CANOPY_LABELS = [
    "Bazaar_N_Canopy_01", "Bazaar_N_Canopy_02", "Bazaar_N_Canopy_03", "Bazaar_N_Canopy_04",
    "Bazaar_S_Canopy_01", "Bazaar_S_Canopy_02", "Bazaar_S_Canopy_03", "Bazaar_S_Canopy_04",
]
WORKING_BOX = unreal.Box(
    min=unreal.Vector(500.0, -10400.0, -100000.0),
    max=unreal.Vector(5100.0, -8200.0, 100000.0),
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
    raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(WORKING_BOX))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_LOAD_DIRTY")

actors = {
    actor.get_actor_label(): actor
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
}
tarp_mesh = unreal.EditorAssetLibrary.load_asset(TARP_MESH_PATH)
if not isinstance(tarp_mesh, unreal.StaticMesh):
    raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_SOURCE_MISSING")
expected_mesh_path = tarp_mesh.get_path_name()
rows = []
for label in CANOPY_LABELS:
    actor = actors.get(label)
    if not isinstance(actor, unreal.StaticMeshActor):
        raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_MISSING " + label)
    component = actor.static_mesh_component
    mesh = component.get_editor_property("static_mesh")
    mesh_path = mesh.get_path_name() if mesh else ""
    if mesh_path != expected_mesh_path:
        raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_MESH %s %s" % (label, mesh_path))
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_COLLISION " + label)
    if bool(component.get_editor_property("can_ever_affect_navigation")):
        raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_NAVIGATION " + label)
    origin, extent = actor.get_actor_bounds(False)
    size = extent * 2.0
    underside = float(origin.z - extent.z)
    rows.append(
        {
            "label": label,
            "mesh": mesh_path,
            "bounds_origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
            "bounds_size_cm": [round(size.x, 3), round(size.y, 3), round(size.z, 3)],
            "underside_z_cm": round(underside, 3),
            "collision": str(component.get_collision_enabled()),
            "navigation": bool(component.get_editor_property("can_ever_affect_navigation")),
            "cast_shadow": bool(component.get_editor_property("cast_shadow")),
            "actor_collision": bool(actor.get_actor_enable_collision()),
            "tags": sorted(str(tag) for tag in actor.tags),
        }
    )

north_inner = min(row["bounds_origin_cm"][1] - row["bounds_size_cm"][1] * 0.5 for row in rows if "_N_" in row["label"])
south_inner = max(row["bounds_origin_cm"][1] + row["bounds_size_cm"][1] * 0.5 for row in rows if "_S_" in row["label"])
corridor_width = north_inner - south_inner
if corridor_width < 600.0:
    raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_CORRIDOR %.3f" % corridor_width)
if dirty_packages():
    raise RuntimeError("ABIVERD_BAZAAR_TARP_AUDIT_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "post_conversion_audit_passed",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "canopy_count": len(rows),
    "central_passage_width_cm": round(corridor_width, 3),
    "canopies": rows,
    "dirty_after": dirty_packages(),
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_bazaar_tarp_canopy_post_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_BAZAAR_TARP_POST_AUDIT_PASS count=%d corridor=%.1f" % (len(rows), corridor_width))
print("ABIVERD_BAZAAR_TARP_POST_AUDIT_PASS", report_path)
