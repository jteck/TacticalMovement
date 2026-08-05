"""Dry-run/apply the performance-oriented Abiverd Landscape material upgrade."""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
TARGET_FOLDER = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3"
TARGET_NAME = "M_OT_Landscape_Abiverd"
TARGET_PATH = TARGET_FOLDER + "/" + TARGET_NAME
PASS_TAG = unreal.Name("SunscarLandscapeAbiverdV3")

LAYERS = [
    {
        "name": "Sand",
        "tile_cm": 240.0,
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv/Sandstone_Rocky_Ground_vmjjfiv_High_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv/Sandstone_Rocky_Ground_vmjjfiv_High_4K_Normal",
        "roughness": 0.94,
        "ao": 0.86,
    },
    {
        "name": "CompactedEarth",
        "tile_cm": 230.0,
        "base": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/DryTrampledSoil/Dry_Trampled_Soil_wcivbfb_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/DryTrampledSoil/Dry_Trampled_Soil_wcivbfb_4K_Normal",
        "roughness": 0.91,
        "ao": 0.88,
    },
    {
        "name": "Rock",
        "tile_cm": 260.0,
        "base": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Rough_02/Textures/T_Mil_Trench_Ground_Dirt_Rough_02_B",
        "normal": "/Game/MilitaryTrench/Assets/Surfaces/Mil_Trench_Ground_Dirt_Rough_02/Textures/T_Mil_Trench_Ground_Dirt_Rough_02_N",
        "roughness": 0.92,
        "ao": 0.88,
    },
    {
        # UE 5.8's reusable non-weight Layer Info carries the internal target
        # layer name "Grass".  The layer's design role remains the Abiverd
        # meadow ground cover.
        "name": "Grass",
        "semantic": "Meadow",
        "tile_cm": 210.0,
        "base": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/WildGrassGround/Wild_Grass_xbreagf_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Heritage/Surfaces/WildGrassGround/Wild_Grass_xbreagf_4K_Normal",
        "roughness": 0.93,
        "ao": 0.90,
    },
]


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
    value = unreal.MaterialEditingLibrary.create_material_expression(material, expression_class, x, y)
    if value is None:
        raise RuntimeError("ABIVERD_MEADOW_MATERIAL_EXPRESSION " + expression_class.__name__)
    return value


def pin_names(value, output=False):
    getter = (
        unreal.MaterialEditingLibrary.get_material_expression_output_names
        if output
        else unreal.MaterialEditingLibrary.get_material_expression_input_names
    )
    return [str(name) for name in getter(value)]


def connect(source, destination, input_name, output_name=""):
    input_names = pin_names(destination)
    resolved_input = input_name
    if resolved_input not in input_names:
        alias = "Layer " + input_name
        if alias in input_names:
            resolved_input = alias
        elif input_name == "Coordinates" and "UVs" in input_names:
            resolved_input = "UVs"
        elif len(input_names) == 1:
            resolved_input = input_names[0]
    if not unreal.MaterialEditingLibrary.connect_material_expressions(
        source, output_name, destination, resolved_input
    ):
        raise RuntimeError(
            "ABIVERD_MEADOW_MATERIAL_CONNECT input=%s resolved=%s inputs=%s"
            % (input_name, resolved_input, "|".join(input_names))
        )


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_MEADOW_MATERIAL_CONTEXT")
if dirty_packages():
    raise RuntimeError("ABIVERD_MEADOW_MATERIAL_DIRTY_BEFORE " + "|".join(dirty_packages()))

sources = {}
for layer in LAYERS:
    for key in ("base", "normal"):
        path = layer[key]
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(asset, unreal.Texture2D):
            raise RuntimeError("ABIVERD_MEADOW_MATERIAL_SOURCE " + path)
        sources[path] = asset

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
parents = [actor for actor in landscapes if actor.get_actor_label() == "Landscape_Sunscar"]
if len(parents) != 1 or len(landscapes) != 3:
    raise RuntimeError("ABIVERD_MEADOW_MATERIAL_LANDSCAPE_SCOPE")
