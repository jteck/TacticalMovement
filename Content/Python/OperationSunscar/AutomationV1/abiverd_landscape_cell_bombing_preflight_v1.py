"""Read-only preflight for the Abiverd Landscape cell-bombing pass.

This script intentionally makes no asset, actor, package, or configuration
changes.  It inventories the saved Landscape material and the already-owned
City Sample texture-cell-bombing function so the later preview can reuse the
existing graph safely instead of guessing at pins or rebuilding the function.
"""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
FUNCTION_PATH = "/Game/CitySampleVehicles/Material/TextureCellBombing/MF_TextureCellBombing"
ENGINE_FUNCTION_PATH = (
    "/Engine/Functions/Engine_MaterialFunctions01/Texturing/Texture_Bombing"
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


def safe_property(value, property_name):
    try:
        result = value.get_editor_property(property_name)
    except Exception:
        return None
    if result is None:
        return None
    if hasattr(result, "get_path_name"):
        return result.get_path_name()
    try:
        return {
            "x": float(result.get_editor_property("x")),
            "y": float(result.get_editor_property("y")),
            "z": float(result.get_editor_property("z")),
            "w": float(result.get_editor_property("w")),
        }
    except Exception:
        pass
    return str(result)


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""

if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_CELL_BOMBING_PREFLIGHT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_CELL_BOMBING_PREFLIGHT_WRONG_LEVEL " + level_path)

dirty_before = dirty_packages()
if dirty_before:
    raise RuntimeError("ABIVERD_CELL_BOMBING_PREFLIGHT_DIRTY_BEFORE " + "|".join(dirty_before))

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
function = unreal.EditorAssetLibrary.load_asset(FUNCTION_PATH)
engine_function = unreal.EditorAssetLibrary.load_asset(ENGINE_FUNCTION_PATH)
if not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_CELL_BOMBING_PREFLIGHT_MATERIAL")
if not isinstance(function, unreal.MaterialFunctionInterface):
    raise RuntimeError("ABIVERD_CELL_BOMBING_PREFLIGHT_FUNCTION")
if not isinstance(engine_function, unreal.MaterialFunctionInterface):
    raise RuntimeError("ABIVERD_CELL_BOMBING_PREFLIGHT_ENGINE_FUNCTION")

expressions = []
for index, expression in enumerate(unreal.MaterialEditingLibrary.get_material_expressions(material)):
    entry = {
        "index": index,
        "class": expression.get_class().get_name(),
        "name": expression.get_name(),
        "parameter_name": safe_property(expression, "parameter_name"),
        "texture": safe_property(expression, "texture"),
        "material_function": safe_property(expression, "material_function"),
        "inputs": [
            str(name)
            for name in unreal.MaterialEditingLibrary.get_material_expression_input_names(expression)
        ],
        "outputs": [
            str(name)
            for name in unreal.MaterialEditingLibrary.get_material_expression_output_names(expression)
        ],
    }
    expressions.append(entry)

function_inputs = []
function_outputs = []
function_expressions = list(
    unreal.MaterialEditingLibrary.get_material_function_expressions(function)
)
for expression in function_expressions:
    class_name = expression.get_class().get_name()
    row = {
        "class": class_name,
        "name": expression.get_name(),
        "input_name": safe_property(expression, "input_name"),
        "output_name": safe_property(expression, "output_name"),
        "description": safe_property(expression, "description"),
        "input_type": safe_property(expression, "input_type"),
        "preview_value": safe_property(expression, "preview_value"),
        "use_preview_value_as_default": safe_property(
            expression, "use_preview_value_as_default"
        ),
        "sort_priority": safe_property(expression, "sort_priority"),
    }
    if class_name == "MaterialExpressionFunctionInput":
        function_inputs.append(row)
    elif class_name == "MaterialExpressionFunctionOutput":
        function_outputs.append(row)

landscapes = sorted(
    [
        actor
        for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
        if isinstance(actor, unreal.LandscapeProxy)
    ],
    key=lambda actor: actor.get_actor_label(),
)

material_properties = {
    "base_color": unreal.MaterialProperty.MP_BASE_COLOR,
    "normal": unreal.MaterialProperty.MP_NORMAL,
    "roughness": unreal.MaterialProperty.MP_ROUGHNESS,
    "ambient_occlusion": unreal.MaterialProperty.MP_AMBIENT_OCCLUSION,
}
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


for label, material_property in material_properties.items():
    root = unreal.MaterialEditingLibrary.get_material_property_input_node(
        material, material_property
    )
    roots[label] = {
        "name": root.get_name() if root else None,
        "class": root.get_class().get_name() if root else None,
        "output": (
            unreal.MaterialEditingLibrary.get_material_property_input_node_output_name(
                material, material_property
            )
            if root
            else None
        ),
    }
    visit(root)

statistics_value = unreal.MaterialEditingLibrary.get_statistics(material)
statistics = {
    property_name: int(statistics_value.get_editor_property(property_name))
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

function_references = []
for asset_data in unreal.MaterialEditingLibrary.get_materials_referencing_function(function):
    function_references.append(str(asset_data.package_name))


def describe_function(function_asset):
    described_inputs = []
    described_outputs = []
    described_expressions = list(
        unreal.MaterialEditingLibrary.get_material_function_expressions(function_asset)
    )
    for described_expression in described_expressions:
        class_name = described_expression.get_class().get_name()
        row = {
            "class": class_name,
            "name": described_expression.get_name(),
            "input_name": safe_property(described_expression, "input_name"),
            "output_name": safe_property(described_expression, "output_name"),
            "description": safe_property(described_expression, "description"),
            "input_type": safe_property(described_expression, "input_type"),
            "preview_value": safe_property(described_expression, "preview_value"),
            "use_preview_value_as_default": safe_property(
                described_expression, "use_preview_value_as_default"
            ),
            "sort_priority": safe_property(described_expression, "sort_priority"),
        }
        if class_name == "MaterialExpressionFunctionInput":
            described_inputs.append(row)
        elif class_name == "MaterialExpressionFunctionOutput":
            described_outputs.append(row)
    described_references = [
        str(asset_data.package_name)
        for asset_data in unreal.MaterialEditingLibrary.get_materials_referencing_function(
            function_asset
        )
    ]
    return {
        "path": function_asset.get_path_name(),
        "class": function_asset.get_class().get_name(),
        "expression_count": len(described_expressions),
        "inputs": described_inputs,
        "outputs": described_outputs,
        "referencing_materials": sorted(described_references),
    }


engine_function_payload = describe_function(engine_function)

payload = {
    "schema_version": 1,
    "status": "read_only_preflight_complete",
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "material": {
        "path": material.get_path_name(),
        "expression_count": len(expressions),
        "reachable_expression_count": len(reachable),
        "unreachable_expression_count": len(expressions) - len(reachable),
        "roots": roots,
        "reachable_expression_names": sorted(reachable),
        "statistics": statistics,
        "expressions": expressions,
    },
    "existing_function": {
        "path": function.get_path_name(),
        "class": function.get_class().get_name(),
        "expression_count": len(function_expressions),
        "inputs": function_inputs,
        "outputs": function_outputs,
        "referencing_materials": sorted(function_references),
    },
    "chosen_engine_function": engine_function_payload,
    "landscapes": [
        {
            "label": actor.get_actor_label(),
            "package": actor.get_package().get_name(),
            "material": (
                actor.get_editor_property("landscape_material").get_path_name()
                if actor.get_editor_property("landscape_material")
                else ""
            ),
        }
        for actor in landscapes
    ],
    "dirty_packages_before": dirty_before,
    "dirty_packages_after": dirty_packages(),
    "changes_made": False,
}

if payload["dirty_packages_after"]:
    raise RuntimeError(
        "ABIVERD_CELL_BOMBING_PREFLIGHT_DIRTY_AFTER "
        + "|".join(payload["dirty_packages_after"])
    )

report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_cell_bombing_preflight_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_CELL_BOMBING_PREFLIGHT expressions=%d function_inputs=%d report=%s"
    % (len(expressions), len(function_inputs), report_path)
)
print("ABIVERD_CELL_BOMBING_PREFLIGHT", report_path)
