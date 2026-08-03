"""Save only the 20 verified packages for 13 support-resolved small electrical boxes."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownElectricalBoxesV2")
EXPECTED_ACTORS = 13
EXPECTED_PACKAGES = 20
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = [actor for actor in common.actor_subsystem().get_all_level_actors() if TAG in list(actor.tags)]
if len(actors) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_REMAINING_ELECTRICAL_SAVE_REFUSED actors=%d" % len(actors))
content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if content:
    raise RuntimeError("SUNSCAR_REMAINING_ELECTRICAL_SAVE_REFUSED dirty_content=%d" % len(content))


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


names = sorted(package_name(package) for package in maps)
prefixes = (
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
)
unexpected = [name for name in names if not name.startswith(prefixes)]
if unexpected or len(names) != EXPECTED_PACKAGES:
    raise RuntimeError(
        "SUNSCAR_REMAINING_ELECTRICAL_SAVE_REFUSED packages=%d unexpected=%s"
        % (len(names), " | ".join(unexpected))
    )
if not unreal.EditorLoadingAndSavingUtils.save_packages(maps, True):
    raise RuntimeError("SUNSCAR_REMAINING_ELECTRICAL_SAVE_FAILED")
target_names = set(names)
remaining = [
    package_name(package)
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package_name(package) in target_names
]
if remaining:
    raise RuntimeError("SUNSCAR_REMAINING_ELECTRICAL_SAVE_INCOMPLETE " + " | ".join(remaining))
payload = {
    "schema_version": 1,
    "status": "verified_remaining_small_electrical_saved",
    "context": context,
    "actor_count": len(actors),
    "saved_package_count": len(names),
    "saved_packages": names,
    "remaining_target_dirty_packages": remaining,
    "protected_or_unrelated_packages_saved": False,
}
report = common.write_json_report(config, "old_town_save_remaining_small_electrical_v1.json", payload)
unreal.log(
    "SUNSCAR_REMAINING_ELECTRICAL_SAVE actors=%d packages=%d report=%s"
    % (len(actors), len(names), report)
)
print("SUNSCAR_REMAINING_ELECTRICAL_SAVE", len(actors), len(names), report)
