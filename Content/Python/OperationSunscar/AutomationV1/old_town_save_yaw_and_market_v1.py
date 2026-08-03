"""Save only the 173 verified packages for the yaw correction and market pass."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


YAW_TAG = unreal.Name("SunscarAutomationYawCorrectionV1")
MARKET_TAG = unreal.Name("SunscarOldTownMarketGroundDebrisV1")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
yaw_actors = [actor for actor in actors if YAW_TAG in list(actor.tags)]
market_actors = [actor for actor in actors if MARKET_TAG in list(actor.tags)]
if len(yaw_actors) != 171 or len(market_actors) != 24:
    raise RuntimeError("SUNSCAR_YAW_MARKET_SAVE_REFUSED yaw=%d market=%d" % (len(yaw_actors), len(market_actors)))

content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if content:
    raise RuntimeError("SUNSCAR_YAW_MARKET_SAVE_REFUSED dirty_content=%d" % len(content))


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
if unexpected or len(names) != 173:
    raise RuntimeError("SUNSCAR_YAW_MARKET_SAVE_REFUSED packages=%d unexpected=%s" % (len(names), " | ".join(unexpected)))
if not unreal.EditorLoadingAndSavingUtils.save_packages(maps, True):
    raise RuntimeError("SUNSCAR_YAW_MARKET_SAVE_FAILED")
target_names = set(names)
remaining = [package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages() if package_name(package) in target_names]
if remaining:
    raise RuntimeError("SUNSCAR_YAW_MARKET_SAVE_INCOMPLETE " + " | ".join(remaining))

payload = {
    "schema_version": 1,
    "status": "verified_yaw_correction_and_market_saved",
    "context": context,
    "yaw_corrected_actor_count": len(yaw_actors),
    "market_actor_count": len(market_actors),
    "saved_package_count": len(names),
    "saved_packages": names,
    "remaining_target_dirty_packages": remaining,
    "protected_or_unrelated_packages_saved": False,
}
report = common.write_json_report(config, "old_town_save_yaw_and_market_v1.json", payload)
unreal.log("SUNSCAR_YAW_MARKET_SAVE yaw=%d market=%d packages=%d report=%s" % (len(yaw_actors), len(market_actors), len(names), report))
print("SUNSCAR_YAW_MARKET_SAVE", len(yaw_actors), len(market_actors), len(names), report)
