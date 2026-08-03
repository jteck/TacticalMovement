"""Discard only the unsaved, explicitly tagged connected-slice preview actors."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
tag = unreal.Name(config["execution"]["placement_tag"])
actor_system = common.actor_subsystem()
targets = [
    actor
    for actor in list(actor_system.get_all_level_actors())
    if tag in list(actor.tags)
    and actor.get_actor_label().startswith("OT_AUTO_")
    and unreal.Name("UnreviewedAutomationPlacement") in list(actor.tags)
]
labels = [actor.get_actor_label() for actor in targets]
for actor in targets:
    actor_system.destroy_actor(actor)

payload = {
    "schema_version": 1,
    "status": "unsaved_preview_discarded",
    "context": context,
    "destroyed_actor_count": len(targets),
    "destroyed_actor_labels": labels,
    "scope": "Only OT_AUTO_ actors carrying both the configured connected-slice tag and UnreviewedAutomationPlacement tag.",
    "level_saved": False,
}
report = common.write_json_report(
    config, "old_town_connected_slice_discard_preview.json", payload
)
unreal.log(
    "SUNSCAR_CONNECTED_SLICE_DISCARD destroyed=%d report=%s"
    % (len(targets), report)
)
print("SUNSCAR_CONNECTED_SLICE_DISCARD", len(targets), report)
