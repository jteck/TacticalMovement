"""Save exactly the 16 grounded Salvage Yard corrugated actor packages."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarCorrugatedAssemblyGroundV1"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = [actor for actor in common.actor_subsystem().get_all_level_actors() if TAG in common.actor_tags(actor)]
if len(actors) != 16:
    raise RuntimeError("SUNSCAR_CORR_SAVE_REFUSED actor_count=%d" % len(actors))
packages = {actor.get_package() for actor in actors}
names = {package.get_name() for package in packages}
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
dirty_names = {package.get_name() for package in dirty_maps}
if dirty_content or dirty_names != names:
    raise RuntimeError("SUNSCAR_CORR_SAVE_REFUSED content=%d dirty=%s targets=%s" % (len(dirty_content), "|".join(sorted(dirty_names)), "|".join(sorted(names))))
if not unreal.EditorLoadingAndSavingUtils.save_packages(list(packages), True):
    raise RuntimeError("SUNSCAR_CORR_SAVE_FAILED")
remaining = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages() if package.get_name() in names)
payload = {"schema_version": 1, "status": "exact_packages_saved", "context": context, "actor_count": len(actors), "package_count": len(packages), "saved_packages": sorted(names), "remaining_target_dirty_packages": remaining}
report = common.write_json_report(config, "old_town_save_corrugated_assemblies_v1.json", payload)
unreal.log("SUNSCAR_CORR_SAVE packages=%d remaining=%d report=%s" % (len(packages), len(remaining), report))
