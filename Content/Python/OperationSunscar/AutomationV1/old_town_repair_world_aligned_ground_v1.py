"""Repair the unsaved ground master defaults required for Metal shader compilation."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


MASTER_PATH = "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/M_OT_WorldAlignedGround"
DEFAULT_BASE_PATH = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_012_sjyjcbja/Crushed_Asphalt_Ground_sjyjcbja_4K_BaseColor"
DEFAULT_NORMAL_PATH = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_012_sjyjcbja/Crushed_Asphalt_Ground_sjyjcbja_4K_Normal"
INSTANCE_PREFIX = "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/MI_OT_"


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
report_path = os.path.join(common.report_directory(config), "old_town_world_aligned_ground_surface_v1.json")
source_report = common.read_json(report_path)
expected_content = set(source_report["dirty_content_packages"])
expected_maps = set(source_report["dirty_map_packages"])
dirty_content = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content != expected_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_GROUND_REPAIR_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps)))
    )

master = common.load_asset_checked(config, MASTER_PATH)
default_base = common.load_asset_checked(config, DEFAULT_BASE_PATH)
default_normal = common.load_asset_checked(config, DEFAULT_NORMAL_PATH)
found = {}
for expression in unreal.MaterialEditingLibrary.get_material_expressions(master):
    if not isinstance(expression, unreal.MaterialExpressionTextureObjectParameter):
        continue
    parameter_name = str(expression.get_editor_property("parameter_name"))
    if parameter_name == "BaseColorTexture":
        expression.set_editor_property("texture", default_base)
        found[parameter_name] = default_base.get_path_name()
    elif parameter_name == "NormalTexture":
        expression.set_editor_property("texture", default_normal)
        expression.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        found[parameter_name] = default_normal.get_path_name()
if set(found) != {"BaseColorTexture", "NormalTexture"}:
    raise RuntimeError("SUNSCAR_GROUND_REPAIR_PARAMETERS_REFUSED found=%s" % found)

unreal.MaterialEditingLibrary.recompile_material(master)
updated_instances = []
for asset_path in source_report["material_assets"]:
    if not asset_path.startswith(INSTANCE_PREFIX):
        continue
    instance = common.load_asset_checked(config, asset_path)
    unreal.MaterialEditingLibrary.update_material_instance(instance)
    updated_instances.append(asset_path)

dirty_content_after = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps_after = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content_after != expected_content or dirty_maps_after != expected_maps:
    raise RuntimeError(
        "SUNSCAR_GROUND_REPAIR_DIRTY_SCOPE_FAILED content=%s maps=%s"
        % ("|".join(sorted(dirty_content_after)), "|".join(sorted(dirty_maps_after)))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_world_aligned_ground_compile_defaults_repaired",
    "context": context,
    "master": MASTER_PATH,
    "parameter_defaults": found,
    "updated_instances": sorted(updated_instances),
    "dirty_content_packages": sorted(dirty_content_after),
    "dirty_map_packages": sorted(dirty_maps_after),
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_repair_world_aligned_ground_v1.json", payload)
unreal.log("SUNSCAR_GROUND_REPAIR instances=%d report=%s" % (len(updated_instances), report))
print("SUNSCAR_GROUND_REPAIR", len(updated_instances), report)
