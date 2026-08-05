"""Import the deterministic 2017x2017 Abiverd meadow mask into edit layer 0."""

import hashlib
import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
MASK_PATH = "/private/tmp/abiverd_meadow_mask_2017.png"
MASK_SHA256 = "135b4b2459decdb500bfb6ee8aa5380601fa93715854e445104375673c41b352"
MASK_SIZE = 2017
LAYER_NAME = unreal.Name("Grass")
LAYER_INFO_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/Layers/LI_Meadow_NonWeight"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
DIRTY_BEFORE_LANDSCAPE_PACKAGES = {
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/PW/GCKDH3SJ6DMPX8ALJXPIKR",
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/8/GT/L3TLG9CXADXV9PPFBSW6JX",
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/D/PO/W2I3PIR4HKE2ZTVN9LNQ4K",
}
EXTERNAL_OBJECT_PREFIX = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"


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
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_CONTEXT")

expected_dirty_before = {LAYER_INFO_PATH, MATERIAL_PATH} | DIRTY_BEFORE_LANDSCAPE_PACKAGES
dirty_before = dirty_packages()
if set(dirty_before) != expected_dirty_before:
    raise RuntimeError(
        "ABIVERD_MEADOW_WEIGHTMAP_DIRTY_BEFORE expected=%s actual=%s"
        % ("|".join(sorted(expected_dirty_before)), "|".join(dirty_before))
    )
if not os.path.isfile(MASK_PATH):
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_MASK_MISSING")
with open(MASK_PATH, "rb") as handle:
    mask_sha256 = hashlib.sha256(handle.read()).hexdigest()
if mask_sha256 != MASK_SHA256:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_MASK_HASH " + mask_sha256)

layer_info = unreal.EditorAssetLibrary.load_asset(LAYER_INFO_PATH)
material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
if not isinstance(layer_info, unreal.LandscapeLayerInfoObject) or not isinstance(material, unreal.Material):
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_ASSETS")
if str(layer_info.get_editor_property("layer_name")) != "Grass":
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_LAYER_NAME")
if layer_info.get_editor_property("blend_method") != unreal.LandscapeTargetLayerBlendMethod.NONE:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_BLEND_METHOD")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
landscapes = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
parents = [actor for actor in landscapes if actor.get_actor_label() == "Landscape_Sunscar"]
proxies = [actor for actor in landscapes if isinstance(actor, unreal.LandscapeStreamingProxy)]
component_count = sum(
    len(proxy.get_components_by_class(unreal.LandscapeComponent)) for proxy in proxies
)
if len(landscapes) != 17 or len(parents) != 1 or len(proxies) != 16 or component_count != 256:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_LANDSCAPE_SCOPE")
parent = parents[0]
for actor in landscapes:
    assigned_material = actor.get_editor_property("landscape_material")
    if not assigned_material or not assigned_material.get_path_name().startswith(MATERIAL_PATH + "."):
        raise RuntimeError(
            "ABIVERD_MEADOW_WEIGHTMAP_MATERIAL " + actor.get_actor_label()
        )
target_layers = parent.get_editor_property("target_layers")
if LAYER_NAME not in target_layers:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_TARGET_LAYER")
assigned_info = target_layers[LAYER_NAME].get_editor_property("layer_info_obj")
if assigned_info != layer_info or "Grass" not in [str(name) for name in parent.get_target_layer_names()]:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_LAYER_REGISTRY")
if len(parent.get_edit_layers_bp()) != 1:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_EDIT_LAYER_SCOPE")

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mask_texture = unreal.RenderingLibrary.import_file_as_texture2d(world, MASK_PATH)
if not isinstance(mask_texture, unreal.Texture2D):
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_TEXTURE_IMPORT")
try:
    mask_texture.set_editor_property("srgb", False)
except Exception:
    pass

render_target = unreal.RenderingLibrary.create_render_target2d(
    world,
    MASK_SIZE,
    MASK_SIZE,
    unreal.TextureRenderTargetFormat.RTF_RGBA8,
    unreal.LinearColor(0.0, 0.0, 0.0, 1.0),
    False,
    False,
)
if not isinstance(render_target, unreal.TextureRenderTarget2D):
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_RENDER_TARGET")
unreal.RenderingLibrary.clear_render_target2d(world, render_target, unreal.LinearColor(0.0, 0.0, 0.0, 1.0))
canvas, size, context = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, render_target)
canvas.draw_texture(
    mask_texture,
    unreal.Vector2D(0.0, 0.0),
    unreal.Vector2D(float(MASK_SIZE), float(MASK_SIZE)),
    unreal.Vector2D(0.0, 0.0),
    unreal.Vector2D(1.0, 1.0),
    unreal.LinearColor(1.0, 1.0, 1.0, 1.0),
    unreal.BlendMode.BLEND_OPAQUE,
    0.0,
    unreal.Vector2D(0.5, 0.5),
)
unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, context)

import_result = parent.landscape_import_weightmap_from_render_target(render_target, LAYER_NAME, 0)
unreal.RenderingLibrary.release_render_target2d(render_target)
if not import_result:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_IMPORT_FAILED")
parent.force_layers_full_update()

dirty_after = dirty_packages()
allowed_dirty_after = {LAYER_INFO_PATH, MATERIAL_PATH} | {
    actor.get_package().get_name() for actor in landscapes
}
unexpected = [
    name for name in dirty_after
    if name not in allowed_dirty_after and not name.startswith(EXTERNAL_OBJECT_PREFIX)
]
payload = {
    "schema_version": 1,
    "status": "unsaved_meadow_weightmap_preview_ready" if not unexpected else "unexpected_dirty_scope",
    "level": level_path,
    "semantic_layer_name": "Meadow",
    "target_layer_name": str(LAYER_NAME),
    "edit_layer_index": 0,
    "landscape_proxy_count": len(proxies),
    "landscape_component_count": component_count,
    "mask_path": MASK_PATH,
    "mask_sha256": mask_sha256,
    "mask_dimensions": [MASK_SIZE, MASK_SIZE],
    "landscape_extent_cm": [-126000, -126000, 126000, 126000],
    "import_result": bool(import_result),
    "dirty_packages_before": dirty_before,
    "dirty_packages_after": dirty_after,
    "unexpected_dirty_packages": unexpected,
    "changes_saved": False,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_meadow_weightmap_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

if unexpected:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHTMAP_DIRTY_SCOPE " + "|".join(unexpected))
unreal.log("ABIVERD_MEADOW_WEIGHTMAP_COMPLETE dirty=%d" % len(dirty_after))
