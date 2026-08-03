"""Create Quixel world-aligned ground materials and apply them to 288 Old Town overlays, unsaved."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


MATERIAL_FOLDER = "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned"
MASTER_NAME = "M_OT_WorldAlignedGround"
MASTER_PATH = MATERIAL_FOLDER + "/" + MASTER_NAME
PASS_TAG = unreal.Name("SunscarWorldAlignedGroundSurfaceV1")
WORLD_ALIGNED_TEXTURE_PATH = "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture"
WORLD_ALIGNED_NORMAL_PATH = "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal"
SOURCE_PATHS = {
    "asphalt": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Asphalt.MI_OT_Ground_Asphalt",
    "concrete": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Concrete.MI_OT_Ground_Concrete",
    "dust": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Dust.MI_OT_Ground_Dust",
    "earth": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Earth.MI_OT_Ground_Earth",
    "silt": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Silt.MI_OT_Ground_Silt",
    "stone": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Stone.MI_OT_Ground_Stone",
}
EXPECTED_SOURCE_COUNTS = {
    "asphalt": 158,
    "concrete": 20,
    "dust": 12,
    "earth": 20,
    "silt": 70,
    "stone": 8,
}
SANDSTONE_BASE = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv/Sandstone_Rocky_Ground_vmjjfiv_High_4K_BaseColor"
SANDSTONE_NORMAL = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_013_vmjjfiv/Sandstone_Rocky_Ground_vmjjfiv_High_4K_Normal"
INSTANCE_DEFINITIONS = {
    "asphalt_fresh": {
        "name": "MI_OT_AsphaltFresh_WorldAligned",
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_011_sfrofg0a/Asphalt_Fresh_sfrofg0a_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_011_sfrofg0a/Asphalt_Fresh_sfrofg0a_4K_Normal",
        "tint": (0.82, 0.78, 0.70),
        "roughness": 0.82,
        "size_cm": 200.0,
    },
    "asphalt_crushed": {
        "name": "MI_OT_CrushedAsphalt_WorldAligned",
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_012_sjyjcbja/Crushed_Asphalt_Ground_sjyjcbja_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_012_sjyjcbja/Crushed_Asphalt_Ground_sjyjcbja_4K_Normal",
        "tint": (0.88, 0.82, 0.72),
        "roughness": 0.9,
        "size_cm": 200.0,
    },
    "asphalt_cracked": {
        "name": "MI_OT_CrackedAsphalt_WorldAligned",
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_013_tjmgfelew/Cracked_Asphalt_tjmgfelew_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_013_tjmgfelew/Cracked_Asphalt_tjmgfelew_4K_Normal",
        "tint": (0.86, 0.80, 0.70),
        "roughness": 0.88,
        "size_cm": 200.0,
    },
    "concrete": {
        "name": "MI_OT_WeatheredConcreteGround_WorldAligned",
        "base": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P0_010_vi4idbm/Weathered_Concrete_Wall_vi4idbm_4K_BaseColor",
        "normal": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P0_010_vi4idbm/Weathered_Concrete_Wall_vi4idbm_4K_Normal",
        "tint": (0.90, 0.86, 0.78),
        "roughness": 0.9,
        "size_cm": 200.0,
    },
    "dust": {
        "name": "MI_OT_SandstoneDust_WorldAligned",
        "base": SANDSTONE_BASE,
        "normal": SANDSTONE_NORMAL,
        "tint": (1.08, 0.96, 0.82),
        "roughness": 0.96,
        "size_cm": 240.0,
    },
    "earth": {
        "name": "MI_OT_SandstoneEarth_WorldAligned",
        "base": SANDSTONE_BASE,
        "normal": SANDSTONE_NORMAL,
        "tint": (0.88, 0.74, 0.58),
        "roughness": 0.95,
        "size_cm": 240.0,
    },
    "silt": {
        "name": "MI_OT_SandstoneSilt_WorldAligned",
        "base": SANDSTONE_BASE,
        "normal": SANDSTONE_NORMAL,
        "tint": (0.78, 0.67, 0.56),
        "roughness": 0.97,
        "size_cm": 240.0,
    },
    "stone": {
        "name": "MI_OT_SandstoneStone_WorldAligned",
        "base": SANDSTONE_BASE,
        "normal": SANDSTONE_NORMAL,
        "tint": (0.96, 0.90, 0.80),
        "roughness": 0.93,
        "size_cm": 220.0,
    },
}


def _pin_names(expression, output=False):
    values = (
        unreal.MaterialEditingLibrary.get_material_expression_output_names(expression)
        if output
        else unreal.MaterialEditingLibrary.get_material_expression_input_names(expression)
    )
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
    raise RuntimeError("SUNSCAR_GROUND_PIN_MISSING names=%s" % "|".join(names))


def _expression(material, expression_class, x, y):
    result = unreal.MaterialEditingLibrary.create_material_expression(material, expression_class, x, y)
    if result is None:
        raise RuntimeError("SUNSCAR_GROUND_EXPRESSION_CREATE_FAILED")
    return result


def source_role(material_path):
    for role, path in SOURCE_PATHS.items():
        if material_path == path:
            return role
    return ""


def treatment_for(actor, role):
    if role != "asphalt":
        return role
    folder = common.actor_folder(actor)
    label = actor.get_actor_label()
    if "Freight" in folder:
        return "asphalt_crushed"
    if "MarketRoute" in folder or "NorthRoute" in folder:
        return "asphalt_cracked"
    if "GroundSurfacePass" in folder:
        digit_sum = sum(int(character) for character in label if character.isdigit())
        return "asphalt_cracked" if digit_sum % 2 else "asphalt_fresh"
    return "asphalt_fresh"


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_GROUND_REFUSED dirty_before=%d" % len(dirty_before))
for path in [MASTER_PATH] + [MATERIAL_FOLDER + "/" + value["name"] for value in INSTANCE_DEFINITIONS.values()]:
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_GROUND_REFUSED existing=" + path)

targets = []
source_counts = collections.Counter()
for actor in common.actor_subsystem().get_all_level_actors():
    if "VisualGroundOverlay" not in common.actor_tags(actor):
        continue
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component and component.get_num_materials() == 1 else None
    material_path = material.get_path_name() if material else ""
    role = source_role(material_path)
    if not role:
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_GROUND_SOURCE_REFUSED %s %s" % (actor.get_actor_label(), material_path))
    source_counts[role] += 1
    targets.append((actor, role))
if len(targets) != 288 or dict(source_counts) != EXPECTED_SOURCE_COUNTS:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_GROUND_SCOPE_REFUSED actors=%d counts=%s"
        % (len(targets), dict(source_counts))
    )

texture_assets = {}
for definition in INSTANCE_DEFINITIONS.values():
    for key in ("base", "normal"):
        texture_assets[definition[key]] = common.load_asset_checked(config, definition[key])
world_aligned_texture = unreal.EditorAssetLibrary.load_asset(WORLD_ALIGNED_TEXTURE_PATH)
world_aligned_normal = unreal.EditorAssetLibrary.load_asset(WORLD_ALIGNED_NORMAL_PATH)
if world_aligned_texture is None or world_aligned_normal is None:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_GROUND_ENGINE_FUNCTION_MISSING")

unreal.EditorAssetLibrary.make_directory(MATERIAL_FOLDER)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
master = asset_tools.create_asset(MASTER_NAME, MATERIAL_FOLDER, unreal.Material, unreal.MaterialFactoryNew())
if master is None:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_GROUND_MASTER_CREATE_FAILED")
master.set_editor_property("tangent_space_normal", False)

base_parameter = _expression(master, unreal.MaterialExpressionTextureObjectParameter, -1100, -350)
base_parameter.set_editor_property("parameter_name", unreal.Name("BaseColorTexture"))
normal_parameter = _expression(master, unreal.MaterialExpressionTextureObjectParameter, -1100, 0)
normal_parameter.set_editor_property("parameter_name", unreal.Name("NormalTexture"))
normal_parameter.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
size_parameter = _expression(master, unreal.MaterialExpressionVectorParameter, -1100, 350)
size_parameter.set_editor_property("parameter_name", unreal.Name("TextureSizeCm"))
size_parameter.set_editor_property("default_value", unreal.LinearColor(200.0, 200.0, 200.0, 1.0))
tint_parameter = _expression(master, unreal.MaterialExpressionVectorParameter, -350, -80)
tint_parameter.set_editor_property("parameter_name", unreal.Name("ColorTint"))
tint_parameter.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
roughness_parameter = _expression(master, unreal.MaterialExpressionScalarParameter, 100, 250)
roughness_parameter.set_editor_property("parameter_name", unreal.Name("Roughness"))
roughness_parameter.set_editor_property("default_value", 0.9)
base_call = _expression(master, unreal.MaterialExpressionMaterialFunctionCall, -650, -350)
base_call.set_editor_property("material_function", world_aligned_texture)
normal_call = _expression(master, unreal.MaterialExpressionMaterialFunctionCall, -650, 50)
normal_call.set_editor_property("material_function", world_aligned_normal)
multiply = _expression(master, unreal.MaterialExpressionMultiply, 0, -250)

base_inputs = _pin_names(base_call)
normal_inputs = _pin_names(normal_call)
base_output = _find_pin(_pin_names(base_call, output=True), ["XYZ Texture", "XYZTexture"])
normal_output = _find_pin(_pin_names(normal_call, output=True), ["XYZ Texture", "XYZTexture"])
connections = [
    (base_parameter, "", base_call, _find_pin(base_inputs, ["TextureObject"])),
    (size_parameter, "", base_call, _find_pin(base_inputs, ["TextureSize"])),
    (normal_parameter, "", normal_call, _find_pin(normal_inputs, ["TextureObject"])),
    (size_parameter, "", normal_call, _find_pin(normal_inputs, ["TextureSize"])),
    (base_call, base_output, multiply, "A"),
    (tint_parameter, "", multiply, "B"),
]
for source, output_name, destination, input_name in connections:
    if not unreal.MaterialEditingLibrary.connect_material_expressions(source, output_name, destination, input_name):
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_GROUND_CONNECT_FAILED " + input_name)
for expression, output_name, material_property in (
    (multiply, "", unreal.MaterialProperty.MP_BASE_COLOR),
    (normal_call, normal_output, unreal.MaterialProperty.MP_NORMAL),
    (roughness_parameter, "", unreal.MaterialProperty.MP_ROUGHNESS),
):
    if not unreal.MaterialEditingLibrary.connect_material_property(expression, output_name, material_property):
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_GROUND_OUTPUT_CONNECT_FAILED")
unreal.MaterialEditingLibrary.recompile_material(master)

instances = {}
for treatment, definition in INSTANCE_DEFINITIONS.items():
    instance = asset_tools.create_asset(
        definition["name"], MATERIAL_FOLDER, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew()
    )
    if instance is None:
        raise RuntimeError("SUNSCAR_WORLD_ALIGNED_GROUND_INSTANCE_CREATE_FAILED " + treatment)
    instance.set_editor_property("parent", master)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(instance, "BaseColorTexture", texture_assets[definition["base"]])
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(instance, "NormalTexture", texture_assets[definition["normal"]])
    size = definition["size_cm"]
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(instance, "TextureSizeCm", unreal.LinearColor(size, size, size, 1.0))
    tint = definition["tint"]
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(instance, "ColorTint", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(instance, "Roughness", definition["roughness"])
    unreal.MaterialEditingLibrary.update_material_instance(instance)
    instances[treatment] = instance

records = []
treatment_counts = collections.Counter()
for actor, role in sorted(targets, key=lambda item: item[0].get_actor_label()):
    treatment = treatment_for(actor, role)
    target = instances[treatment]
    component = actor.static_mesh_component
    source = component.get_material(0)
    actor.modify()
    component.modify()
    component.set_material(0, target)
    if PASS_TAG not in list(actor.tags):
        actor.tags = list(actor.tags) + [PASS_TAG]
    treatment_counts[treatment] += 1
    records.append(
        {
            "label": actor.get_actor_label(),
            "folder": common.actor_folder(actor),
            "source_role": role,
            "treatment": treatment,
            "source_material": source.get_path_name() if source else "",
            "target_material": target.get_path_name(),
            "package": actor.get_package().get_name(),
        }
    )

dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
expected_content = sorted([MASTER_PATH] + [MATERIAL_FOLDER + "/" + value["name"] for value in INSTANCE_DEFINITIONS.values()])
expected_maps = sorted({record["package"] for record in records})
if dirty_content != expected_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_GROUND_DIRTY_SCOPE_FAILED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_world_aligned_ground_surface_ready",
    "context": context,
    "actor_count": len(records),
    "source_counts": dict(sorted(source_counts.items())),
    "treatment_counts": dict(sorted(treatment_counts.items())),
    "material_assets": expected_content,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_world_aligned_ground_surface_v1.json", payload)
unreal.log("SUNSCAR_WORLD_ALIGNED_GROUND actors=%d materials=%d report=%s" % (len(records), len(expected_content), report))
print("SUNSCAR_WORLD_ALIGNED_GROUND", len(records), report)
