"""Dry-run-first material pass for the 82 Old Town structural actors."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarStructuralMaterialPassV1")
PROTOTYPE_PREFIX = "/Game/LevelPrototyping/Materials/"
MATERIAL_ROOT = "/Game/Maps/Sunscar/Art/Materials"
CONCRETE = MATERIAL_ROOT + "/Ground/MI_OT_Ground_Concrete"
STONE = MATERIAL_ROOT + "/Instances/MI_OT_Stone"
METAL = MATERIAL_ROOT + "/Instances/MI_OT_Metal"
WALL_MATERIALS = {
    "SS_003": MATERIAL_ROOT + "/Instances/MI_OT_Stone",
    "SS_004": MATERIAL_ROOT + "/Instances/MI_OT_WarmStucco",
    "SS_005": MATERIAL_ROOT + "/Instances/MI_OT_PaleStucco",
    "SS_006": MATERIAL_ROOT + "/Instances/MI_OT_Stone",
    "SS_007": MATERIAL_ROOT + "/Instances/MI_OT_PaleStucco",
    "SS_010": MATERIAL_ROOT + "/Instances/MI_OT_Detention",
    "SS_011": MATERIAL_ROOT + "/Instances/MI_OT_WarmStucco",
    "SS_012": MATERIAL_ROOT + "/Instances/MI_OT_PaleStucco",
    "SS_013": MATERIAL_ROOT + "/Instances/MI_OT_Stone",
    "SS_015": MATERIAL_ROOT + "/Instances/MI_OT_Metal",
    "SS_016": MATERIAL_ROOT + "/Instances/MI_OT_Metal",
    "SS_017": MATERIAL_ROOT + "/Instances/MI_OT_WarmStucco",
    "SS_018": MATERIAL_ROOT + "/Instances/MI_OT_Stone",
}
METAL_ROOF_SITES = {"SS_003", "SS_006", "SS_013", "SS_015", "SS_016", "SS_018"}
EXPECTED_COUNTS = {"floor": 19, "parapet": 4, "roof": 12, "wall": 47}


def classify(label):
    if "Parapet" in label:
        return "parapet"
    if "Roof" in label:
        return "roof"
    if "Floor" in label:
        return "floor"
    if "Wall" in label:
        return "wall"
    return ""


def target_path(site_id, role):
    if role == "floor":
        return CONCRETE
    if role == "roof":
        return METAL if site_id in METAL_ROOF_SITES else STONE
    return WALL_MATERIALS[site_id]


config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
if apply_requested and (dirty_content or dirty_maps):
    raise RuntimeError(
        "SUNSCAR_STRUCTURAL_MATERIAL_APPLY_REFUSED preexisting_dirty_content=%d preexisting_dirty_maps=%d"
        % (len(dirty_content), len(dirty_maps))
    )

actors = []
for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    if not label.startswith("Core_SS_"):
        continue
    role = classify(label)
    if role:
        actors.append((actor, role))

actual_counts = collections.Counter(role for _, role in actors)
if len(actors) != 82 or dict(actual_counts) != EXPECTED_COUNTS:
    raise RuntimeError(
        "SUNSCAR_STRUCTURAL_MATERIAL_SCOPE_REFUSED actor_count=%d role_counts=%s"
        % (len(actors), dict(actual_counts))
    )

material_paths = {target_path(label, role) for label in WALL_MATERIALS for role in EXPECTED_COUNTS}
materials = {path: common.load_asset_checked(config, path) for path in material_paths}
records = []
for actor, role in sorted(actors, key=lambda item: item[0].get_actor_label()):
    label = actor.get_actor_label()
    site_id = label[5:11]
    if site_id not in WALL_MATERIALS:
        raise RuntimeError("SUNSCAR_STRUCTURAL_MATERIAL_UNCLASSIFIED " + label)
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        raise RuntimeError("SUNSCAR_STRUCTURAL_MATERIAL_COMPONENT_REFUSED " + label)
    current = component.get_material(0)
    current_path = current.get_path_name() if current else ""
    desired_path = target_path(site_id, role)
    allowed_targets = set(WALL_MATERIALS.values()) | {CONCRETE, STONE, METAL}
    if not (current_path.startswith(PROTOTYPE_PREFIX) or current_path in allowed_targets):
        raise RuntimeError(
            "SUNSCAR_STRUCTURAL_MATERIAL_UNEXPECTED_SOURCE %s %s" % (label, current_path)
        )
    record = {
        "site_id": site_id,
        "label": label,
        "role": role,
        "source_material": current_path,
        "target_material": desired_path,
        "package": actor.get_package().get_name(),
    }
    if apply_requested:
        actor.modify()
        component.modify()
        component.set_material(0, materials[desired_path])
        if PASS_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [PASS_TAG]
        record["applied_material"] = component.get_material(0).get_path_name()
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "role_counts": dict(sorted(actual_counts.items())),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_structural_material_apply_v1.json"
    if apply_requested
    else "old_town_structural_material_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_STRUCTURAL_MATERIAL mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report)
)
print("SUNSCAR_STRUCTURAL_MATERIAL", len(records), report)
