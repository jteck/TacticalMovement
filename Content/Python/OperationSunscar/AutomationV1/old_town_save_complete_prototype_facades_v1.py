"""Save exactly the reviewed 40 prototype-facade replacement actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = "SunscarCompletePrototypeFacadesV1"
EXPECTED_COUNTS = {
    "SS_003": 6,
    "SS_010": 9,
    "SS_013": 5,
    "SS_015": 5,
    "SS_016": 6,
    "SS_018": 9,
}
SITE_TARGETS = {
    "SS_003": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone",
    "SS_010": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Detention",
    "SS_013": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone",
    "SS_015": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal",
    "SS_016": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal",
    "SS_018": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone",
}


def site_from_label(label):
    marker = label.find("SS_")
    return label[marker:marker + 6] if marker >= 0 else ""


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
materials = {
    site_id: common.load_asset_checked(config, path)
    for site_id, path in SITE_TARGETS.items()
}
actors = sorted(
    [
        actor
        for actor in common.actor_subsystem().get_all_level_actors()
        if PASS_TAG in common.actor_tags(actor)
    ],
    key=lambda actor: actor.get_actor_label(),
)
counts = {site_id: 0 for site_id in EXPECTED_COUNTS}
for actor in actors:
    site_id = site_from_label(actor.get_actor_label())
    if site_id not in counts:
        raise RuntimeError(
            "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SAVE_SITE_REFUSED "
            + actor.get_actor_label()
        )
    counts[site_id] += 1
    component = getattr(actor, "static_mesh_component", None)
    material = component.get_material(0) if component else None
    if material != materials[site_id]:
        raise RuntimeError(
            "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SAVE_MATERIAL_REFUSED "
            + actor.get_actor_label()
        )
if counts != EXPECTED_COUNTS or len(actors) != 40:
    raise RuntimeError(
        "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SAVE_SCOPE_REFUSED counts=%s" % counts
    )

packages = {actor.get_package() for actor in actors}
expected_maps = {package.get_name() for package in packages}
dirty_content = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
}
dirty_maps = {
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
}
if dirty_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SAVE_DIRTY_SCOPE_REFUSED content=%s maps=%s"
        % ("|".join(sorted(dirty_content)), "|".join(sorted(dirty_maps)))
    )

ordered_packages = sorted(packages, key=lambda package: package.get_name())
if not unreal.EditorLoadingAndSavingUtils.save_packages(ordered_packages, True):
    raise RuntimeError("SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError(
        "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SAVE_DIRTY_AFTER %s"
        % "|".join(remaining)
    )

payload = {
    "schema_version": 1,
    "status": "exact_complete_prototype_facades_saved",
    "context": context,
    "actor_count": len(actors),
    "counts_by_site": counts,
    "saved_packages": [package.get_name() for package in ordered_packages],
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report = common.write_json_report(
    config, "old_town_save_complete_prototype_facades_v1.json", payload
)
unreal.log(
    "SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SAVE packages=%d report=%s"
    % (len(ordered_packages), report)
)
print("SUNSCAR_COMPLETE_PROTOTYPE_FACADES_SAVE", len(ordered_packages), report)
