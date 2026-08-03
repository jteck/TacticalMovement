"""Save only the verified Old Town furniture World Partition packages."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


EXPECTED_ACTORS = 62
EXPECTED_PACKAGES = 68
TAG = unreal.Name("SunscarOldTownFurnitureV1")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
preview = [
    actor
    for actor in actors
    if TAG in list(actor.tags) and actor.get_actor_label().startswith("OT_FURN_")
]
if len(preview) != EXPECTED_ACTORS:
    raise RuntimeError(
        "SUNSCAR_FURNITURE_SAVE_REFUSED expected_actors=%d actual=%d"
        % (EXPECTED_ACTORS, len(preview))
    )

dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if dirty_content:
    raise RuntimeError(
        "SUNSCAR_FURNITURE_SAVE_REFUSED dirty_content_packages=%d" % len(dirty_content)
    )


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
    raise RuntimeError(
        "SUNSCAR_FURNITURE_SAVE_REFUSED unexpected_packages=" + " | ".join(unexpected)
    )
if len(package_names) != EXPECTED_PACKAGES:
    raise RuntimeError(
        "SUNSCAR_FURNITURE_SAVE_REFUSED expected_packages=%d actual=%d"
        % (EXPECTED_PACKAGES, len(package_names))
    )

saved = unreal.EditorLoadingAndSavingUtils.save_packages(dirty_maps, True)
if not saved:
    raise RuntimeError("SUNSCAR_FURNITURE_SAVE_FAILED save_packages_returned_false")

target_names = set(package_names)
remaining = sorted(
    package_name(package)
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package_name(package) in target_names
)
if remaining:
    raise RuntimeError(
        "SUNSCAR_FURNITURE_SAVE_INCOMPLETE remaining=" + " | ".join(remaining)
    )

payload = {
    "schema_version": 1,
    "status": "verified_furniture_packages_saved",
    "context": context,
    "furniture_actor_count": len(preview),
    "saved_package_count": len(package_names),
    "saved_packages": package_names,
    "dirty_content_package_count": 0,
    "remaining_target_dirty_packages": remaining,
    "protected_or_unrelated_packages_saved": False,
}
report = common.write_json_report(config, "old_town_save_furniture_packages_v1.json", payload)
unreal.log(
    "SUNSCAR_FURNITURE_SAVE actors=%d packages=%d report=%s"
    % (len(preview), len(package_names), report)
)
print("SUNSCAR_FURNITURE_SAVE", len(preview), len(package_names), report)
