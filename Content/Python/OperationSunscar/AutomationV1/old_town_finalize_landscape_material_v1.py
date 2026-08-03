"""Save the parent Landscape material while discarding proxy-only preview edits."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarLandscapeMaterialPassV1")
TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/Landscape/MI_OT_Landscape_Sandstone"
PARENT_LABEL = "Landscape_Sunscar"
PROXY_LABELS = {
    "LandscapeStreamingProxy_1_1_0",
    "LandscapeStreamingProxy_1_2_0",
    "LandscapeStreamingProxy_2_1_0",
    "LandscapeStreamingProxy_2_2_0",
}


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
material = unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
if material is None:
    raise RuntimeError("SUNSCAR_LANDSCAPE_FINALIZE_REFUSED missing_material")

actors_by_label = {
    actor.get_actor_label(): actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if isinstance(actor, unreal.LandscapeProxy)
}
expected_labels = PROXY_LABELS | {PARENT_LABEL}
if set(actors_by_label) != expected_labels:
    raise RuntimeError(
        "SUNSCAR_LANDSCAPE_FINALIZE_REFUSED labels=%s"
        % "|".join(sorted(actors_by_label))
    )

parent = actors_by_label[PARENT_LABEL]
parent_material = parent.get_editor_property("landscape_material")
if parent_material is None or parent_material.get_path_name() != TARGET_PATH + ".MI_OT_Landscape_Sandstone":
    raise RuntimeError("SUNSCAR_LANDSCAPE_FINALIZE_REFUSED parent_material")

material_package = material.get_package()
parent_package = parent.get_package()
proxy_packages = [actors_by_label[label].get_package() for label in sorted(PROXY_LABELS)]
expected_dirty_names = {
    package_name(material_package),
    package_name(parent_package),
    *(package_name(package) for package in proxy_packages),
}
dirty_before = {
    package_name(package)
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
}
if dirty_before not in (set(), expected_dirty_names):
    raise RuntimeError(
        "SUNSCAR_LANDSCAPE_FINALIZE_REFUSED dirty=%s"
        % "|".join(sorted(dirty_before))
    )

already_finalized = not dirty_before
save_packages = [material_package, parent_package]
reloaded_package_names = []
if not already_finalized:
    # The streaming proxies inherit the parent Landscape material. Remove only
    # the temporary preview tag/property, save the parent and material, then
    # discard the proxy-only preview edits by reloading their packages.
    for label in sorted(PROXY_LABELS):
        proxy = actors_by_label[label]
        proxy.modify()
        proxy.set_editor_property("landscape_material", None)
        proxy.tags = [tag for tag in list(proxy.tags) if tag != PASS_TAG]

    parent.tags = [tag for tag in list(parent.tags) if tag != PASS_TAG] + [PASS_TAG]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(save_packages, True):
        raise RuntimeError("SUNSCAR_LANDSCAPE_FINALIZE_SAVE_FAILED")

    reloaded, error = unreal.EditorLoadingAndSavingUtils.reload_packages(
        proxy_packages, unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE
    )
    if not reloaded:
        raise RuntimeError("SUNSCAR_LANDSCAPE_FINALIZE_RELOAD_FAILED error=%s" % error)
    reloaded_package_names = sorted(package_name(package) for package in proxy_packages)

actors_after = {
    actor.get_actor_label(): actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if isinstance(actor, unreal.LandscapeProxy)
}
proxy_results = []
for label in sorted(PROXY_LABELS):
    proxy = actors_after[label]
    inherited_slot = proxy.get_editor_property("landscape_material")
    tags = list(proxy.tags)
    inherited_path = inherited_slot.get_path_name() if inherited_slot else ""
    if inherited_path != TARGET_PATH + ".MI_OT_Landscape_Sandstone" or PASS_TAG in tags:
        raise RuntimeError("SUNSCAR_LANDSCAPE_FINALIZE_PROXY_RESTORE_FAILED " + label)
    proxy_results.append({
        "label": label,
        "landscape_material": inherited_path,
        "pass_tag_present": False,
        "package": package_name(proxy.get_package()),
    })

parent_after = actors_after[PARENT_LABEL]
parent_after_material = parent_after.get_editor_property("landscape_material")
if parent_after_material is None or parent_after_material.get_path_name() != TARGET_PATH + ".MI_OT_Landscape_Sandstone":
    raise RuntimeError("SUNSCAR_LANDSCAPE_FINALIZE_PARENT_VERIFY_FAILED")

dirty_after = sorted(
    package_name(package)
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
if dirty_after:
    raise RuntimeError(
        "SUNSCAR_LANDSCAPE_FINALIZE_DIRTY_AFTER %s" % "|".join(dirty_after)
    )

payload = {
    "schema_version": 1,
    "status": (
        "already_finalized_verified"
        if already_finalized
        else "exact_parent_and_material_saved_proxies_reloaded"
    ),
    "context": context,
    "material_path": TARGET_PATH,
    "saved_packages": (
        [] if already_finalized else sorted(package_name(package) for package in save_packages)
    ),
    "reloaded_unsaved_proxy_packages": reloaded_package_names,
    "parent_actor": PARENT_LABEL,
    "proxy_results": proxy_results,
    "dirty_packages_after": dirty_after,
    "changes_saved": True,
}
report = common.write_json_report(config, "old_town_finalize_landscape_material_v1.json", payload)
unreal.log("SUNSCAR_LANDSCAPE_FINALIZE saved=2 reloaded=4 report=%s" % report)
print("SUNSCAR_LANDSCAPE_FINALIZE", report)
