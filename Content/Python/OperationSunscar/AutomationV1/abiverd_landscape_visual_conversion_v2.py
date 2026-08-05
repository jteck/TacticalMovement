"""Apply and save the UE 5.8 Old Town/Abiverd Landscape visual conversion.

The pass replaces overlapping visible ground tiles with Landscape paint,
upgrades the Landscape material to six locally-pruned layers, and hides only
map-owned planning guides/collision visuals while preserving their data.
"""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
LAYER_FOLDER = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/Layers"
MASK_ROOT = os.path.join(
    "/Users/jasonteck/UnrealEngine/_worktrees/map-development",
    "Saved/OperationSunscar/Generated/LandscapeMasksV2",
)
PASS_TAG = unreal.Name("SunscarLandscapeVisualConversionV2")
HIDDEN_TAG = unreal.Name("SunscarVisualConversionHiddenV2")
SIZE = 2017

LAYERS = (
    {
        "target": "Sand",
        "semantic": "AridSandBase",
        "tile_cm": 310.0,
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv/Sandstone_Rocky_Ground_vmjjfiv_High_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv/Sandstone_Rocky_Ground_vmjjfiv_High_4K_Normal",
        "tint": (0.84, 0.78, 0.67),
        "roughness": 0.93,
    },
    {
        "target": "Mud",
        "semantic": "CompactedEarth",
        "tile_cm": 280.0,
        "base": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/DryTrampledSoil/Dry_Trampled_Soil_wcivbfb_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/DryTrampledSoil/Dry_Trampled_Soil_wcivbfb_4K_Normal",
        "tint": (0.82, 0.72, 0.59),
        "roughness": 0.91,
        "mask": "Abiverd_Mud_2017.png",
        "source_layer_info": "/Landmass/PreviewContent/LayerInfos/Mud_LayerInfo",
        "layer_info": LAYER_FOLDER + "/LI_CompactedEarth_FromMud",
    },
    {
        "target": "Desert",
        "semantic": "WeatheredAsphalt",
        "tile_cm": 360.0,
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_012_sjyjcbja/Crushed_Asphalt_Ground_sjyjcbja_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_012_sjyjcbja/Crushed_Asphalt_Ground_sjyjcbja_4K_Normal",
        "tint": (0.70, 0.66, 0.58),
        "roughness": 0.90,
        "mask": "Abiverd_Desert_2017.png",
        "source_layer_info": "/Landmass/PreviewContent/LayerInfos/Desert_LayerInfo",
        "layer_info": LAYER_FOLDER + "/LI_WeatheredAsphalt_FromDesert",
    },
    {
        "target": "Rock",
        "semantic": "StoneAndConcreteHardstand",
        "tile_cm": 260.0,
        "base": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Rough_02/Textures/T_Mil_Trench_Ground_Dirt_Rough_02_B",
        "normal": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Rough_02/Textures/T_Mil_Trench_Ground_Dirt_Rough_02_N",
        "tint": (0.78, 0.75, 0.68),
        "roughness": 0.92,
        "mask": "Abiverd_Rock_2017.png",
        "source_layer_info": "/Landmass/PreviewContent/LayerInfos/Rock_LayerInfo",
        "layer_info": LAYER_FOLDER + "/LI_StoneHardstand_FromRock",
    },
    {
        "target": "Farm",
        "semantic": "RoadsideSilt",
        "tile_cm": 250.0,
        "base": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Fine_02/Textures/T_Mil_Trench_Ground_Dirt_Fine_02_B",
        "normal": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Fine_02/Textures/T_Mil_Trench_Ground_Dirt_Fine_02_N",
        "tint": (0.88, 0.78, 0.63),
        "roughness": 0.95,
        "mask": "Abiverd_Farm_2017.png",
        "source_layer_info": "/Landmass/PreviewContent/LayerInfos/Farm_LayerInfo",
        "layer_info": LAYER_FOLDER + "/LI_RoadsideSilt_FromFarm",
    },
    {
        "target": "Grass",
        "semantic": "AbiverdSpringMeadow",
        "tile_cm": 240.0,
        "base": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/WildGrassGround/Wild_Grass_xbreagf_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/WildGrassGround/Wild_Grass_xbreagf_4K_Normal",
        "tint": (0.52, 0.78, 0.44),
        "roughness": 0.94,
        "mask": "Abiverd_Grass_2017.png",
        "layer_info": LAYER_FOLDER + "/LI_Meadow_NonWeight",
    },
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


def expression(material, expression_class, x, y):
    result = unreal.MaterialEditingLibrary.create_material_expression(material, expression_class, x, y)
    if result is None:
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_EXPRESSION " + expression_class.__name__)
    return result


def pin_names(value):
    return [str(name) for name in unreal.MaterialEditingLibrary.get_material_expression_input_names(value)]


def connect(source, destination, input_name, output_name=""):
    names = pin_names(destination)
    resolved = input_name
    if resolved not in names:
        if "Layer " + resolved in names:
            resolved = "Layer " + resolved
        elif resolved == "Coordinates" and "UVs" in names:
            resolved = "UVs"
        elif len(names) == 1:
            resolved = names[0]
    if not unreal.MaterialEditingLibrary.connect_material_expressions(source, output_name, destination, resolved):
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_CONNECT %s %s" % (input_name, "|".join(names)))


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_DIRTY_BEFORE " + "|".join(dirty_packages()))

full_box = unreal.Box(
    min=unreal.Vector(-130000.0, -130000.0, -100000.0),
    max=unreal.Vector(130000.0, 130000.0, 100000.0),
)
working_box = unreal.Box(
    min=unreal.Vector(-20000.0, -16000.0, -100000.0),
    max=unreal.Vector(20000.0, 25000.0, 100000.0),
)
full_descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(full_box))
landscape_descriptors = [
    descriptor for descriptor in full_descriptors
    if str(descriptor.label).startswith("LandscapeStreamingProxy_")
]
working_descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
guids = [descriptor.guid for descriptor in landscape_descriptors + working_descriptors]
unreal.WorldPartitionBlueprintLibrary.load_actors(guids)
unreal.WorldPartitionBlueprintLibrary.pin_actors(guids)
if dirty_packages():
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_LOAD_DIRTY")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
parents = [actor for actor in landscapes if actor.get_actor_label() == "Landscape_Sunscar"]
proxies = [actor for actor in landscapes if isinstance(actor, unreal.LandscapeStreamingProxy)]
component_count = sum(len(proxy.get_components_by_class(unreal.LandscapeComponent)) for proxy in proxies)
if len(parents) != 1 or len(proxies) != 16 or component_count != 256:
    raise RuntimeError(
        "ABIVERD_LANDSCAPE_V2_SCOPE parents=%d proxies=%d components=%d"
        % (len(parents), len(proxies), component_count)
    )
