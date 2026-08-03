"""Apply the validated world-aligned facade standard to planned Old Town sites, unsaved."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


MASTER_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/M_OT_WorldAlignedFacade"
STUCCO_NAME = "MI_OT_Stucco_WorldAligned"
STUCCO_FOLDER = "/Game/Maps/Sunscar/Art/Materials/Facade"
STUCCO_PATH = STUCCO_FOLDER + "/" + STUCCO_NAME
FLAKED_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_WorldAligned"
STUCCO_BASE_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_016_vigrejf/"
    "Stucco_Wall_vigrejf_4K_BaseColor"
)
STUCCO_NORMAL_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_016_vigrejf/"
    "Stucco_Wall_vigrejf_4K_Normal"
)
STUCCO_SITES = {"SS_004", "SS_005", "SS_007", "SS_012"}
FLAKED_SITE = "SS_011"
STUCCO_TAG = unreal.Name("SunscarWorldAlignedStuccoRolloutV1")
FLAKED_TAG = unreal.Name("SunscarWorldAlignedFlakedRolloutV1")
OLD_STUCCO_PATH = (
    "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_Quixel."
    "MI_OT_Stucco_Quixel"
)
ALLOWED_FLAKED_SOURCE_PREFIXES = (
    "/Game/LevelPrototyping/Materials/",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_WarmStucco.",
    FLAKED_PATH + ".MI_OT_FlakedPaint_WorldAligned",
)


def site_from_label(label):
    marker = label.find("SS_")
    return label[marker:marker + 6] if marker >= 0 else ""


def is_core_exterior(actor):
    label = actor.get_actor_label()
    return (
        common.actor_folder(actor).startswith("Sunscar/CorePlayable/Buildings/")
        and "CoreCategory_Building" in common.actor_tags(actor)
        and "Floor" not in label
        and "Roof" not in label
    )


def is_stucco_target(actor):
    label = actor.get_actor_label()
    site_id = site_from_label(label)
    art_parapet = common.actor_folder(actor).startswith("OldTown_ArtDraft/") and "Parapet" in label
    return site_id in STUCCO_SITES and (is_core_exterior(actor) or art_parapet)


def is_flaked_target(actor):
    return site_from_label(actor.get_actor_label()) == FLAKED_SITE and is_core_exterior(actor)


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
if dirty_before:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_ROLLOUT_REFUSED dirty_before=%d" % len(dirty_before))
if unreal.EditorAssetLibrary.does_asset_exist(STUCCO_PATH):
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_ROLLOUT_REFUSED existing=" + STUCCO_PATH)

master = common.load_asset_checked(config, MASTER_PATH)
flaked = common.load_asset_checked(config, FLAKED_PATH)
stucco_base = common.load_asset_checked(config, STUCCO_BASE_PATH)
stucco_normal = common.load_asset_checked(config, STUCCO_NORMAL_PATH)

actors = list(common.actor_subsystem().get_all_level_actors())
stucco_targets = sorted(
    [actor for actor in actors if is_stucco_target(actor)],
    key=lambda actor: actor.get_actor_label(),
)
flaked_targets = sorted(
    [actor for actor in actors if is_flaked_target(actor)],
    key=lambda actor: actor.get_actor_label(),
)
if len(stucco_targets) != 66 or len(flaked_targets) != 14:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_ROLLOUT_SCOPE_REFUSED stucco=%d flaked=%d"
        % (len(stucco_targets), len(flaked_targets))
    )
for actor in stucco_targets:
    component = getattr(actor, "static_mesh_component", None)
    current = component.get_material(0) if component else None
    current_path = current.get_path_name() if current else ""
    if component is None or component.get_num_materials() != 1 or current_path != OLD_STUCCO_PATH:
        raise RuntimeError(
            "SUNSCAR_WORLD_ALIGNED_ROLLOUT_STUCCO_SOURCE_REFUSED %s %s"
            % (actor.get_actor_label(), current_path)
        )
for actor in flaked_targets:
    component = getattr(actor, "static_mesh_component", None)
    current = component.get_material(0) if component else None
    current_path = current.get_path_name() if current else ""
    if (
        component is None
        or component.get_num_materials() != 1
        or not current_path.startswith(ALLOWED_FLAKED_SOURCE_PREFIXES)
    ):
        raise RuntimeError(
            "SUNSCAR_WORLD_ALIGNED_ROLLOUT_FLAKED_SOURCE_REFUSED %s %s"
            % (actor.get_actor_label(), current_path)
        )

stucco = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    STUCCO_NAME,
    STUCCO_FOLDER,
    unreal.MaterialInstanceConstant,
    unreal.MaterialInstanceConstantFactoryNew(),
)
if stucco is None:
    raise RuntimeError("SUNSCAR_WORLD_ALIGNED_ROLLOUT_STUCCO_CREATE_FAILED")
stucco.set_editor_property("parent", master)
unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
    stucco, "BaseColorTexture", stucco_base
)
unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
    stucco, "NormalTexture", stucco_normal
)
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
    stucco, "TextureSizeCm", unreal.LinearColor(r=200.0, g=200.0, b=200.0, a=1.0)
)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
    stucco, "Roughness", 0.9
)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
    stucco, "Specular", 0.15
)
unreal.MaterialEditingLibrary.update_material_instance(stucco)

records = []
for actor, target, pass_tag, treatment in (
    [(actor, stucco, STUCCO_TAG, "stucco") for actor in stucco_targets]
    + [(actor, flaked, FLAKED_TAG, "flaked_paint") for actor in flaked_targets]
):
    component = actor.static_mesh_component
    current = component.get_material(0)
    actor.modify()
    component.modify()
    component.set_material(0, target)
    if pass_tag not in list(actor.tags):
        actor.tags = list(actor.tags) + [pass_tag]
    records.append(
        {
            "site_id": site_from_label(actor.get_actor_label()),
            "label": actor.get_actor_label(),
            "treatment": treatment,
            "source_material": current.get_path_name() if current else "",
            "target_material": target.get_path_name(),
            "package": actor.get_package().get_name(),
        }
    )

dirty_content = sorted(
    package.get_name()
    for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
expected_content = [STUCCO_PATH]
expected_maps = sorted({record["package"] for record in records})
if dirty_content != expected_content or dirty_maps != expected_maps:
    raise RuntimeError(
        "SUNSCAR_WORLD_ALIGNED_ROLLOUT_DIRTY_SCOPE_FAILED content=%s maps=%s"
        % ("|".join(dirty_content), "|".join(dirty_maps))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_world_aligned_facade_rollout_ready",
    "context": context,
    "material_instance_created": STUCCO_PATH,
    "stucco_actor_count": len(stucco_targets),
    "flaked_actor_count": len(flaked_targets),
    "held_stone_parapet_count": 4,
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "level_saved": False,
}
report = common.write_json_report(
    config, "old_town_world_aligned_facade_rollout_v1.json", payload
)
unreal.log(
    "SUNSCAR_WORLD_ALIGNED_ROLLOUT stucco=%d flaked=%d report=%s"
    % (len(stucco_targets), len(flaked_targets), report)
)
print("SUNSCAR_WORLD_ALIGNED_ROLLOUT", report)
