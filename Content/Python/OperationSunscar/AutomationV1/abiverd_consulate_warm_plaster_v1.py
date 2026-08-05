"""Dry-run-first warm plaster conversion for the SS_012 Consulate shell."""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/M_OT_WorldAlignedFacade"
MATERIAL_FOLDER = "/Game/Maps/Sunscar/Art/Materials/Facade"
MATERIAL_NAME = "MI_OT_WallPaint_WorldAligned"
MATERIAL_PATH = MATERIAL_FOLDER + "/" + MATERIAL_NAME
BASE_PATH = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_BaseColor"
NORMAL_PATH = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_Normal"
SITE = "SS_012"
REPORT_NAME = (
    "abiverd_consulate_warm_plaster_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_consulate_warm_plaster_dry_run_v1.json"
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


def actor_site(actor):
    for tag in actor.tags:
        value = str(tag)
        if value.startswith("Building_"):
            return value[len("Building_"):]
    return ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_DIRTY_BEFORE " + "|".join(dirty_packages()))

master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
base = unreal.EditorAssetLibrary.load_asset(BASE_PATH)
normal = unreal.EditorAssetLibrary.load_asset(NORMAL_PATH)
if not isinstance(master, unreal.Material) or not isinstance(base, unreal.Texture2D) or not isinstance(normal, unreal.Texture2D):
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_ASSET_MISSING")
existing_material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
if existing_material is not None and not isinstance(existing_material, unreal.MaterialInstanceConstant):
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_MATERIAL_CLASS")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
targets = []
rows = []
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    if unreal.Name("CoreCategory_Building") not in list(actor.tags) or actor_site(actor) != SITE:
        continue
    label = actor.get_actor_label()
    if any(token in label for token in ("_Floor", "_Roof", "_Interior", "_Lintel")):
        continue
    if not any(token in label for token in ("_Wall", "_Left", "_Right")):
        continue
    component = actor.static_mesh_component
    current = component.get_material(0)
    rows.append(
        {
            "label": label,
            "source_material": current.get_outermost().get_name() if current else "",
            "target_material": MATERIAL_PATH,
            "collision": str(component.get_collision_enabled()),
        }
    )
    targets.append(actor)
rows.sort(key=lambda row: row["label"])
targets.sort(key=lambda actor: actor.get_actor_label())
if len(targets) < 8 or len(targets) > 20:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_TARGET_COUNT %d" % len(targets))

saved_packages = []
if APPLY_CHANGES:
    material = existing_material
    if material is None:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            MATERIAL_NAME,
            MATERIAL_FOLDER,
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew(),
        )
        if material is None:
            raise RuntimeError("ABIVERD_CONSULATE_PLASTER_CREATE_FAILED")
    material.set_editor_property("parent", master)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, "BaseColorTexture", base)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, "NormalTexture", normal)
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
        material, "TextureSizeCm", unreal.LinearColor(r=200.0, g=200.0, b=200.0, a=1.0)
    )
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material, "Roughness", 0.9)
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material, "Specular", 0.15)
    unreal.MaterialEditingLibrary.update_material_instance(material)
    for actor in targets:
        actor.modify()
        component = actor.static_mesh_component
        component.modify()
        component.set_material(0, material)

    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_WallPaint_WorldAligned",
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_CONSULATE_PLASTER_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_CONSULATE_PLASTER_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_CONSULATE_PLASTER_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "target_count": len(rows),
    "records": rows,
    "material": {
        "path": MATERIAL_PATH,
        "base_color": BASE_PATH,
        "normal": NORMAL_PATH,
        "world_aligned_size_cm": 200.0,
        "roughness": 0.9,
        "specular": 0.15,
    },
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "scope": "SS_012 exterior wall shell pieces only",
        "preserved": "floors, roof, interiors, brick lintels, foundation, doors, windows, collision and navigation",
        "performance": "one shared world-aligned material instance; no new actors or replicated state",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_CONSULATE_PLASTER_COMPLETE apply=%s targets=%d" % (APPLY_CHANGES, len(rows)))
print("ABIVERD_CONSULATE_PLASTER_COMPLETE", report_path)
