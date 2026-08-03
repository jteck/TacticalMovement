"""Read-only inventory of Old Town structural actors and their materials."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


ROLE_TOKENS = (
    ("window_glass", "WindowGlass"),
    ("window_frame", "WindowFrame"),
    ("parapet", "Parapet"),
    ("roof", "Roof"),
    ("floor", "Floor"),
    ("wall", "Wall"),
)


def classify(label):
    lowered = label.lower()
    if "window" in lowered and "glass" in lowered:
        return "window_glass"
    if "window" in lowered and "frame" in lowered:
        return "window_frame"
    for role, token in ROLE_TOKENS:
        if token in label:
            return role
    return ""


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
records = []
for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    if not label.startswith("Core_SS_"):
        continue
    role = classify(label)
    if not role:
        continue
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        continue
    materials = []
    for index in range(component.get_num_materials()):
        material = component.get_material(index)
        materials.append(material.get_path_name() if material else "")
    origin, extent = actor.get_actor_bounds(False)
    records.append({
        "site_id": label[5:11],
        "label": label,
        "role": role,
        "folder": common.actor_folder(actor),
        "mesh_path": common.actor_mesh_path(actor),
        "material_paths": materials,
        "origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "package": actor.get_package().get_name(),
    })

records.sort(key=lambda item: item["label"])
role_counts = collections.Counter(item["role"] for item in records)
site_counts = collections.Counter(item["site_id"] for item in records)
material_counts = collections.Counter(
    material
    for item in records
    for material in item["material_paths"]
)
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "role_counts": dict(sorted(role_counts.items())),
    "site_counts": dict(sorted(site_counts.items())),
    "material_counts": dict(sorted(material_counts.items())),
    "records": records,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_structural_material_audit_v1.json", payload)
unreal.log("SUNSCAR_STRUCTURAL_MATERIAL_AUDIT actors=%d report=%s" % (len(records), report))
print("SUNSCAR_STRUCTURAL_MATERIAL_AUDIT", len(records), report)
