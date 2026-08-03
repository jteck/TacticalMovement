"""Dry-run-first terrain grounding for eight Salvage Yard corrugated assemblies."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarCorrugatedAssemblyGroundV1")
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x, y, 100000.0), unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, non_landscapes,
        unreal.DrawDebugTrace.NONE, True,
    )
    result = hit.to_dict() if hit is not None else {}
    return result["location"].z if result.get("blocking_hit") else None


records = []
for index in range(1, 9):
    barrier_label = "QX_Corr_Salvage_S_%02d" % index
    base_label = "QX_Corr_Base_Salvage_%02d" % index
    barrier = by_label.get(barrier_label)
    base = by_label.get(base_label)
    if barrier is None or base is None:
        raise RuntimeError("SUNSCAR_CORR_GROUND_MISSING %s|%s" % (barrier_label, base_label))
    base_origin, base_extent = base.get_actor_bounds(False)
    support_z = terrain_z(base_origin.x, base_origin.y)
    if support_z is None:
        raise RuntimeError("SUNSCAR_CORR_GROUND_NO_TERRAIN " + base_label)
    delta_z = support_z - (base_origin.z - base_extent.z)
    if not (-35.0 <= delta_z <= -15.0):
        raise RuntimeError("SUNSCAR_CORR_GROUND_BAD_DELTA %s %.3f" % (base_label, delta_z))
    record = {
        "barrier_label": barrier_label,
        "base_label": base_label,
        "terrain_z_cm": round(support_z, 3),
        "delta_z_cm": round(delta_z, 3),
    }
    if apply_requested:
        for actor in (barrier, base):
            actor.modify()
            actor.add_actor_world_offset(unreal.Vector(0.0, 0.0, delta_z), False, False)
            if TAG not in list(actor.tags):
                actor.tags = list(actor.tags) + [TAG]
        after_origin, after_extent = base.get_actor_bounds(False)
        barrier_origin, barrier_extent = barrier.get_actor_bounds(False)
        record["after_base_gap_cm"] = round((after_origin.z - after_extent.z) - support_z, 3)
        record["after_barrier_to_base_embed_cm"] = round((barrier_origin.z - barrier_extent.z) - (after_origin.z + after_extent.z), 3)
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "assembly_count": len(records),
    "actor_count": len(records) * 2,
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
name = "old_town_ground_corrugated_assemblies_apply_v1.json" if apply_requested else "old_town_ground_corrugated_assemblies_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_CORR_GROUND mode=%s actors=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records) * 2, report))
