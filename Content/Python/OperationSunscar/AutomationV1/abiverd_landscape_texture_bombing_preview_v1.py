"""Build one bounded, unsaved UE 5.8 Texture_Bombing Landscape preview.

The pass reuses Epic's engine-supplied Texture_Bombing material function on
only the dominant Sand base-color path.  It preserves the existing world-space
tile scale, normals, layer masks and shared macro variation.  It also removes
unreachable legacy expressions.  Nothing is saved by this script.
"""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
FUNCTION_PATH = "/Engine/Functions/Engine_MaterialFunctions01/Texturing/Texture_Bombing"
REPORT_NAME = "abiverd_landscape_texture_bombing_preview_v1.json"
MAXIMUMS = {
    "num_pixel_shader_instructions": 240,
    "num_vertex_shader_instructions": 140,
    "num_pixel_texture_samples": 9,
    "num_samplers": 5,
}


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


def statistics(material):
    value = unreal.MaterialEditingLibrary.get_statistics(material)
    return {
        property_name: int(value.get_editor_property(property_name))
        for property_name in (
            "num_vertex_shader_instructions",
            "num_pixel_shader_instructions",
            "num_samplers",
            "num_vertex_texture_samples",
            "num_pixel_texture_samples",
            "num_virtual_texture_samples",
            "num_uv_scalars",
            "num_interpolator_scalars",
        )
    }


def roots_and_reachable(material):
    roots = {}
    reachable = set()

    def visit(expression):
        if expression is None or expression.get_name() in reachable:
            return
        reachable.add(expression.get_name())
        for input_expression in unreal.MaterialEditingLibrary.get_inputs_for_material_expression(
            material, expression
        ):
            visit(input_expression)

    for label, material_property in {
        "base_color": unreal.MaterialProperty.MP_BASE_COLOR,
        "normal": unreal.MaterialProperty.MP_NORMAL,
        "roughness": unreal.MaterialProperty.MP_ROUGHNESS,
        "ambient_occlusion": unreal.MaterialProperty.MP_AMBIENT_OCCLUSION,
    }.items():
        root = unreal.MaterialEditingLibrary.get_material_property_input_node(
            material, material_property
        )
        roots[label] = root.get_name() if root else None
        visit(root)
    return roots, reachable


def pin_names(expression, output=False):
    getter = (
        unreal.MaterialEditingLibrary.get_material_expression_output_names
        if output
        else unreal.MaterialEditingLibrary.get_material_expression_input_names
    )
    return [str(name) for name in getter(expression)]


def connect(source, source_output, destination, destination_input):
    available = pin_names(destination)
    if destination_input not in available:
        raise RuntimeError(
            "ABIVERD_TEXTURE_BOMBING_PIN expected=%s available=%s"
            % (destination_input, "|".join(available))
        )
    if not unreal.MaterialEditingLibrary.connect_material_expressions(
        source, source_output, destination, destination_input
    ):
        raise RuntimeError("ABIVERD_TEXTURE_BOMBING_CONNECT " + destination_input)


