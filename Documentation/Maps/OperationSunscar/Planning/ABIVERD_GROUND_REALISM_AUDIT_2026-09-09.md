# Abiverd — Ground Realism Audit (read-only)

**Date:** 2026-09-09
**Scope:** the MAWI + Megascans landscape stack on `Lvl_Blockout_01`, measured
against a Bodycam-level photoreal ground target.
**Nature:** read-only. No asset, material, or setting was modified.
**Published report:** https://claude.ai/code/artifact/b15e833c-1745-4152-8046-9920cc709a94

## Method

The editor was closed and the MCP bridge on `127.0.0.1:8000` was down, so nothing
could be read through the editor. Every finding was parsed directly out of the
`.uasset` binaries using `bridge_scripts/uasset_reader.py` (written for this
audit; see its docstring for the UE 5.8 format notes).

Confidence is marked per finding: **confirmed** (explicit serialized value, or
proven by a class's presence in an import table), **inferred**, or **unknown**.

One structural limit: a node's presence in a material graph proves the asset is
referenced, not that the node is wired to the output.

## Verdict

| Question | Answer |
|---|---|
| Keep MAWI? | **Yes, for now** — 4 of 5 defects are content/config, not shader capability |
| Is Brushify necessary? | **No** — duplicates existing auto-layering, forces a full re-tune |
| Next for realism | **Scatter → roughness → RVT**, in that order |

## Confirmed configuration

- **Landscape:** 1 `Landscape` + 16 `LandscapeStreamingProxy`. Scale
  125 x 125 x 29.2969 → **quad = 125 cm**. Components 126 quads, 2 x 63 subsections.
- **Material:** `MI_Sunscar_LandscapeAuto_v1`, parent
  `/Game/MWLandscapeAutoMaterial/Materials/MASTER/MTL_MWAM_AutoMaterial_MASTER`
  (~225 expression nodes, 100 `MW_` parameters).
- **Instance overrides:** 12 scalar, 1 vector, 11 texture, 9 static switch.

### Scalar overrides (exact)

| Parameter | Value |
|---|---|
| `MW_LandscapeWorldUVSize` | 512.0 (→ 5.12 m tile, ~1.25 mm/texel on 4K) |
| `MW_LandscapeWorldUVSizeFar` | 6144.0 (→ 61.44 m tile) |
| `MW_VariationWorldUVSize` | 128.0 |
| `MW_RoughnessMultiplier` | 1.3 |
| `MW_RoughnessPower` | 1.2 |
| `MW_DirtSlopePower` | 512.0 |
| `MW_GrassSlopePower` | 4.0 |
| `MW_StonesSlopePower` | 0.70 |
| `MW_DirtNormalIntensity` | 1.0 |
| `MW_GrassNormalIntensity` | 0.75 |
| `MW_GrassSpecular` | 1.0 |
| `MW_SnowWorldPosition` | 0.0 |
| `MW_DirtColorCorrection` (vector) | (1.25, 1.25, 1.25, 1.0) |

### Static switches (exact)

All five procedural-scatter switches are **OFF**:

| Switch | Value |
|---|---|
| `MW_[x]_UseDirtAdvanced` | true |
| `MW_[x]_UseGrassAdvanced` | true |
| `MW_[x]_UseDirtProcedurals` | **false** |
| `MW_[x]_UseGrassProcedurals` | **false** |
| `MW_[x]_UseStonesProcedurals` | **false** |
| `MW_[x]_UseRockProcedurals` | **false** |
| `MW_[x]_UseSnowProcedurals` | **false** |
| `MW_UseSnow` | false |
| `MW_UseWater` | false |

`MW_[x]_UseLandscapeVariation` is **not** overridden — it inherits the master
default (true), so macro variation is on.

### Texture slots

| Slot | Asset | Notes |
|---|---|---|
| Dirt | `Dry_Trampled_Soil_wcivbfb_4K` B/N | Heritage/Surfaces/DryTrampledSoil |
| Grass | `Desert_Debris_pblacidh2_4K` B/N | FAB_P1A_017 |
| Rock | `Sandstone_Rocky_Ground_vmjjfiv_High_4K` B/N | FAB_P1A_013 |
| Stones | `T_xbohccs_4k_B` / `_N` | **`MaxTextureSize = 2048`** — 4K source discarded |
| Snow | `TEX_MWAM_SandA_col/_nrm` | MAWI default, layer disabled |
| Variation | `TEX_MWAM_Variation_msk` | `..._nrm` exists but is **unassigned** |

All source textures are 4096 x 4096 `TSF_BGRA8`. No texture in the landscape
stack has `VirtualTextureStreaming` enabled.

## The five defects

1. **Roughness is a constant.** `MF_MWAM_Roughness` contains **no texture
   sample** — its complete node inventory is FunctionInput, FunctionOutput,
   ScalarParameter, StaticSwitchParameter, Multiply, OneMinus, Power. MAWI
   exposes no roughness/AO/height texture parameter at all, so every owned
   Megascans Roughness / AO / ORM / Displacement map is unreachable.
   `MW_RoughnessMultiplier = 1.3` against a channel clamped at 1.0 pins most of
   the range fully rough, removing per-layer separation. No wet/dry variation
   (`MW_UseWater = false`).

2. **Nothing below 1.25 m exists.** No POM, displacement, tessellation, VHM,
   bump offset, PDO write, or height-based layer blending — `MF_MWAM_LayerBlend`
   is `LinearInterpolate` only. Real geometry comes solely from the heightfield:
   - `LandscapeTexturePatch` x1 — `T_HM_Sunscar_CoreRelief_v2`, 512x400,
     `TSF_G16`, `TC_SingleFloat`, no mips, **Additive**, priority 1211,
     coverage 32000 x 25000 cm → **62.5 cm/texel**, amplitude **±150 cm**.
   - `LandscapeCircleHeightPatch` **x139 — still live**, all additive, radii
     ~620–700 cm, priorities ~1027–1153 (`ABV_BundC`, `ABV_BundE`, `ABV_GullyW`).
     These were NOT removed when the authored heightmap landed; they stack.
   - Landscape quad 125 cm sets the floor. The heightmap is finer than the grid
     can carry, so roughly half its authored detail is discarded.

3. **No 3D ground scatter.** Five `LandscapeGrassType` assets are wired to the
   master's `LandscapeGrassOutput` and referenced by all 16 proxies, but all five
   switches are off. `LGT_MWAM_Stones` holds `SM_MWAM_StoneA/B/C/D`;
   `LGT_MWAM_Grass` holds `SM_MWAM_GrassA–D`; **`LGT_MWAM_Dirt` and
   `LGT_MWAM_Rock` are empty assets** (1310 bytes). PCG: `PCG_ABV_PoppyField_V1`
   exists with 13 mesh variants but **0 PCG volumes** in the level. **0**
   `InstancedFoliageActor`. Hand-placed ground props total ~130 over 8 ha:
   44 Ground_Patch_Rock_S_04, 38 Urb_Street_Grass_Dry_01, 18 vmjjfiv tier,
   11 Mil_Trench_Scatter_Rock_S_01–05, 8 Des_West_Grass_Wild_01,
   6 Desert_Western_Rock_Medium_08, 5 Dry_Grass_tbbqejqr.

4. **No RVT.** 0 `RuntimeVirtualTextureVolume` actors; no RVT object in any
   landscape proxy import table; no `MaterialExpressionRuntimeVirtualTextureOutput`
   class in the master's import table. Every road slab, canal bund, silt slab and
   rock meets terrain as a hard intersecting edge with no blending mechanism.

5. **Anti-tiling is thin and probably mis-scaled.** Base tile repeats every
   5.12 m. `MF_MWAM_LandscapeUVs` (confirmed) divides world position by
   `MW_LandscapeWorldUVSize`. If the variation path uses the same form
   (**inferred**), `MW_VariationWorldUVSize = 128` puts the breakup mask on a
   1.28 m repeat — four times tighter than the surface it is hiding. No texture
   bombing, no macro colour noise, variation normal unassigned.

## Layer blending

Four active layers driven purely by slope (`MF_MWAM_SlopeMask` ← engine
`SlopeMask` + `PixelNormalWS` + `CheapContrast`) and altitude
(`MaxWorldPosition`/`Power`), blended with straight linear interpolation. No
erosion masks, no noise in the blend.

Five `LandscapeLayerInfoObject` assets remain bound from the superseded
LandscapeV3 material. **`LayerAllocations` totals 5 across all 16 proxies** —
fifteen have zero. There is essentially no hand-painted weight data.

## Decals — 58 placed

30 Decal_Debris_Dirt_01, 6 Ind_Decal_Leak_02, 6 Decal_Debris_Pile_Rubble,
4 Decal_Leak_Dirt_01, 3 `M_ABV_MudStain_Decal`, 3 Decal_Edge_Garbage_Tiling,
3 Decal_Pile_Wood_Splinters, 2 Ind_Decal_Leak_10.
`M_ABV_OilStain_Decal` is authored and placed **0** times.

**Absent and not owned:** tyre marks / wheel ruts, cracks, dust accumulation,
erosion runoff, road-edge gravel. The plan calls for wheel ruts; no rut or track
decal exists anywhere in the owned library.

## The finding that decides the Brushify question

`M_OT_Landscape_Abiverd` — **currently unassigned**, in
`/Materials/LandscapeV3` — references in its graph:

- `Engine_MaterialFunctions01/Texturing/ParallaxOcclusionMapping`
- `Engine_MaterialFunctions02/Texturing/HeightLerp` (height-based blending)
- `Texture_Bombing` and `TextureBomb_SingleSample` (real anti-tiling)
- `LandscapeLayerWeight` nodes
- `CameraVectorWS`, `TransformToZVector`, `InverseTransformMatrix`

**Confirmed:** these are referenced in that material's dependency graph.
**Unknown:** whether they are wired through to the output. That check requires
opening the material and it decides whether we ever need to buy a new one.

## Blocked by MAWI without editing the master

Roughness/AO/height texture inputs · parallax/displacement/tessellation ·
height-based layer blending · RVT output · triplanar UVs · a third distance tier.

## Next actions, in order of visual return

1. **Turn the scatter on.** Enable `MW_[x]_UseStonesProcedurals`; then fill
   `LGT_MWAM_Dirt` and `LGT_MWAM_Rock` with owned meshes
   (`Mil_Trench_Scatter_Rock_S_01–05`, `Des_West_Grass_Wild_01`,
   `Urb_Street_Grass_Dry_01`, `Dry_Grass_tbbqejqr`, `Dried_Grass_xbrgaba`).
   Instance switch + two data assets. No master change. No new assets.
2. **One material-instance pass.** Variation scale off 128; roughness multiplier
   off 1.3 with per-layer constants separated; assign
   `MW_TextureLandscapeVariationNormal`; Dirt slope power off 512; remove the
   Stones `MaxTextureSize` cap; stagger the eight per-layer UV multipliers.
3. **Decide the RVT question** by opening `M_OT_Landscape_Abiverd`.

## Adjacent finding (outside the ground brief)

**1,940 of 3,748** external actors still reference `LevelPrototyping`, including
**538** `SM_Cube` and 143 on `MI_DefaultColorway`. The blockout is still standing
throughout the map. It does not affect the landscape shader but will dominate any
photoreal comparison shot.
