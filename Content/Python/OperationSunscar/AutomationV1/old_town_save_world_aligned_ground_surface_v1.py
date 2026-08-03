"""Save exactly the reviewed Quixel ground material family and 288 Old Town overlay actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarWorldAlignedGroundSurfaceV1"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/M_OT_WorldAlignedGround"


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
report_path = os.path.join(common.report_directory(config), "old_town_world_aligned_ground_surface_v1.json")
source_report = common.read_json(report_path)
if source_report.get("actor_count") != 288 or len(source_report.get("material_assets", [])) != 9:
    raise RuntimeError("SUNSCAR_GROUND_SAVE_REPORT_SCOPE_REFUSED")

record_by_package = {record["package"]: record for record in source_report["records"]}
if len(record_by_package) != 288:
    raise RuntimeError("SUNSCAR_GROUND_SAVE_REPORT_PACKAGES_REFUSED count=%d" % len(record_by_package))
actors = sorted(
    [actor for actor in common.actor_subsystem().get_all_level_actors() if PASS_TAG in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
if len(actors) != 288:
    raise RuntimeError("SUNSCAR_GROUND_SAVE_ACTOR_SCOPE_REFUSED count=%d" % len(actors))
actor_packages = set()
for actor in actors:
    package = actor.get_package()
    package_name = package.get_name()
    record = record_by_package.get(package_name)
    if record is None or record["label"] != actor.get_actor_label():
        raise RuntimeError("SUNSCAR_GROUND_SAVE_ACTOR_REFUSED " + actor.get_actor_label())
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    material_path = material.get_path_name() if material else ""
    if material_path != record["target_material"]:
        raise RuntimeError(
            "SUNSCAR_GROUND_SAVE_MATERIAL_REFUSED %s %s"
            % (actor.get_actor_label(), material_path)
        )
    actor_packages.add(package)

assets = [common.load_asset_checked(config, path) for path in source_report["material_assets"]]
master = common.load_asset_checked(config, MASTER_PATH)
for asset in assets:
    if isinstance(asset, unreal.MaterialInstanceConstant) and asset.get_editor_property("parent") != master:
        raise RuntimeError("SUNSCAR_GROUND_SAVE_PARENT_REFUSED " + asset.get_path_name())
asset_packages = {asset.get_package() for asset in assets}
expected_content = set(source_report["dirty_content_packages"])
expected_maps = set(source_report["dirty_map_packages"])
dirty_content = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content != expected_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_GROUND_SAVE_DIRTY_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps)))
    )

packages = sorted(asset_packages | actor_packages, key=lambda package: package.get_name())
if len(packages) != 297:
    raise RuntimeError("SUNSCAR_GROUND_SAVE_PACKAGE_COUNT_REFUSED count=%d" % len(packages))
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("SUNSCAR_GROUND_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("SUNSCAR_GROUND_SAVE_DIRTY_AFTER %s" % "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_world_aligned_ground_surface_saved",
    "context": context,
    "actor_count": len(actors),
    "material_asset_count": len(assets),
    "saved_package_count": len(packages),
    "saved_packages": [package.get_name() for package in packages],
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_world_aligned_ground_surface_v1.json", payload)
unreal.log("SUNSCAR_GROUND_SAVE packages=%d report=%s" % (len(packages), report))
print("SUNSCAR_GROUND_SAVE", len(packages), report)
