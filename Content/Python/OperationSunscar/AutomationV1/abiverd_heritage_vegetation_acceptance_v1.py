"""Validate and accept the complete unsaved Abiverd HISM vegetation preview."""

import json
import os
import runpy

import unreal


_dispatcher_dirty = [
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
]
if _dispatcher_dirty == ["/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"]:
    runpy.run_path(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "abiverd_cleanup_unsaved_meadow_material_v1.py"),
        run_name="__main__",
    )
    raise SystemExit
if not _dispatcher_dirty:
    runpy.run_path(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "abiverd_landscape_meadow_material_v1.py"),
        run_name="__main__",
    )
    raise SystemExit


TAG = unreal.Name("SunscarAbiverdVegetationHISMV1")
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_LABEL = "ABV_SS025_PoppyMeadow_HISM"
EXPECTED_COMPONENTS = 16
EXPECTED_INSTANCES = 1415
EXPECTED_POPPIES = 765
EXPECTED_GRASS = 650
ACTOR_PREFIX = "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/"
OBJECT_PREFIX = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"
MATERIALS = {
    "/Game/Maps/Sunscar/Art/Heritage/Foliage/FieldPoppy/MI_FieldPoppy",
    "/Game/Maps/Sunscar/Art/Heritage/Foliage/WildGrass/MI_WildGrass",
}

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_WRONG_LEVEL " + level_path)

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = [actor for actor in actor_subsystem.get_all_level_actors() if TAG in list(actor.tags)]
if len(actors) != 1 or actors[0].get_actor_label() != EXPECTED_LABEL:
    raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_ACTOR_SCOPE count=%d" % len(actors))
actor = actors[0]
if actor.get_editor_property("replicates"):
    raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_REPLICATION_ENABLED")

components = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
if len(components) != EXPECTED_COMPONENTS:
    raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_COMPONENT_SCOPE count=%d" % len(components))

rows = []
counts = {"poppy": 0, "grass": 0}
for component in sorted(components, key=lambda item: item.get_name()):
    name = component.get_name()
    mesh = component.get_editor_property("static_mesh")
    if mesh is None:
        raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_MISSING_MESH " + name)
    mesh_path = mesh.get_path_name()
    if "/FieldPoppy/" in mesh_path:
        kind = "poppy"
    elif "/WildGrass/" in mesh_path:
        kind = "grass"
    else:
        raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_UNEXPECTED_MESH " + mesh_path)
    instance_count = component.get_instance_count()
    counts[kind] += instance_count
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_COLLISION " + name)
    if component.cast_shadow:
        raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_SHADOW " + name)
    if component.instance_start_cull_distance != 6000 or component.instance_end_cull_distance != 20000:
        raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_CULL " + name)
    rows.append(
        {
            "component": name,
            "kind": kind,
            "mesh": mesh_path,
            "instance_count": instance_count,
            "collision": str(component.get_collision_enabled()),
            "cast_shadow": component.cast_shadow,
            "start_cull_distance_cm": component.instance_start_cull_distance,
            "end_cull_distance_cm": component.instance_end_cull_distance,
        }
    )

if counts != {"poppy": EXPECTED_POPPIES, "grass": EXPECTED_GRASS}:
    raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_INSTANCE_SCOPE " + repr(counts))
if sum(counts.values()) != EXPECTED_INSTANCES:
    raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_TOTAL")

actor_package = actor.get_package().get_name()
if not actor_package.startswith(ACTOR_PREFIX):
    raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_ACTOR_PACKAGE " + actor_package)
dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
unexpected = [
    name for name in dirty
    if name != actor_package and name not in MATERIALS and not name.startswith(OBJECT_PREFIX)
]
if unexpected or actor_package not in dirty:
    raise RuntimeError("ABIVERD_VEGETATION_ACCEPTANCE_DIRTY_SCOPE " + "|".join(unexpected))

payload = {
    "schema_version": 1,
    "status": "complete_unsaved_hism_vegetation_preview_accepted",
    "actor_label": actor.get_actor_label(),
    "actor_package": actor_package,
    "component_count": len(components),
    "instance_counts": counts,
    "total_instance_count": sum(counts.values()),
    "components": rows,
    "material_assets": sorted(MATERIALS),
    "dirty_packages": dirty,
    "changes_saved": False,
}
path = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", "abiverd_heritage_vegetation_acceptance_v1.json"
)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_VEGETATION_ACCEPTANCE components=%d instances=%d" % (len(components), sum(counts.values())))
print("ABIVERD_VEGETATION_ACCEPTANCE", sum(counts.values()), path)
