"""Validate and accept the complete unsaved Abiverd architecture preview."""

import json
import os

import unreal


TAG = unreal.Name("SunscarAbiverdHeritageCompositionV1")
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MATERIALS = {
    "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
    "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
}
ACTOR_PREFIX = "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/"
OBJECT_PREFIX = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
plan_path = os.path.join(report_root, "abiverd_heritage_architecture_composition_dry_run_v1.json")
with open(plan_path, "r", encoding="utf-8") as handle:
    plan = json.load(handle)
expected = {item["label"]: item for item in plan["placements"]}

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_ACCEPTANCE_WRONG_LEVEL " + level_path)

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = [actor for actor in actor_subsystem.get_all_level_actors() if TAG in list(actor.tags)]
by_label = {actor.get_actor_label(): actor for actor in actors}
if len(actors) != len(by_label) or set(by_label) != set(expected):
    raise RuntimeError(
        "ABIVERD_ACCEPTANCE_LABEL_SCOPE expected=%d actors=%d labels=%s"
        % (len(expected), len(actors), "|".join(sorted(by_label)))
    )

rows = []
actor_packages = set()
for label in sorted(by_label):
    actor = by_label[label]
    item = expected[label]
    component = actor.static_mesh_component
    mesh = component.get_editor_property("static_mesh")
    if mesh is None or mesh.get_path_name().split(".", 1)[0] != item["mesh"]:
        raise RuntimeError("ABIVERD_ACCEPTANCE_MESH_MISMATCH " + label)
    collision = component.get_collision_enabled()
    expected_collision = (
        unreal.CollisionEnabled.QUERY_AND_PHYSICS
        if item["collision"] == "QueryAndPhysics"
        else unreal.CollisionEnabled.NO_COLLISION
    )
    if collision != expected_collision:
        raise RuntimeError("ABIVERD_ACCEPTANCE_COLLISION_MISMATCH " + label)
    if component.is_visible() != bool(item["visible"]):
        raise RuntimeError("ABIVERD_ACCEPTANCE_VISIBILITY_MISMATCH " + label)
    location = actor.get_actor_location()
    if abs(location.x - item["x"]) > 0.1 or abs(location.y - item["y"]) > 0.1:
        raise RuntimeError("ABIVERD_ACCEPTANCE_LOCATION_MISMATCH " + label)
    package = actor.get_package().get_name()
    if not package.startswith(ACTOR_PREFIX):
        raise RuntimeError("ABIVERD_ACCEPTANCE_ACTOR_PACKAGE " + package)
    actor_packages.add(package)
    origin, extent = actor.get_actor_bounds(False)
    rows.append(
        {
            "label": label,
            "site": item["site"],
            "mesh": mesh.get_path_name(),
            "location_cm": [location.x, location.y, location.z],
            "bounds_bottom_cm": origin.z - extent.z,
            "terrain_z_cm": item["terrain_z_cm"],
            "collision": str(collision),
            "visible": component.is_visible(),
            "material": component.get_material(0).get_path_name() if component.get_material(0) else "",
            "package": package,
        }
    )

dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
unexpected = [
    name for name in dirty
    if name not in MATERIALS and name not in actor_packages and not name.startswith(OBJECT_PREFIX)
]
if unexpected:
    raise RuntimeError("ABIVERD_ACCEPTANCE_UNEXPECTED_DIRTY " + "|".join(unexpected))
if not MATERIALS.issubset(set(dirty)) or actor_packages != set(name for name in dirty if name.startswith(ACTOR_PREFIX)):
    raise RuntimeError("ABIVERD_ACCEPTANCE_INCOMPLETE_DIRTY_SCOPE")

payload = {
    "schema_version": 1,
    "status": "complete_unsaved_architecture_preview_accepted",
    "actor_count": len(actors),
    "material_assets": sorted(MATERIALS),
    "actor_package_count": len(actor_packages),
    "external_object_package_count": sum(1 for name in dirty if name.startswith(OBJECT_PREFIX)),
    "rows": rows,
    "dirty_packages": dirty,
    "changes_saved": False,
}
path = os.path.join(report_root, "abiverd_heritage_architecture_acceptance_v1.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_ACCEPTANCE actors=%d dirty=%d" % (len(actors), len(dirty)))
print("ABIVERD_ACCEPTANCE", len(actors), path)
