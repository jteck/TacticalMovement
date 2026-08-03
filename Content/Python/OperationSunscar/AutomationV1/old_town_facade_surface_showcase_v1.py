"""Spawn three transient Quixel facade panels for visual selection; never saves."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PREFIX = "TEMP_OT_FACADE_"
MASTER_PATH = "/Game/Fab/Materials/Standard/M_MS_Srf"
MASKS_PATH = "/Game/Fab/Textures/Standard/T_DefaultMasks"
HEIGHT_PATH = "/Game/Fab/Textures/Standard/T_DefaultDisplacement"
SPECS = [
    (
        "01_WallPaint",
        "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_BaseColor",
        "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_Normal",
    ),
    (
        "02_Stucco",
        "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_016_vigrejf/Stucco_Wall_vigrejf_4K_BaseColor",
        "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_016_vigrejf/Stucco_Wall_vigrejf_4K_Normal",
    ),
    (
        "03_FlakedPaint",
        "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_017_vhqkeff/Flaked_Paint_Wall_vhqkeff_4K_BaseColor",
        "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_017_vhqkeff/Flaked_Paint_Wall_vhqkeff_4K_Normal",
    ),
]


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
for actor in actors:
    if actor.get_actor_label().startswith(PREFIX):
        actor_system.destroy_actor(actor)

master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
masks = unreal.EditorAssetLibrary.load_asset(MASKS_PATH)
height = unreal.EditorAssetLibrary.load_asset(HEIGHT_PATH)
cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
if None in (master, masks, height, cube):
    raise RuntimeError("SUNSCAR_FACADE_SHOWCASE_REQUIRED_ASSET_MISSING")

landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
non_landscapes = [actor for actor in actors if actor not in landscapes]
records = []
for index, (name, base_path, normal_path) in enumerate(SPECS):
    x = -13500.0 + index * 700.0
    y = -12500.0
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        non_landscapes,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    hit_data = hit.to_dict() if hit is not None else {}
    if not hit_data.get("blocking_hit"):
        raise RuntimeError("SUNSCAR_FACADE_SHOWCASE_TERRAIN_TRACE_FAILED " + name)
    support_z = hit_data["location"].z
    base_color = common.load_asset_checked(config, base_path)
    normal = common.load_asset_checked(config, normal_path)
    actor = actor_system.spawn_actor_from_object(
        cube,
        unreal.Vector(x, y, support_z + 200.0),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0),
        transient=True,
    )
    actor.set_actor_label(PREFIX + name)
    actor.set_actor_scale3d(unreal.Vector(2.5, 0.2, 2.0))
    dynamic = actor.static_mesh_component.create_dynamic_material_instance(
        0, master, PREFIX + name + "_MID"
    )
    if dynamic is None:
        raise RuntimeError("SUNSCAR_FACADE_SHOWCASE_MID_FAILED " + name)
    dynamic.set_texture_parameter_value("BaseColorTexture", base_color)
    dynamic.set_texture_parameter_value("NormalTexture", normal)
    dynamic.set_texture_parameter_value("MetallicRoughnessTexture", masks)
    dynamic.set_texture_parameter_value("HeightTexture", height)
    dynamic.set_scalar_parameter_value("Tiling", 4.0)
    dynamic.set_scalar_parameter_value("Normal Intensity", 0.55)
    dynamic.set_scalar_parameter_value("Specular", 0.2)
    dynamic.set_scalar_parameter_value("Min Roughness", 0.7)
    dynamic.set_scalar_parameter_value("Max Roughness", 1.0)
    dynamic.set_scalar_parameter_value("Saturation", 0.8)
    dynamic.set_scalar_parameter_value("Brightness", 0.86)
    dynamic.set_scalar_parameter_value("Contrast", 0.92)
    actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    records.append({
        "label": actor.get_actor_label(),
        "base_color": base_path,
        "normal": normal_path,
        "location_cm": [x, y, support_z + 200.0],
        "dimensions_cm": [500.0, 40.0, 400.0],
        "tiling": 4.0,
    })

dirty = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
if dirty:
    raise RuntimeError("SUNSCAR_FACADE_SHOWCASE_DIRTIED_PACKAGES %s" % "|".join(dirty))

payload = {
    "schema_version": 1,
    "status": "transient_showcase_ready",
    "context": context,
    "records": records,
    "dirty_packages": dirty,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_facade_surface_showcase_v1.json", payload)
unreal.log("SUNSCAR_FACADE_SHOWCASE panels=%d report=%s" % (len(records), report))
print("SUNSCAR_FACADE_SHOWCASE", len(records), report)
