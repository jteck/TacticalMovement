"""Read-only audit of the bounded Old Town exposure correction."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = [actor for actor in common.actor_subsystem().get_all_level_actors() if actor.get_actor_label() == "Sunscar_PostProcessVolume"]
review = []
record = {}
if len(actors) != 1 or not isinstance(actors[0], unreal.PostProcessVolume):
    review.append("exact_post_process_volume_required")
else:
    actor = actors[0]
    settings = actor.get_editor_property("settings")
    record = {
        "label": actor.get_actor_label(),
        "package": actor.get_package().get_name(),
        "unbound": bool(actor.get_editor_property("unbound")),
        "override_auto_exposure_bias": bool(settings.get_editor_property("override_auto_exposure_bias")),
        "auto_exposure_bias": float(settings.get_editor_property("auto_exposure_bias")),
        "tag_present": "SunscarOldTownLightingBalanceV1" in common.actor_tags(actor),
    }
    if not record["unbound"]:
        review.append("post_process_not_unbound")
    if not record["override_auto_exposure_bias"] or abs(record["auto_exposure_bias"] + 0.75) > 0.001:
        review.append("unexpected_exposure_bias")
    if not record["tag_present"]:
        review.append("lighting_balance_tag_missing")
payload = {
    "schema_version": 1,
    "status": "read_only_lighting_balance_audit_complete",
    "context": context,
    "record": record,
    "review_required_count": len(review),
    "review": review,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_lighting_balance_audit_v1.json", payload)
unreal.log("SUNSCAR_LIGHTING_BALANCE_AUDIT review=%d report=%s" % (len(review), report))
print("SUNSCAR_LIGHTING_BALANCE_AUDIT", len(review), report)
