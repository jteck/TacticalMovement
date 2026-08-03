"""Dry-run-first replacement of eight raw grass instances with proven Epic meshes."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


RAW_PREFIX = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_015_tbbqejqr/"
REPLACEMENTS = (
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/SM_Urb_Street_Grass_Dry_01_A",
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/SM_Urb_Street_Grass_Dry_01_B",
)
EXPECTED = 8
EXPECTED_LABELS = {
    "OT_AUTO_SS_008_VEGETATION_001",
    "OT_AUTO_SS_008_VEGETATION_004",
    "OT_AUTO_SS_008_VEGETATION_007",
    "OT_AUTO_SS_008_VEGETATION_010",
    "OT_AUTO_SS_008_VEGETATION_013",
    "OT_AUTO_SS_008_VEGETATION_016",
    "OT_AUTO_SS_008_VEGETATION_019",
    "OT_AUTO_SS_008_VEGETATION_022",
}
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
tag = unreal.Name(config["execution"]["placement_tag"])
actors = [
    actor
    for actor in list(common.actor_subsystem().get_all_level_actors())
    if tag in list(actor.tags) and actor.get_actor_label().startswith("OT_AUTO_")
]

targets = []
for actor in actors:
    component = actor.static_mesh_component if isinstance(actor, unreal.StaticMeshActor) else None
    mesh = component.static_mesh if component else None
    mesh_path = mesh.get_path_name().split(".")[0] if mesh else ""
    if actor.get_actor_label() in EXPECTED_LABELS:
        allowed_current = mesh_path.startswith(RAW_PREFIX) or mesh_path in REPLACEMENTS
        if not allowed_current:
            raise RuntimeError(
                "SUNSCAR_GRASS_REPLACE_REFUSED unexpected_current_mesh=%s actor=%s"
                % (mesh_path, actor.get_actor_label())
            )
        targets.append((actor, component, mesh_path))
targets.sort(key=lambda item: item[0].get_actor_label())
if len(targets) != EXPECTED:
    raise RuntimeError(
        "SUNSCAR_GRASS_REPLACE_REFUSED expected=%d actual=%d" % (EXPECTED, len(targets))
    )

replacement_assets = [unreal.EditorAssetLibrary.load_asset(path) for path in REPLACEMENTS]
if not all(isinstance(asset, unreal.StaticMesh) for asset in replacement_assets):
    raise RuntimeError("SUNSCAR_GRASS_REPLACE_REFUSED replacement_mesh_missing")

records = []
for index, (actor, component, old_path) in enumerate(targets):
    before_origin, before_extent = actor.get_actor_bounds(False)
    before_bottom = before_origin.z - before_extent.z
    new_asset = replacement_assets[index % len(replacement_assets)]
    record = {
        "actor_label": actor.get_actor_label(),
        "old_mesh": old_path,
        "new_mesh": REPLACEMENTS[index % len(REPLACEMENTS)],
        "preserved_bottom_z_cm": round(before_bottom, 3),
    }
    if apply_requested:
        actor.modify()
        component.modify()
        component.set_static_mesh(new_asset)
        after_origin, after_extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(
            unreal.Vector(0.0, 0.0, before_bottom - (after_origin.z - after_extent.z)),
            False,
            False,
        )
        actor.tags = list(actor.tags) + [unreal.Name("SunscarOfficialGrassReplacementV1")]
        actor.get_package().mark_package_dirty()
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "target_count": len(targets),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
name = "old_town_replace_raw_grass_apply_v1.json" if apply_requested else "old_town_replace_raw_grass_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_GRASS_REPLACE mode=%s targets=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(targets), report)
)
print("SUNSCAR_GRASS_REPLACE", len(targets), report)
