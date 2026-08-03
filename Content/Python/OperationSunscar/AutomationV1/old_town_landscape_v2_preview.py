"""Build an unsaved, performance-oriented UE 5.8 Landscape material preview.

This pass is intentionally reversible. It creates one map-owned opaque master
material, assigns it to the Sunscar Landscape actors, and only *temporarily*
hides the legacy VisualGroundOverlay actors in the editor. It does not save,
delete actors, alter project settings, or enable Landscape Nanite.
"""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development/"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TARGET_FOLDER = "/Game/Maps/Sunscar/Art/Materials/LandscapeV2"
TARGET_NAME = "M_OT_Landscape_Performance"
TARGET_PATH = TARGET_FOLDER + "/" + TARGET_NAME
PASS_TAG = unreal.Name("SunscarLandscapePerformanceV2Preview")
DEBUG_PATH = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar",
    "Reports",
    "old_town_landscape_v2_preview_phase.txt",
)

LAYER_DEFINITIONS = [
    {
        "name": "Sand",
        "blend": unreal.LandscapeLayerBlendType.LB_ALPHA_BLEND,
        "preview": 1.0,
        "tile_cm": 240.0,
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv/Sandstone_Rocky_Ground_vmjjfiv_High_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv/Sandstone_Rocky_Ground_vmjjfiv_High_4K_Normal",
        "orm": "",
        "roughness": 0.94,
        "ao": 0.86,
    },
    {
        "name": "CompactedEarth",
        "blend": unreal.LandscapeLayerBlendType.LB_WEIGHT_BLEND,
        "preview": 0.0,
        "tile_cm": 220.0,
        "base": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Fine_02/Textures/T_Mil_Trench_Ground_Dirt_Fine_02_B",
        "normal": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Fine_02/Textures/T_Mil_Trench_Ground_Dirt_Fine_02_N",
        "orm": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Fine_02/Textures/T_Mil_Trench_Ground_Dirt_Fine_02_ORM",
        "roughness": 0.9,
        "ao": 0.9,
    },
    {
        "name": "Rock",
        "blend": unreal.LandscapeLayerBlendType.LB_WEIGHT_BLEND,
        "preview": 0.0,
        "tile_cm": 260.0,
        "base": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Rough_02/Textures/T_Mil_Trench_Ground_Dirt_Rough_02_B",
        "normal": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Rough_02/Textures/T_Mil_Trench_Ground_Dirt_Rough_02_N",
        "orm": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Rough_02/Textures/T_Mil_Trench_Ground_Dirt_Rough_02_ORM",
        "roughness": 0.92,
        "ao": 0.88,
    },
]


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def mark_phase(value):
    os.makedirs(os.path.dirname(DEBUG_PATH), exist_ok=True)
    with open(DEBUG_PATH, "a", encoding="utf-8") as handle:
        handle.write(str(value) + "\n")


def expression(material, expression_class, x, y):
    value = unreal.MaterialEditingLibrary.create_material_expression(material, expression_class, x, y)
    if value is None:
        raise RuntimeError("SUNSCAR_LANDSCAPE_V2_EXPRESSION_CREATE_FAILED " + expression_class.__name__)
    return value


def pin_names(value, output=False):
    getter = (
        unreal.MaterialEditingLibrary.get_material_expression_output_names
        if output
        else unreal.MaterialEditingLibrary.get_material_expression_input_names
    )
    return [str(name) for name in getter(value)]


def find_pin(value, preferred, output=False):
    names = pin_names(value, output=output)
    lowered = {name.lower(): name for name in names}
    for candidate in preferred:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    for name in names:
        compact = name.lower().replace(" ", "")
        for candidate in preferred:
            if candidate.lower().replace(" ", "") in compact:
                return name
    raise RuntimeError(
        "SUNSCAR_LANDSCAPE_V2_PIN_MISSING preferred=%s names=%s"
        % ("|".join(preferred), "|".join(names))
    )


