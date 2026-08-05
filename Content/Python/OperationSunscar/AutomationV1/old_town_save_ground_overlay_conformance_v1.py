"""Save exactly the authorized 288 conformed Old Town ground-overlay actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarGroundOverlayConformanceV1"
TARGET_COUNT = 288
EXPECTED_PACKAGE_PREFIX = "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/"
SOURCE_REPORT = "old_town_ground_overlay_conformance_apply_preview_v1.json"
AUDIT_REPORT = "old_town_ground_overlay_conformance_audit_v1.json"
OUTPUT_REPORT = "old_town_save_ground_overlay_conformance_v1.json"
ALLOWED_REVIEW_ISSUES = {"surface_gap_over_18cm"}


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
context["write_requested"] = True
report_directory = common.report_directory(config)

source_report = common.read_json(os.path.join(report_directory, SOURCE_REPORT))
if (
    source_report.get("status") != "apply_unsaved_preview_complete"
    or source_report.get("actor_count") != TARGET_COUNT
    or source_report.get("changes_made") is not True
):
    raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_SOURCE_REPORT_REFUSED")

record_by_package = {record["package"]: record for record in source_report.get("records", [])}
if len(record_by_package) != TARGET_COUNT:
    raise RuntimeError(
        "SUNSCAR_CONFORMANCE_SAVE_SOURCE_PACKAGES_REFUSED count=%d" % len(record_by_package)
    )
if any(not package.startswith(EXPECTED_PACKAGE_PREFIX) for package in record_by_package):
    raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_SOURCE_PREFIX_REFUSED")

audit_report = common.read_json(os.path.join(report_directory, AUDIT_REPORT))
if (
    audit_report.get("status") != "read_only_ground_overlay_conformance_audit_complete"
    or audit_report.get("actor_count") != TARGET_COUNT
    or audit_report.get("collision_disabled_count") != TARGET_COUNT
    or audit_report.get("unexpected_dirty_packages")
):
    raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_AUDIT_REFUSED")
for review_record in audit_report.get("review", []):
    if set(review_record.get("issues", [])) - ALLOWED_REVIEW_ISSUES:
        raise RuntimeError(
            "SUNSCAR_CONFORMANCE_SAVE_REVIEW_REFUSED %s" % review_record.get("label", "")
        )

actors = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if PASS_TAG in common.actor_tags(actor)
    ],
    key=lambda actor: actor.get_actor_label(),
)
if len(actors) != TARGET_COUNT:
    raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_ACTOR_SCOPE_REFUSED count=%d" % len(actors))

actor_packages = {}
for actor in actors:
    package = actor.get_package()
    package_name = package.get_name()
    record = record_by_package.get(package_name)
    if record is None or record.get("label") != actor.get_actor_label():
        raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_ACTOR_REFUSED " + actor.get_actor_label())
    if not package_name.startswith(EXPECTED_PACKAGE_PREFIX):
        raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_PACKAGE_PREFIX_REFUSED " + package_name)

    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_COMPONENT_REFUSED " + actor.get_actor_label())
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_COLLISION_REFUSED " + actor.get_actor_label())
    mesh = component.get_editor_property("static_mesh")
    if mesh is None:
        raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_MESH_REFUSED " + actor.get_actor_label())
    bounds = mesh.get_bounds()
    thickness_cm = bounds.box_extent.z * 2.0 * actor.get_actor_scale3d().z
    if abs(thickness_cm - 0.8) > 0.05:
        raise RuntimeError(
            "SUNSCAR_CONFORMANCE_SAVE_THICKNESS_REFUSED %s %.3f"
            % (actor.get_actor_label(), thickness_cm)
        )
    actor_packages[package_name] = package

if set(actor_packages) != set(record_by_package):
    raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_ACTOR_PACKAGE_SET_REFUSED")

dirty_packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
dirty_by_name = {package.get_name(): package for package in dirty_packages}
expected_names = set(record_by_package)
if len(dirty_by_name) != TARGET_COUNT or set(dirty_by_name) != expected_names:
    unexpected = sorted(set(dirty_by_name) - expected_names)
    missing = sorted(expected_names - set(dirty_by_name))
    raise RuntimeError(
        "SUNSCAR_CONFORMANCE_SAVE_DIRTY_SCOPE_REFUSED count=%d unexpected=%s missing=%s"
        % (len(dirty_by_name), "|".join(unexpected), "|".join(missing))
    )

packages = [actor_packages[name] for name in sorted(actor_packages)]
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_FAILED")

remaining_packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
remaining = sorted({package.get_name() for package in remaining_packages})
remaining_targets = sorted(set(remaining) & expected_names)
if remaining_targets:
    raise RuntimeError(
        "SUNSCAR_CONFORMANCE_SAVE_TARGETS_DIRTY_AFTER %s" % "|".join(remaining_targets)
    )
if remaining:
    raise RuntimeError("SUNSCAR_CONFORMANCE_SAVE_UNEXPECTED_DIRTY_AFTER %s" % "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_ground_overlay_conformance_saved",
    "context": context,
    "actor_count": len(actors),
    "saved_package_count": len(packages),
    "saved_packages": [package.get_name() for package in packages],
    "dirty_packages_before": sorted(dirty_by_name),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, OUTPUT_REPORT, payload)
unreal.log("SUNSCAR_GROUND_CONFORMANCE_SAVE packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_GROUND_CONFORMANCE_SAVE", len(packages), report)
