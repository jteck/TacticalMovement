"""Read back and validate the final UE 5.8 Grass/Meadow Landscape weightmap."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
LAYER_INFO_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/Layers/LI_Meadow_NonWeight"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"


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


level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHT_ACCEPTANCE_CONTEXT")
actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
parents = [actor for actor in actors if isinstance(actor, unreal.Landscape) and actor.get_actor_label() == "Landscape_Sunscar"]
landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
proxies = [actor for actor in landscapes if isinstance(actor, unreal.LandscapeStreamingProxy)]
component_count = sum(
    len(proxy.get_components_by_class(unreal.LandscapeComponent)) for proxy in proxies
)
if len(parents) != 1 or len(proxies) != 16 or component_count != 256:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHT_ACCEPTANCE_LANDSCAPE_SCOPE")
parent = parents[0]
expected_dirty = {LAYER_INFO_PATH, MATERIAL_PATH} | {
    actor.get_package().get_name() for actor in landscapes
}
dirty = dirty_packages()
if set(dirty) != expected_dirty:
    raise RuntimeError(
        "ABIVERD_MEADOW_WEIGHT_ACCEPTANCE_DIRTY expected=%s actual=%s"
        % ("|".join(sorted(expected_dirty)), "|".join(dirty))
    )
if "Grass" not in [str(name) for name in parent.get_target_layer_names()]:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHT_ACCEPTANCE_LAYER")

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
resolution = 512
render_target = unreal.RenderingLibrary.create_render_target2d(
    world,
    resolution,
    resolution,
    unreal.TextureRenderTargetFormat.RTF_RGBA8,
    unreal.LinearColor(0.0, 0.0, 0.0, 1.0),
    False,
    False,
)
rendered = parent.render_weightmap(
    unreal.Transform(),
    unreal.Box2D(),
    unreal.Name("Grass"),
    render_target,
)
if not rendered:
    unreal.RenderingLibrary.release_render_target2d(render_target)
    raise RuntimeError("ABIVERD_MEADOW_WEIGHT_ACCEPTANCE_RENDER")

samples = unreal.RenderingLibrary.read_render_target(world, render_target, False)
unreal.RenderingLibrary.release_render_target2d(render_target)
if samples is None or len(samples) != resolution * resolution:
    raise RuntimeError("ABIVERD_MEADOW_WEIGHT_ACCEPTANCE_READBACK")

red_values = [int(sample.r) for sample in samples]
nonzero = sum(1 for value in red_values if value > 0)
strong = sum(1 for value in red_values if value >= 200)
maximum = max(red_values)
mean = sum(red_values) / float(len(red_values))
if nonzero <= 0 or strong <= 0 or maximum < 240:
    raise RuntimeError(
        "ABIVERD_MEADOW_WEIGHT_ACCEPTANCE_EMPTY nonzero=%d strong=%d max=%d"
        % (nonzero, strong, maximum)
    )

payload = {
    "schema_version": 1,
    "status": "accepted_unsaved_meadow_weightmap",
    "level": level_path,
    "semantic_layer_name": "Meadow",
    "target_layer_name": "Grass",
    "landscape_proxy_count": len(proxies),
    "landscape_component_count": component_count,
    "readback_resolution": [resolution, resolution],
    "sample_count": len(red_values),
    "nonzero_sample_count": nonzero,
    "strong_sample_count": strong,
    "maximum_weight": maximum,
    "mean_weight": mean,
    "nonzero_coverage_percent": 100.0 * nonzero / float(len(red_values)),
    "dirty_packages": dirty,
    "changes_saved": False,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_meadow_weightmap_acceptance_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_MEADOW_WEIGHT_ACCEPTANCE_COMPLETE nonzero=%d strong=%d max=%d"
    % (nonzero, strong, maximum)
)