def connect(source, destination, input_name, output_name=""):
    input_names = pin_names(destination)
    resolved_input = input_name
    if resolved_input not in input_names:
        landscape_layer_pin = "Layer " + input_name
        if landscape_layer_pin in input_names:
            resolved_input = landscape_layer_pin
        else:
            aliases = {
                "Coordinates": ("UVs", "Coordinates"),
                "Input": ("Input",),
            }
            for candidate in aliases.get(input_name, ()):
                if candidate in input_names:
                    resolved_input = candidate
                    break
            else:
                if len(input_names) == 1:
                    resolved_input = input_names[0]
    output_names = pin_names(source, output=True)
    resolved_output = output_name
    if not unreal.MaterialEditingLibrary.connect_material_expressions(
        source, resolved_output, destination, resolved_input
    ):
        raise RuntimeError(
            "SUNSCAR_LANDSCAPE_V2_CONNECT_FAILED input=%s resolved_input=%s output=%s resolved_output=%s input_names=%s output_names=%s"
            % (
                input_name,
                resolved_input,
                output_name,
                resolved_output,
                "|".join(input_names),
                "|".join(output_names),
            )
        )


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/")
if os.path.exists(DEBUG_PATH):
    os.remove(DEBUG_PATH)
mark_phase("START")
if not project_directory.endswith("/"):
    project_directory += "/"
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("SUNSCAR_UNSAFE_PROJECT_DIRECTORY " + project_directory)

world = unreal.UnrealEditorSubsystem().get_editor_world()
level_path = world.get_path_name().split(":", 1)[0].split(".", 1)[0]
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("SUNSCAR_UNSAFE_LEVEL " + level_path)

