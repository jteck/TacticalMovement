"""Audit or apply persistent NoCollision profiles to tagged Old Town decoration."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TARGET_TAGS = {
    "VisualGroundOverlay",
    "SunscarOldTownExteriorCompletionV1",
    "SunscarOldTownWindowShutterV1",
    "SunscarOldTownIndustrialDetailV1",
    "SunscarOldTownHandToolV1",
    "SunscarOldTownRooftopUtilityV1",
    "SunscarOldTownLandmarkSignV1",
    "SunscarOldTownFacadeConduitV1",
}
PROTECTED_TAG_TERMS = {"hardcover", "collisionproxy", "vehiclecollision", "sandbag"}


config = common.load_config()
apply_changes = bool(config.get("execution", {}).get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_changes)
dirty_content_before = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps_before = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content_before or (dirty_maps_before and not apply_changes):
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_REFUSED dirty_scope")

records = []
targets = []
for actor in common.actor_subsystem().get_all_level_actors():
    actor_tags = set(common.actor_tags(actor))
    matched_tags = sorted(actor_tags & TARGET_TAGS)
    if not matched_tags:
        continue
    components = actor.get_components_by_class(unreal.StaticMeshComponent)
    if not components:
        continue
    lowered_tags = {tag.lower() for tag in actor_tags}
    protected_hits = sorted(
        term for term in PROTECTED_TAG_TERMS if any(term in tag for tag in lowered_tags)
    )
    if protected_hits:
        raise RuntimeError(
            "SUNSCAR_PERSISTENT_COLLISION_PROTECTED %s %s"
            % (actor.get_actor_label(), "|".join(protected_hits))
        )
    for component in components:
        targets.append((actor, component, matched_tags))

if len(targets) != 460:
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_REFUSED target_count=%d" % len(targets))

for actor, component, matched_tags in targets:
    before = str(component.get_collision_enabled())
    if apply_changes:
        actor.modify()
        component.modify()
        component.set_collision_profile_name("NoCollision")
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    after = str(component.get_collision_enabled())
    records.append({
        "label": actor.get_actor_label(),
        "component": component.get_name(),
        "matched_tags": matched_tags,
        "before": before,
        "after": after,
        "profile": str(component.get_collision_profile_name()),
        "package": actor.get_package().get_name(),
    })

target_packages = {record["package"] for record in records}
if len(target_packages) != 460:
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_REFUSED package_count=%d" % len(target_packages))
if dirty_maps_before - target_packages:
    raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_REFUSED preexisting_dirty_scope")

dirty_content_ready = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps_ready = {
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if apply_changes:
    if dirty_content_ready or dirty_maps_ready != target_packages:
        raise RuntimeError(
            "SUNSCAR_PERSISTENT_COLLISION_DIRTY_SCOPE content=%d maps=%d"
            % (len(dirty_content_ready), len(dirty_maps_ready))
        )
else:
    if dirty_content_ready or dirty_maps_ready:
        raise RuntimeError("SUNSCAR_PERSISTENT_COLLISION_DRY_RUN_DIRTIED_PACKAGES")

payload = {
    "schema_version": 1,
    "status": "persistent_decorative_collision_applied_unsaved" if apply_changes else "persistent_decorative_collision_dry_run_complete",
    "context": context,
    "apply_changes": apply_changes,
    "target_actor_component_count": len(records),
    "target_package_count": len(target_packages),
    "target_tag_counts": {
        tag: sum(tag in record["matched_tags"] for record in records)
        for tag in sorted(TARGET_TAGS)
    },
    "no_collision_after_count": sum("NO_COLLISION" in record["after"] for record in records),
    "records": sorted(records, key=lambda record: record["label"]),
    "dirty_content_packages": sorted(dirty_content_ready),
    "dirty_map_packages": sorted(dirty_maps_ready),
    "changes_made": apply_changes,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_persistent_decorative_collision_v1.json", payload)
unreal.log(
    "SUNSCAR_PERSISTENT_COLLISION apply=%s targets=%d no_collision=%d maps=%d report=%s"
    % (
        apply_changes,
        len(records),
        payload["no_collision_after_count"],
        len(dirty_maps_ready),
        report,
    )
)
print(
    "SUNSCAR_PERSISTENT_COLLISION",
    apply_changes,
    len(records),
    payload["no_collision_after_count"],
    len(dirty_maps_ready),
    report,
)
