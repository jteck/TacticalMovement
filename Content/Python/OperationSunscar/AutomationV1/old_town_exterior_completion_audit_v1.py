"""Read-only inventory for Old Town ground, façade-detail, lighting, and PIE completion."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
sites = ["SS_%03d" % index for index in range(1, 21)]


def bounds_record(actor):
    origin, extent = actor.get_actor_bounds(False)
    return {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_name(),
        "folder": common.actor_folder(actor),
        "location_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "mesh_path": common.actor_mesh_path(actor),
        "tags": common.actor_tags(actor),
        "package": actor.get_package().get_name(),
    }


site_records = {}
for site in sites:
    members = [actor for actor in actors if site in (actor.get_actor_label() + " " + " ".join(common.actor_tags(actor)))]
    site_records[site] = {
        "floors": [bounds_record(actor) for actor in members if "floor" in actor.get_actor_label().lower()],
        "walls": [bounds_record(actor) for actor in members if "wall" in actor.get_actor_label().lower()],
        "doors": [bounds_record(actor) for actor in members if "door" in actor.get_actor_label().lower()],
        "windows": [bounds_record(actor) for actor in members if "window" in actor.get_actor_label().lower() or "_win_" in actor.get_actor_label().lower()],
        "utilities": [bounds_record(actor) for actor in members if any(term in actor.get_actor_label().lower() for term in ("utility", "electrical", "conduit", "pipe", "cabinet"))],
    }

ground = []
for actor in actors:
    tags = set(common.actor_tags(actor))
    if "VisualGroundOverlay" in tags:
        record = bounds_record(actor)
        component = getattr(actor, "static_mesh_component", None)
        material = component.get_material(0) if component and component.get_num_materials() else None
        record["material_path"] = material.get_path_name() if material else ""
        ground.append(record)

lights = []
for actor in actors:
    class_name = actor.get_class().get_name().lower()
    if "light" not in class_name and "postprocess" not in class_name and "sky" not in class_name:
        continue
    record = bounds_record(actor)
    component = None
    for name in ("light_component", "directional_light_component", "sky_light_component", "post_process_component"):
        component = getattr(actor, name, None)
        if component is not None:
            break
    properties = {}
    if component is not None:
        for prop in ("intensity", "indirect_lighting_intensity", "volumetric_scattering_intensity", "temperature", "use_temperature"):
            try:
                properties[prop] = str(component.get_editor_property(prop))
            except Exception:
                pass
    if isinstance(actor, unreal.PostProcessVolume):
        settings = actor.get_editor_property("settings")
        for prop in (
            "override_auto_exposure_method",
            "auto_exposure_method",
            "override_auto_exposure_min_brightness",
            "auto_exposure_min_brightness",
            "override_auto_exposure_max_brightness",
            "auto_exposure_max_brightness",
            "override_auto_exposure_bias",
            "auto_exposure_bias",
            "override_auto_exposure_speed_up",
            "auto_exposure_speed_up",
            "override_auto_exposure_speed_down",
            "auto_exposure_speed_down",
        ):
            try:
                properties[prop] = str(settings.get_editor_property(prop))
            except Exception:
                pass
    record["properties"] = properties
    lights.append(record)

material_counts = collections.Counter(record.get("material_path", "") for record in ground)
payload = {
    "schema_version": 1,
    "status": "read_only_exterior_completion_audit",
    "context": context,
    "actor_count": len(actors),
    "ground_overlay_count": len(ground),
    "ground_material_counts": dict(sorted(material_counts.items())),
    "ground_overlays": sorted(ground, key=lambda row: row["label"]),
    "site_records": site_records,
    "lights": sorted(lights, key=lambda row: row["label"]),
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_exterior_completion_audit_v1.json", payload)
unreal.log("SUNSCAR_EXTERIOR_COMPLETION_AUDIT ground=%d lights=%d report=%s" % (len(ground), len(lights), report))
print("SUNSCAR_EXTERIOR_COMPLETION_AUDIT", len(ground), len(lights), report)
