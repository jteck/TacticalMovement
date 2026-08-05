"""Read-only sampling probe for the transient Abiverd meadow mask render target."""

import json
import os

import unreal


MASK_PATH = "/private/tmp/abiverd_meadow_mask_2017.png"
SIZE = 2017
WORLD_MIN = -126000.0
SPACING = 125.0
CENTERS = [
    (-4500.0, 16300.0),
    (-4500.0, 18700.0),
    (-4300.0, 21100.0),
    (4400.0, 16900.0),
    (4300.0, 19400.0),
    (4400.0, 21600.0),
]


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


dirty_before = dirty_packages()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
texture = unreal.RenderingLibrary.import_file_as_texture2d(world, MASK_PATH)
if not isinstance(texture, unreal.Texture2D):
    raise RuntimeError("ABIVERD_MASK_RT_PROBE_TEXTURE")
try:
    texture.set_editor_property("srgb", False)
except Exception:
    pass

render_target = unreal.RenderingLibrary.create_render_target2d(
    world,
    SIZE,
    SIZE,
    unreal.TextureRenderTargetFormat.RTF_RGBA8,
    unreal.LinearColor(0.0, 0.0, 0.0, 1.0),
    False,
    False,
)
unreal.RenderingLibrary.clear_render_target2d(world, render_target, unreal.LinearColor(0.0, 0.0, 0.0, 1.0))
canvas, draw_size, context = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, render_target)
canvas.draw_texture(
    texture,
    unreal.Vector2D(0.0, 0.0),
    unreal.Vector2D(float(SIZE), float(SIZE)),
    unreal.Vector2D(0.0, 0.0),
    unreal.Vector2D(1.0, 1.0),
    unreal.LinearColor(1.0, 1.0, 1.0, 1.0),
    unreal.BlendMode.BLEND_OPAQUE,
    0.0,
    unreal.Vector2D(0.5, 0.5),
)
unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, context)

samples = []
for world_x, world_y in CENTERS:
    pixel_x = int(round((world_x - WORLD_MIN) / SPACING))
    pixel_y = int(round((world_y - WORLD_MIN) / SPACING))
    flipped_y = SIZE - 1 - pixel_y
    normal = unreal.RenderingLibrary.read_render_target_pixel(world, render_target, pixel_x, pixel_y)
    flipped = unreal.RenderingLibrary.read_render_target_pixel(world, render_target, pixel_x, flipped_y)
    samples.append(
        {
            "world_cm": [world_x, world_y],
            "pixel": [pixel_x, pixel_y],
            "normal": [normal.r, normal.g, normal.b, normal.a],
            "flipped_y_pixel": [pixel_x, flipped_y],
            "flipped_y": [flipped.r, flipped.g, flipped.b, flipped.a],
        }
    )
unreal.RenderingLibrary.release_render_target2d(render_target)
dirty_after = dirty_packages()
if dirty_after != dirty_before:
    raise RuntimeError("ABIVERD_MASK_RT_PROBE_DIRTY_SCOPE")

payload = {
    "schema_version": 1,
    "status": "read_only_mask_render_target_probe_complete",
    "texture_path": texture.get_path_name(),
    "render_target_size": [SIZE, SIZE],
    "samples": samples,
    "dirty_packages": dirty_after,
    "changes_made": False,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_meadow_mask_rt_probe_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_MASK_RT_PROBE_COMPLETE")