dirty_before = sorted(
    package_name(package)
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
allowed_preexisting_dirty = {
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/D/V0/DDA88QQA4MM015F4V2G4MJ",
    TARGET_PATH,
}
if set(dirty_before) - allowed_preexisting_dirty:
    raise RuntimeError(
        "SUNSCAR_LANDSCAPE_V2_REFUSED_PREEXISTING_DIRTY " + "|".join(dirty_before)
    )

if unreal.EditorAssetLibrary.does_asset_exist(TARGET_PATH):
    if TARGET_PATH not in dirty_before:
        raise RuntimeError("SUNSCAR_LANDSCAPE_V2_REFUSED_SAVED_EXISTING_ASSET " + TARGET_PATH)
    material = unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
    if material is None or not isinstance(material, unreal.Material):
        raise RuntimeError("SUNSCAR_LANDSCAPE_V2_FAILED_PREVIEW_SHELL_LOAD " + TARGET_PATH)
    unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
else:
    material = None

loaded_assets = {}
for layer in LAYER_DEFINITIONS:
    for key in ("base", "normal", "orm"):
        path = layer[key]
        if not path:
            continue
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None:
            raise RuntimeError("SUNSCAR_LANDSCAPE_V2_MISSING_SOURCE " + path)
        loaded_assets[path] = asset

actors = list(unreal.EditorActorSubsystem().get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
if not any(actor.get_actor_label() == "Landscape_Sunscar" for actor in landscapes):
    raise RuntimeError("SUNSCAR_LANDSCAPE_V2_REFUSED_PARENT_MISSING")

overlays = sorted(
    [actor for actor in actors if "VisualGroundOverlay" in [str(tag) for tag in actor.tags]],
    key=lambda actor: actor.get_actor_label(),
)
if len(overlays) != 288:
    raise RuntimeError("SUNSCAR_LANDSCAPE_V2_REFUSED_OVERLAY_COUNT %d" % len(overlays))

unreal.EditorAssetLibrary.make_directory(TARGET_FOLDER)
if material is None:
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        TARGET_NAME, TARGET_FOLDER, unreal.Material, unreal.MaterialFactoryNew()
    )
if material is None:
    raise RuntimeError("SUNSCAR_LANDSCAPE_V2_CREATE_FAILED")
material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
material.set_editor_property("two_sided", False)
material.set_editor_property("tangent_space_normal", True)

world_position = expression(material, unreal.MaterialExpressionWorldPosition, -1800, -100)
xy = expression(material, unreal.MaterialExpressionComponentMask, -1600, -100)
xy.set_editor_properties({"r": True, "g": True, "b": False, "a": False})
connect(world_position, xy, "Input")

layer_sources = {}

for index, layer in enumerate(LAYER_DEFINITIONS):
    y = -900 + index * 560
    tile = expression(material, unreal.MaterialExpressionScalarParameter, -1600, y + 160)
    tile.set_editor_property("parameter_name", unreal.Name(layer["name"] + "_TileCm"))
    tile.set_editor_property("default_value", float(layer["tile_cm"]))
    uv = expression(material, unreal.MaterialExpressionDivide, -1380, y)
    connect(xy, uv, "A")
    connect(tile, uv, "B")

    base = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1120, y - 160)
    base.set_editor_property("parameter_name", unreal.Name(layer["name"] + "_BaseColor"))
    base.set_editor_property("texture", loaded_assets[layer["base"]])
    connect(uv, base, "Coordinates")

    # One additional low-frequency color sample breaks obvious repetition on
    # the always-present sand base. Normals remain single-sampled, and painted
    # Landscape layers still compile out per component when unused.
    if layer["name"] == "Sand":
        macro_tile = expression(material, unreal.MaterialExpressionScalarParameter, -1600, y - 300)
        macro_tile.set_editor_property("parameter_name", unreal.Name("Sand_MacroTileCm"))
        macro_tile.set_editor_property("default_value", 2400.0)
        macro_uv = expression(material, unreal.MaterialExpressionDivide, -1380, y - 300)
        connect(xy, macro_uv, "A")
        connect(macro_tile, macro_uv, "B")
        macro_base = expression(
            material, unreal.MaterialExpressionTextureSampleParameter2D, -1120, y - 380
        )
        macro_base.set_editor_property("parameter_name", unreal.Name("Sand_MacroBaseColor"))
        macro_base.set_editor_property("texture", loaded_assets[layer["base"]])
        connect(macro_uv, macro_base, "Coordinates")
        macro_alpha = expression(material, unreal.MaterialExpressionConstant, -700, y - 300)
        macro_alpha.set_editor_property("r", 0.16)
        macro_blend = expression(material, unreal.MaterialExpressionLinearInterpolate, -480, y - 180)
        connect(base, macro_blend, "A")
        connect(macro_base, macro_blend, "B")
        connect(macro_alpha, macro_blend, "Alpha")
        base = macro_blend

    normal = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1120, y + 40)
    normal.set_editor_property("parameter_name", unreal.Name(layer["name"] + "_Normal"))
    normal.set_editor_property("texture", loaded_assets[layer["normal"]])
    normal.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    connect(uv, normal, "Coordinates")

    roughness_source = expression(material, unreal.MaterialExpressionConstant, -700, y + 220)
    roughness_source.set_editor_property("r", float(layer["roughness"]))
    ao_source = expression(material, unreal.MaterialExpressionConstant, -700, y + 330)
    ao_source.set_editor_property("r", float(layer["ao"]))

    if layer["orm"]:
        orm = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1120, y + 240)
        orm.set_editor_property("parameter_name", unreal.Name(layer["name"] + "_ORM"))
        orm.set_editor_property("texture", loaded_assets[layer["orm"]])
        orm.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
        connect(uv, orm, "Coordinates")
        roughness_mask = expression(material, unreal.MaterialExpressionComponentMask, -850, y + 230)
        roughness_mask.set_editor_properties({"r": False, "g": True, "b": False, "a": False})
        connect(orm, roughness_mask, "Input")
        ao_mask = expression(material, unreal.MaterialExpressionComponentMask, -850, y + 350)
        ao_mask.set_editor_properties({"r": True, "g": False, "b": False, "a": False})
        connect(orm, ao_mask, "Input")
        roughness_source = roughness_mask
        ao_source = ao_mask

    layer_sources[layer["name"]] = {
        "base_color": base,
        "normal": normal,
        "roughness": roughness_source,
        "ambient_occlusion": ao_source,
    }


