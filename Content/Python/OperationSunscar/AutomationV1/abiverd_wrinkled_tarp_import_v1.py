"""Dry-run-first map-owned import for Quixel Wrinkled Tarp (vieldbo).

The default mode performs only validation and writes a report. Set
``APPLY_CHANGES`` to True for the reviewed import. The apply mode imports the
verified High glTF source, creates a lightweight opaque two-sided packed-ORM
cloth master, configures Nanite and runtime texture caps, and saves only the
intentionally created map-owned content assets. It never loads or modifies the
level.
"""

import json
import math
import os
from datetime import datetime, timezone

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
SOURCE_ROOT = (
    "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/"
    "Wrinkled_Tarp-b4cd9451/gltf/high/wrinkled_tarp_vieldbo_ue_extracted"
)
SOURCE_FILE = SOURCE_ROOT + "/vieldbo_tier_1.gltf"
SOURCE_FILES = {
    "gltf": SOURCE_FILE,
    "bin": SOURCE_ROOT + "/vieldbo_tier_1.bin",
    "metadata": SOURCE_ROOT + "/vieldbo.json",
    "BaseColor": SOURCE_ROOT + "/Textures/T_vieldbo_4K_B.png",
    "Normal": SOURCE_ROOT + "/Textures/T_vieldbo_4K_N.png",
    "ORM": SOURCE_ROOT + "/Textures/T_vieldbo_4K_ORM.png",
    "Height": SOURCE_ROOT + "/Textures/T_vieldbo_4K_H.png",
}
DESTINATION = "/Game/Maps/Sunscar/Art/Heritage/Props/WrinkledTarp"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/M_ABV_Cloth_ORM"
MATERIAL_PATH = DESTINATION + "/MI_ABV_WrinkledTarp"
REPORT_STEM = "abiverd_wrinkled_tarp_import_v1"


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


def write_report(payload, suffix):
    report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
    os.makedirs(report_root, exist_ok=True)
    report_path = os.path.join(report_root, REPORT_STEM + suffix + ".json")
    payload["generated_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return report_path


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_TARP_WRONG_PROJECT %s %s" % (project_name, project_directory))

missing_sources = [path for path in SOURCE_FILES.values() if not os.path.isfile(path)]
if missing_sources:
    raise RuntimeError("ABIVERD_TARP_SOURCE_MISSING " + "|".join(missing_sources))

dirty_before = dirty_packages()
if dirty_before:
    raise RuntimeError("ABIVERD_TARP_DIRTY_BEFORE " + "|".join(dirty_before))

existing = (
    unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True)
    if unreal.EditorAssetLibrary.does_directory_exist(DESTINATION)
    else []
)

base_payload = {
    "schema_version": 1,
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level_changed": False,
    },
    "source_id": "vieldbo",
    "source_listing_suffix": "b4cd9451",
    "source_file": SOURCE_FILE,
    "source_files": SOURCE_FILES,
    "source_physical_size_cm": [277.0, 151.0, 10.0],
    "source_lod0_vertices": 6678,
    "destination": DESTINATION,
    "master": MASTER_PATH,
    "material": MATERIAL_PATH,
    "runtime_texture_max_size": 2048,
    "planned_material_policy": {
        "blend_mode": "opaque",
        "two_sided": True,
        "packed_orm": True,
        "height_texture_imported_but_not_sampled": True,
    },
    "planned_mesh_policy": {
        "nanite_enabled": True,
        "placement_collision": "NoCollision",
        "placement_affects_navigation": False,
    },
    "dirty_before": dirty_before,
    "existing_destination_assets": existing,
}

if not APPLY_CHANGES:
    base_payload["status"] = "dry_run_passed" if not existing else "dry_run_blocked_destination_not_empty"
    report_path = write_report(base_payload, "_dry_run")
    if existing:
        raise RuntimeError("ABIVERD_TARP_DESTINATION_NOT_EMPTY " + repr(existing))
    unreal.log("ABIVERD_TARP_IMPORT_DRY_RUN_PASS " + report_path)
    print("ABIVERD_TARP_IMPORT_DRY_RUN_PASS", report_path)
