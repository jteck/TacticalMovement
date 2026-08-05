"""Discard only orphaned unsaved ExternalObjects left by the failed preview."""

import json
import os

import unreal


prefix = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
packages = dirty_content + dirty_maps
names = sorted(package.get_name() for package in packages)
if not names or any(not name.startswith(prefix) for name in names):
    raise RuntimeError("ABIVERD_EXTERNAL_OBJECT_RELOAD_REFUSED " + "|".join(names))
reloaded, error = unreal.EditorLoadingAndSavingUtils.reload_packages(
    packages, unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE
)
if not reloaded:
    raise RuntimeError("ABIVERD_EXTERNAL_OBJECT_RELOAD_FAILED " + str(error))
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "status": "orphaned_external_objects_reloaded",
    "reloaded_packages": names,
    "dirty_after": remaining,
    "changes_saved": False,
}
path = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", "abiverd_reload_partial_external_objects_v1.json"
)
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_EXTERNAL_OBJECT_RELOAD dirty_after=%d" % len(remaining))
