"""Save only the verified Old Town exterior, ground-conformance, and lighting packages."""

import json
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


EXPECTED_DIRTY_MAP_PACKAGES = 412
EXPECTED_EXTERNAL_ACTORS = 401
EXPECTED_EXTERNAL_OBJECTS = 11
EXPECTED_EXTERIOR_ACTORS = 112
EXPECTED_GROUND_ACTORS = 288

config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
exterior = [actor for actor in actors if "SunscarOldTownExteriorCompletionV1" in common.actor_tags(actor)]
ground = [actor for actor in actors if "SunscarGroundOverlayConformanceV1" in common.actor_tags(actor)]
lighting = [actor for actor in actors if "SunscarOldTownLightingBalanceV1" in common.actor_tags(actor)]
if len(exterior) != EXPECTED_EXTERIOR_ACTORS or len(ground) != EXPECTED_GROUND_ACTORS or len(lighting) != 1:
    raise RuntimeError("SUNSCAR_EXTERIOR_SAVE_SCOPE_REFUSED exterior=%d ground=%d lighting=%d" % (len(exterior), len(ground), len(lighting)))

for filename in (
    "old_town_exterior_completion_audit_v2.json",
    "old_town_ground_overlay_conformance_audit_v1.json",
    "old_town_lighting_balance_audit_v1.json",
    "old_town_sandbag_audit.json",
):
    path = os.path.join(common.report_directory(config), filename)
    with open(path, "r", encoding="utf-8") as handle:
        report = json.load(handle)
    if report.get("review_required_count", 0) != 0:
        raise RuntimeError("SUNSCAR_EXTERIOR_SAVE_AUDIT_REFUSED " + filename)

content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if content:
    raise RuntimeError("SUNSCAR_EXTERIOR_SAVE_REFUSED dirty_content=%d" % len(content))


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


names = sorted(package_name(package) for package in maps)
external_actor_prefix = "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/"
external_object_prefix = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"
actor_names = [name for name in names if name.startswith(external_actor_prefix)]
object_names = [name for name in names if name.startswith(external_object_prefix)]
unexpected = [name for name in names if not name.startswith((external_actor_prefix, external_object_prefix))]
if (
    len(names) != EXPECTED_DIRTY_MAP_PACKAGES
    or len(actor_names) != EXPECTED_EXTERNAL_ACTORS
    or len(object_names) != EXPECTED_EXTERNAL_OBJECTS
    or unexpected
):
    raise RuntimeError(
        "SUNSCAR_EXTERIOR_SAVE_DIRTY_SCOPE_REFUSED total=%d actors=%d objects=%d unexpected=%s"
        % (len(names), len(actor_names), len(object_names), "|".join(unexpected))
    )

intentional_actor_packages = {actor.get_package().get_name() for actor in exterior + ground + lighting}
if intentional_actor_packages != set(actor_names):
    missing = sorted(intentional_actor_packages - set(actor_names))
    extra = sorted(set(actor_names) - intentional_actor_packages)
    raise RuntimeError("SUNSCAR_EXTERIOR_SAVE_ACTOR_SCOPE_REFUSED missing=%s extra=%s" % ("|".join(missing), "|".join(extra)))

if not unreal.EditorLoadingAndSavingUtils.save_packages(maps, True):
    raise RuntimeError("SUNSCAR_EXTERIOR_SAVE_FAILED")
remaining = sorted(
    package_name(package)
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if package_name(package) in set(names)
)
if remaining:
    raise RuntimeError("SUNSCAR_EXTERIOR_SAVE_INCOMPLETE " + "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_exterior_completion_packages_saved",
    "context": context,
    "exterior_actor_count": len(exterior),
    "ground_actor_count": len(ground),
    "lighting_actor_count": len(lighting),
    "saved_package_count": len(names),
    "saved_external_actor_count": len(actor_names),
    "saved_external_object_count": len(object_names),
    "saved_packages": names,
    "remaining_target_dirty_packages": remaining,
    "protected_or_unrelated_packages_saved": False,
}
report = common.write_json_report(config, "old_town_save_exterior_completion_v1.json", payload)
unreal.log("SUNSCAR_EXTERIOR_COMPLETION_SAVE packages=%d actors=%d objects=%d report=%s" % (len(names), len(actor_names), len(object_names), report))
print("SUNSCAR_EXTERIOR_COMPLETION_SAVE", len(names), len(actor_names), len(object_names), report)
