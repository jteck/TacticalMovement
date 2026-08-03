"""Save only the verified Old Town facade-conduit World Partition packages."""

import json
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownFacadeConduitV1"
EXPECTED_ACTORS = 16
EXPECTED_PACKAGES = 25
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = [actor for actor in common.actor_subsystem().get_all_level_actors() if TAG in common.actor_tags(actor)]
if len(actors) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_SAVE_REFUSED expected_actors=%d actual=%d" % (EXPECTED_ACTORS, len(actors)))

audit_path = os.path.join(common.report_directory(config), "old_town_facade_conduit_audit_v1.json")
with open(audit_path, "r", encoding="utf-8") as handle:
    audit = json.load(handle)
if audit.get("actor_count") != EXPECTED_ACTORS or audit.get("review_required_count") != 0 or audit.get("pair_overlap_count") != 0:
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_SAVE_REFUSED audit_not_clean")

content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if content:
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_SAVE_REFUSED dirty_content=%d" % len(content))


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
        "SUNSCAR_FACADE_CONDUIT_SAVE_REFUSED packages=%d unexpected=%s"
        % (len(names), " | ".join(unexpected))
    )
if not unreal.EditorLoadingAndSavingUtils.save_packages(maps, True):
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_SAVE_FAILED")

target_names = set(names)
remaining = [
    package_name(package)
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package_name(package) in target_names
]
if remaining:
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_SAVE_INCOMPLETE " + " | ".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_facade_conduit_saved",
    "context": context,
    "actor_count": len(actors),
    "saved_package_count": len(names),
    "saved_packages": names,
    "remaining_target_dirty_packages": remaining,
    "protected_or_unrelated_packages_saved": False,
}
report = common.write_json_report(config, "old_town_save_facade_conduit_v1.json", payload)
unreal.log("SUNSCAR_FACADE_CONDUIT_SAVE actors=%d packages=%d report=%s" % (len(actors), len(names), report))
print("SUNSCAR_FACADE_CONDUIT_SAVE", len(actors), len(names), report)