parent = parents[0]

sources = {}
for layer_definition in LAYERS:
    for key in ("base", "normal"):
        path = layer_definition[key]
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(asset, unreal.Texture2D):
            raise RuntimeError("ABIVERD_LANDSCAPE_V2_TEXTURE " + path)
        sources[path] = asset

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_MATERIAL")
material.modify()
unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
material.set_editor_properties(
    {"blend_mode": unreal.BlendMode.BLEND_OPAQUE, "two_sided": False, "tangent_space_normal": True}
)

world_position = expression(material, unreal.MaterialExpressionWorldPosition, -1900, -100)
xy = expression(material, unreal.MaterialExpressionComponentMask, -1730, -100)
xy.set_editor_properties({"r": True, "g": True, "b": False, "a": False})
connect(world_position, xy, "Input")

layer_sources = {}
for index, layer_definition in enumerate(LAYERS):
    y = -1500 + index * 520
    target = layer_definition["target"]
    tile = expression(material, unreal.MaterialExpressionScalarParameter, -1700, y + 170)
    tile.set_editor_property("parameter_name", unreal.Name(target + "_TileCm"))
    tile.set_editor_property("default_value", float(layer_definition["tile_cm"]))
    uv = expression(material, unreal.MaterialExpressionDivide, -1480, y)
    connect(xy, uv, "A")
    connect(tile, uv, "B")
    base = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1240, y - 100)
    base.set_editor_property("parameter_name", unreal.Name(target + "_BaseColor"))
    base_texture = sources[layer_definition["base"]]
    base.set_editor_property("texture", base_texture)
    base.set_editor_property(
        "sampler_type",
        unreal.MaterialSamplerType.SAMPLERTYPE_VIRTUAL_COLOR
        if bool(base_texture.get_editor_property("virtual_texture_streaming"))
        else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
    )
    connect(uv, base, "Coordinates")
    tint = expression(material, unreal.MaterialExpressionVectorParameter, -980, y - 180)
    tint.set_editor_property("parameter_name", unreal.Name(target + "_Tint"))
    r, g, b = layer_definition["tint"]
    tint.set_editor_property("default_value", unreal.LinearColor(r, g, b, 1.0))
    tinted = expression(material, unreal.MaterialExpressionMultiply, -720, y - 100)
    connect(base, tinted, "A")
    connect(tint, tinted, "B")
    normal = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1240, y + 100)
    normal.set_editor_property("parameter_name", unreal.Name(target + "_Normal"))
    normal_texture = sources[layer_definition["normal"]]
    normal.set_editor_property("texture", normal_texture)
    normal.set_editor_property(
        "sampler_type",
        unreal.MaterialSamplerType.SAMPLERTYPE_VIRTUAL_NORMAL
        if bool(normal_texture.get_editor_property("virtual_texture_streaming"))
        else unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
    )
    connect(uv, normal, "Coordinates")
    roughness = expression(material, unreal.MaterialExpressionConstant, -720, y + 250)
    roughness.set_editor_property("r", float(layer_definition["roughness"]))
    ao = expression(material, unreal.MaterialExpressionConstant, -720, y + 340)
    ao.set_editor_property("r", 0.90)
    layer_sources[target] = {
        "base_color": tinted,
        "normal": normal,
        "roughness": roughness,
        "ambient_occlusion": ao,
    }


