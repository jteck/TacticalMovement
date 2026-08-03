"""Dry-run-first material pass for the 50 legacy CoreRoute actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarCoreRouteMaterialPassV1")
PROTOTYPE_PREFIX = "/Game/LevelPrototyping/Materials/"
MATERIAL_PATHS = {
    "alpha_dry_canal": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Silt",
    "bravo_courtyard": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Earth",
    "charlie_bazaar": (
        "/Game/Fab/Megascans/Surfaces/Crushed_Asphalt_Ground_sjyjcbja/"
        "Medium/sjyjcbja_tier_2/Materials/MI_sjyjcbja"
    ),
    "alley": "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Earth",
}


def route_key(tags):
    if "Route_Alpha_DryCanal" in tags:
        return "alpha_dry_canal"
    if "Route_Bravo_Courtyard" in tags:
        return "bravo_courtyard"
    if "Route_Charlie_Bazaar" in tags:
        return "charlie_bazaar"
    if "CoreCategory_Alley" in tags:
        return "alley"
    return ""


config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)

dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if apply_requested and (dirty_content or dirty_maps):
    raise RuntimeError(
        "SUNSCAR_ROUTE_MATERIAL_APPLY_REFUSED preexisting_dirty_content=%d preexisting_dirty_maps=%d"
        % (len(dirty_content), len(dirty_maps))
    )

materials = {
    key: common.load_asset_checked(config, path)
    for key, path in MATERIAL_PATHS.items()
}
actors = [
    actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if actor.get_actor_label().startswith("CoreRoute_")
]
if len(actors) != 50:
    raise RuntimeError("SUNSCAR_ROUTE_MATERIAL_SCOPE_REFUSED actor_count=%d" % len(actors))

records = []
for actor in sorted(actors, key=lambda value: value.get_actor_label()):
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        raise RuntimeError("SUNSCAR_ROUTE_MATERIAL_NO_COMPONENT " + actor.get_actor_label())
    tags = set(common.actor_tags(actor))
    key = route_key(tags)
    if not key:
        raise RuntimeError("SUNSCAR_ROUTE_MATERIAL_UNCLASSIFIED " + actor.get_actor_label())
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    target = materials[key]
    target_path = target.get_path_name()
    if not (
        current_path.startswith(PROTOTYPE_PREFIX)
        or current_path == target_path
    ):
        raise RuntimeError(
            "SUNSCAR_ROUTE_MATERIAL_UNEXPECTED_SOURCE %s %s"
            % (actor.get_actor_label(), current_path)
        )
    record = {
        "label": actor.get_actor_label(),
        "route_key": key,
        "source_material": current_path,
        "target_material": target_path,
        "package": actor.get_package().get_name(),
    }
    if apply_requested:
        actor.modify()
        component.modify()
        component.set_material(0, target)
        if PASS_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [PASS_TAG]
        record["applied_material"] = component.get_material(0).get_path_name()
    records.append(record)

counts = {}
for record in records:
    key = record["route_key"]
    counts[key] = counts.get(key, 0) + 1

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "route_counts": counts,
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_core_route_material_apply_v1.json"
    if apply_requested
    else "old_town_core_route_material_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_ROUTE_MATERIAL mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report)
)
print("SUNSCAR_ROUTE_MATERIAL", len(records), report)
