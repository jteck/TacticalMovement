"""Generate a fast, reversible 2017px Abiverd relief heightmap.

The pass retains the existing regional heightmap, adds broad low-frequency
relief around Old Town, and protects verified first-floor foundation
footprints.  It runs outside Unreal and writes a base backup, V1 heightmap,
preview and machine-readable report.
"""

import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw


SIZE = 2017
CENTER = 1008
METERS_PER_PIXEL = 1.25
ENCODED_MIN_M = 300.0
ENCODED_RANGE_M = 150.0


def smoothstep(edge0, edge1, value):
    t = np.clip((value - edge0) / max(edge1 - edge0, 1.0e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def coarse_noise(size, seed, cells):
    rng = np.random.default_rng(seed)
    grid = rng.normal(0.0, 1.0, (cells, cells)).astype(np.float32)
    image = Image.fromarray(grid, mode="F").resize((size, size), Image.Resampling.BICUBIC)
    values = np.asarray(image, dtype=np.float32).copy()
    values -= float(values.mean())
    deviation = float(values.std())
    return values / deviation if deviation > 1.0e-6 else values


def rotated_gaussian(x, y, center_x, center_y, sigma_x, sigma_y, angle_degrees):
    angle = math.radians(angle_degrees)
    cosine = math.cos(angle)
    sine = math.sin(angle)
    dx = x - center_x
    dy = y - center_y
    rx = dx * cosine + dy * sine
    ry = -dx * sine + dy * cosine
    return np.exp(-0.5 * ((rx / sigma_x) ** 2 + (ry / sigma_y) ** 2))


def hillshade(height_m):
    gy, gx = np.gradient(height_m.astype(np.float32))
    slope_x = -gx * 6.0
    slope_y = gy * 6.0
    light = 0.55 + slope_x * 0.17 + slope_y * 0.12
    light /= np.sqrt(1.0 + slope_x * slope_x + slope_y * slope_y)
    normalized = np.clip((light - np.percentile(light, 1)) / max(np.percentile(light, 99) - np.percentile(light, 1), 1.0e-6), 0.0, 1.0)
    return (normalized * 255.0).astype(np.uint8)


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--preflight", required=True)
parser.add_argument("--output-root", required=True)
args = parser.parse_args()

source_image = Image.open(args.source)
source = np.asarray(source_image, dtype=np.uint16)
if source.shape != (SIZE, SIZE):
    raise RuntimeError("ABIVERD_RELIEF_SOURCE_RESOLUTION %s" % (source.shape,))
with open(args.preflight, "r", encoding="utf-8") as handle:
    preflight = json.load(handle)
if preflight.get("status") != "terrain_relief_preflight_complete":
    raise RuntimeError("ABIVERD_RELIEF_PREFLIGHT_STATUS")

pixels = np.arange(SIZE, dtype=np.float32)
world_x = (pixels - CENTER) * METERS_PER_PIXEL
# Unreal's Landscape import addresses image rows in positive world-Y order for
# this map.  Keeping the row sign aligned prevents north/south foundation masks
# from being applied to mirrored locations.
world_y = (pixels - CENTER) * METERS_PER_PIXEL
x, y = np.meshgrid(world_x, world_y)

# Fade the pass out before it reaches the authored outer districts.
elliptical_radius = np.sqrt((x / 680.0) ** 2 + (y / 590.0) ** 2)
regional_mask = 1.0 - smoothstep(0.72, 1.0, elliptical_radius)

relief = np.zeros((SIZE, SIZE), dtype=np.float32)
relief += coarse_noise(SIZE, 1701, 13) * 0.42
relief += coarse_noise(SIZE, 1702, 25) * 0.20
relief += coarse_noise(SIZE, 1703, 49) * 0.08

# Broad alluvial tilt and irregular ancient-settlement/erosion forms.
relief += np.clip(y / 600.0, -1.0, 1.0) * 0.55
relief += rotated_gaussian(x, y, -280.0, 215.0, 165.0, 100.0, -18.0) * 3.6
relief += rotated_gaussian(x, y, 285.0, 205.0, 120.0, 165.0, 22.0) * 2.8
relief += rotated_gaussian(x, y, 310.0, -235.0, 155.0, 105.0, -12.0) * 2.1
relief += rotated_gaussian(x, y, -360.0, -155.0, 145.0, 100.0, 16.0) * 1.9

# Two shallow dry drainage lines provide readable, natural low routes.
east_wash_distance = np.abs(x - (185.0 + y * 0.20))
east_wash_length = 1.0 - smoothstep(310.0, 500.0, np.abs(y + 5.0))
relief -= np.exp(-0.5 * (east_wash_distance / 24.0) ** 2) * east_wash_length * 1.55
south_wash_distance = np.abs(y - (-175.0 + x * 0.10))
south_wash_length = 1.0 - smoothstep(300.0, 520.0, np.abs(x - 10.0))
relief -= np.exp(-0.5 * (south_wash_distance / 30.0) ** 2) * south_wash_length * 0.95

relief *= regional_mask
relief = np.clip(relief, -1.9, 4.2)

# Preserve verified building slabs exactly, feathering relief back in over 12m.
foundation_factor = np.ones((SIZE, SIZE), dtype=np.float32)
foundation_records = preflight["old_town"]["floor_records"]
for record in foundation_records:
    origin_x = float(record["origin_cm"][0]) / 100.0
    origin_y = float(record["origin_cm"][1]) / 100.0
    extent_x = float(record["extent_cm"][0]) / 100.0 + 4.0
    extent_y = float(record["extent_cm"][1]) / 100.0 + 4.0
    outside_x = np.maximum(np.abs(x - origin_x) - extent_x, 0.0)
    outside_y = np.maximum(np.abs(y - origin_y) - extent_y, 0.0)
    outside_distance = np.sqrt(outside_x * outside_x + outside_y * outside_y)
    inside = (np.abs(x - origin_x) <= extent_x) & (np.abs(y - origin_y) <= extent_y)
    local_factor = smoothstep(0.0, 12.0, outside_distance)
    local_factor[inside] = 0.0
    foundation_factor = np.minimum(foundation_factor, local_factor.astype(np.float32))

relief *= foundation_factor
source_m = ENCODED_MIN_M + source.astype(np.float64) / 65535.0 * ENCODED_RANGE_M
target_m = source_m + relief.astype(np.float64)

# Match the physical Landscape to every verified first-floor slab.  The older
# graybox relied on elevated visual overlay tiles, so preserving its source
# height alone could leave a building buried or floating.  Hold each footprint
# at the slab bottom and feather back to the surrounding relief over 12m.
for record in foundation_records:
    origin_x = float(record["origin_cm"][0]) / 100.0
    origin_y = float(record["origin_cm"][1]) / 100.0
    extent_x = float(record["extent_cm"][0]) / 100.0 + 4.0
    extent_y = float(record["extent_cm"][1]) / 100.0 + 4.0
    desired_height_m = float(record["bottom_z_cm"]) / 100.0
    outside_x = np.maximum(np.abs(x - origin_x) - extent_x, 0.0)
    outside_y = np.maximum(np.abs(y - origin_y) - extent_y, 0.0)
    outside_distance = np.sqrt(outside_x * outside_x + outside_y * outside_y)
    inside = (np.abs(x - origin_x) <= extent_x) & (np.abs(y - origin_y) <= extent_y)
    foundation_weight = 1.0 - smoothstep(0.0, 12.0, outside_distance)
    foundation_weight[inside] = 1.0
    target_m = target_m * (1.0 - foundation_weight) + desired_height_m * foundation_weight

target_encoded = np.clip(
    np.rint((target_m - ENCODED_MIN_M) / ENCODED_RANGE_M * 65535.0), 0, 65535
).astype(np.uint16)

os.makedirs(args.output_root, exist_ok=True)
base_path = os.path.join(args.output_root, "Sunscar_Height_2017_BaseBackup.png")
height_path = os.path.join(args.output_root, "Abiverd_TerrainReliefV1_2017.png")
preview_path = os.path.join(args.output_root, "Abiverd_TerrainReliefV1_Preview.png")
report_path = os.path.join(args.output_root, "Abiverd_TerrainReliefV1_Report.json")
Image.fromarray(source, mode="I;16").save(base_path)
Image.fromarray(target_encoded, mode="I;16").save(height_path)

shade = hillshade(target_m)
preview = Image.fromarray(np.dstack((shade, shade, shade)), mode="RGB").resize((1008, 1008), Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(preview)
draw.rectangle((0, 0, 1007, 52), fill=(18, 18, 18))
draw.text((18, 17), "Abiverd Terrain Relief V1 — building foundations preserved", fill=(245, 245, 245))
preview.save(preview_path)

foundation_delta_max = 0.0
for record in foundation_records:
    ox = float(record["origin_cm"][0]) / 100.0
    oy = float(record["origin_cm"][1]) / 100.0
    ex = float(record["extent_cm"][0]) / 100.0
    ey = float(record["extent_cm"][1]) / 100.0
    mask = (np.abs(x - ox) <= ex) & (np.abs(y - oy) <= ey)
    if np.any(mask):
        foundation_delta_max = max(foundation_delta_max, float(np.max(np.abs(relief[mask]))))

report = {
    "schema_version": 1,
    "status": "terrain_relief_heightmap_generated",
    "source": os.path.abspath(args.source),
    "resolution": [SIZE, SIZE],
    "meters_per_pixel": METERS_PER_PIXEL,
    "relief_delta_m": {
        "minimum": round(float(relief.min()), 4),
        "maximum": round(float(relief.max()), 4),
        "mean": round(float(relief.mean()), 4),
        "standard_deviation": round(float(relief.std()), 4),
    },
    "foundation_count": len(foundation_records),
    "maximum_abs_foundation_delta_m": round(foundation_delta_max, 6),
    "outputs": {"base_backup": base_path, "heightmap": height_path, "preview": preview_path},
    "rollback": "Reimport Sunscar_Height_2017_BaseBackup.png into Landscape edit layer index 0.",
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
print(json.dumps(report, indent=2))
