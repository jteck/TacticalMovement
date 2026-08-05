"""Pack the authored 16-bit relief heightmap into UE Landscape RG channels."""

import json
import os

import numpy as np
from PIL import Image


ROOT = "/Users/jasonteck/UnrealEngine/_worktrees/map-development"
SOURCE = os.path.join(
    ROOT,
    "Documentation/Maps/OperationSunscar/Source/Heightmaps/Abiverd_TerrainReliefV1_2017.png",
)
OUTPUT = os.path.join(
    ROOT,
    "Documentation/Maps/OperationSunscar/Source/Heightmaps/Abiverd_TerrainReliefV1_RG16_2017.png",
)
REPORT = os.path.join(
    ROOT,
    "Documentation/Maps/OperationSunscar/Source/Heightmaps/Abiverd_TerrainReliefV1_RG16_Report.json",
)


height = np.asarray(Image.open(SOURCE), dtype=np.uint16).copy()
if height.shape != (2017, 2017):
    raise RuntimeError("ABIVERD_RG16_SOURCE_SIZE %s" % (height.shape,))

packed = np.zeros((2017, 2017, 4), dtype=np.uint8)
packed[:, :, 0] = (height >> 8).astype(np.uint8)
packed[:, :, 1] = (height & 255).astype(np.uint8)
packed[:, :, 3] = 255
Image.fromarray(packed, mode="RGBA").save(OUTPUT, optimize=False, compress_level=6)

decoded = (packed[:, :, 0].astype(np.uint16) << 8) | packed[:, :, 1].astype(np.uint16)
exact = bool(np.array_equal(decoded, height))
payload = {
    "schema_version": 1,
    "status": "rg16_heightmap_generated",
    "source": SOURCE,
    "output": OUTPUT,
    "resolution": [2017, 2017],
    "source_min": int(height.min()),
    "source_max": int(height.max()),
    "round_trip_exact": exact,
    "output_size_bytes": os.path.getsize(OUTPUT),
    "encoding": "R=high byte, G=low byte, B=0, A=255",
}
with open(REPORT, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
if not exact:
    raise RuntimeError("ABIVERD_RG16_ROUND_TRIP_FAILED")
print("ABIVERD_RG16_GENERATED", OUTPUT)
