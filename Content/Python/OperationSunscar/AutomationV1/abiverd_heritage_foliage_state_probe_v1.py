"""Report current in-memory foliage staging state without modifying assets."""

import json
import os

import unreal


ROOT = "/Game/Maps/Sunscar/Art/Heritage/Foliage"


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


paths = sorted(unreal.EditorAssetLibrary.list_assets(ROOT, recursive=True, include_folder=False))
rows = []
mesh_subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for path in paths:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    row = {"path": path, "class": asset.get_class().get_name() if asset else None}
    if isinstance(asset, unreal.Texture2D):
        row.update(
            {
                "size": [asset.blueprint_get_size_x(), asset.blueprint_get_size_y()],
                "srgb": bool(asset.get_editor_property("srgb")),
                "compression": str(asset.get_editor_property("compression_settings")),
                "lod_group": str(asset.get_editor_property("lod_group")),
            }
        )
    elif isinstance(asset, unreal.StaticMesh):
        bounds = asset.get_bounds()
        row.update(
            {
                "lod_count": mesh_subsystem.get_lod_count(asset),
                "bounds_extent_cm": [bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z],
                "materials": [
                    value.material_interface.get_path_name() if value.material_interface else None
                    for value in asset.get_editor_property("static_materials")
                ],
                "nanite": bool(asset.get_editor_property("nanite_settings").enabled),
            }
        )
    elif isinstance(asset, unreal.MaterialInstanceConstant):
        parent = asset.get_editor_property("parent")
        row["parent"] = parent.get_path_name() if parent else None
    rows.append(row)

dirty = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_heritage_foliage_state_probe_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump({"asset_count": len(rows), "rows": rows, "dirty_packages": dirty}, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_FOLIAGE_STATE_PROBE_COMPLETE " + report_path)
