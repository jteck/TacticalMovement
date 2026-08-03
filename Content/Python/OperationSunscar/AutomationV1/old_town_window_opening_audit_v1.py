"""Read-only inventory of Old Town window frame/glass pairs and current finishes."""

import collections
import os
import re
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())


def role_for(label):
    lowered = label.lower()
    if "win" not in lowered and "window" not in lowered:
        return ""
    if "frame" in lowered:
        return "frame"
    if "glass" in lowered:
        return "glass"
    return ""


def pair_key(label):
    value = re.sub(r"(?i)[_-](frame|glass)$", "", label)
    return value.lower()


records = []
for actor in actors:
    label = actor.get_actor_label()
    role = role_for(label)
    if not role or not isinstance(actor, unreal.StaticMeshActor):
        continue
    origin, extent = actor.get_actor_bounds(False)
    if not (-18000.0 <= origin.x <= 18000.0 and -13000.0 <= origin.y <= 12500.0):
        continue
    component = actor.static_mesh_component
    materials = []
    for index in range(component.get_num_materials()):
        material = component.get_material(index)
        materials.append(material.get_path_name() if material else "")
    site = next((tag for tag in common.actor_tags(actor) if tag.startswith("SS_") and len(tag) == 6), "")
    records.append({
        "label": label,
        "pair_key": pair_key(label),
        "role": role,
        "site_id": site,
        "folder": common.actor_folder(actor),
        "mesh_path": common.actor_mesh_path(actor),
        "material_paths": materials,
        "collision": str(component.get_collision_enabled()),
        "origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "dimensions_cm": [round(extent.x * 2.0, 3), round(extent.y * 2.0, 3), round(extent.z * 2.0, 3)],
        "package": actor.get_package().get_name(),
    })

records.sort(key=lambda item: item["label"])
pairs = collections.defaultdict(list)
for item in records:
    pairs[item["pair_key"]].append(item)
pair_issues = []
for key, values in sorted(pairs.items()):
    roles = sorted(item["role"] for item in values)
    if roles != ["frame", "glass"]:
        pair_issues.append({"pair_key": key, "roles": roles, "labels": [item["label"] for item in values]})

role_counts = collections.Counter(item["role"] for item in records)
material_counts = collections.Counter(path for item in records for path in item["material_paths"])
site_counts = collections.Counter(item["site_id"] for item in records)
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "pair_count": len(pairs),
    "pair_issue_count": len(pair_issues),
    "pair_issues": pair_issues,
    "role_counts": dict(sorted(role_counts.items())),
    "site_counts": dict(sorted(site_counts.items())),
    "material_counts": dict(sorted(material_counts.items())),
    "records": records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_window_opening_audit_v1.json", payload)
unreal.log("SUNSCAR_WINDOW_OPENING_AUDIT actors=%d pairs=%d issues=%d report=%s" % (len(records), len(pairs), len(pair_issues), report))
print("SUNSCAR_WINDOW_OPENING_AUDIT", len(records), len(pairs), len(pair_issues), report)
