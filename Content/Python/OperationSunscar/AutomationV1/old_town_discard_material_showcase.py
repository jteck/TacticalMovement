"""Remove only the transient material-review actors created outside Old Town."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actor_system = common.actor_subsystem()
targets = sorted(
    [actor for actor in actor_system.get_all_level_actors() if actor.get_actor_label().startswith("TEMP_OT_MAT_")],
    key=lambda actor: actor.get_actor_label(),
)
labels = [actor.get_actor_label() for actor in targets]
for actor in targets:
    actor_system.destroy_actor(actor)

payload = {
    "schema_version": 1,
    "status": "transient_showcase_removed",
    "context": context,
    "destroyed_actor_count": len(labels),
    "destroyed_actor_labels": labels,
    "level_saved": False,
    "persistent_map_assets_changed": False,
}
report = common.write_json_report(config, "old_town_discard_material_showcase.json", payload)
unreal.log("SUNSCAR_SHOWCASE_DISCARD actors=%d report=%s" % (len(labels), report))
print("SUNSCAR_SHOWCASE_DISCARD", len(labels), report)