if unreal.EditorAssetLibrary.does_asset_exist(TARGET_PATH):
    raise RuntimeError("ABIVERD_MEADOW_MATERIAL_EXISTING_TARGET " + TARGET_PATH)

payload = {
    "schema_version": 1,
    "status": "dry_run_complete",
    "apply_changes": APPLY_CHANGES,
    "level": level_path,
    "target_material": TARGET_PATH,
    "layers": LAYERS,
    "landscape_actor_count": len(landscapes),
    "performance_design": {
        "opaque": True,
        "world_xy_mapping": True,
        "sand_macro_sample": True,
        "samples_per_layer": {"Sand": 3, "CompactedEarth": 2, "Rock": 2, "Meadow": 2},
        "estimated_max_texture_samples": 9,
        "meadow_is_non_weight_blended_overlay": True,
        "landscape_nanite_changed": False,
        "project_settings_changed": False,
    },
    "dirty_packages_after": [],
    "changes_saved": False,
}

if APPLY_CHANGES:
    unreal.EditorAssetLibrary.make_directory(TARGET_FOLDER)
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        TARGET_NAME, TARGET_FOLDER, unreal.Material, unreal.MaterialFactoryNew()
    )
    if not isinstance(material, unreal.Material):
        raise RuntimeError("ABIVERD_MEADOW_MATERIAL_CREATE")
    material.set_editor_properties(
        {"blend_mode": unreal.BlendMode.BLEND_OPAQUE, "two_sided": False, "tangent_space_normal": True}
    )

    world_position = expression(material, unreal.MaterialExpressionWorldPosition, -1850, -100)
    xy = expression(material, unreal.MaterialExpressionComponentMask, -1660, -100)
    xy.set_editor_properties({"r": True, "g": True, "b": False, "a": False})
    connect(world_position, xy, "Input")

    layer_sources = {}
    for index, layer in enumerate(LAYERS):
        y = -1000 + index * 560
        tile = expression(material, unreal.MaterialExpressionScalarParameter, -1630, y + 150)
        tile.set_editor_property("parameter_name", unreal.Name(layer["name"] + "_TileCm"))
        tile.set_editor_property("default_value", float(layer["tile_cm"]))
        uv = expression(material, unreal.MaterialExpressionDivide, -1410, y)
        connect(xy, uv, "A")
        connect(tile, uv, "B")

        base = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1160, y - 130)
        base.set_editor_property("parameter_name", unreal.Name(layer["name"] + "_BaseColor"))
        base.set_editor_property("texture", sources[layer["base"]])
        connect(uv, base, "Coordinates")

        if layer["name"] == "Sand":
            macro_tile = expression(material, unreal.MaterialExpressionScalarParameter, -1630, y - 300)
            macro_tile.set_editor_property("parameter_name", unreal.Name("Sand_MacroTileCm"))
            macro_tile.set_editor_property("default_value", 2400.0)
            macro_uv = expression(material, unreal.MaterialExpressionDivide, -1410, y - 300)
            connect(xy, macro_uv, "A")
            connect(macro_tile, macro_uv, "B")
            macro = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1160, y - 360)
            macro.set_editor_property("parameter_name", unreal.Name("Sand_MacroBaseColor"))
            macro.set_editor_property("texture", sources[layer["base"]])
            connect(macro_uv, macro, "Coordinates")
            alpha = expression(material, unreal.MaterialExpressionConstant, -850, y - 280)
            alpha.set_editor_property("r", 0.14)
            blend = expression(material, unreal.MaterialExpressionLinearInterpolate, -620, y - 180)
            connect(base, blend, "A")
            connect(macro, blend, "B")
            connect(alpha, blend, "Alpha")
            base = blend

        normal = expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1160, y + 70)
        normal.set_editor_property("parameter_name", unreal.Name(layer["name"] + "_Normal"))
        normal.set_editor_property("texture", sources[layer["normal"]])
        normal.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        connect(uv, normal, "Coordinates")

        roughness = expression(material, unreal.MaterialExpressionConstant, -730, y + 240)
        roughness.set_editor_property("r", float(layer["roughness"]))
        ao = expression(material, unreal.MaterialExpressionConstant, -730, y + 340)
        ao.set_editor_property("r", float(layer["ao"]))
        layer_sources[layer["name"]] = {
            "base_color": base,
            "normal": normal,
            "roughness": roughness,
            "ambient_occlusion": ao,
        }

    def build_chain(channel, x, y):
        current = layer_sources["Sand"][channel]
        for layer_index, layer_name in enumerate(("CompactedEarth", "Rock", "Grass")):
            weight = expression(material, unreal.MaterialExpressionLandscapeLayerWeight, x + layer_index * 260, y)
            weight.set_editor_properties(
                {
                    "parameter_name": unreal.Name(layer_name),
                    "preview_weight": 0.0,
                    "const_base": unreal.Vector(0.0, 0.0, 0.0),
                }
            )
            connect(current, weight, "Base")
            connect(layer_sources[layer_name][channel], weight, "Layer")
            current = weight
        return current

    outputs = (
        (build_chain("base_color", 350, -650), unreal.MaterialProperty.MP_BASE_COLOR),
        (build_chain("normal", 350, -50), unreal.MaterialProperty.MP_NORMAL),
        (build_chain("roughness", 350, 500), unreal.MaterialProperty.MP_ROUGHNESS),
        (build_chain("ambient_occlusion", 350, 900), unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),
    )
    for node, material_property in outputs:
        if not unreal.MaterialEditingLibrary.connect_material_property(node, "", material_property):
            raise RuntimeError("ABIVERD_MEADOW_MATERIAL_OUTPUT")
    compiler_errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
    if compiler_errors:
        raise RuntimeError("ABIVERD_MEADOW_MATERIAL_COMPILE " + "|".join(str(item) for item in compiler_errors))

    parent = parents[0]
    parent.modify()
    parent.set_editor_property("landscape_material", material)
    if PASS_TAG not in list(parent.tags):
        parent.tags = list(parent.tags) + [PASS_TAG]
    parent.force_layers_full_update()
    dirty_after = dirty_packages()
    allowed = {
        TARGET_PATH,
        parent.get_package().get_name(),
    }
    # Changing the shared Landscape material legitimately synchronizes each
    # loaded LandscapeStreamingProxy.  Restrict the allowance to the packages
    # of the Landscape actors discovered above; do not broadly allow external
    # actor packages.
    allowed.update(actor.get_package().get_name() for actor in landscapes)
    unexpected = [
        name for name in dirty_after
        if name not in allowed and not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")
    ]
    if unexpected:
        raise RuntimeError("ABIVERD_MEADOW_MATERIAL_DIRTY_SCOPE " + "|".join(unexpected))
    payload.update(
        {
            "status": "unsaved_meadow_material_preview_ready",
            "material_expression_count": len(unreal.MaterialEditingLibrary.get_material_expressions(material)),
            "landscape_materials": {
                actor.get_actor_label(): (
                    actor.get_editor_property("landscape_material").get_path_name()
                    if actor.get_editor_property("landscape_material") else ""
                )
                for actor in landscapes
            },
            "target_layers_after": [str(name) for name in parent.get_target_layer_names()],
            "dirty_packages_after": dirty_after,
        }
    )

report_name = (
    "abiverd_landscape_meadow_material_apply_v1.json"
    if APPLY_CHANGES else "abiverd_landscape_meadow_material_dry_run_v1.json"
)
report_path = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", report_name)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_MEADOW_MATERIAL %s %s" % (payload["status"], report_path))
print("ABIVERD_MEADOW_MATERIAL", report_path)
