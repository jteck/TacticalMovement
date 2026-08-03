"""Expand the reviewed SS_010 support plinth to the full building footprint, unsaved."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarSS010FoundationSupportV1"
LABEL = "Foundation_SS_010_West_Support"
TARGET_ORIGIN = unreal.Vector(2200.0, 9100.0, 34954.8)
TARGET_SCALE = unreal.Vector(34.0, 28.0, 0.6)
TARGET_EXTENT = unreal.Vector(1700.0, 1400.0, 30.0)


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if dirty_before:
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_DIRTY_BEFORE_REFUSED %s" % "|".join(dirty_before))
actors = [
    actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if PASS_TAG in common.actor_tags(actor)
]
if len(actors) != 1 or actors[0].get_actor_label() != LABEL:
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_ACTOR_REFUSED count=%d" % len(actors))
actor = actors[0]
old_origin, old_extent = actor.get_actor_bounds(False)
if (
    abs(old_origin.x - 1350.0) > 0.1
    or abs(old_origin.y - 9100.0) > 0.1
    or abs(old_origin.z - 34954.8) > 0.1
    or abs(old_extent.x - 850.0) > 0.1
    or abs(old_extent.y - 1400.0) > 0.1
    or abs(old_extent.z - 30.0) > 0.1
):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_SOURCE_BOUNDS_REFUSED")

actor.modify()
actor.static_mesh_component.modify()
actor.set_actor_scale3d(TARGET_SCALE)
origin, extent = actor.get_actor_bounds(False)
actor.add_actor_world_offset(TARGET_ORIGIN - origin, False, False)
origin, extent = actor.get_actor_bounds(False)
if (
    abs(origin.x - TARGET_ORIGIN.x) > 0.1
    or abs(origin.y - TARGET_ORIGIN.y) > 0.1
    or abs(origin.z - TARGET_ORIGIN.z) > 0.1
    or abs(extent.x - TARGET_EXTENT.x) > 0.1
    or abs(extent.y - TARGET_EXTENT.y) > 0.1
    or abs(extent.z - TARGET_EXTENT.z) > 0.1
):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_EXPAND_TARGET_BOUNDS_REFUSED")

dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
actor_package = actor.get_package().get_name()
if dirty_content or dirty_maps != [actor_package]:
    raise RuntimeError(
        "SUNSCAR_SS010_SUPPORT_EXPAND_DIRTY_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_ss010_foundation_support_expanded",
    "context": context,
    "actor_count": 1,
    "label": LABEL,
    "actor_package": actor_package,
    "source_origin_cm": [old_origin.x, old_origin.y, old_origin.z],
    "source_extent_cm": [old_extent.x, old_extent.y, old_extent.z],
    "target_origin_cm": [origin.x, origin.y, origin.z],
    "target_extent_cm": [extent.x, extent.y, extent.z],
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_ss010_foundation_support_expand_v1.json", payload)
unreal.log("SUNSCAR_SS010_SUPPORT_EXPAND actor=%s report=%s" % (LABEL, report))
print("SUNSCAR_SS010_SUPPORT_EXPAND", LABEL, report)
