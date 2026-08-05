"""Write a minimal state report for the current unsaved architecture batch."""

import json
import os

import unreal


root = "/Game/Maps/Sunscar/Art/Heritage/Architecture"
paths = sorted(unreal.EditorAssetLibrary.list_assets(root, recursive=True, include_folder=False))
rows = []
for path in paths:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    row = {"path": path, "class": asset.get_class().get_name() if asset else ""}
    if isinstance(asset, unreal.StaticMesh):
        row["material"] = asset.get_material(0).get_path_name() if asset.get_material(0) else ""
        try:
            row["nanite"] = bool(asset.get_editor_property("nanite_settings").enabled)
        except Exception as exc:
            row["nanite_error"] = repr(exc)
    if isinstance(asset, unreal.MaterialInstanceConstant):
        parent = asset.get_editor_property("parent")
        row["parent"] = parent.get_path_name() if parent else ""
        row["textures"] = {
            str(name): (
                value.get_path_name()
                if (value := unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(asset, name))
                else ""
            )
            for name in unreal.MaterialEditingLibrary.get_texture_parameter_names(asset)
        }
    rows.append(row)

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report = os.path.join(report_root, "abiverd_heritage_architecture_state_probe_v1.json")
with open(report, "w", encoding="utf-8") as handle:
    json.dump({"asset_count": len(rows), "rows": rows}, handle, indent=2)
    handle.write("\n")
print("ABIVERD_ARCH_STATE_PROBE", len(rows), report)
