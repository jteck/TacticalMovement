"""Save exactly the ten reviewed SS_017 flaked-paint facade packages."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarFlakedFacadePrototypeV1"
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_Quixel.MI_OT_FlakedPaint_Quixel"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = sorted(
    [actor for actor in common.actor_subsystem().get_all_level_actors() if PASS_TAG in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
if len(actors) != 10:
    raise RuntimeError("SUNSCAR_FLAKED_FACADE_SAVE_REFUSED actors=%d" % len(actors))
for actor in actors:
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    if material is None or material.get_path_name() != TARGET_PATH:
        raise RuntimeError("SUNSCAR_FLAKED_FACADE_SAVE_REFUSED material=" + actor.get_actor_label())
packages = {actor.get_package() for actor in actors}
target_names = {package.get_name() for package in packages}
dirty_content = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content or dirty_maps != target_names:
    raise RuntimeError("SUNSCAR_FLAKED_FACADE_SAVE_REFUSED content=%s maps=%s" % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps))))
if not unreal.EditorLoadingAndSavingUtils.save_packages(list(packages), True):
    raise RuntimeError("SUNSCAR_FLAKED_FACADE_SAVE_FAILED")
remaining = sorted(package.get_name() for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()))
if remaining:
    raise RuntimeError("SUNSCAR_FLAKED_FACADE_SAVE_DIRTY_AFTER %s" % "|".join(remaining))
payload = {"schema_version": 1, "status": "exact_flaked_facade_packages_saved", "context": context, "actor_count": len(actors), "saved_packages": sorted(target_names), "dirty_packages_after": remaining, "changes_saved": True}
report = common.write_json_report(config, "old_town_save_flaked_facade_v1.json", payload)
unreal.log("SUNSCAR_FLAKED_FACADE_SAVE packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_FLAKED_FACADE_SAVE", len(packages), report)
