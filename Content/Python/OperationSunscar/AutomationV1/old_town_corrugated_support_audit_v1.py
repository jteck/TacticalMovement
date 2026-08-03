"""Read-only support audit for the eight Salvage Yard corrugated assemblies."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        non_landscapes,
        unreal.DrawDebugTrace.NONE,
        True,
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
        raise RuntimeError("SUNSCAR_CORR_SUPPORT_MISSING %s|%s" % (barrier_label, base_label))
    barrier_origin, barrier_extent = barrier.get_actor_bounds(False)
    base_origin, base_extent = base.get_actor_bounds(False)
    support_z = terrain_z(base_origin.x, base_origin.y)
    if support_z is None:
        raise RuntimeError("SUNSCAR_CORR_SUPPORT_NO_TERRAIN " + base_label)
    records.append({
        "barrier_label": barrier_label,
        "base_label": base_label,
        "barrier_bottom_z_cm": round(barrier_origin.z - barrier_extent.z, 3),
        "base_bottom_z_cm": round(base_origin.z - base_extent.z, 3),
        "base_top_z_cm": round(base_origin.z + base_extent.z, 3),
        "barrier_to_base_gap_cm": round((barrier_origin.z - barrier_extent.z) - (base_origin.z + base_extent.z), 3),
        "terrain_z_cm": round(support_z, 3),
        "base_to_terrain_gap_cm": round((base_origin.z - base_extent.z) - support_z, 3),
    })

payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "assembly_count": len(records),
    "records": records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_corrugated_support_audit_v1.json", payload)
unreal.log("SUNSCAR_CORR_SUPPORT_AUDIT assemblies=%d report=%s" % (len(records), report))
