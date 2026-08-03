"""Read-only audit of remaining prototype-grid materials in the Old Town level."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PROTOTYPE_PREFIX = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_"


def site_from_label(label):
    marker = label.find("SS_")
    return label[marker:marker + 6] if marker >= 0 else ""


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
records = []
for actor in common.actor_subsystem().get_all_level_actors():
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        continue
    material = component.get_material(0)
    material_path = material.get_path_name() if material else ""
    if not material_path.startswith(PROTOTYPE_PREFIX):
        continue
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    tags = common.actor_tags(actor)
    role = "other"
    if "Roof" in label:
        role = "roof"
    elif "Floor" in label:
        role = "floor"
    elif "Parapet" in label:
        role = "parapet"
    elif "Window" in label:
        role = "window"
    elif "Door" in label:
        role = "door"
    elif "CoreCategory_Building" in tags:
        role = "building_other"
    records.append(
        {
            "site_id": site_from_label(label),
            "label": label,
            "role": role,
            "folder": folder,
            "tags": tags,
            "material_path": material_path,
            "mesh_path": common.actor_mesh_path(actor),
            "visible": bool(component.get_editor_property("visible")),
            "collision": str(component.get_collision_enabled()),
            "package": actor.get_package().get_name(),
        }
    )
records.sort(key=lambda row: (row["role"], row["site_id"], row["label"]))
role_counts = collections.Counter(row["role"] for row in records)
site_counts = collections.Counter(row["site_id"] or "unassigned" for row in records)
material_counts = collections.Counter(row["material_path"] for row in records)
dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "schema_version": 1,
    "status": "read_only_remaining_prototype_material_audit_complete",
    "context": context,
    "actor_count": len(records),
    "role_counts": dict(sorted(role_counts.items())),
    "site_counts": dict(sorted(site_counts.items())),
    "material_counts": dict(sorted(material_counts.items())),
    "records": records,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(
    config, "old_town_remaining_prototype_material_audit_v1.json", payload
)
unreal.log(
    "SUNSCAR_REMAINING_PROTOTYPE_AUDIT actors=%d dirty=%d report=%s"
    % (len(records), len(dirty), report)
)
print("SUNSCAR_REMAINING_PROTOTYPE_AUDIT", len(records), report)