def build_weight_chain(channel, x, y):
    current = layer_sources["Sand"][channel]
    for layer_index, layer_name in enumerate(("CompactedEarth", "Rock")):
        layer_weight = expression(
            material,
            unreal.MaterialExpressionLandscapeLayerWeight,
            x + layer_index * 260,
            y,
        )
        layer_weight.set_editor_properties(
            {
                "parameter_name": unreal.Name(layer_name),
                "preview_weight": 0.0,
                "const_base": unreal.Vector(0.0, 0.0, 0.0),
            }
        )
        connect(current, layer_weight, "Base")
        connect(layer_sources[layer_name][channel], layer_weight, "Layer")
        current = layer_weight
    return current


material_outputs = (
    (build_weight_chain("base_color", 300, -600), unreal.MaterialProperty.MP_BASE_COLOR),
    (build_weight_chain("normal", 300, 0), unreal.MaterialProperty.MP_NORMAL),
    (build_weight_chain("roughness", 300, 500), unreal.MaterialProperty.MP_ROUGHNESS),
    (
        build_weight_chain("ambient_occlusion", 300, 850),
        unreal.MaterialProperty.MP_AMBIENT_OCCLUSION,
    ),
)
for material_output, material_property in material_outputs:
    if not unreal.MaterialEditingLibrary.connect_material_property(
        material_output, "", material_property
    ):
        raise RuntimeError("SUNSCAR_LANDSCAPE_V2_OUTPUT_CONNECT_FAILED")

compiler_errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
mark_phase("RECOMPILED errors=" + "|".join(str(error) for error in compiler_errors))
if compiler_errors:
    raise RuntimeError("SUNSCAR_LANDSCAPE_V2_COMPILER_ERRORS " + "|".join(compiler_errors))

landscape_records = []
parent_landscape = next(
    actor for actor in landscapes if actor.get_actor_label() == "Landscape_Sunscar"
)
mark_phase("ASSIGNING_PARENT_LANDSCAPE")
parent_landscape.modify()
parent_landscape.set_editor_property("landscape_material", material)
if PASS_TAG not in list(parent_landscape.tags):
    parent_landscape.tags = list(parent_landscape.tags) + [PASS_TAG]
for actor in landscapes:
    effective_material = actor.get_editor_property("landscape_material")
    landscape_records.append(
        {
            "label": actor.get_actor_label(),
            "package": package_name(actor.get_package()),
            "material": effective_material.get_path_name() if effective_material else "",
            "modified_by_preview": actor == parent_landscape,
        }
    )
mark_phase("LANDSCAPES_ASSIGNED count=%d" % len(landscape_records))

for actor in overlays:
    actor.set_is_temporarily_hidden_in_editor(True)
mark_phase("OVERLAYS_HIDDEN count=%d" % len(overlays))

dirty_content_after = sorted(
    package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_map_after = sorted(
    package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)

payload = {
    "schema_version": 1,
    "status": "unsaved_reversible_preview_ready",
    "project_directory": project_directory,
    "level": level_path,
    "material_path": TARGET_PATH,
    "material_mode": "opaque_base_sand_plus_two_weight_layers_world_xy",
    "macro_variation": {
        "sand_macro_tile_cm": 2400.0,
        "sand_macro_blend": 0.16,
        "additional_base_color_samples": 1,
    },
    "layers": LAYER_DEFINITIONS,
    "landscape_actor_count": len(landscapes),
    "landscape_records": landscape_records,
    "legacy_overlays_temporarily_hidden": len(overlays),
    "landscape_nanite_changed": False,
    "project_settings_changed": False,
    "actors_deleted": 0,
    "dirty_before": dirty_before,
    "dirty_content_after": dirty_content_after,
    "dirty_map_after": dirty_map_after,
    "changes_saved": False,
}
report_directory = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_directory, exist_ok=True)
report_path = os.path.join(report_directory, "old_town_landscape_v2_preview.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, default=str)
    handle.write("\n")
mark_phase("REPORT_WRITTEN " + report_path)

unreal.log(
    "SUNSCAR_LANDSCAPE_V2_PREVIEW landscapes=%d overlays_hidden=%d report=%s"
    % (len(landscapes), len(overlays), report_path)
)
print("SUNSCAR_LANDSCAPE_V2_PREVIEW", len(landscapes), len(overlays), report_path)
