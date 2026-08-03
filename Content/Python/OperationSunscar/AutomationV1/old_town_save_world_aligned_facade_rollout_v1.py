"""Save exactly the reviewed Old Town world-aligned facade rollout."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


STUCCO_TAG = "SunscarWorldAlignedStuccoRolloutV1"
FLAKED_TAG = "SunscarWorldAlignedFlakedRolloutV1"
STUCCO_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_WorldAligned"
FLAKED_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_WorldAligned"


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
stucco = common.load_asset_checked(config, STUCCO_PATH)
flaked = common.load_asset_checked(config, FLAKED_PATH)
actors = list(common.actor_subsystem().get_all_level_actors())
stucco_actors = sorted(
    [actor for actor in actors if STUCCO_TAG in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
flaked_actors = sorted(
    [actor for actor in actors if FLAKED_TAG in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
if len(stucco_actors) != 66 or len(flaked_actors) != 14:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_ROLLOUT_SAVE_REFUSED stucco=%d flaked=%d"
        % (len(stucco_actors), len(flaked_actors))
    )
for actor, target in (
    [(actor, stucco) for actor in stucco_actors]
    + [(actor, flaked) for actor in flaked_actors]
):
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    if material != target:
        raise RuntimeError(
            "SUNSCAR_WORLD_ALIGNED_ROLLOUT_SAVE_REFUSED material="
            + actor.get_actor_label()
        )

actor_packages = {actor.get_package() for actor in stucco_actors + flaked_actors}
expected_maps = {package.get_name() for package in actor_packages}
dirty_content = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content != {STUCCO_PATH} or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_ROLLOUT_SAVE_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps)))
    )

packages = sorted(
    actor_packages | {stucco.get_package()}, key=lambda package: package.get_name()
)
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_ROLLOUT_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_ROLLOUT_SAVE_DIRTY_AFTER %s" % "|".join(remaining)
    )

payload = {
    "schema_version": 1,
    "status": "exact_world_aligned_facade_rollout_saved",
    "context": context,
    "stucco_actor_count": len(stucco_actors),
    "flaked_actor_count": len(flaked_actors),
    "saved_packages": [package.get_name() for package in packages],
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(
    config, "old_town_save_world_aligned_facade_rollout_v1.json", payload
)
unreal.log(
    "SUNSCAR_WORLD_ALIGNED_ROLLOUT_SAVE packages=%d report=%s"
    % (len(packages), report)
)
print("SUNSCAR_WORLD_ALIGNED_ROLLOUT_SAVE", len(packages), report)