def build_chain(channel, x, y):
    current = layer_sources["Sand"][channel]
    for layer_index, target in enumerate(("Mud", "Desert", "Rock", "Farm", "Grass")):
        weight = expression(material, unreal.MaterialExpressionLandscapeLayerWeight, x + layer_index * 230, y)
        weight.set_editor_properties(
            {
                "parameter_name": unreal.Name(target),
                "preview_weight": 0.0,
                "const_base": unreal.Vector(0.0, 0.0, 0.0),
            }
        )
        connect(current, weight, "Base")
        connect(layer_sources[target][channel], weight, "Layer")
        current = weight
    return current


base_chain = build_chain("base_color", 50, -900)
normal_chain = build_chain("normal", 50, -300)
roughness_chain = build_chain("roughness", 50, 300)
ao_chain = build_chain("ambient_occlusion", 50, 800)

# One shared low-frequency sample breaks repetition across every layer without
# multiplying the texture cost per layer.
macro_tile = expression(material, unreal.MaterialExpressionConstant, 1250, -1150)
macro_tile.set_editor_property("r", 3600.0)
macro_uv = expression(material, unreal.MaterialExpressionDivide, 1450, -1150)
connect(xy, macro_uv, "A")
connect(macro_tile, macro_uv, "B")
macro_sample = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, 1660, -1150)
macro_sample.set_editor_property("parameter_name", unreal.Name("SharedMacroBase"))
macro_texture = sources[LAYERS[0]["base"]]
macro_sample.set_editor_property("texture", macro_texture)
macro_sample.set_editor_property(
    "sampler_type",
    unreal.MaterialSamplerType.SAMPLERTYPE_VIRTUAL_COLOR
    if bool(macro_texture.get_editor_property("virtual_texture_streaming"))
    else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
)
connect(macro_uv, macro_sample, "Coordinates")
desaturate = expression(material, unreal.MaterialExpressionDesaturation, 1870, -1150)
if not unreal.MaterialEditingLibrary.connect_material_expressions(macro_sample, "", desaturate, ""):
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_CONNECT_DESATURATION_INPUT")
desaturate_fraction = expression(material, unreal.MaterialExpressionConstant, 1660, -980)
desaturate_fraction.set_editor_property("r", 1.0)
connect(desaturate_fraction, desaturate, "Fraction")
macro_strength = expression(material, unreal.MaterialExpressionConstant, 1870, -980)
macro_strength.set_editor_property("r", 0.28)
macro_scaled = expression(material, unreal.MaterialExpressionMultiply, 2080, -1100)
connect(desaturate, macro_scaled, "A")
connect(macro_strength, macro_scaled, "B")
macro_floor = expression(material, unreal.MaterialExpressionConstant3Vector, 2080, -930)
macro_floor.set_editor_property("constant", unreal.LinearColor(0.78, 0.78, 0.78, 1.0))
macro_factor = expression(material, unreal.MaterialExpressionAdd, 2290, -1050)
connect(macro_scaled, macro_factor, "A")
connect(macro_floor, macro_factor, "B")
final_base = expression(material, unreal.MaterialExpressionMultiply, 2510, -850)
connect(base_chain, final_base, "A")
connect(macro_factor, final_base, "B")

