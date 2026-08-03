"""Read-only five-point support audit for Old Town first-floor building slabs."""

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
building_actors = [actor for actor in actors if "CoreCategory_Building" in common.actor_tags(actor)]
floors = sorted(
    [
        actor
        for actor in building_actors
        if "_F1_Floor" in actor.get_actor_label()
        and common.actor_folder(actor).startswith("Sunscar/CorePlayable/Buildings/")
    ],
    key=lambda actor: actor.get_actor_label(),
)
overlays = []
for actor in actors:
    if "VisualGroundOverlay" not in common.actor_tags(actor):
        continue
    origin, extent = actor.get_actor_bounds(False)
    overlays.append(
        {
            "actor": actor,
            "min_x": origin.x - extent.x,
            "max_x": origin.x + extent.x,
            "min_y": origin.y - extent.y,
            "max_y": origin.y + extent.y,
            "top_z": origin.z + extent.z,
        }
    )


def allowed_trace_support(actor):
    if actor is None:
        return False
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    class_name = actor.get_class().get_name()
    return (
        "Landscape" in class_name
        or folder.startswith("OldTown_GroundElevationPassV2/")
        or folder.startswith("OldTown_GroundSurfacePass/")
        or label.startswith("District_")
        or label.startswith("Ground_")
    )


def overlay_support(x, y, bottom_z):
    candidates = [
        entry
        for entry in overlays
        if entry["min_x"] - 2.0 <= x <= entry["max_x"] + 2.0
        and entry["min_y"] - 2.0 <= y <= entry["max_y"] + 2.0
        and entry["top_z"] <= bottom_z + 25.0
        and entry["top_z"] >= bottom_z - 300.0
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda entry: entry["top_z"])


def trace_support(x, y, bottom_z):
    hits = unreal.SystemLibrary.line_trace_multi(
        world,
        unreal.Vector(x, y, bottom_z + 100.0),
        unreal.Vector(x, y, bottom_z - 3000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        building_actors,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    for hit in hits or []:
        data = hit.to_dict()
        candidate = data.get("hit_actor")
        location = data.get("location")
        if data.get("blocking_hit") and allowed_trace_support(candidate) and location:
            return {"actor": candidate, "top_z": location.z}
    return None


records = []
flagged = []
for floor in floors:
    origin, extent = floor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    inset_x = max(0.0, extent.x * 0.60)
    inset_y = max(0.0, extent.y * 0.60)
    points = [
        ("center", origin.x, origin.y),
        ("north_east", origin.x + inset_x, origin.y + inset_y),
        ("north_west", origin.x - inset_x, origin.y + inset_y),
        ("south_east", origin.x + inset_x, origin.y - inset_y),
        ("south_west", origin.x - inset_x, origin.y - inset_y),
    ]
    samples = []
    for sample_name, x, y in points:
        overlay = overlay_support(x, y, bottom_z)
        trace = trace_support(x, y, bottom_z)
        candidates = []
        if overlay:
            candidates.append(("overlay", overlay["actor"], overlay["top_z"]))
        if trace:
            candidates.append(("trace", trace["actor"], trace["top_z"]))
        best = max(candidates, key=lambda item: item[2]) if candidates else None
        support_z = best[2] if best else None
        gap = bottom_z - support_z if support_z is not None else None
        samples.append(
            {
                "sample": sample_name,
                "x_cm": round(x, 3),
                "y_cm": round(y, 3),
                "support_method": best[0] if best else "",
                "support_actor": best[1].get_actor_label() if best else "",
                "support_z_cm": round(support_z, 3) if support_z is not None else None,
                "support_gap_cm": round(gap, 3) if gap is not None else None,
            }
        )
    found = [sample for sample in samples if sample["support_gap_cm"] is not None]
    severe_gaps = [sample for sample in found if sample["support_gap_cm"] > 25.0]
    below_support = [sample for sample in found if sample["support_gap_cm"] < -5.0]
    reasons = []
    if not found:
        classification = "unknown_no_support_samples"
        reasons.append("support_not_found")
    elif severe_gaps:
        classification = "verified_gap"
        reasons.append("visible_support_gap")
    elif below_support:
        classification = "floor_below_support"
        reasons.append("floor_below_support")
    else:
        classification = "supported"
    record = {
        "label": floor.get_actor_label(),
        "folder": common.actor_folder(floor),
        "bottom_z_cm": round(bottom_z, 3),
        "classification": classification,
        "support_samples_found": len(found),
        "maximum_gap_cm": max((sample["support_gap_cm"] for sample in found), default=None),
        "minimum_gap_cm": min((sample["support_gap_cm"] for sample in found), default=None),
        "samples": samples,
        "review_reasons": reasons,
        "package": floor.get_package().get_name(),
    }
    records.append(record)
    if reasons:
        flagged.append(record)

dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "schema_version": 2,
    "status": "read_only_building_support_audit_v2_complete",
    "context": context,
    "floor_count": len(records),
    "overlay_count": len(overlays),
    "supported_count": sum(record["classification"] == "supported" for record in records),
    "verified_gap_count": sum(record["classification"] == "verified_gap" for record in records),
    "unknown_count": sum(record["classification"].startswith("unknown") for record in records),
    "flagged_count": len(flagged),
    "records": records,
    "flagged": flagged,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_building_support_audit_v2.json", payload)
unreal.log(
    "SUNSCAR_BUILDING_SUPPORT_AUDIT_V2 floors=%d supported=%d gaps=%d unknown=%d report=%s"
    % (
        len(records),
        payload["supported_count"],
        payload["verified_gap_count"],
        payload["unknown_count"],
        report,
    )
)
print("SUNSCAR_BUILDING_SUPPORT_AUDIT_V2", len(records), report)
