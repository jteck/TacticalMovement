"""Resolve the two remaining SS_014 decorations floating above Landscape."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


EXPECTED = {
    "OT_INDDETAIL_SS_014_INDUSTRIAL_004",
    "OT_INDDETAIL_SS_014_INDUSTRIAL_009",
}


config = common.load_config()
apply_changes = bool(config.get("execution", {}).get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_changes)
dirty_content_before = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps_before = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content_before or dirty_maps_before:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_REFUSED dirty_scope")

source = common.read_json(
    os.path.join(common.report_directory(config), "old_town_industrial_detail_audit_v1.json")
)
review = source.get("review_required", [])
if {record.get("label") for record in review} != EXPECTED:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_REFUSED review_scope")

by_label = {
    actor.get_actor_label(): actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if actor.get_actor_label() in EXPECTED
}
if set(by_label) != EXPECTED:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_REFUSED actor_scope")

records = []
for source_record in sorted(review, key=lambda record: record["label"]):
    label = source_record["label"]
    gap = float(source_record["support_gap_cm"])
    if not 3.0 < gap < 10.0 or "Landscape" not in source_record.get("support_actor", ""):
        raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_REFUSED gap " + label)
    actor = by_label[label]
    if apply_changes:
        actor.modify()
        actor.add_actor_world_offset(unreal.Vector(0.0, 0.0, -gap), False, False)
    records.append({
        "label": label,
        "support_actor": source_record["support_actor"],
        "before_gap_cm": round(gap, 3),
        "delta_z_cm": round(-gap, 3),
        "package": actor.get_package().get_name(),
    })

expected_packages = {record["package"] for record in records}
dirty_content_after = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps_after = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if apply_changes:
    if dirty_content_after or dirty_maps_after != expected_packages:
        raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_SCOPE_FAILED")
else:
    if dirty_content_after or dirty_maps_after:
        raise RuntimeError("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT_DRY_RUN_DIRTIED_PACKAGES")

payload = {
    "schema_version": 1,
    "status": "industrial_landscape_support_applied_unsaved" if apply_changes else "industrial_landscape_support_dry_run_complete",
    "context": context,
    "apply_changes": apply_changes,
    "actor_count": len(records),
    "records": records,
    "dirty_map_packages": sorted(dirty_maps_after),
    "changes_made": apply_changes,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_industrial_detail_landscape_support_fix_v2.json", payload)
unreal.log(
    "SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT apply=%s actors=%d maps=%d report=%s"
    % (apply_changes, len(records), len(dirty_maps_after), report)
)
print("SUNSCAR_INDUSTRIAL_LANDSCAPE_SUPPORT", apply_changes, len(records), len(dirty_maps_after), report)
