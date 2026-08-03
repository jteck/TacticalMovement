"""Save exactly the four reviewed large cabinets and required folder packages."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownLargeUtilityResolvedV1"
EXPECTED_LABELS = {
    "OT_UTIL_SS_003_UTILITY_008",
    "OT_UTIL_SS_003_UTILITY_013",
    "OT_UTIL_SS_016_UTILITY_020",
    "OT_UTIL_SS_016_UTILITY_027",
}
MESH_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_004_ujzfde2/"
    "Electrical_Cabinet_ujzfde2_High.Electrical_Cabinet_ujzfde2_High"
)


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
actors = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if TAG in common.actor_tags(actor)
    ],
    key=lambda actor: actor.get_actor_label(),
)
labels = {actor.get_actor_label() for actor in actors}
if labels != EXPECTED_LABELS:
    raise RuntimeError(
        "SUNSCAR_LARGE_UTILITY_SAVE_REFUSED labels=%s" % "|".join(sorted(labels))
    )
for actor in actors:
    component = getattr(actor, "static_mesh_component", None)
    mesh = component.get_editor_property("static_mesh") if component else None
    if mesh is None or mesh.get_path_name() != MESH_PATH:
        raise RuntimeError(
            "SUNSCAR_LARGE_UTILITY_SAVE_REFUSED mesh=" + actor.get_actor_label()
        )
    if "QUERY_AND_PHYSICS" not in str(component.get_collision_enabled()):
        raise RuntimeError(
            "SUNSCAR_LARGE_UTILITY_SAVE_REFUSED collision=" + actor.get_actor_label()
        )

actor_package_names = {actor.get_package().get_name() for actor in actors}
dirty_content_packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_map_packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
dirty_content_names = {package.get_name() for package in dirty_content_packages}
dirty_map_names = {package.get_name() for package in dirty_map_packages}
folder_package_names = dirty_map_names - actor_package_names
if dirty_content_names or not actor_package_names.issubset(dirty_map_names):
    raise RuntimeError(
        "SUNSCAR_LARGE_UTILITY_SAVE_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content_names)), "|".join(sorted(dirty_map_names)))
    )
if len(folder_package_names) != 3 or any(
    not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")
    for name in folder_package_names
):
    raise RuntimeError(
        "SUNSCAR_LARGE_UTILITY_SAVE_FOLDER_SCOPE_REFUSED %s"
        % "|".join(sorted(folder_package_names))
    )
if dirty_map_names != actor_package_names | folder_package_names:
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_SAVE_UNEXPECTED_MAP_SCOPE")

packages = sorted(dirty_map_packages, key=lambda package: package.get_name())
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("SUNSCAR_LARGE_UTILITY_SAVE_DIRTY_AFTER %s" % "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "exact_large_utility_scope_saved",
    "context": context,
    "actor_count": len(actors),
    "actor_packages": sorted(actor_package_names),
    "folder_packages": sorted(folder_package_names),
    "saved_packages": [package.get_name() for package in packages],
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_save_large_utility_v1.json", payload)
unreal.log(
    "SUNSCAR_LARGE_UTILITY_SAVE packages=%d report=%s" % (len(packages), report)
)
print("SUNSCAR_LARGE_UTILITY_SAVE", len(packages), report)
