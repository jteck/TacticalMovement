"""Discard exactly the ten rejected unsaved SS_017 flaked-facade packages."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarFlakedFacadePrototypeV1"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = sorted(
    [actor for actor in common.actor_subsystem().get_all_level_actors() if PASS_TAG in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
if len(actors) != 10:
    raise RuntimeError("SUNSCAR_FLAKED_DISCARD_REFUSED actors=%d" % len(actors))
packages = {actor.get_package() for actor in actors}
target_names = {package.get_name() for package in packages}
dirty_content = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content or dirty_maps != target_names:
    raise RuntimeError("SUNSCAR_FLAKED_DISCARD_REFUSED content=%s maps=%s" % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps))))
reloaded, error = unreal.EditorLoadingAndSavingUtils.reload_packages(
    list(packages), unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE
)
if not reloaded:
    raise RuntimeError("SUNSCAR_FLAKED_DISCARD_RELOAD_FAILED error=%s" % error)
remaining = sorted(package.get_name() for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()))
if remaining:
    raise RuntimeError("SUNSCAR_FLAKED_DISCARD_DIRTY_AFTER %s" % "|".join(remaining))
payload = {"schema_version": 1, "status": "rejected_flaked_facade_preview_reloaded", "context": context, "reloaded_packages": sorted(target_names), "dirty_packages_after": remaining, "changes_saved": False}
report = common.write_json_report(config, "old_town_discard_flaked_facade_preview_v1.json", payload)
unreal.log("SUNSCAR_FLAKED_DISCARD packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_FLAKED_DISCARD", len(packages), report)
