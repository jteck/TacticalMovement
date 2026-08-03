"""Create and apply an unsaved, world-aligned Quixel facade prototype at SS_017."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


MASTER_FOLDER = "/Game/Maps/Sunscar/Art/Materials/Facade"
MASTER_NAME = "M_OT_WorldAlignedFacade"
MASTER_PATH = MASTER_FOLDER + "/" + MASTER_NAME
INSTANCE_NAME = "MI_OT_FlakedPaint_WorldAligned"
INSTANCE_PATH = MASTER_FOLDER + "/" + INSTANCE_NAME
BASE_COLOR_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_017_vhqkeff/"
    "Flaked_Paint_Wall_vhqkeff_4K_BaseColor"
)
NORMAL_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_017_vhqkeff/"
    "Flaked_Paint_Wall_vhqkeff_4K_Normal"
)
WORLD_ALIGNED_TEXTURE_PATH = (
    "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture"
)
WORLD_ALIGNED_NORMAL_PATH = (
    "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal"
)
PASS_TAG = unreal.Name("SunscarWorldAlignedFacadePrototypeV1")
EXPECTED_LABELS = [
    "Core_SS_017_F1_E_Left",
    "Core_SS_017_F1_E_Lintel",
    "Core_SS_017_F1_E_Right",
    "Core_SS_017_F1_N_Left",
    "Core_SS_017_F1_N_Lintel",
    "Core_SS_017_F1_N_Right",
    "Core_SS_017_F1_S_Wall",
    "Core_SS_017_F1_W_Left",
    "Core_SS_017_F1_W_Lintel",
    "Core_SS_017_F1_W_Right",
]
ALLOWED_SOURCE_PREFIXES = (
    "/Game/LevelPrototyping/Materials/",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_WarmStucco.",
    "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_Quixel.",
    INSTANCE_PATH + "." + INSTANCE_NAME,
)


def _pin_names(expression, output=False):
    if output:
        values = unreal.MaterialEditingLibrary.get_material_expression_output_names(expression)
    else:
        values = unreal.MaterialEditingLibrary.get_material_expression_input_names(expression)
    return [str(value) for value in values]


def _find_pin(names, preferred):
    lowered = {name.lower(): name for name in names}
    for candidate in preferred:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    for name in names:
        compact = name.lower().replace(" ", "")
        for candidate in preferred:
            if candidate.lower().replace(" ", "") in compact:
                return name
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_PIN_MISSING names=%s" % "|".join(names))


def _create_expression(material, expression_class, x, y):
    expression = unreal.MaterialEditingLibrary.create_material_expression(
        material, expression_class, x, y
    )
    if expression is None:
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_EXPRESSION_CREATE_FAILED")
    return expression


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_REFUSED dirty_before=%d" % len(dirty_before))
for path in (MASTER_PATH, INSTANCE_PATH):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_REFUSED existing=" + path)

base_color = common.load_asset_checked(config, BASE_COLOR_PATH)
normal = common.load_asset_checked(config, NORMAL_PATH)
world_aligned_texture = unreal.EditorAssetLibrary.load_asset(WORLD_ALIGNED_TEXTURE_PATH)
world_aligned_normal = unreal.EditorAssetLibrary.load_asset(WORLD_ALIGNED_NORMAL_PATH)
if world_aligned_texture is None or world_aligned_normal is None:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_ENGINE_FUNCTION_MISSING")

actors_by_label = {
    actor.get_actor_label(): actor for actor in common.actor_subsystem().get_all_level_actors()
}
missing = sorted(set(EXPECTED_LABELS) - set(actors_by_label))
if missing:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_SCOPE_REFUSED missing=%s" % "|".join(missing))
for label in EXPECTED_LABELS:
    component = getattr(actors_by_label[label], "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_COMPONENT_REFUSED " + label)
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    if not current_path.startswith(ALLOWED_SOURCE_PREFIXES):
        raise RuntimeError(
            "SUNSCAR_WORLD_ALIGNED_SOURCE_REFUSED %s %s" % (label, current_path)
        )

unreal.EditorAssetLibrary.make_directory(MASTER_FOLDER)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
master = asset_tools.create_asset(
    MASTER_NAME, MASTER_FOLDER, unreal.Material, unreal.MaterialFactoryNew()
)
if master is None:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_MASTER_CREATE_FAILED")
master.set_editor_property("tangent_space_normal", False)

base_parameter = _create_expression(
    master, unreal.MaterialExpressionTextureObjectParameter, -1000, -300
)
base_parameter.set_editor_property("parameter_name", unreal.Name("BaseColorTexture"))
base_parameter.set_editor_property("texture", base_color)

normal_parameter = _create_expression(
    master, unreal.MaterialExpressionTextureObjectParameter, -1000, 50
)
normal_parameter.set_editor_property("parameter_name", unreal.Name("NormalTexture"))
normal_parameter.set_editor_property("texture", normal)
normal_parameter.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)

size_parameter = _create_expression(
    master, unreal.MaterialExpressionVectorParameter, -1000, 350
)
size_parameter.set_editor_property("parameter_name", unreal.Name("TextureSizeCm"))
size_parameter.set_editor_property(
    "default_value", unreal.LinearColor(r=200.0, g=200.0, b=200.0, a=1.0)
)

roughness_parameter = _create_expression(
    master, unreal.MaterialExpressionScalarParameter, 100, 250
)
roughness_parameter.set_editor_property("parameter_name", unreal.Name("Roughness"))
roughness_parameter.set_editor_property("default_value", 0.85)

specular_parameter = _create_expression(
    master, unreal.MaterialExpressionScalarParameter, 100, 400
)
specular_parameter.set_editor_property("parameter_name", unreal.Name("Specular"))
specular_parameter.set_editor_property("default_value", 0.2)

base_call = _create_expression(
    master, unreal.MaterialExpressionMaterialFunctionCall, -450, -300
)
base_call.set_editor_property("material_function", world_aligned_texture)
normal_call = _create_expression(
    master, unreal.MaterialExpressionMaterialFunctionCall, -450, 50
)
normal_call.set_editor_property("material_function", world_aligned_normal)

base_inputs = _pin_names(base_call)
normal_inputs = _pin_names(normal_call)
base_outputs = _pin_names(base_call, output=True)
normal_outputs = _pin_names(normal_call, output=True)
base_texture_pin = _find_pin(base_inputs, ["TextureObject"])
base_size_pin = _find_pin(base_inputs, ["TextureSize"])
normal_texture_pin = _find_pin(normal_inputs, ["TextureObject"])
normal_size_pin = _find_pin(normal_inputs, ["TextureSize"])
base_output_pin = _find_pin(base_outputs, ["XYZ Texture", "XYZTexture"])
normal_output_pin = _find_pin(normal_outputs, ["XYZ Texture", "XYZTexture"])

connections = [
    (base_parameter, "", base_call, base_texture_pin),
    (size_parameter, "", base_call, base_size_pin),
    (normal_parameter, "", normal_call, normal_texture_pin),
    (size_parameter, "", normal_call, normal_size_pin),
]
for source, output_name, destination, input_name in connections:
    if not unreal.MaterialEditingLibrary.connect_material_expressions(
        source, output_name, destination, input_name
    ):
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_CONNECT_FAILED " + input_name)
for expression, output_name, material_property in (
    (base_call, base_output_pin, unreal.MaterialProperty.MP_BASE_COLOR),
    (normal_call, normal_output_pin, unreal.MaterialProperty.MP_NORMAL),
    (roughness_parameter, "", unreal.MaterialProperty.MP_ROUGHNESS),
    (specular_parameter, "", unreal.MaterialProperty.MP_SPECULAR),
):
    if not unreal.MaterialEditingLibrary.connect_material_property(
        expression, output_name, material_property
    ):
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_OUTPUT_CONNECT_FAILED")
unreal.MaterialEditingLibrary.recompile_material(master)

instance = asset_tools.create_asset(
    INSTANCE_NAME,
    MASTER_FOLDER,
    unreal.MaterialInstanceConstant,
    unreal.MaterialInstanceConstantFactoryNew(),
)
if instance is None:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_INSTANCE_CREATE_FAILED")
instance.set_editor_property("parent", master)
unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
    instance, "BaseColorTexture", base_color
)
unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
    instance, "NormalTexture", normal
)
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
    instance, "TextureSizeCm", unreal.LinearColor(r=200.0, g=200.0, b=200.0, a=1.0)
)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
    instance, "Roughness", 0.85
)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
    instance, "Specular", 0.2
)
unreal.MaterialEditingLibrary.update_material_instance(instance)

records = []
for label in EXPECTED_LABELS:
    actor = actors_by_label[label]
    component = actor.static_mesh_component
    current = component.get_material(0)
    actor.modify()
    component.modify()
    component.set_material(0, instance)
    if PASS_TAG not in list(actor.tags):
        actor.tags = list(actor.tags) + [PASS_TAG]
    records.append(
        {
            "label": label,
            "source_material": current.get_path_name() if current else "",
            "target_material": instance.get_path_name(),
            "package": actor.get_package().get_name(),
        }
    )

dirty_content = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
expected_content = sorted([MASTER_PATH, INSTANCE_PATH])
expected_maps = sorted({record["package"] for record in records})
if dirty_content != expected_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_DIRTY_SCOPE_FAILED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_world_aligned_facade_prototype_ready",
    "context": context,
    "site_id": "SS_017",
    "material_master": MASTER_PATH,
    "material_instance": INSTANCE_PATH,
    "engine_functions": [WORLD_ALIGNED_TEXTURE_PATH, WORLD_ALIGNED_NORMAL_PATH],
    "texture_size_cm": [200.0, 200.0, 200.0],
    "function_pins": {
        "base_inputs": base_inputs,
        "base_outputs": base_outputs,
        "normal_inputs": normal_inputs,
        "normal_outputs": normal_outputs,
    },
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "level_saved": False,
}
report = common.write_json_report(
    config, "old_town_world_aligned_facade_prototype_v1.json", payload
)
unreal.log(
    "SUNSCAR_WORLD_ALIGNED_PROTOTYPE actors=%d report=%s" % (len(records), report)
)
print("SUNSCAR_WORLD_ALIGNED_PROTOTYPE", report)