for node, material_property in (
    (final_base, unreal.MaterialProperty.MP_BASE_COLOR),
    (normal_chain, unreal.MaterialProperty.MP_NORMAL),
    (roughness_chain, unreal.MaterialProperty.MP_ROUGHNESS),
    (ao_chain, unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),
):
    if not unreal.MaterialEditingLibrary.connect_material_property(node, "", material_property):
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_OUTPUT")
compiler_errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
if compiler_errors:
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_COMPILE " + "|".join(str(item) for item in compiler_errors))

unreal.EditorAssetLibrary.make_directory(LAYER_FOLDER)
layer_infos = {}
created_layer_info_paths = []
for layer_definition in LAYERS[1:]:
    path = layer_definition["layer_info"]
    layer_info = unreal.EditorAssetLibrary.load_asset(path)
    if layer_info is None:
        source_path = layer_definition.get("source_layer_info")
        if not source_path:
            raise RuntimeError("ABIVERD_LANDSCAPE_V2_LAYERINFO_MISSING " + path)
        layer_info = unreal.EditorAssetLibrary.duplicate_asset(source_path, path)
        created_layer_info_paths.append(path)
    if not isinstance(layer_info, unreal.LandscapeLayerInfoObject):
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_LAYERINFO_TYPE " + path)
    if str(layer_info.get_editor_property("layer_name")) != layer_definition["target"]:
        raise RuntimeError(
            "ABIVERD_LANDSCAPE_V2_LAYERINFO_NAME %s actual=%s"
            % (path, str(layer_info.get_editor_property("layer_name")))
        )
    if layer_info.get_editor_property("blend_method") != unreal.LandscapeTargetLayerBlendMethod.NONE:
        layer_info.modify()
        layer_info.set_editor_property("blend_method", unreal.LandscapeTargetLayerBlendMethod.NONE)
    layer_infos[layer_definition["target"]] = layer_info

target_layers = parent.get_editor_property("target_layers")
for target, layer_info in layer_infos.items():
    settings = unreal.LandscapeTargetLayerSettings()
    settings.set_editor_property("layer_info_obj", layer_info)
    target_layers[unreal.Name(target)] = settings
parent.modify()
parent.set_editor_property("landscape_material", None)
parent.set_editor_property("landscape_material", material)
if PASS_TAG not in list(parent.tags):
    parent.tags = list(parent.tags) + [PASS_TAG]
parent.force_layers_full_update()

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
import_rows = []
for layer_definition in LAYERS[1:]:
    target = layer_definition["target"]
    mask_path = os.path.join(MASK_ROOT, layer_definition["mask"])
    if not os.path.isfile(mask_path):
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_MASK " + mask_path)
    texture = unreal.RenderingLibrary.import_file_as_texture2d(world, mask_path)
    if not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_MASK_TEXTURE " + target)
    try:
        texture.set_editor_property("srgb", False)
    except Exception:
        pass
    render_target = unreal.RenderingLibrary.create_render_target2d(
        world,
        SIZE,
        SIZE,
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
        unreal.LinearColor(0.0, 0.0, 0.0, 1.0),
        False,
        False,
    )
    if not isinstance(render_target, unreal.TextureRenderTarget2D):
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_RENDER_TARGET " + target)
    canvas, _size, context = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, render_target)
    canvas.draw_texture(
        texture,
        unreal.Vector2D(0.0, 0.0),
        unreal.Vector2D(float(SIZE), float(SIZE)),
        unreal.Vector2D(0.0, 0.0),
        unreal.Vector2D(1.0, 1.0),
        unreal.LinearColor(1.0, 1.0, 1.0, 1.0),
        unreal.BlendMode.BLEND_OPAQUE,
        0.0,
        unreal.Vector2D(0.5, 0.5),
    )
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, context)
    imported = parent.landscape_import_weightmap_from_render_target(render_target, unreal.Name(target), 0)
    unreal.RenderingLibrary.release_render_target2d(render_target)
    if not imported:
        raise RuntimeError("ABIVERD_LANDSCAPE_V2_IMPORT " + target)
    import_rows.append({"target": target, "semantic": layer_definition["semantic"], "mask": mask_path})
