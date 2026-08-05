"""Create and assign the non-weight-blended Meadow Landscape Layer Info."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
SOURCE_LAYER_INFO = "/Landmass/PreviewContent/LayerInfos/Grass_LayerInfo"
TARGET_FOLDER = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/Layers"
TARGET_PATH = TARGET_FOLDER + "/LI_Meadow_NonWeight"
PARENT_PACKAGE = "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/8/GT/L3TLG9CXADXV9PPFBSW6JX"


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_CONTEXT")
dirty_before = dirty_packages()
target_exists = unreal.EditorAssetLibrary.does_asset_exist(TARGET_PATH)
resume_allowed = {TARGET_PATH, MATERIAL_PATH, PARENT_PACKAGE}
resume_unsaved_duplicate = (
    target_exists
    and TARGET_PATH in dirty_before
    and set(dirty_before).issubset(resume_allowed)
)
if dirty_before and not resume_unsaved_duplicate:
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_DIRTY_BEFORE " + "|".join(dirty_before))
if target_exists and not resume_unsaved_duplicate:
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_EXISTS " + TARGET_PATH)

material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
source = unreal.EditorAssetLibrary.load_asset(SOURCE_LAYER_INFO)
if not isinstance(material, unreal.Material) or not isinstance(source, unreal.LandscapeLayerInfoObject):
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_SOURCE")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
parents = [actor for actor in landscapes if actor.get_actor_label() == "Landscape_Sunscar"]
if len(landscapes) != 3 or len(parents) != 1:
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_LANDSCAPE_SCOPE")
parent = parents[0]
for actor in landscapes:
    assigned = actor.get_editor_property("landscape_material")
    if not assigned or not assigned.get_path_name().startswith(MATERIAL_PATH + "."):
        raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_MATERIAL " + actor.get_actor_label())

unreal.EditorAssetLibrary.make_directory(TARGET_FOLDER)
layer_info = (
    unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
    if resume_unsaved_duplicate
    else unreal.EditorAssetLibrary.duplicate_asset(SOURCE_LAYER_INFO, TARGET_PATH)
)
if not isinstance(layer_info, unreal.LandscapeLayerInfoObject):
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_DUPLICATE")
if str(layer_info.get_editor_property("layer_name")) != "Grass":
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_NAME")
if layer_info.get_editor_property("blend_method") != unreal.LandscapeTargetLayerBlendMethod.NONE:
    layer_info.set_editor_property("blend_method", unreal.LandscapeTargetLayerBlendMethod.NONE)

# Keep the design-facing concept "Meadow" while using the UE 5.8 target-layer
# key "Grass" required by the duplicated Layer Info Object.
renamed_weight_nodes = 0
grass_weight_nodes = 0
for node in unreal.MaterialEditingLibrary.get_material_expressions(material):
    if isinstance(node, unreal.MaterialExpressionLandscapeLayerWeight):
        parameter_name = str(node.get_editor_property("parameter_name"))
        if parameter_name == "Meadow":
            node.set_editor_property("parameter_name", unreal.Name("Grass"))
            renamed_weight_nodes += 1
            grass_weight_nodes += 1
        elif parameter_name == "Grass":
            grass_weight_nodes += 1
if grass_weight_nodes != 4:
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_WEIGHT_NODES count=%d" % grass_weight_nodes)
compiler_errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
if compiler_errors:
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_COMPILE " + "|".join(str(item) for item in compiler_errors))

settings = unreal.LandscapeTargetLayerSettings()
settings.set_editor_property("layer_info_obj", layer_info)
target_layers = parent.get_editor_property("target_layers")
target_layers[unreal.Name("Grass")] = settings
parent.modify()
# UE 5.8 exposes TargetLayers as an in-place mutable map but marks the
# property itself read-only in Python.  Reapplying the already-validated
# Landscape material triggers the actor's normal PostEditChange path so the
# LandscapeInfo layer registry and loaded proxies synchronize with that map.
parent.set_editor_property("landscape_material", None)
parent.set_editor_property("landscape_material", material)
parent.force_layers_full_update()

dirty = dirty_packages()
allowed = {TARGET_PATH, MATERIAL_PATH} | {actor.get_package().get_name() for actor in landscapes}
unexpected = [name for name in dirty if name not in allowed]
payload = {
    "schema_version": 1,
    "status": "unsaved_meadow_layer_info_ready" if not unexpected else "unexpected_dirty_scope",
    "level": level_path,
    "source_layer_info": SOURCE_LAYER_INFO,
    "target_layer_info": layer_info.get_path_name(),
    "layer_name": str(layer_info.get_editor_property("layer_name")),
    "semantic_layer_name": "Meadow",
    "blend_method": str(layer_info.get_editor_property("blend_method")),
    "renamed_weight_nodes": renamed_weight_nodes,
    "grass_weight_nodes": grass_weight_nodes,
    "target_layer_names": [str(name) for name in parent.get_target_layer_names()],
    "target_layers": str(parent.get_editor_property("target_layers")),
    "dirty_packages": dirty,
    "unexpected_dirty_packages": unexpected,
    "changes_saved": False,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_meadow_layerinfo_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

if unexpected:
    raise RuntimeError("ABIVERD_MEADOW_LAYERINFO_DIRTY_SCOPE " + "|".join(unexpected))
unreal.log("ABIVERD_MEADOW_LAYERINFO_COMPLETE dirty=%d" % len(dirty))
