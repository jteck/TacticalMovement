"""Read-only geometry/opening manifest for the SS_005 building-conversion pilot."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


SITE_ID = "SS_005"
STRUCTURAL_ROLES = ("Wall", "Lintel", "Parapet", "Roof", "Floor", "Ramp", "Landing")
ENGINE_PRIMITIVE_PREFIXES = ("/Engine/BasicShapes/", "/Game/LevelPrototyping/")


def property_value(obj, name, default=None):
    try:
        return obj.get_editor_property(name)
    except Exception:
        return default


def vector_dict(value):
    return {
        "x": round(float(value.x), 3),
        "y": round(float(value.y), 3),
        "z": round(float(value.z), 3),
    }


def rotator_dict(value):
    return {
        "pitch": round(float(value.pitch), 3),
        "yaw": round(float(value.yaw), 3),
        "roll": round(float(value.roll), 3),
    }


def component_for(actor):
    component = getattr(actor, "static_mesh_component", None)
    if component is not None:
        return component
    components = actor.get_components_by_class(unreal.StaticMeshComponent)
    return components[0] if components else None


def role_from_label(label):
    for role in STRUCTURAL_ROLES:
        if role.lower() in label.lower():
            return role.lower()
    if "interior" in label.lower():
        return "interior_partition"
    if label.endswith("_Left") or label.endswith("_Right"):
        return "opening_side"
    return "structural_other"


def actor_tick_enabled(actor):
    try:
        return bool(actor.is_actor_tick_enabled())
    except Exception:
        return None


def interval(record, axis):
    center = record["bounds_origin_cm"][axis]
    half = record["bounds_size_cm"][axis] * 0.5
    return center - half, center + half


def derive_opening(prefix, records_by_label):
    left = records_by_label.get(prefix + "_Left")
    right = records_by_label.get(prefix + "_Right")
    lintel = records_by_label.get(prefix + "_Lintel")
    if not left or not right or not lintel:
        return None

    # The opening width follows the wall's long horizontal axis. The thinner
    # horizontal bounds axis is the wall depth and is not used for the gap.
    span_axis = "x" if left["bounds_size_cm"]["x"] > left["bounds_size_cm"]["y"] else "y"
    left_interval = interval(left, span_axis)
    right_interval = interval(right, span_axis)
    first, second = sorted((left_interval, right_interval), key=lambda item: item[0])
    opening_min = first[1]
    opening_max = second[0]
    lintel_bottom = interval(lintel, "z")[0]
    story_prefix = prefix.rsplit("_", 1)[0]
    floor_label = story_prefix + "_Floor"
    floor = records_by_label.get(floor_label)
    # Finished clear height is measured from the top surface of the floor.
    # The graybox wall sides intentionally extend slightly below that surface.
    floor_reference = interval(floor, "z")[1] if floor else min(
        interval(left, "z")[0], interval(right, "z")[0]
    )
    return {
        "opening_id": prefix,
        "orientation_span_axis": span_axis,
        "width_cm": round(max(0.0, opening_max - opening_min), 3),
        "height_cm": round(max(0.0, lintel_bottom - floor_reference), 3),
        "span_min_cm": round(opening_min, 3),
        "span_max_cm": round(opening_max, 3),
        "lintel_bottom_z_cm": round(lintel_bottom, 3),
        "floor_reference_label": floor_label if floor else "wall_base_fallback",
        "floor_surface_z_cm": round(floor_reference, 3),
        "structural_actor_labels": [left["label"], right["label"], lintel["label"]],
        "classification": "verified_from_current_graybox_bounds",
        "conversion_rule": "Preserve this clear opening in the invisible gameplay collision shell; fit visual jamb, lintel, and door art around it.",
    }


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
records = []

for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    if SITE_ID not in label and SITE_ID not in folder:
        continue

    component = component_for(actor)
    mesh = property_value(component, "static_mesh") if component else None
    mesh_path = mesh.get_path_name() if mesh else ""
    materials = []
    if component:
        for index in range(component.get_num_materials()):
            material = component.get_material(index)
            materials.append(material.get_path_name() if material else "")

    bounds_origin, bounds_extent = actor.get_actor_bounds(False)
    tags = common.actor_tags(actor)
    package = actor.get_package().get_name()
    hlod_layer = property_value(actor, "hlod_layer")
    records.append({
        "label": label,
        "actor_class": actor.get_class().get_path_name(),
        "role": role_from_label(label),
        "folder": folder,
        "tags": tags,
        "package": package,
        "location_cm": vector_dict(actor.get_actor_location()),
        "rotation_degrees": rotator_dict(actor.get_actor_rotation()),
        "scale": vector_dict(actor.get_actor_scale3d()),
        "bounds_origin_cm": vector_dict(bounds_origin),
        "bounds_size_cm": vector_dict(bounds_extent * 2.0),
        "mesh_path": mesh_path,
        "materials": materials,
        "visible_engine_primitive": bool(mesh_path.startswith(ENGINE_PRIMITIVE_PREFIXES) and not actor.is_hidden_ed()),
        "hidden_in_editor": bool(actor.is_hidden_ed()),
        "hidden_in_game": bool(property_value(actor, "hidden", False)),
        "mobility": str(property_value(component, "mobility", "none")) if component else "none",
        "collision_enabled": str(property_value(component, "collision_enabled", "none")) if component else "none",
        "collision_profile": str(property_value(component, "collision_profile_name", "")) if component else "",
        "replicates": bool(property_value(actor, "replicates", False)),
        "actor_tick_enabled": actor_tick_enabled(actor),
        "spatially_loaded": bool(property_value(actor, "is_spatially_loaded", True)),
        "hlod_layer": hlod_layer.get_path_name() if hlod_layer else "",
    })

records.sort(key=lambda item: item["label"])
records_by_label = {item["label"]: item for item in records}
opening_prefixes = sorted({
    item["label"][:-5]
    for item in records
    if item["label"].endswith("_Left")
})
openings = []
for opening_prefix in opening_prefixes:
    opening = derive_opening(opening_prefix, records_by_label)
    if opening:
        openings.append(opening)

payload = {
    "schema_version": 1,
    "status": "read_only_ss005_pilot_manifest_complete",
    "site_id": SITE_ID,
    "context": context,
    "summary": {
        "actor_count": len(records),
        "static_mesh_actor_count": sum(1 for item in records if item["mesh_path"]),
        "visible_engine_primitive_count": sum(1 for item in records if item["visible_engine_primitive"]),
        "derived_opening_count": len(openings),
        "replicated_actor_count": sum(1 for item in records if item["replicates"]),
        "ticking_actor_count": sum(1 for item in records if item["actor_tick_enabled"]),
    },
    "counts_by_role": dict(sorted(collections.Counter(item["role"] for item in records).items())),
    "derived_openings": openings,
    "conversion_contract": {
        "collision_shell": "Retain or recreate the verified dimensions as simple invisible collision; never use detailed scan meshes as gameplay collision.",
        "visual_shell": "Replace visible cubes with a coherent modular masonry kit while preserving the manifest footprint, floor elevations, openings, and combat sightlines.",
        "multiplayer": "Static visual and collision scenery remains non-replicated, non-ticking, and Static mobility.",
        "nanite": "Use Nanite only on approved opaque high-detail visual modules, never on the collision shell or tiny props.",
        "streaming": "Keep the site spatially loaded; build Packed Level Actor/HLOD only after visual and gameplay acceptance.",
        "save_gate": "No pilot conversion or external-actor package is saved until an intentional before/after scope audit passes.",
    },
    "records": records,
    "changes_made": False,
    "level_saved": False,
}

report = common.write_json_report(config, "old_town_ss005_pilot_manifest_v1.json", payload)
unreal.log(
    "SUNSCAR_SS005_MANIFEST actors=%d openings=%d report=%s"
    % (len(records), len(openings), report)
)
print("SUNSCAR_SS005_MANIFEST", len(records), len(openings), report)
