"""Remove only the transient Quixel facade review panels; never saves."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PREFIX = "TEMP_OT_FACADE_"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actor_system = common.actor_subsystem()
targets = sorted(
    [actor for actor in actor_system.get_all_level_actors() if actor.get_actor_label().startswith(PREFIX)],
    key=lambda actor: actor.get_actor_label(),
)
labels = [actor.get_actor_label() for actor in targets]
for actor in targets:
    actor_system.destroy_actor(actor)
dirty = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
if dirty:
    raise RuntimeError("SUNSCAR_FACADE_SHOWCASE_DISCARD_DIRTIED_PACKAGES %s" % "|".join(dirty))
payload = {
    "schema_version": 1,
    "status": "transient_showcase_removed",
    "context": context,
    "destroyed_actor_labels": labels,
    "dirty_packages": dirty,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_discard_facade_surface_showcase_v1.json", payload)
unreal.log("SUNSCAR_FACADE_SHOWCASE_DISCARD actors=%d report=%s" % (len(labels), report))
print("SUNSCAR_FACADE_SHOWCASE_DISCARD", len(labels), report)
