"""Generate deterministic Landscape masks from the verified Old Town overlay plan.

This script runs outside Unreal.  It preserves the authored road/courtyard
layout while replacing visible overlapping mesh tiles with soft-edged
Landscape paint masks.  The generated PNG files are transient build inputs;
the resulting Landscape weight data is stored in Unreal assets.
"""

import hashlib
import json
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter


PROJECT_ROOT = "/Users/jasonteck/UnrealEngine/_worktrees/map-development"
REPORT_PATH = os.path.join(
    PROJECT_ROOT,
    "Saved/OperationSunscar/Reports/abiverd_visual_conversion_preflight_v1.json",
)
OUTPUT_ROOT = os.path.join(
    PROJECT_ROOT,
    "Saved/OperationSunscar/Generated/LandscapeMasksV2",
)
REPORT_OUTPUT = os.path.join(
    PROJECT_ROOT,
    "Saved/OperationSunscar/Reports/abiverd_generate_landscape_masks_v2.json",
)
SIZE = 2017
LANDSCAPE_MIN_CM = -126000.0
LANDSCAPE_MAX_CM = 126000.0
CM_PER_PIXEL = (LANDSCAPE_MAX_CM - LANDSCAPE_MIN_CM) / float(SIZE - 1)


def world_to_pixel(x_cm, y_cm):
    return (
        (float(x_cm) - LANDSCAPE_MIN_CM) / CM_PER_PIXEL,
        (float(y_cm) - LANDSCAPE_MIN_CM) / CM_PER_PIXEL,
    )


def add_actor_rect(draw, row, value=255, padding_cm=80.0):
    x, y = row["bounds_origin_cm"][:2]
    ex, ey = row["bounds_extent_cm"][:2]
    p0 = world_to_pixel(x - ex - padding_cm, y - ey - padding_cm)
    p1 = world_to_pixel(x + ex + padding_cm, y + ey + padding_cm)
    draw.rounded_rectangle([p0, p1], radius=2.0, fill=int(value))


def blurred_mask(source, blur_radius=1.35, expand=3):
    value = source
    if expand:
        value = value.filter(ImageFilter.MaxFilter(expand * 2 + 1))
    if blur_radius:
        value = value.filter(ImageFilter.GaussianBlur(blur_radius))
    return value


with open(REPORT_PATH, "r", encoding="utf-8") as handle:
    inventory = json.load(handle)
if inventory.get("status") != "read_only_preflight_complete":
    raise RuntimeError("ABIVERD_MASKS_PREFLIGHT_STATUS")

overlays = [
    row for row in inventory["scoped_actors"]
    if "VisualGroundOverlay" in row["tags"]
]
if len(overlays) != 288:
    raise RuntimeError("ABIVERD_MASKS_OVERLAY_SCOPE expected=288 actual=%d" % len(overlays))

images = {
    "Mud": Image.new("L", (SIZE, SIZE), 0),
    "Desert": Image.new("L", (SIZE, SIZE), 0),
    "Rock": Image.new("L", (SIZE, SIZE), 0),
    "Farm": Image.new("L", (SIZE, SIZE), 0),
    "Grass": Image.new("L", (SIZE, SIZE), 0),
}
draws = {name: ImageDraw.Draw(image) for name, image in images.items()}
counts = {name: 0 for name in images}

for row in overlays:
    tags = set(row["tags"])
    folder = row["folder"]
    label = row["label"]
    if "Asphalt" in tags:
        target = "Desert"  # Semantic role: weathered asphalt.
        padding = 105.0
    elif "Silt" in tags:
        target = "Farm"  # Semantic role: roadside/drain silt.
        padding = 40.0
    elif "/Stone" in folder or label.startswith("Ground_Concrete_"):
        target = "Rock"  # Semantic role: stone/concrete hardstand.
        padding = 70.0
    else:
        target = "Mud"  # Semantic role: compacted earth and dust.
        padding = 95.0
    add_actor_rect(draws[target], row, 255, padding)
    counts[target] += 1

# Preserve a readable, walkable heritage route north of the town without
# turning the open meadow into a straight sniper lane.
heritage_route = [
    world_to_pixel(-400.0, 10400.0),
    world_to_pixel(250.0, 13200.0),
    world_to_pixel(-300.0, 15300.0),
    world_to_pixel(-900.0, 17700.0),
    world_to_pixel(-250.0, 20100.0),
    world_to_pixel(350.0, 23200.0),
]
draws["Mud"].line(heritage_route, fill=230, width=5, joint="curve")

