"""Discard only the visually rejected, unsaved facade-damage preview actors."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownFacadeDamageV1")
UNREVIEWED = unreal.Name("UnreviewedAutomationPlacement")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actor_system = common.actor_subsystem()
targets = [
    actor for actor in actor_system.get_all_level_actors()
    if TAG in list(actor.tags)
    and UNREVIEWED in list(actor.tags)
    and actor.get_actor_label().startswith("OT_DAMAGE_")
]
if len(targets) != 44:
    raise RuntimeError("SUNSCAR_FACADE_DISCARD_REFUSED expected=44 actual=%d" % len(targets))
labels = sorted(actor.get_actor_label() for actor in targets)
for actor in targets:
    actor_system.destroy_actor(actor)
payload = {
    "schema_version": 1, "status": "rejected_preview_discarded", "context": context,
    "destroyed_actor_count": len(labels), "destroyed_actor_labels": labels,
    "rejection_reason": "Visual review showed flat brown panels rather than believable plaster damage.",
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_discard_facade_damage_preview_v1.json", payload)
unreal.log("SUNSCAR_FACADE_DISCARD actors=%d report=%s" % (len(labels), report))
print("SUNSCAR_FACADE_DISCARD", len(labels), report)
