"""Save exactly the accepted UE 5.8 Landscape Meadow scope."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
LAYER_INFO_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/Layers/LI_Meadow_NonWeight"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_MEADOW_SAVE_CONTEXT")

acceptance_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_meadow_weightmap_acceptance_v1.json",
)
with open(acceptance_path, "r", encoding="utf-8") as handle:
    acceptance = json.load(handle)
if acceptance.get("status") != "accepted_unsaved_meadow_weightmap":
    raise RuntimeError("ABIVERD_MEADOW_SAVE_ACCEPTANCE")

layer_info = unreal.EditorAssetLibrary.load_asset(LAYER_INFO_PATH)
material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
if not isinstance(layer_info, unreal.LandscapeLayerInfoObject) or not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_MEADOW_SAVE_ASSETS")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
proxies = [actor for actor in landscapes if isinstance(actor, unreal.LandscapeStreamingProxy)]
component_count = sum(
    len(proxy.get_components_by_class(unreal.LandscapeComponent)) for proxy in proxies
)
if len(landscapes) != 17 or len(proxies) != 16 or component_count != 256:
    raise RuntimeError("ABIVERD_MEADOW_SAVE_LANDSCAPE_SCOPE")

expected = {LAYER_INFO_PATH, MATERIAL_PATH} | {
    actor.get_package().get_name() for actor in landscapes
}
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
actual = {package_name(package) for package in packages}
if actual != expected or sorted(actual) != sorted(acceptance.get("dirty_packages", [])):
    raise RuntimeError(
        "ABIVERD_MEADOW_SAVE_DIRTY expected=%s actual=%s"
        % ("|".join(sorted(expected)), "|".join(sorted(actual)))
    )

if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_MEADOW_SAVE_FAILED")

remaining = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
if remaining:
    raise RuntimeError("ABIVERD_MEADOW_SAVE_DIRTY_AFTER " + "|".join(remaining))

payload = {
    "schema_version": 1,
    "status": "accepted_landscape_meadow_scope_saved",
    "level": level_path,
    "material": material.get_path_name(),
    "layer_info": layer_info.get_path_name(),
    "landscape_proxy_count": len(proxies),
    "landscape_component_count": component_count,
    "landscape_labels": [actor.get_actor_label() for actor in landscapes],
    "saved_packages": sorted(actual),
    "dirty_packages_after": remaining,
    "changes_saved": True,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_save_landscape_meadow_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_MEADOW_SAVE_COMPLETE packages=%d" % len(actual))
