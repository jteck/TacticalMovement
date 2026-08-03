"""Read-only report of dirty Unreal packages before an intentional map save."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


content_names = sorted(package_name(package) for package in content)
map_names = sorted(package_name(package) for package in maps)
all_names = sorted(set(content_names + map_names))
allowed_prefixes = (
    "/Game/Maps/Blockout/Lvl_Blockout_01",
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/Maps/Sunscar/",
)
unexpected = [name for name in all_names if not name.startswith(allowed_prefixes)]
payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "dirty_content_packages": content_names,
    "dirty_map_packages": map_names,
    "dirty_package_count": len(all_names),
    "unexpected_dirty_packages": unexpected,
    "safe_map_only_scope": not unexpected,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_dirty_package_audit.json", payload)
unreal.log(
    "SUNSCAR_DIRTY_PACKAGE_AUDIT packages=%d unexpected=%d report=%s"
    % (len(all_names), len(unexpected), report)
)
print("SUNSCAR_DIRTY_PACKAGE_AUDIT", len(all_names), len(unexpected), report)
