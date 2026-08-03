"""Save only the verified World Partition package for eight grass replacements."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOfficialGrassReplacementV1")
EXPECTED_ACTORS = 8
EXPECTED_PACKAGES = 1
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = [actor for actor in common.actor_subsystem().get_all_level_actors() if TAG in list(actor.tags)]
if len(actors) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_GRASS_SAVE_REFUSED expected_actors=%d actual=%d" % (EXPECTED_ACTORS, len(actors)))

dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if dirty_content:
    raise RuntimeError("SUNSCAR_GRASS_SAVE_REFUSED dirty_content=%d" % len(dirty_content))


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


names = sorted(package_name(package) for package in dirty_maps)
prefix = "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/"
unexpected = [name for name in names if not name.startswith(prefix)]
if unexpected or len(names) != EXPECTED_PACKAGES:
    raise RuntimeError(
        "SUNSCAR_GRASS_SAVE_REFUSED packages=%d unexpected=%s"
        % (len(names), " | ".join(unexpected))
    )

if not unreal.EditorLoadingAndSavingUtils.save_packages(dirty_maps, True):
    raise RuntimeError("SUNSCAR_GRASS_SAVE_FAILED")
remaining = [
    package_name(package)
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package_name(package) in set(names)
]
if remaining:
    raise RuntimeError("SUNSCAR_GRASS_SAVE_INCOMPLETE " + " | ".join(remaining))

payload = {
    "schema_version": 1,
    "status": "verified_grass_replacement_saved",
    "context": context,
    "actor_count": len(actors),
    "saved_package_count": len(names),
    "saved_packages": names,
    "remaining_target_dirty_packages": remaining,
    "protected_or_unrelated_packages_saved": False,
}
report = common.write_json_report(config, "old_town_save_grass_replacement_v1.json", payload)
unreal.log("SUNSCAR_GRASS_SAVE actors=%d packages=%d report=%s" % (len(actors), len(names), report))
print("SUNSCAR_GRASS_SAVE", len(actors), len(names), report)
