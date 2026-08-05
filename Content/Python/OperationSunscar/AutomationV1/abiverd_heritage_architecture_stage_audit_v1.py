"""Read-only audit of the unsaved Abiverd architectural staging batch."""

import json
import os
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ROOT = "/Game/Maps/Sunscar/Art/Heritage/Architecture"
EXPECTED_ASSET_COUNT = 18


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


def vector_payload(vector):
    return {"x": float(vector.x), "y": float(vector.y), "z": float(vector.z)}


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_ARCH_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_ARCH_AUDIT_WRONG_LEVEL " + level_path)

paths = sorted(unreal.EditorAssetLibrary.list_assets(ROOT, recursive=True, include_folder=False))
if len(paths) != EXPECTED_ASSET_COUNT:
    raise RuntimeError("ABIVERD_ARCH_AUDIT_SCOPE expected=18 actual=%d paths=%s" % (len(paths), repr(paths)))

records = []
for path in paths:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset is None:
        raise RuntimeError("ABIVERD_ARCH_AUDIT_LOAD_FAILED " + path)
    record = {
        "path": path,
        "class": asset.get_class().get_name(),
    }
    if isinstance(asset, unreal.StaticMesh):
        try:
            bounds = asset.get_bounds()
            extent = bounds.box_extent
            record["bounds_extent_cm"] = vector_payload(extent)
            record["bounds_size_cm"] = {
                "x": float(extent.x * 2.0),
                "y": float(extent.y * 2.0),
                "z": float(extent.z * 2.0),
            }
            record["sphere_radius_cm"] = float(bounds.sphere_radius)
        except Exception as exc:
            record["bounds_error"] = repr(exc)
        for key, getter in (
            ("lod_count", lambda: int(unreal.EditorStaticMeshLibrary.get_lod_count(asset))),
            ("lod0_vertices", lambda: int(unreal.EditorStaticMeshLibrary.get_number_verts(asset, 0))),
            ("material_slot_count", lambda: len(list(asset.static_materials))),
            ("allow_cpu_access", lambda: bool(asset.get_editor_property("allow_cpu_access"))),
            ("simple_collision_count", lambda: int(unreal.EditorStaticMeshLibrary.get_simple_collision_count(asset))),
        ):
            try:
                record[key] = getter()
            except Exception as exc:
                record[key + "_error"] = repr(exc)
        try:
            record["nanite_enabled"] = bool(asset.get_editor_property("nanite_settings").enabled)
        except Exception as exc:
            record["nanite_enabled_error"] = repr(exc)
        try:
            body_setup = asset.get_editor_property("body_setup")
            record["body_setup_present"] = body_setup is not None
            if body_setup is not None:
                record["collision_trace_flag"] = str(body_setup.get_editor_property("collision_trace_flag"))
        except Exception as exc:
            record["body_setup_error"] = repr(exc)
    elif isinstance(asset, unreal.Texture2D):
        for key, getter in (
            ("size_x", lambda: int(asset.blueprint_get_size_x())),
            ("size_y", lambda: int(asset.blueprint_get_size_y())),
            ("srgb", lambda: bool(asset.get_editor_property("srgb"))),
            ("compression_settings", lambda: str(asset.get_editor_property("compression_settings"))),
            ("virtual_texture_streaming", lambda: bool(asset.get_editor_property("virtual_texture_streaming"))),
        ):
            try:
                record[key] = getter()
            except Exception as exc:
                record[key + "_error"] = repr(exc)
    elif isinstance(asset, unreal.MaterialInstanceConstant):
        parent = asset.get_editor_property("parent")
        record["parent"] = parent.get_path_name() if parent else ""
        record["texture_parameters"] = {
            str(name): (
                value.get_path_name()
                if (value := unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(asset, name))
                else ""
            )
            for name in unreal.MaterialEditingLibrary.get_texture_parameter_names(asset)
        }
    else:
        raise RuntimeError("ABIVERD_ARCH_AUDIT_UNEXPECTED_CLASS %s %s" % (path, record["class"]))
    records.append(record)

dirty_maps = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
dirty_content = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
unexpected_dirty = [name for name in dirty_maps + dirty_content if not name.startswith(ROOT + "/")]

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_heritage_architecture_stage_audit_v1.json")
payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "asset_count": len(records),
    "records": records,
    "dirty_map_packages": sorted(dirty_maps),
    "dirty_content_packages": sorted(dirty_content),
    "unexpected_dirty_packages": sorted(unexpected_dirty),
    "safe_map_only_scope": not unexpected_dirty and not dirty_maps,
    "changes_made": False,
    "level_saved": False,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_ARCH_AUDIT_COMPLETE assets=%d report=%s" % (len(records), report_path))
print("ABIVERD_ARCH_AUDIT_COMPLETE", len(records), report_path)
