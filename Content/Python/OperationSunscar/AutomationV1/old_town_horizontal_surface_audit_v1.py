"""Read-only audit of Old Town horizontal building and access surfaces."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


ROLE_MARKERS = {
    "floor": ("floor",),
    "roof": ("roof",),
    "ramp": ("ramp",),
    "landing": ("landing",),
    "balcony": ("balcony",),
    "terrace": ("terrace",),
    "stair": ("stair", "step"),
}


def role_for(label):
    lowered = label.lower()
    for role, markers in ROLE_MARKERS.items():
        if any(marker in lowered for marker in markers):
            return role
    return ""


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
records = []
ss010_nearby = []
for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    tags = common.actor_tags(actor)
    is_old_town = folder.startswith("Sunscar/CorePlayable/") or folder.startswith("OldTown_")
    if not is_old_town:
        continue
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        continue
    origin, extent = actor.get_actor_bounds(False)
    materials = []
    for index in range(component.get_num_materials()):
        material = component.get_material(index)
        materials.append(material.get_path_name() if material else "")
    role = role_for(label)
    if role or "CoreCategory_Building" in tags:
        records.append(
            {
                "label": label,
                "folder": folder,
                "role": role or "building_other",
                "tags": tags,
                "location_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
                "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
                "materials": materials,
                "mesh_path": common.actor_mesh_path(actor),
                "package": actor.get_package().get_name(),
            }
        )
    if "SS_010" in label or "Detention" in label:
        ss010_nearby.append(
            {
                "label": label,
                "folder": folder,
                "tags": tags,
                "location_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
                "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
                "materials": materials,
                "mesh_path": common.actor_mesh_path(actor),
                "package": actor.get_package().get_name(),
            }
        )

records.sort(key=lambda row: (row["role"], row["folder"], row["label"]))
ss010_nearby.sort(key=lambda row: (row["folder"], row["label"]))
role_counts = collections.Counter(row["role"] for row in records)
material_counts = collections.Counter(material for row in records for material in row["materials"])
dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "schema_version": 1,
    "status": "read_only_horizontal_surface_audit_complete",
    "context": context,
    "actor_count": len(records),
    "role_counts": dict(sorted(role_counts.items())),
    "material_counts": dict(sorted(material_counts.items())),
    "records": records,
    "ss010_nearby": ss010_nearby,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_horizontal_surface_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_HORIZONTAL_SURFACE_AUDIT actors=%d ss010=%d dirty=%d report=%s"
    % (len(records), len(ss010_nearby), len(dirty), report)
)
print("SUNSCAR_HORIZONTAL_SURFACE_AUDIT", len(records), report)