# Mosque forecourt, well court, and ruin-footpath clearings.
for x, y, rx, ry, strength in (
    (1600.0, 16500.0, 1300.0, 1050.0, 235),
    (-2000.0, 15400.0, 850.0, 650.0, 215),
    (-4200.0, 18800.0, 850.0, 520.0, 185),
    (4300.0, 19700.0, 900.0, 540.0, 185),
):
    p0 = world_to_pixel(x - rx, y - ry)
    p1 = world_to_pixel(x + rx, y + ry)
    draws["Mud"].ellipse([p0, p1], fill=strength)

# Irregular spring meadow belts derived from the Abiverd reference photos.
meadow_belts = (
    (-4550.0, 16300.0, 2050.0, 900.0, 12.0),
    (-4550.0, 18700.0, 2350.0, 980.0, -14.0),
    (-4300.0, 21100.0, 2050.0, 900.0, 7.0),
    (4400.0, 16900.0, 2150.0, 900.0, -10.0),
    (4300.0, 19400.0, 2400.0, 1020.0, 13.0),
    (4400.0, 21600.0, 2050.0, 850.0, -5.0),
)
for index, (x, y, rx, ry, yaw) in enumerate(meadow_belts):
    local_size = (max(16, int(rx * 2.4 / CM_PER_PIXEL)), max(10, int(ry * 2.4 / CM_PER_PIXEL)))
    patch = Image.new("L", local_size, 0)
    patch_draw = ImageDraw.Draw(patch)
    cx, cy = local_size[0] / 2.0, local_size[1] / 2.0
    patch_draw.ellipse(
        [cx - rx / CM_PER_PIXEL, cy - ry / CM_PER_PIXEL,
         cx + rx / CM_PER_PIXEL, cy + ry / CM_PER_PIXEL],
        fill=245,
    )
    # Break the silhouette so the belts read as natural growth, not decals.
    for notch in range(5):
        angle = math.radians((index * 53 + notch * 67) % 360)
        nx = cx + math.cos(angle) * (rx / CM_PER_PIXEL) * 0.78
        ny = cy + math.sin(angle) * (ry / CM_PER_PIXEL) * 0.78
        nr = 2.0 + ((index + notch) % 3)
        patch_draw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=0)
    patch = patch.rotate(yaw, resample=Image.Resampling.BICUBIC, expand=True)
    px, py = world_to_pixel(x, y)
    images["Grass"].paste(
        ImageChops.lighter(
            images["Grass"].crop(
                (
                    int(px - patch.width / 2),
                    int(py - patch.height / 2),
                    int(px + patch.width / 2),
                    int(py + patch.height / 2),
                )
            ).resize(patch.size),
            patch,
        ),
        (int(px - patch.width / 2), int(py - patch.height / 2)),
    )

images["Mud"] = blurred_mask(images["Mud"], 1.5, 2)
images["Desert"] = blurred_mask(images["Desert"], 1.15, 2)
images["Rock"] = blurred_mask(images["Rock"], 1.4, 1)
images["Farm"] = blurred_mask(images["Farm"], 0.8, 1)
images["Grass"] = blurred_mask(images["Grass"], 2.0, 2)

os.makedirs(OUTPUT_ROOT, exist_ok=True)
records = []
for layer_name, image in images.items():
    path = os.path.join(OUTPUT_ROOT, "Abiverd_%s_2017.png" % layer_name)
    image.save(path, optimize=True)
    with open(path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    histogram = image.histogram()
    nonzero = sum(histogram[1:])
    records.append(
        {
            "layer_name": layer_name,
            "path": path,
            "sha256": digest,
            "dimensions": [SIZE, SIZE],
            "nonzero_pixels": nonzero,
            "coverage_percent": round(nonzero * 100.0 / (SIZE * SIZE), 6),
            "source_overlay_count": counts[layer_name],
        }
    )

payload = {
    "schema_version": 2,
    "status": "landscape_masks_generated",
    "source_report": REPORT_PATH,
    "landscape_extent_cm": [LANDSCAPE_MIN_CM, LANDSCAPE_MIN_CM, LANDSCAPE_MAX_CM, LANDSCAPE_MAX_CM],
    "cm_per_pixel": CM_PER_PIXEL,
    "overlay_actor_count": len(overlays),
    "records": records,
    "semantic_mapping": {
        "Mud": "CompactedEarth",
        "Desert": "WeatheredAsphalt",
        "Rock": "StoneAndConcreteHardstand",
        "Farm": "RoadsideSilt",
        "Grass": "AbiverdSpringMeadow",
    },
}
os.makedirs(os.path.dirname(REPORT_OUTPUT), exist_ok=True)
with open(REPORT_OUTPUT, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
print(json.dumps(payload, indent=2))
