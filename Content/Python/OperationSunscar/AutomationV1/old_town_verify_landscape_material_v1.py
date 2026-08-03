"""Read-only verification for the finalized Old Town Landscape material pass."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Landscape/MI_OT_Landscape_Sandstone"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
material = unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
records = []
for actor in sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if isinstance(actor, unreal.LandscapeProxy)
    ],
    key=lambda actor: actor.get_actor_label(),
):
    assigned = actor.get_editor_property("landscape_material")
    records.append({
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_name(),
        "landscape_material": assigned.get_path_name() if assigned else "",
        "tags": common.actor_tags(actor),
        "package": actor.get_package().get_name(),
    })

dirty = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
payload = {
    "schema_version": 1,
    "status": "read_only_verification_complete",
    "context": context,
    "material_path": TARGET_PATH,
    "material_loaded": material is not None,
    "material_parent": material.parent.get_path_name() if material and material.parent else "",
    "landscape_actor_count": len(records),
    "records": records,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_verify_landscape_material_v1.json", payload)
unreal.log("SUNSCAR_LANDSCAPE_VERIFY actors=%d dirty=%d report=%s" % (len(records), len(dirty), report))
print("SUNSCAR_LANDSCAPE_VERIFY", len(records), len(dirty), report)
