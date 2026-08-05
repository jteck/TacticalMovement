"""Read-only audit of current Old Town window visuals and shared materials."""

import json
import os
import re

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
WINDOW_PATTERN = re.compile(r"^(.*(?:_Win_|_Window_).*)_(Frame|Glass)$", re.IGNORECASE)
FRAME_MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Timber"
GLASS_MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Glass"


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
    raise RuntimeError("ABIVERD_WINDOW_MATERIAL_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WINDOW_MATERIAL_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_WINDOW_MATERIAL_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

records = []
pair_roles = {}
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    label = actor.get_actor_label()
    match = WINDOW_PATTERN.match(label)
    if not match:
        continue
    key, role = match.groups()
    component = actor.static_mesh_component
    origin, extent = actor.get_actor_bounds(False)
    material = component.get_material(0)
    records.append(
        {
            "key": key.lower(),
            "label": label,
            "role": role.lower(),
            "location_cm": [round(origin.x, 2), round(origin.y, 2), round(origin.z, 2)],
            "dimensions_cm": [round(extent.x * 2.0, 2), round(extent.y * 2.0, 2), round(extent.z * 2.0, 2)],
            "material": asset_path(material),
            "visible": component.is_visible(),
            "hidden_in_game": bool(component.get_editor_property("hidden_in_game")),
            "collision": str(component.get_collision_enabled()),
        }
    )
    pair_roles.setdefault(key.lower(), set()).add(role.lower())

records.sort(key=lambda item: item["label"].lower())
if len(records) != 80 or len(pair_roles) != 40:
    raise RuntimeError("ABIVERD_WINDOW_MATERIAL_AUDIT_COUNTS records=%d pairs=%d" % (len(records), len(pair_roles)))
bad_pairs = sorted(key for key, roles in pair_roles.items() if roles != {"frame", "glass"})
if bad_pairs:
    raise RuntimeError("ABIVERD_WINDOW_MATERIAL_AUDIT_PAIRS " + "|".join(bad_pairs))

materials = {}
for path in (FRAME_MATERIAL_PATH, GLASS_MATERIAL_PATH):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.MaterialInterface):
        raise RuntimeError("ABIVERD_WINDOW_MATERIAL_AUDIT_MISSING " + path)
    parent = asset.get_editor_property("parent") if isinstance(asset, unreal.MaterialInstance) else None
    materials[path] = {
        "class": asset.get_class().get_name(),
        "parent": asset_path(parent),
        "scalar_parameter_names": [str(item) for item in unreal.MaterialEditingLibrary.get_scalar_parameter_names(asset)],
        "vector_parameter_names": [str(item) for item in unreal.MaterialEditingLibrary.get_vector_parameter_names(asset)],
        "texture_parameter_names": [str(item) for item in unreal.MaterialEditingLibrary.get_texture_parameter_names(asset)],
    }

dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_WINDOW_MATERIAL_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))
report = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "record_count": len(records),
    "pair_count": len(pair_roles),
    "visible_count": sum(item["visible"] and not item["hidden_in_game"] for item in records),
    "collision_counts": {
        value: sum(item["collision"] == value for item in records)
        for value in sorted({item["collision"] for item in records})
    },
    "material_counts": {
        value: sum(item["material"] == value for item in records)
        for value in sorted({item["material"] for item in records})
    },
    "materials": materials,
    "records": records,
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_window_material_state_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_WINDOW_MATERIAL_AUDIT_COMPLETE records=80 pairs=40")
print("ABIVERD_WINDOW_MATERIAL_AUDIT_COMPLETE", report_path)
