"""Apply a restrained map-only exposure correction for Old Town readability."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownLightingBalanceV1")
TARGET_LABEL = "Sunscar_PostProcessVolume"
EXPOSURE_BIAS = -0.75

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
actors = list(common.actor_subsystem().get_all_level_actors())
matches = [actor for actor in actors if actor.get_actor_label() == TARGET_LABEL and isinstance(actor, unreal.PostProcessVolume)]
if len(matches) != 1:
    raise RuntimeError("SUNSCAR_LIGHTING_BALANCE_SCOPE_REFUSED post_process_count=%d" % len(matches))
actor = matches[0]
settings = actor.get_editor_property("settings")
before = {
    "override_auto_exposure_bias": bool(settings.get_editor_property("override_auto_exposure_bias")),
    "auto_exposure_bias": float(settings.get_editor_property("auto_exposure_bias")),
    "unbound": bool(actor.get_editor_property("unbound")),
}
if apply_requested:
    actor.modify()
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", EXPOSURE_BIAS)
    actor.set_editor_property("settings", settings)
    actor.set_editor_property("unbound", True)
    if TAG not in list(actor.tags):
        actor.tags = list(actor.tags) + [TAG]
after_settings = actor.get_editor_property("settings")
after = {
    "override_auto_exposure_bias": bool(after_settings.get_editor_property("override_auto_exposure_bias")),
    "auto_exposure_bias": float(after_settings.get_editor_property("auto_exposure_bias")),
    "unbound": bool(actor.get_editor_property("unbound")),
}
payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_label": actor.get_actor_label(),
    "actor_package": actor.get_package().get_name(),
    "before": before,
    "after": after,
    "changes_made": apply_requested,
    "level_saved": False,
    "scope": "Map-local PostProcessVolume only; no project configuration or camera assets changed.",
}
filename = "old_town_lighting_balance_apply_preview_v1.json" if apply_requested else "old_town_lighting_balance_dry_run_v1.json"
report = common.write_json_report(config, filename, payload)
unreal.log("SUNSCAR_LIGHTING_BALANCE mode=%s bias=%.2f report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", after["auto_exposure_bias"], report))
print("SUNSCAR_LIGHTING_BALANCE", after["auto_exposure_bias"], report)
