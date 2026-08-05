"""Read-only post-audit for the opaque Old Town window-recess conversion."""

import json
import os
import re

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
WINDOW_PATTERN = re.compile(r"^(.*(?:_Win_|_Window_).*)_(Frame|Glass)$", re.IGNORECASE)
MASTER_PATH = "/Game/LevelPrototyping/Materials/M_FlatCol"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_DustyWindowRecess"


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


def asset_path(asset):
    return asset.get_outermost().get_name() if asset else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
if not isinstance(material, unreal.MaterialInstanceConstant) or material.get_editor_property("parent") != master:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_MATERIAL")
base_color = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(material, "Base Color")
roughness = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(material, "Roughness")
metallic = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(material, "Metallic")
if any(abs(actual - expected) > 0.001 for actual, expected in zip((base_color.r, base_color.g, base_color.b), (0.018, 0.022, 0.018))):
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_COLOR " + repr(base_color))
if abs(roughness - 0.92) > 0.001 or abs(metallic) > 0.001:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_SURFACE")

records = []
pairs = {}
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    label = actor.get_actor_label()
    match = WINDOW_PATTERN.match(label)
    if not match:
        continue
    key, role = match.groups()
    role = role.lower()
    component = actor.static_mesh_component
    row = {
        "key": key.lower(),
        "label": label,
        "role": role,
        "material": asset_path(component.get_material(0)),
        "visible": component.is_visible(),
        "hidden_in_game": bool(component.get_editor_property("hidden_in_game")),
        "collision": str(component.get_collision_enabled()),
    }
    if not row["visible"] or row["hidden_in_game"]:
        raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_VISIBILITY " + repr(row))
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_COLLISION " + repr(row))
    if role == "glass" and component.get_material(0) != material:
        raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_ASSIGNMENT " + repr(row))
    records.append(row)
    pairs.setdefault(key.lower(), set()).add(role)

records.sort(key=lambda item: item["label"].lower())
if len(records) != 80 or len(pairs) != 40:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_COUNTS records=%d pairs=%d" % (len(records), len(pairs)))
if any(roles != {"frame", "glass"} for roles in pairs.values()):
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_PAIRS")
dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))

report = {
    "schema_version": 1,
    "status": "post_apply_audit_passed",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "record_count": len(records),
    "pair_count": len(pairs),
    "glass_material_count": sum(row["role"] == "glass" and row["material"] == MATERIAL_PATH for row in records),
    "no_collision_count": sum("NO_COLLISION" in row["collision"] for row in records),
    "material": {
        "path": MATERIAL_PATH,
        "parent": MASTER_PATH,
        "base_color_linear": [base_color.r, base_color.g, base_color.b, base_color.a],
        "roughness": roughness,
        "metallic": metallic,
    },
    "records": records,
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_window_recess_post_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_WINDOW_RECESS_POST_AUDIT_PASS records=80 pairs=40")
print("ABIVERD_WINDOW_RECESS_POST_AUDIT_PASS", report_path)
