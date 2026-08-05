"""Read-only state probe for the unsaved Abiverd surface batch."""

import json
import os

import unreal


root = "/Game/Maps/Sunscar/Art/Heritage/Surfaces"
paths = sorted(unreal.EditorAssetLibrary.list_assets(root, recursive=True, include_folder=False))
rows = []
for path in paths:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    row = {"path": path, "class": asset.get_class().get_name() if asset else ""}
    if isinstance(asset, unreal.Texture2D):
        for key, getter in (
            ("size_x", lambda: int(asset.blueprint_get_size_x())),
            ("size_y", lambda: int(asset.blueprint_get_size_y())),
            ("srgb", lambda: bool(asset.get_editor_property("srgb"))),
            ("compression", lambda: str(asset.get_editor_property("compression_settings"))),
            ("virtual_texture_streaming", lambda: bool(asset.get_editor_property("virtual_texture_streaming"))),
            ("package", lambda: asset.get_package().get_name()),
        ):
            try:
                row[key] = getter()
            except Exception as exc:
                row[key + "_error"] = repr(exc)
    rows.append(row)

dirty_content = []
for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages():
    try:
        dirty_content.append(package.get_name())
    except Exception as exc:
        dirty_content.append("ERROR:" + repr(exc))
dirty_maps = []
for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
    try:
        dirty_maps.append(package.get_name())
    except Exception as exc:
        dirty_maps.append("ERROR:" + repr(exc))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report = os.path.join(report_root, "abiverd_heritage_surfaces_state_probe_v1.json")
with open(report, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "asset_count": len(rows),
            "rows": rows,
            "dirty_content": sorted(dirty_content),
            "dirty_maps": sorted(dirty_maps),
        },
        handle,
        indent=2,
    )
    handle.write("\n")
print("ABIVERD_SURFACE_STATE_PROBE", len(rows), report)
