"""Repair opaque raw Quixel imports with a shared map-owned compatibility material."""

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_PROJECT_SUFFIX = "/UnrealEngine/_worktrees/map-development/"
MASTER_PATH = "/Game/MilitaryTrench/Materials/MasterMaterials/M_MS_Base_VT"
TARGETS = {
    "FAB_P1A_002_tdgecegda": ["Electrical_Box_tdgecegda_High"],
    "FAB_P1A_012_ydyqbjds": ["Military_Trenches_Debris_Patch_Rock_Corner_ydyqbjds_High"],
    "FAB_P1B_001_wbmgdcpdw": ["Old_Wooden_Door_wbmgdcpdw_High"],
    "FAB_P1B_008_ukknbeyaw": ["Old_Metal_Stool_ukknbeyaw_High"],
    "FAB_P1B_009_veigfjmaw": ["Wooden_Table_veigfjmaw_High"],
    "FAB_P1B_010_vlroadt": ["Wooden_Bench_vlroadt_High"],
    "FAB_P1B_014_tlhjacuva": [
        "tlhjacuva_LOD0_TIER1_000",
        "tlhjacuva_LOD0_TIER1_001",
        "tlhjacuva_LOD0_TIER1_002",
        "tlhjacuva_LOD0_TIER1_003",
        "tlhjacuva_LOD0_TIER1_004",
    ],
}


project_dir = unreal.Paths.project_dir().replace("\\", "/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_dir.endswith(EXPECTED_PROJECT_SUFFIX):
    raise RuntimeError("SUNSCAR_QUX_MAT_WRONG_PROJECT " + project_dir)
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("SUNSCAR_QUX_MAT_WRONG_LEVEL " + level_path)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
created_master = False
if master is None:
    raise RuntimeError("SUNSCAR_QUX_EPIC_MASTER_MISSING " + MASTER_PATH)


def choose_texture(asset_paths, terms):
    for path in asset_paths:
        name = path.rsplit("/", 1)[-1].lower()
        if all(term in name for term in terms):
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(asset, unreal.Texture):
                return asset
    return None


results = []
for source_id, mesh_names in TARGETS.items():
    folder = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/" + source_id
    assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=False, include_folder=False)
    base_color = choose_texture(assets, ["basecolor"]) or choose_texture(assets, ["diffuse"])
    normal = choose_texture(assets, ["normal"])
    roughness = choose_texture(assets, ["roughness"])
    if not base_color or not normal or not roughness:
        results.append(
            {
                "source_id": source_id,
                "status": "blocked_missing_required_texture",
                "base_color": bool(base_color),
                "normal": bool(normal),
                "roughness": bool(roughness),
            }
        )
        continue

    base_color.set_editor_property("srgb", True)
    normal.set_editor_property("srgb", False)
    normal.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    roughness.set_editor_property("srgb", False)
    for texture in (base_color, normal, roughness):
        unreal.EditorAssetLibrary.save_loaded_asset(texture, only_if_is_dirty=True)

    mi_name = "MI_OT_" + source_id
    mi_path = folder + "/" + mi_name
    mi = unreal.EditorAssetLibrary.load_asset(mi_path)
    if mi is None:
        mi = asset_tools.create_asset(
            mi_name,
            folder,
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew(),
        )
    if mi is None:
        raise RuntimeError("SUNSCAR_QUX_MI_CREATE_FAILED " + mi_path)
    mi.set_editor_property("parent", master)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
        mi, "BaseColorTexture", base_color
    )
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
        mi, "NormalTexture", normal
    )
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
        mi, "Min Roughness", 0.35
    )
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
        mi, "Max Roughness", 0.95
    )
    unreal.MaterialEditingLibrary.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_loaded_asset(mi, only_if_is_dirty=False)

    repaired_meshes = []
    for mesh_name in mesh_names:
        mesh_path = folder + "/" + mesh_name
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError("SUNSCAR_QUX_MESH_MISSING " + mesh_path)
        slot_count = max(1, len(mesh.get_editor_property("static_materials")))
        for slot in range(slot_count):
            mesh.set_material(slot, mi)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False)
        repaired_meshes.append(mesh_path)

    results.append(
        {
            "source_id": source_id,
            "status": "repaired",
            "material_instance": mi_path,
            "base_color": base_color.get_path_name(),
            "normal": normal.get_path_name(),
            "roughness": roughness.get_path_name(),
            "meshes": repaired_meshes,
        }
    )

report = {
    "schema_version": 1,
    "status": "complete",
    "master_material": MASTER_PATH,
    "created_master": created_master,
    "target_count": len(TARGETS),
    "repaired_count": sum(1 for row in results if row["status"] == "repaired"),
    "results": results,
    "level_changed": False,
    "level_saved": False,
}
report_path = unreal.Paths.project_saved_dir() + "OperationSunscar/Reports/repair_downloaded_quixel_materials_v1.json"
import json
import os
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log(
    "SUNSCAR_QUX_MATERIAL_REPAIR repaired=%d targets=%d report=%s"
    % (report["repaired_count"], len(TARGETS), report_path)
)
print("SUNSCAR_QUX_MATERIAL_REPAIR", report["repaired_count"], len(TARGETS), report_path)
