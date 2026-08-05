"""Blend the unsaved temporary terrain forms into their nearest ground overlays."""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = "AbiverdTemporaryTerrainFormsV1"
EXPECTED_COUNT = 18


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_BLEND_CONTEXT")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
forms = sorted(
    [actor for actor in actors if PASS_TAG in [str(tag) for tag in actor.tags]],
    key=lambda actor: actor.get_actor_label(),
)
if len(forms) != EXPECTED_COUNT:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_BLEND_SCOPE %d" % len(forms))

overlays = []
for actor in actors:
    if "VisualGroundOverlay" not in [str(tag) for tag in actor.tags]:
        continue
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    if material is None:
        continue
    origin, extent = actor.get_actor_bounds(False)
    overlays.append((origin, extent, origin.z + extent.z, material))
if len(overlays) != 288:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_BLEND_OVERLAYS %d" % len(overlays))


def nearest_surface(x, y):
    covering = [
        item
        for item in overlays
        if abs(x - item[0].x) <= item[1].x + 25.0 and abs(y - item[0].y) <= item[1].y + 25.0
    ]
    if covering:
        return max(covering, key=lambda item: item[2])
    return min(overlays, key=lambda item: (item[0].x - x) ** 2 + (item[0].y - y) ** 2)


records = []
for index, actor in enumerate(forms):
    location = actor.get_actor_location()
    origin, extent, ground_z, material = nearest_surface(location.x, location.y)
    old_scale = actor.get_actor_scale3d()
    visible_rise = 90.0 + (index % 5) * 15.0
    vertical_radius = 250.0
    actor.set_actor_location(
        unreal.Vector(location.x, location.y, ground_z - (vertical_radius - visible_rise)),
        False,
        False,
    )
    actor.set_actor_scale3d(unreal.Vector(old_scale.x * 1.12, old_scale.y * 1.12, 5.0))
    actor.static_mesh_component.set_material(0, material)
    records.append(
        {
            "label": actor.get_actor_label(),
            "visible_rise_cm": visible_rise,
            "ground_z_cm": ground_z,
            "material": material.get_path_name(),
            "scale": list(actor.get_actor_scale3d().to_tuple()),
            "package": actor.get_package().get_name(),
        }
    )

dirty = sorted(
    {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
payload = {
    "schema_version": 1,
    "status": "unsaved_preview_blended",
    "actor_count": len(records),
    "actors": records,
    "dirty_packages": dirty,
    "changes_made": True,
}
root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(root, exist_ok=True)
path = os.path.join(root, "abiverd_temporary_terrain_forms_blend_preview_v1.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_TEMP_TERRAIN_BLEND_PASS actors=%d dirty=%d" % (len(records), len(dirty)))
print("ABIVERD_TEMP_TERRAIN_BLEND_PASS", path)