def write_report(payload):
    report_path = os.path.join(
        unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", REPORT_NAME
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return report_path


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_TEXTURE_BOMBING_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_TEXTURE_BOMBING_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_TEXTURE_BOMBING_DIRTY_BEFORE " + "|".join(dirty_packages()))

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
function = unreal.EditorAssetLibrary.load_asset(FUNCTION_PATH)
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_TEXTURE_BOMBING_MATERIAL")
if not isinstance(function, unreal.MaterialFunctionInterface):
    raise RuntimeError("ABIVERD_TEXTURE_BOMBING_FUNCTION")

expressions_before = list(unreal.MaterialEditingLibrary.get_material_expressions(material))
roots_before, reachable_before = roots_and_reachable(material)
baseline_statistics = statistics(material)

reachable_expressions = [
    expression for expression in expressions_before if expression.get_name() in reachable_before
]
sand_base_nodes = []
for expression in reachable_expressions:
    if not isinstance(expression, unreal.MaterialExpressionTextureSampleParameter2D):
        continue
    try:
        parameter_name = str(expression.get_editor_property("parameter_name"))
    except Exception:
        parameter_name = ""
    if parameter_name == "Sand_BaseColor":
        sand_base_nodes.append(expression)
if len(sand_base_nodes) != 1:
    raise RuntimeError("ABIVERD_TEXTURE_BOMBING_SAND_BASE count=%d" % len(sand_base_nodes))
sand_base = sand_base_nodes[0]
sand_texture = sand_base.get_editor_property("texture")
if not isinstance(sand_texture, unreal.Texture2D):
    raise RuntimeError("ABIVERD_TEXTURE_BOMBING_SAND_TEXTURE")

sand_uv_inputs = [
    item
    for item in unreal.MaterialEditingLibrary.get_inputs_for_material_expression(material, sand_base)
    if item is not None
]
if len(sand_uv_inputs) != 1 or not isinstance(
    sand_uv_inputs[0], unreal.MaterialExpressionDivide
):
    raise RuntimeError(
        "ABIVERD_TEXTURE_BOMBING_SAND_UV count=%d classes=%s"
        % (len(sand_uv_inputs), "|".join(item.get_class().get_name() for item in sand_uv_inputs))
    )
sand_uv = sand_uv_inputs[0]

tinted_candidates = []
for expression in reachable_expressions:
    if not isinstance(expression, unreal.MaterialExpressionMultiply):
        continue
    inputs = [
        item
        for item in unreal.MaterialEditingLibrary.get_inputs_for_material_expression(
            material, expression
        )
        if item is not None
    ]
    if sand_base in inputs:
        tinted_candidates.append(expression)
if len(tinted_candidates) != 1:
    raise RuntimeError("ABIVERD_TEXTURE_BOMBING_TINTED count=%d" % len(tinted_candidates))
sand_tinted = tinted_candidates[0]

material_package = material.get_package()
payload = {
    "schema_version": 1,
    "status": "preview_started",
    "changes_saved": False,
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "material": material.get_path_name(),
    "function": function.get_path_name(),
    "scope": "Sand base color only; normal, roughness, AO, masks and macro variation preserved",
    "baseline": {
        "expression_count": len(expressions_before),
        "reachable_expression_count": len(reachable_before),
        "unreachable_expression_count": len(expressions_before) - len(reachable_before),
        "roots": roots_before,
        "statistics": baseline_statistics,
    },
    "limits": MAXIMUMS,
}

try:
    material.modify()

    texture_object = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionTextureObjectParameter, -1240, -1810
    )
    texture_object.set_editor_property("parameter_name", unreal.Name("Sand_BaseColor"))
    texture_object.set_editor_property("texture", sand_texture)
    texture_object.set_editor_property(
        "sampler_type",
        unreal.MaterialSamplerType.SAMPLERTYPE_VIRTUAL_COLOR
        if bool(sand_texture.get_editor_property("virtual_texture_streaming"))
        else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
    )

    function_call = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionMaterialFunctionCall, -870, -1660
    )
    function_call.set_editor_property("material_function", function)

    tiling = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, -1240, -1500
    )
    tiling.set_editor_property("parameter_name", unreal.Name("SandBomb_Tiling"))
    tiling.set_editor_property("default_value", 1.0)

    offset = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, -1240, -1400
    )
    offset.set_editor_property("parameter_name", unreal.Name("SandBomb_Offset"))
    offset.set_editor_property("default_value", 0.75)

    connect(texture_object, "", function_call, "Texture Object")
    connect(sand_uv, "", function_call, "UVs")
    connect(tiling, "", function_call, "Tiling")
    connect(offset, "", function_call, "Offset")

    if not unreal.MaterialEditingLibrary.disconnect_material_expressions(sand_tinted, "A"):
        raise RuntimeError("ABIVERD_TEXTURE_BOMBING_DISCONNECT_SAND")
    connect(function_call, "Result", sand_tinted, "A")

    unreal.MaterialEditingLibrary.delete_unused_expressions(material)
    compiler_errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
    if compiler_errors:
        raise RuntimeError(
            "ABIVERD_TEXTURE_BOMBING_COMPILE " + "|".join(str(item) for item in compiler_errors)
        )

    expressions_after = list(unreal.MaterialEditingLibrary.get_material_expressions(material))
    roots_after, reachable_after = roots_and_reachable(material)
    after_statistics = statistics(material)
    exceeded = {
        key: {"actual": after_statistics[key], "maximum": maximum}
        for key, maximum in MAXIMUMS.items()
        if after_statistics[key] > maximum
    }
    if exceeded:
        raise RuntimeError("ABIVERD_TEXTURE_BOMBING_COST " + json.dumps(exceeded, sort_keys=True))

    function_calls = [
        expression
        for expression in expressions_after
        if isinstance(expression, unreal.MaterialExpressionMaterialFunctionCall)
        and expression.get_editor_property("material_function") == function
    ]
    if len(function_calls) != 1:
        raise RuntimeError("ABIVERD_TEXTURE_BOMBING_CALL_COUNT %d" % len(function_calls))

    dirty_after = dirty_packages()
    if dirty_after != [MATERIAL_PATH]:
        raise RuntimeError("ABIVERD_TEXTURE_BOMBING_DIRTY_SCOPE " + "|".join(dirty_after))

    payload.update(
        {
            "status": "unsaved_preview_ready",
            "preview": {
                "expression_count": len(expressions_after),
                "reachable_expression_count": len(reachable_after),
                "unreachable_expression_count": len(expressions_after) - len(reachable_after),
                "roots": roots_after,
                "statistics": after_statistics,
                "statistics_delta": {
                    key: after_statistics[key] - baseline_statistics[key]
                    for key in after_statistics
                },
                "texture": sand_texture.get_path_name(),
                "tile_scale_preserved": True,
                "tiling_multiplier": 1.0,
                "offset_strength": 0.75,
                "height_lerp": False,
                "normal_bombing": False,
                "function_call_inputs": pin_names(function_call),
                "function_call_outputs": pin_names(function_call, output=True),
            },
            "dirty_packages_after": dirty_after,
        }
    )
    report_path = write_report(payload)
    unreal.log(
        "ABIVERD_TEXTURE_BOMBING_PREVIEW_READY expressions=%d pixel_instructions=%d samples=%d report=%s"
        % (
            len(expressions_after),
            after_statistics["num_pixel_shader_instructions"],
            after_statistics["num_pixel_texture_samples"],
            report_path,
        )
    )
    print("ABIVERD_TEXTURE_BOMBING_PREVIEW_READY", report_path)
except Exception as error:
    payload.update({"status": "preview_rejected_and_rolled_back", "error": str(error)})
    reload_ok, reload_error = unreal.EditorLoadingAndSavingUtils.reload_packages(
        [material_package], unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE
    )
    payload["rollback"] = {
        "reload_ok": bool(reload_ok),
        "reload_error": str(reload_error),
        "dirty_packages_after": dirty_packages(),
    }
    report_path = write_report(payload)
    unreal.log_error(
        "ABIVERD_TEXTURE_BOMBING_PREVIEW_REJECTED error=%s report=%s" % (error, report_path)
    )
    raise
