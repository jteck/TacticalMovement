"""Read-only UE 5.8 building conversion and multiplayer-cost audit for Old Town."""

import collections
import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


STRUCTURAL_ROLES = ("Wall", "Lintel", "Parapet", "Roof", "Floor", "Ramp", "Landing")
VISUAL_FOLDERS = (
    "Sunscar/CorePlayable/Buildings/",
    "OldTown_ArtDraft/",
)
ENGINE_PRIMITIVE_PREFIXES = (
    "/Engine/BasicShapes/",
    "/Game/LevelPrototyping/",
)


def site_from_label(label):
    marker = label.find("SS_")
    return label[marker:marker + 6] if marker >= 0 else ""


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
    return "structural_other"


def actor_tick_enabled(actor):
    try:
        return bool(actor.is_actor_tick_enabled())
    except Exception:
        tick = property_value(actor, "primary_actor_tick")
        if tick is None:
            return None
        can_ever_tick = bool(property_value(tick, "can_ever_tick", False))
        starts_enabled = bool(property_value(tick, "start_with_tick_enabled", False))
        return can_ever_tick and starts_enabled


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
records = []

for actor in actors:
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    site_id = site_from_label(label)
    if not site_id:
        continue
    tags = common.actor_tags(actor)
    is_building = (
        any(folder.startswith(prefix) for prefix in VISUAL_FOLDERS)
        and ("CoreCategory_Building" in tags or label.startswith("Core_SS_"))
    )
    if not is_building:
        continue

    component = component_for(actor)
    if component is None:
        continue
    mesh = property_value(component, "static_mesh")
    if mesh is None:
        continue
    mesh_path = mesh.get_path_name()
    materials = []
    for index in range(component.get_num_materials()):
        material = component.get_material(index)
        materials.append(material.get_path_name() if material else "")

    scale = actor.get_actor_scale3d()
    absolute = sorted([abs(float(scale.x)), abs(float(scale.y)), abs(float(scale.z))])
    scale_ratio = absolute[-1] / max(absolute[0], 0.0001)
    bounds_origin, bounds_extent = actor.get_actor_bounds(False)
    nanite_settings = property_value(mesh, "nanite_settings")
    nanite_enabled = bool(property_value(nanite_settings, "enabled", False)) if nanite_settings else False
    visible = bool(property_value(component, "visible", True)) and not actor.is_hidden_ed()
    is_graybox_visual = visible and mesh_path.startswith(ENGINE_PRIMITIVE_PREFIXES)
    collision = str(property_value(component, "collision_enabled", "unknown"))

    records.append({
        "site_id": site_id,
        "label": label,
        "role": role_from_label(label),
        "folder": folder,
        "package": actor.get_package().get_name(),
        "mesh_path": mesh_path,
        "materials": materials,
        "visible": visible,
        "graybox_visual": is_graybox_visual,
        "actor_scale": vector_dict(scale),
        "nonuniform_scale_ratio": round(scale_ratio, 3),
        "nonuniform_scale_over_1_25": scale_ratio > 1.25,
        "bounds_origin_cm": vector_dict(bounds_origin),
        "bounds_size_cm": vector_dict(bounds_extent * 2.0),
        "mobility": str(property_value(component, "mobility", "unknown")),
        "collision_enabled": collision,
        "casts_shadow": bool(property_value(component, "cast_shadow", True)),
        "nanite_enabled_on_source_mesh": nanite_enabled,
        "replicates": bool(property_value(actor, "replicates", False)),
        "net_load_on_client": bool(property_value(actor, "net_load_on_client", False)),
        "actor_tick_starts_enabled": actor_tick_enabled(actor),
        "spatially_loaded": bool(property_value(actor, "is_spatially_loaded", True)),
        "hlod_layer": (
            property_value(actor, "hlod_layer").get_path_name()
            if property_value(actor, "hlod_layer")
            else ""
        ),
    })

records.sort(key=lambda item: (item["site_id"], item["label"]))
graybox_records = [item for item in records if item["graybox_visual"]]
replicated = [item for item in records if item["replicates"]]
ticking = [item for item in records if item["actor_tick_starts_enabled"]]
movable = [item for item in records if "STATIC" not in item["mobility"].upper()]
nonuniform = [item for item in records if item["nonuniform_scale_over_1_25"]]

payload = {
    "schema_version": 1,
    "status": "read_only_ue58_building_conversion_audit_complete",
    "evidence_labels": {
        "actor_and_asset_values": "verified_fact",
        "graybox_visual": "verified_fact_based_on_visible_engine_primitive_mesh",
        "conversion_architecture": "recommendation_based_on_epic_ue58_workflows",
    },
    "context": context,
    "summary": {
        "building_static_mesh_actor_count": len(records),
        "site_count": len(set(item["site_id"] for item in records)),
        "visible_engine_primitive_count": len(graybox_records),
        "nonuniform_scale_over_1_25_count": len(nonuniform),
        "replicated_static_scenery_count": len(replicated),
        "ticking_static_scenery_count": len(ticking),
        "non_static_mobility_count": len(movable),
        "unique_mesh_count": len(set(item["mesh_path"] for item in records)),
        "unique_material_count": len(set(path for item in records for path in item["materials"])),
    },
    "counts_by_site": dict(sorted(collections.Counter(item["site_id"] for item in records).items())),
    "counts_by_role": dict(sorted(collections.Counter(item["role"] for item in records).items())),
    "performance_violations": {
        "replicated": [item["label"] for item in replicated],
        "ticking": [item["label"] for item in ticking],
        "non_static_mobility": [item["label"] for item in movable],
    },
    "conversion_architecture": {
        "gameplay_collision": "Preserve simple non-rendering collision actors and verified openings; never use scan meshes as gameplay collision.",
        "visible_building_art": "Replace visible engine primitives site-by-site with owned modular Epic/Quixel pieces or audited map-owned modules.",
        "repetition": "Use ISM/HISM or Packed Level Actors only after a site kit is visually accepted; keep per-instance collision disabled for decorative art.",
        "nanite": "Enable selectively on opaque high-detail static art meshes; do not enable on simple collision shells, glass, tiny props, or by filename alone.",
        "streaming": "Keep scenery spatially loaded in World Partition and build HLOD after visual acceptance.",
        "network": "Static scenery must not replicate or tick; only interactive doors or destructibles use replicated gameplay actors.",
        "materials": "Use shared opaque masters and instances, physical world scale, packed masks, restrained layer count, and decal budgets.",
    },
    "records": records,
    "changes_made": False,
    "level_saved": False,
}

report = common.write_json_report(config, "old_town_ue58_building_conversion_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_UE58_BUILDING_AUDIT actors=%d graybox=%d replicated=%d ticking=%d movable=%d report=%s"
    % (len(records), len(graybox_records), len(replicated), len(ticking), len(movable), report)
)
print("SUNSCAR_UE58_BUILDING_AUDIT", len(records), len(graybox_records), report)