parent.force_layers_full_update()

hidden_actors = []
hidden_actor_packages = set()
for actor in actors:
    tags = {str(tag) for tag in list(actor.tags)}
    label = actor.get_actor_label()
    hide_reason = ""
    if "VisualGroundOverlay" in tags:
        hide_reason = "LandscapePaintReplacement"
    elif "SunscarTemporaryLabel" in tags:
        hide_reason = "TemporaryLabel"
    elif "SunscarVisualizationGuide" in tags:
        hide_reason = "PlanningGuide"
    elif "SimpleCollisionProxy" in tags or label.startswith("COL_"):
        hide_reason = "CollisionVisualization"
    if not hide_reason:
        continue
    if HIDDEN_TAG in list(actor.tags):
        continue
    changed = False
    actor.modify()
    actor.set_actor_hidden_in_game(True)
    changed = True
    for component in actor.get_components_by_class(unreal.PrimitiveComponent):
        component.modify()
        component.set_visibility(False, True)
        changed = True
    if HIDDEN_TAG not in list(actor.tags):
        actor.tags = list(actor.tags) + [HIDDEN_TAG]
        changed = True
    if changed:
        hidden_actors.append({"label": label, "reason": hide_reason, "package": package_name(actor.get_package())})
        hidden_actor_packages.add(package_name(actor.get_package()))

dirty_before_save = dirty_packages()
allowed_content = {MATERIAL_PATH} | {definition["layer_info"] for definition in LAYERS[1:]}
allowed_map = {package_name(actor.get_package()) for actor in landscapes} | hidden_actor_packages
unexpected = [
    name for name in dirty_before_save
    if name not in allowed_content
    and name not in allowed_map
    and not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")
]
if unexpected:
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_UNEXPECTED_DIRTY " + "|".join(unexpected))

packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_SAVE_FAILED")
remaining = dirty_packages()
if remaining:
    raise RuntimeError("ABIVERD_LANDSCAPE_V2_DIRTY_AFTER " + "|".join(remaining))

payload = {
    "schema_version": 2,
    "status": "landscape_visual_conversion_saved",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "material": MATERIAL_PATH,
    "layers": [
        {"target": definition["target"], "semantic": definition["semantic"], "tile_cm": definition["tile_cm"]}
        for definition in LAYERS
    ],
    "landscape_proxy_count": len(proxies),
    "landscape_component_count": component_count,
    "import_rows": import_rows,
    "created_layer_info_paths": created_layer_info_paths,
    "hidden_actor_count": len(hidden_actors),
    "hidden_reasons": {
        reason: sum(1 for row in hidden_actors if row["reason"] == reason)
        for reason in sorted({row["reason"] for row in hidden_actors})
    },
    "hidden_actors": hidden_actors,
    "saved_packages": dirty_before_save,
    "saved_package_count": len(dirty_before_save),
    "dirty_packages_after": remaining,
    "performance_design": {
        "opaque_landscape": True,
        "world_xy_mapping": True,
        "texture_samples_per_active_layer": 2,
        "shared_macro_texture_samples": 1,
        "layer_usage_pruned_per_component": True,
        "visible_ground_overlay_meshes_removed_from_rendering": True,
        "landscape_nanite_unchanged": True,
        "project_settings_unchanged": True,
    },
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_visual_conversion_v2.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_LANDSCAPE_V2_COMPLETE saved=%d hidden=%d imports=%d report=%s"
    % (len(dirty_before_save), len(hidden_actors), len(import_rows), report_path)
)
print("ABIVERD_LANDSCAPE_V2_COMPLETE", len(dirty_before_save), len(hidden_actors), len(import_rows), report_path)
