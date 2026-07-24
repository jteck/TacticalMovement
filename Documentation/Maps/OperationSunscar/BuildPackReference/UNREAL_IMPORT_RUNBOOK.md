# Operation Sunscar — Unreal Engine 5.8 Import Runbook

This runbook creates the first playable-scale graybox without touching an
existing game map.

## 1. Open the project

Open `TacticalMovement-Code-UI1/TacticalMovement.uproject`. The project now
enables Python Editor Script and Editor Scripting Utilities. Unreal may ask for
one editor restart the first time it loads those plugins.

## 2. Create the protected Sunscar map

1. Choose **File → New Level → Open World**.
2. Immediately save it as:
   `/Game/Maps/Graybox/L_GB_Sunscar`
3. Do not run the automation in another level. The script checks this exact
   path and stops if a different map is open.

The Open World template supplies World Partition. Keep it enabled.

## 3. Import the Landscape

Open Landscape Mode and choose **Import from File**.

- Heightmap:
  `BuildPack_v1/Heightmaps/Sunscar_Height_2017.png`
- Resolution: `2017 × 2017`
- Section Size: `63 × 63 quads`
- Sections Per Component: `2 × 2`
- Components: `16 × 16`
- Location X: `0 cm`
- Location Y: `0 cm`
- Location Z: `37,500 cm`
- Scale X: `125 cm`
- Scale Y: `125 cm`
- Scale Z: `29.296875`
- Enable Edit Layers: `On`

The resulting terrain is exactly `2,520 × 2,520 m`. Old Town is at world
origin. East is positive X and north is positive Y.

Before continuing, verify in Top view:

- The canal is on the east/right side.
- The foothills and quarry are on the south/bottom side.
- The lower desert is on the north/top side.

If those three checks are correct, the map orientation is correct.

## 4. Build the graybox automatically

Open **Window → Output Log**, switch the command input to Python, and run:

```python
import sunscar_bootstrap
sunscar_bootstrap.preview()
```

The preview should report:

- `levelIsSafe: true`
- `untaggedActorsWillBePreserved: true`
- the expected landmark and infrastructure counts

Then run:

```python
sunscar_bootstrap.build()
```

The builder places the landmarks plus road, rail, and canal guide segments,
organizes them in World Outliner folders, tags each actor with its intended
Data Layer, and saves the level.

Re-running `sunscar_bootstrap.build()` is safe: it removes only actors tagged
`SunscarGenerated`. Hand-authored actors without that tag are preserved.

## 5. First playtest gate

Do not add final art yet. First confirm:

1. Old Town traversal feels right at infantry speed.
2. Each outer district has at least two viable approaches.
3. The quarry and canal do not create accidental dead ends.
4. Eight-player modes use a selected sector, not the entire battlefield.
5. The whole terrain remains available for future vehicles, AI, or larger
   player counts.

After this gate, replace the blockout segments with editable Landscape Splines,
create real Data Layer assets, and begin PCG/material dressing district by
district.
