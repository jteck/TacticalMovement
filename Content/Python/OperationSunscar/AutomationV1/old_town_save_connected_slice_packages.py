"""Save only verified dirty packages belonging to the Old Town blockout level."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actor_system = common.actor_subsystem()
tag = unreal.Name(config["execution"]["placement_tag"])
preview = [
    actor
    for actor in list(actor_system.get_all_level_actors())
    if tag in list(actor.tags) and actor.get_actor_label().startswith("OT_AUTO_")
]
if len(preview) != 60:
    raise RuntimeError("SUNSCAR_SAVE_REFUSED expected_preview=60 actual=%d" % len(preview))

dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if dirty_content:
    raise RuntimeError("SUNSCAR_SAVE_REFUSED dirty_content_packages=%d" % len(dirty_content))


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


allowed_prefixes = (
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
)
package_names = sorted(package_name(package) for package in dirty_maps)
unexpected = [name for name in package_names if not name.startswith(allowed_prefixes)]
if unexpected:
    raise RuntimeError("SUNSCAR_SAVE_REFUSED unexpected_packages=" + " | ".join(unexpected))
if len(package_names) != 67:
    raise RuntimeError("SUNSCAR_SAVE_REFUSED expected_dirty_packages=67 actual=%d" % len(package_names))

saved = unreal.EditorLoadingAndSavingUtils.save_packages(dirty_maps, True)
if not saved:
    raise RuntimeError("SUNSCAR_SAVE_FAILED save_packages_returned_false")

remaining = sorted(
    package_name(package)
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package_name(package) in set(package_names)
)
if remaining:
    raise RuntimeError("SUNSCAR_SAVE_INCOMPLETE remaining=" + " | ".join(remaining))

payload = {
    "schema_version": 1,
    "status": "verified_map_packages_saved",
    "context": context,
    "preview_actor_count": len(preview),
    "saved_package_count": len(package_names),
    "saved_packages": package_names,
    "dirty_content_package_count": 0,
    "remaining_target_dirty_packages": remaining,
    "protected_or_unrelated_packages_saved": False,
}
report = common.write_json_report(
    config, "old_town_save_connected_slice_packages.json", payload
)
unreal.log(
    "SUNSCAR_CONNECTED_SLICE_SAVE actors=%d packages=%d report=%s"
    % (len(preview), len(package_names), report)
)
print("SUNSCAR_CONNECTED_SLICE_SAVE", len(preview), len(package_names), report)
