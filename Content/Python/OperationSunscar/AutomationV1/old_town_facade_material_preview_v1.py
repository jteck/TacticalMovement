"""Create three unsaved Quixel facade MICs and transient review panels."""

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
TARGET_FOLDER = "/Game/Maps/Sunscar/Art/Materials/Facade"
SPECS = [
    {
        "name": "MI_OT_WallPaint_Quixel",
        "label": "01_WallPaint",
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_Normal",
    },
    {
        "name": "MI_OT_Stucco_Quixel",
        "label": "02_Stucco",
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_016_vigrejf/Stucco_Wall_vigrejf_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_016_vigrejf/Stucco_Wall_vigrejf_4K_Normal",
    },
    {
        "name": "MI_OT_FlakedPaint_Quixel",
        "label": "03_FlakedPaint",
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_017_vhqkeff/Flaked_Paint_Wall_vhqkeff_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_017_vhqkeff/Flaked_Paint_Wall_vhqkeff_4K_Normal",
    },
]


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_FACADE_MATERIAL_PREVIEW_REFUSED dirty_before=%d" % len(dirty_before))

actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
for actor in actors:
    if actor.get_actor_label().startswith(PREFIX):
        actor_system.destroy_actor(actor)

master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
masks = unreal.EditorAssetLibrary.load_asset(MASKS_PATH)
height = unreal.EditorAssetLibrary.load_asset(HEIGHT_PATH)
cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
if None in (master, masks, height, cube):
    raise RuntimeError("SUNSCAR_FACADE_MATERIAL_PREVIEW_REQUIRED_ASSET_MISSING")

for spec in SPECS:
    path = TARGET_FOLDER + "/" + spec["name"]
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError("SUNSCAR_FACADE_MATERIAL_PREVIEW_REFUSED existing=" + path)

world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
non_landscapes = [actor for actor in actors if actor not in landscapes]
unreal.EditorAssetLibrary.make_directory(TARGET_FOLDER)
records = []
for index, spec in enumerate(SPECS):
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        spec["name"],
        TARGET_FOLDER,
        unreal.MaterialInstanceConstant,
        unreal.MaterialInstanceConstantFactoryNew(),
    )
    if material is None:
        raise RuntimeError("SUNSCAR_FACADE_MATERIAL_PREVIEW_CREATE_FAILED " + spec["name"])
    base_color = common.load_asset_checked(config, spec["base"])
    normal = common.load_asset_checked(config, spec["normal"])
    material.set_editor_property("parent", master)
    for parameter, texture in (
        ("BaseColorTexture", base_color),
        ("NormalTexture", normal),
        ("MetallicRoughnessTexture", masks),
        ("HeightTexture", height),
    ):
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
            material, parameter, texture
        )
    for parameter, value in (
        ("Tiling", 4.0),
        ("Normal Intensity", 0.55),
        ("Specular", 0.2),
        ("Min Roughness", 0.7),
        ("Max Roughness", 1.0),
        ("Saturation", 0.8),
        ("Brightness", 0.86),
        ("Contrast", 0.92),
    ):
        unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
            material, parameter, value
        )
    unreal.MaterialEditingLibrary.update_material_instance(material)

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
        raise RuntimeError("SUNSCAR_FACADE_MATERIAL_PREVIEW_TRACE_FAILED " + spec["label"])
    support_z = hit_data["location"].z
    panel = actor_system.spawn_actor_from_object(
        cube,
        unreal.Vector(x, y, support_z + 200.0),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0),
        transient=True,
    )
    panel.set_actor_label(PREFIX + spec["label"])
    panel.set_actor_scale3d(unreal.Vector(2.5, 0.2, 2.0))
    panel.static_mesh_component.set_material(0, material)
    panel.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    records.append({
        "label": panel.get_actor_label(),
        "material_path": material.get_path_name(),
        "base_color": spec["base"],
        "normal": spec["normal"],
        "location_cm": [x, y, support_z + 200.0],
    })

dirty_content = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
expected_content = sorted(TARGET_FOLDER + "/" + spec["name"] for spec in SPECS)
dirty_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_content != expected_content or dirty_maps:
    raise RuntimeError(
        "SUNSCAR_FACADE_MATERIAL_PREVIEW_SCOPE_FAILED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_material_preview_ready",
    "context": context,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_facade_material_preview_v1.json", payload)
unreal.log("SUNSCAR_FACADE_MATERIAL_PREVIEW materials=3 panels=3 report=%s" % report)
print("SUNSCAR_FACADE_MATERIAL_PREVIEW", report)