else:
    if existing:
        raise RuntimeError("ABIVERD_TARP_DESTINATION_NOT_EMPTY " + repr(existing))

    task = unreal.AssetImportTask()
    task.filename = SOURCE_FILE
    task.destination_path = DESTINATION
    task.automated = True
    task.replace_existing = False
    task.save = False
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    assets = [
        unreal.EditorAssetLibrary.load_asset(path)
        for path in unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True)
    ]
    meshes = [item for item in assets if isinstance(item, unreal.StaticMesh)]
    textures = [item for item in assets if isinstance(item, unreal.Texture2D)]
    source_materials = [item for item in assets if isinstance(item, unreal.MaterialInstanceConstant)]
    if len(meshes) != 1 or len(textures) != 4 or len(source_materials) != 1:
        raise RuntimeError(
            "ABIVERD_TARP_IMPORT_SCOPE meshes=%d textures=%d materials=%d"
            % (len(meshes), len(textures), len(source_materials))
        )

    roles = {}
    for texture in textures:
        lower = texture.get_name().lower()
        if lower.endswith("_b"):
            roles["BaseColor"] = texture
        elif lower.endswith("_n"):
            roles["Normal"] = texture
        elif lower.endswith("_orm"):
            roles["ORM"] = texture
        elif lower.endswith("_h"):
            roles["Height"] = texture
    if set(roles) != {"BaseColor", "Normal", "ORM", "Height"}:
        raise RuntimeError("ABIVERD_TARP_TEXTURE_ROLES " + repr(sorted(roles)))

    roles["ORM"].modify()
    roles["ORM"].set_editor_properties(
        {
            "srgb": False,
            "compression_settings": unreal.TextureCompressionSettings.TC_MASKS,
            "max_texture_size": 2048,
        }
    )
    roles["Normal"].modify()
    roles["Normal"].set_editor_properties(
        {
            "srgb": False,
            "compression_settings": unreal.TextureCompressionSettings.TC_NORMALMAP,
            "max_texture_size": 2048,
        }
    )
    roles["BaseColor"].modify()
    roles["BaseColor"].set_editor_property("max_texture_size", 2048)
    roles["Height"].modify()
    roles["Height"].set_editor_properties({"srgb": False, "max_texture_size": 1024})

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
    if master is None:
        master = asset_tools.create_asset(
            MASTER_PATH.rsplit("/", 1)[1],
            MASTER_PATH.rsplit("/", 1)[0],
            unreal.Material,
            unreal.MaterialFactoryNew(),
        )
        if not isinstance(master, unreal.Material):
            raise RuntimeError("ABIVERD_TARP_MASTER_CREATE")
        master.modify()
        unreal.MaterialEditingLibrary.delete_all_material_expressions(master)
        master.set_editor_properties(
            {
                "blend_mode": unreal.BlendMode.BLEND_OPAQUE,
                "two_sided": True,
                "tangent_space_normal": True,
            }
        )
        base_sample = unreal.MaterialEditingLibrary.create_material_expression(
            master, unreal.MaterialExpressionTextureSampleParameter2D, -600, -180
        )
        normal_sample = unreal.MaterialEditingLibrary.create_material_expression(
            master, unreal.MaterialExpressionTextureSampleParameter2D, -600, 40
        )
        orm_sample = unreal.MaterialEditingLibrary.create_material_expression(
            master, unreal.MaterialExpressionTextureSampleParameter2D, -600, 260
        )
        if base_sample is None or normal_sample is None or orm_sample is None:
            raise RuntimeError("ABIVERD_TARP_MASTER_EXPRESSIONS")
        base_sample.set_editor_properties(
            {
                "parameter_name": unreal.Name("BaseColor"),
                "texture": roles["BaseColor"],
                "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
            }
        )
        normal_sample.set_editor_properties(
            {
                "parameter_name": unreal.Name("Normal"),
                "texture": roles["Normal"],
                "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
            }
        )
        orm_sample.set_editor_properties(
            {
                "parameter_name": unreal.Name("ORM"),
                "texture": roles["ORM"],
                "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_MASKS,
            }
        )
        for expression, output_name, material_property in (
            (base_sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR),
            (normal_sample, "RGB", unreal.MaterialProperty.MP_NORMAL),
            (orm_sample, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),
            (orm_sample, "G", unreal.MaterialProperty.MP_ROUGHNESS),
            (orm_sample, "B", unreal.MaterialProperty.MP_METALLIC),
        ):
            if not unreal.MaterialEditingLibrary.connect_material_property(
                expression, output_name, material_property
            ):
                raise RuntimeError("ABIVERD_TARP_MASTER_CONNECT " + str(material_property))
        compile_errors = list(unreal.MaterialEditingLibrary.recompile_material(master))
        if compile_errors:
            raise RuntimeError("ABIVERD_TARP_MASTER_COMPILE " + "|".join(str(item) for item in compile_errors))
    if not isinstance(master, unreal.Material):
        raise RuntimeError("ABIVERD_TARP_MASTER_TYPE")
    if master.get_editor_property("blend_mode") != unreal.BlendMode.BLEND_OPAQUE:
        raise RuntimeError("ABIVERD_TARP_MASTER_NOT_OPAQUE")
    if not bool(master.get_editor_property("two_sided")):
        raise RuntimeError("ABIVERD_TARP_MASTER_NOT_TWO_SIDED")

    material = asset_tools.create_asset(
        MATERIAL_PATH.rsplit("/", 1)[1],
        DESTINATION,
        unreal.MaterialInstanceConstant,
        unreal.MaterialInstanceConstantFactoryNew(),
    )
    if not isinstance(material, unreal.MaterialInstanceConstant):
        raise RuntimeError("ABIVERD_TARP_MATERIAL_CREATE")
    material.modify()
    material.set_editor_property("parent", master)
    for parameter, texture in (
        ("BaseColor", roles["BaseColor"]),
        ("Normal", roles["Normal"]),
        ("ORM", roles["ORM"]),
    ):
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
            material, parameter, texture
        )
    unreal.MaterialEditingLibrary.update_material_instance(material)

    mesh = meshes[0]
    mesh.modify()
    nanite = mesh.get_editor_property("nanite_settings")
    nanite.enabled = True
    mesh.set_editor_property("nanite_settings", nanite)
    mesh.set_material(0, material)

    bounds = mesh.get_bounds()
    extent = bounds.box_extent
    bounds_size_cm = [
        round(float(extent.x) * 2.0, 3),
        round(float(extent.y) * 2.0, 3),
        round(float(extent.z) * 2.0, 3),
    ]
    if not all(math.isfinite(value) for value in bounds_size_cm):
        raise RuntimeError("ABIVERD_TARP_BOUNDS_NONFINITE " + repr(bounds_size_cm))
    expected_sorted = sorted([277.0, 151.0, 10.0])
    actual_sorted = sorted(bounds_size_cm)
    if any(abs(actual - expected) > 5.0 for actual, expected in zip(actual_sorted, expected_sorted)):
        raise RuntimeError("ABIVERD_TARP_BOUNDS " + repr(bounds_size_cm))

    dirty_before_save = dirty_packages()
    allowed_prefixes = [DESTINATION + "/", MASTER_PATH]
    unexpected = [
        name for name in dirty_before_save
        if not any(name == prefix or name.startswith(prefix) for prefix in allowed_prefixes)
    ]
    if unexpected:
        raise RuntimeError("ABIVERD_TARP_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_TARP_SAVE_FAILED")
    remaining = dirty_packages()
    if remaining:
        raise RuntimeError("ABIVERD_TARP_DIRTY_AFTER " + "|".join(remaining))

    base_payload.update(
        {
            "status": "imported_configured_and_saved",
            "mesh": mesh.get_path_name(),
            "bounds_size_cm": bounds_size_cm,
            "lod0_vertices": int(mesh.get_num_vertices(0)),
            "nanite_enabled": bool(mesh.get_editor_property("nanite_settings").enabled),
            "assets": sorted(item.get_path_name() for item in assets),
            "created_material": material.get_path_name(),
            "dirty_before_save": dirty_before_save,
            "dirty_after_save": remaining,
        }
    )
    report_path = write_report(base_payload, "_apply")
    unreal.log("ABIVERD_TARP_IMPORT_COMPLETE " + report_path)
    print("ABIVERD_TARP_IMPORT_COMPLETE", report_path)
