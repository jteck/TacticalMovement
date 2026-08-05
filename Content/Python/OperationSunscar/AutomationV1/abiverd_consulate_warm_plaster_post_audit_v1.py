"""Read-only post-audit for the SS_012 warm plaster material conversion."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/M_OT_WorldAlignedFacade"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_WallPaint_WorldAligned"
BASE_PATH = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_BaseColor"
NORMAL_PATH = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_015_qj2luvs0/Wall_Paint_qj2luvs0_4K_Normal"
SITE = "SS_012"


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


def asset_path(asset):
    return asset.get_outermost().get_name() if asset else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
base = unreal.EditorAssetLibrary.load_asset(BASE_PATH)
normal = unreal.EditorAssetLibrary.load_asset(NORMAL_PATH)
if not isinstance(material, unreal.MaterialInstanceConstant):
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_MATERIAL_MISSING")
if material.get_editor_property("parent") != master:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_PARENT")

material_library = unreal.MaterialEditingLibrary
actual_base = material_library.get_material_instance_texture_parameter_value(material, "BaseColorTexture")
actual_normal = material_library.get_material_instance_texture_parameter_value(material, "NormalTexture")
actual_size = material_library.get_material_instance_vector_parameter_value(material, "TextureSizeCm")
actual_roughness = material_library.get_material_instance_scalar_parameter_value(material, "Roughness")
actual_specular = material_library.get_material_instance_scalar_parameter_value(material, "Specular")
if actual_base != base or actual_normal != normal:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_TEXTURES")
if abs(actual_size.r - 200.0) > 0.01 or abs(actual_size.g - 200.0) > 0.01 or abs(actual_size.b - 200.0) > 0.01:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_SCALE " + repr(actual_size))
if abs(actual_roughness - 0.9) > 0.001 or abs(actual_specular - 0.15) > 0.001:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_SURFACE")

targets = []
excluded_using_target = []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    if unreal.Name("CoreCategory_Building") not in list(actor.tags) or actor_site(actor) != SITE:
        continue
    label = actor.get_actor_label()
    component = actor.static_mesh_component
    current = component.get_material(0)
    is_excluded = any(token in label for token in ("_Floor", "_Roof", "_Interior", "_Lintel"))
    is_wall = any(token in label for token in ("_Wall", "_Left", "_Right"))
    if is_excluded or not is_wall:
        if current == material:
            excluded_using_target.append(label)
        continue
    row = {
        "label": label,
        "material": asset_path(current),
        "collision": str(component.get_collision_enabled()),
    }
    if current != material:
        raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_ASSIGNMENT " + repr(row))
    if component.get_collision_enabled() != unreal.CollisionEnabled.QUERY_AND_PHYSICS:
        raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_COLLISION " + repr(row))
    targets.append(row)

targets.sort(key=lambda item: item["label"])
excluded_using_target.sort()
if len(targets) != 10:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_TARGET_COUNT %d" % len(targets))
if excluded_using_target:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_EXCLUDED " + "|".join(excluded_using_target))
dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_CONSULATE_PLASTER_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))

report = {
    "schema_version": 1,
    "status": "post_apply_audit_passed",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "target_count": len(targets),
    "targets": targets,
    "excluded_using_target": excluded_using_target,
    "material": {
        "path": MATERIAL_PATH,
        "parent": MASTER_PATH,
        "base_color": asset_path(actual_base),
        "normal": asset_path(actual_normal),
        "world_aligned_size_cm": [actual_size.r, actual_size.g, actual_size.b],
        "roughness": actual_roughness,
        "specular": actual_specular,
    },
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_consulate_warm_plaster_post_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_CONSULATE_PLASTER_POST_AUDIT_PASS targets=10")
print("ABIVERD_CONSULATE_PLASTER_POST_AUDIT_PASS", report_path)
