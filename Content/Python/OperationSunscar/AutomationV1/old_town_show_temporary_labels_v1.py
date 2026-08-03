"""Restore temporary Old Town TextRender navigation labels without dirtying packages."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
before_content = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
before_maps = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
targets = [
    actor for actor in common.actor_subsystem().get_all_level_actors()
    if isinstance(actor, unreal.TextRenderActor) and common.actor_folder(actor).startswith("Sunscar/TemporaryLabels")
]
for actor in targets:
    actor.set_is_temporarily_hidden_in_editor(False)
after_content = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
after_maps = [package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
if before_content != after_content or before_maps != after_maps:
    raise RuntimeError("SUNSCAR_SHOW_LABELS_DIRTIED_PACKAGES")
payload = {
    "schema_version": 1,
    "status": "temporary_labels_visible",
    "context": context,
    "actor_count": len(targets),
    "dirty_content_packages": after_content,
    "dirty_map_packages": after_maps,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_show_temporary_labels_v1.json", payload)
unreal.log("SUNSCAR_SHOW_LABELS actors=%d report=%s" % (len(targets), report))
print("SUNSCAR_SHOW_LABELS", len(targets), report)
