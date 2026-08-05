"""Read-only API inspection for reverting the unsaved Landscape preview."""

import json
import os

import unreal


members = [name for name in dir(unreal.EditorLoadingAndSavingUtils) if "reload" in name.lower()]
payload = {
    "members": members,
    "docs": {
        name: str(getattr(unreal.EditorLoadingAndSavingUtils, name).__doc__)
        for name in members
    },
    "package_members": sorted(name for name in dir(unreal.Package) if any(term in name.lower() for term in ("dirty", "load", "save", "object"))),
    "package_tools_members": sorted(name for name in dir(unreal.PackageTools) if any(term in name.lower() for term in ("dirty", "load", "save", "unload", "reload"))),
    "system_members": sorted(name for name in dir(unreal.SystemLibrary) if any(term in name.lower() for term in ("dirty", "load", "save", "unload", "garbage"))),
}
root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(root, exist_ok=True)
path = os.path.join(root, "inspect_package_reload_api_v1.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
print("INSPECT_PACKAGE_RELOAD_API_V1", path)
