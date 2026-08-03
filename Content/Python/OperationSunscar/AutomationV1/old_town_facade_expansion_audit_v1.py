"""Read-only exterior-piece audit for expanding the SS_005 facade standard."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


STUCCO_SITES = {"SS_004", "SS_005", "SS_007", "SS_012"}
FLAKED_SITES = {"SS_011", "SS_017"}
HELD_SITES = {"SS_003", "SS_006", "SS_010", "SS_013", "SS_015", "SS_016", "SS_018"}
STUCCO_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_Quixel"
FLAKED_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_Quixel"


def site_from_label(label):
    marker = label.find("SS_")
    return label[marker:marker + 6] if marker >= 0 else ""


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
records = []
for actor in common.actor_subsystem().get_all_level_actors():
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    tags = common.actor_tags(actor)
    component = getattr(actor, "static_mesh_component", None)
    if component is None or component.get_num_materials() != 1:
        continue
    core_exterior = (
        folder.startswith("Sunscar/CorePlayable/Buildings/")
        and "CoreCategory_Building" in tags
        and "Floor" not in label
        and "Roof" not in label
    )
    art_parapet = folder.startswith("OldTown_ArtDraft/") and "Parapet" in label
    if not (core_exterior or art_parapet):
        continue
    site_id = site_from_label(label)
    if site_id not in STUCCO_SITES | FLAKED_SITES | HELD_SITES:
        continue
    material = component.get_material(0)
    material_path = material.get_path_name() if material else ""
    if site_id in STUCCO_SITES:
        recommendation = STUCCO_PATH
        disposition = "stucco_expand" if site_id != "SS_005" else "stucco_standard_complete"
    elif site_id in FLAKED_SITES:
        recommendation = FLAKED_PATH
        disposition = "flaked_paint_prototype_required"
    else:
        recommendation = material_path
        disposition = "hold_existing_role_material"
    records.append({
        "site_id": site_id,
        "label": label,
        "folder": folder,
        "material_path": material_path,
        "prototype_grid": material_path.startswith("/Game/LevelPrototyping/Materials/"),
        "recommended_material": recommendation,
        "disposition": disposition,
        "package": actor.get_package().get_name(),
    })
records.sort(key=lambda row: (row["site_id"], row["label"]))
site_counts = collections.Counter(row["site_id"] for row in records)
prototype_counts = collections.Counter(
    row["site_id"] for row in records if row["prototype_grid"]
)
disposition_counts = collections.Counter(row["disposition"] for row in records)
dirty = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "site_counts": dict(sorted(site_counts.items())),
    "prototype_grid_counts": dict(sorted(prototype_counts.items())),
    "disposition_counts": dict(sorted(disposition_counts.items())),
    "records": records,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_facade_expansion_audit_v1.json", payload)
unreal.log("SUNSCAR_FACADE_EXPANSION_AUDIT actors=%d dirty=%d report=%s" % (len(records), len(dirty), report))
print("SUNSCAR_FACADE_EXPANSION_AUDIT", len(records), report)
