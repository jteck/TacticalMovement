"""Read-only Operation Sunscar map/session preflight. Does not save assets."""

import os
import sys
from collections import Counter

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())

class_counts = Counter(actor.get_class().get_name() for actor in actors)
tag_counts = Counter(tag for actor in actors for tag in common.actor_tags(actor))
sandbag_candidates = []
audit_config = config["sandbag_audit"]

for actor in actors:
    label = actor.get_actor_label()
    mesh_path = common.actor_mesh_path(actor)
    tags = common.actor_tags(actor)
    if (
        common.has_any_term(label, audit_config["label_terms"])
        or common.has_any_term(mesh_path, audit_config["mesh_path_terms"])
        or any(tag in audit_config["tag_terms"] for tag in tags)
    ):
        sandbag_candidates.append(
            {
                "label": label,
                "class": actor.get_class().get_name(),
                "mesh_path": mesh_path,
                "tags": tags,
                "folder": common.actor_folder(actor),
            }
        )

planning_paths = {
    "resolved_plan": common.planning_file(config, "resolved_plan_file"),
    "import_queue": common.planning_file(config, "import_queue_file"),
    "final_registry": common.planning_file(config, "final_registry_file"),
}
planning_presence = {name: os.path.exists(path) for name, path in planning_paths.items()}

payload = {
    "schema_version": 1,
    "status": "read_only_preflight_complete",
    "context": context,
    "actor_count": len(actors),
    "class_counts": dict(class_counts.most_common()),
    "tag_counts": dict(tag_counts.most_common()),
    "sandbag_candidate_count": len(sandbag_candidates),
    "sandbag_candidates": sandbag_candidates,
    "planning_paths": planning_paths,
    "planning_file_presence": planning_presence,
    "execution_gate": {
        "apply_changes": config["execution"]["apply_changes"],
        "save_current_level": config["execution"]["save_current_level"],
        "automatic_save_permitted": False,
    },
    "warnings": [
        "This script does not prove placements are correct.",
        "Run old_town_sandbag_audit.py before any connected-slice apply pass.",
        "Missing final registry is expected until staging inspection is complete.",
    ],
}

path = common.write_json_report(config, "old_town_preflight.json", payload)
unreal.log("SUNSCAR_PREFLIGHT_OK actors=%d sandbags=%d report=%s" % (len(actors), len(sandbag_candidates), path))
print("SUNSCAR_PREFLIGHT_OK", len(actors), len(sandbag_candidates), path)
