"""Read-only probe of Epic Megascans master-material parameter conventions."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
paths = [
    "/Game/Maps/Sunscar/Art/Materials/M_OT_QuixelOpaqueCompat",
    "/Game/Fab/Materials/Standard/M_MS_Srf",
    "/Game/Fab/Megascans/Surfaces/Weathered_Concrete_Wall_vi4idbm/Medium/vi4idbm_tier_2/Materials/MI_vi4idbm",
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_001_wbmgdcpdw/MI_OT_FAB_P1B_001_wbmgdcpdw",
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_001_wbmgdcpdw/Old_Wooden_Door_wbmgdcpdw_High",
    "/Game/Scene_Junkyard/Materials/MSPresets/M_MS_Default_Material/M_MS_Default_Material",
    "/Game/Scene_Junkyard/Materials/MSPresets/M_MS_Surface_Material/M_MS_Surface_Material",
    "/Game/Scene_Junkyard/Materials/MSPresets/M_MS_SurfaceBlend_Material/M_MS_SurfaceBlend_Material",
    "/Game/Scene_Junkyard/Materials/MasterMaterials/M_Ind_Jun_LayerSurface_01",
    "/Game/MilitaryTrench/Materials/MasterMaterials/M_MS_Base_VT",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Storage_Crate_Wood_M_02/StaticMeshes/SM_Mil_Trench_Storage_Crate_Wood_M_02_A",
]
rows = []
for path in paths:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    row = {"path": path, "loaded": asset is not None}
    if asset is not None:
        row["class"] = asset.get_class().get_name()
        try:
            row["texture_parameters"] = [
                str(name) for name in unreal.MaterialEditingLibrary.get_texture_parameter_names(asset)
            ]
        except Exception as error:
            row["texture_parameter_error"] = str(error)
        try:
            row["scalar_parameters"] = [
                str(name) for name in unreal.MaterialEditingLibrary.get_scalar_parameter_names(asset)
            ]
        except Exception as error:
            row["scalar_parameter_error"] = str(error)
        if isinstance(asset, unreal.MaterialInstanceConstant):
            parent = asset.get_editor_property("parent")
            row["parent"] = parent.get_path_name() if parent else ""
            names = unreal.MaterialEditingLibrary.get_texture_parameter_names(asset)
            row["texture_values"] = {
                str(name): (
                    value.get_path_name()
                    if (value := unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(asset, name))
                    else ""
                )
                for name in names
            }
            scalar_names = unreal.MaterialEditingLibrary.get_scalar_parameter_names(asset)
            row["scalar_values"] = {
                str(name): unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(asset, name)
                for name in scalar_names
            }
        if isinstance(asset, unreal.StaticMesh):
            materials = []
            for index in range(asset.get_num_sections(0)):
                material = asset.get_material(index)
                if material is None:
                    continue
                material_row = {
                    "slot": index,
                    "path": material.get_path_name(),
                    "class": material.get_class().get_name(),
                }
                try:
                    parent = material.get_editor_property("parent")
                    material_row["parent"] = parent.get_path_name() if parent else ""
                except Exception:
                    material_row["parent"] = ""
                try:
                    names = unreal.MaterialEditingLibrary.get_texture_parameter_names(material)
                    material_row["texture_values"] = {
                        str(name): (
                            value.get_path_name()
                            if (value := unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(material, name))
                            else ""
                        )
                        for name in names
                    }
                except Exception as error:
                    material_row["texture_value_error"] = str(error)
                materials.append(material_row)
            row["materials"] = materials
    rows.append(row)

payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "rows": rows,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_material_master_probe.json", payload)
unreal.log("SUNSCAR_MATERIAL_MASTER_PROBE rows=%d report=%s" % (len(rows), report))
print("SUNSCAR_MATERIAL_MASTER_PROBE", len(rows), report)
