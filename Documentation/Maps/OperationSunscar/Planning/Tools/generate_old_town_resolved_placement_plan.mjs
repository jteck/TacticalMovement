import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const root = path.basename(scriptDirectory) === "Tools" && path.basename(path.dirname(scriptDirectory)) === "Planning"
  ? path.resolve(scriptDirectory, "..", "..")
  : path.resolve(scriptDirectory, "..");
const planning = path.join(root, "Planning");
const downloads = path.join(root, "Assets", "FabDownloads");
const candidatesPath = path.join(planning, "OldTown_PropCandidatePlacements_v1.json");
const inventoryPath = path.join(planning, "OldTown_DownloadedAssetInventory_v1.json");
const jsonOut = path.join(planning, "OldTown_ResolvedPlacementPlan_v1.json");
const csvOut = path.join(planning, "OLD_TOWN_RESOLVED_PLACEMENT_PLAN_V1.csv");
const selectionOut = path.join(planning, "OLD_TOWN_ASSET_SELECTION_MATRIX_V1.csv");
const importQueueOut = path.join(planning, "OLD_TOWN_UE_IMPORT_QUEUE_V1.csv");

const source = (recordId, label) => `source://${recordId}/${label}`;
const mapOwned = (label) => `map-owned://${label}`;
const project = (assetPath) => `project://${assetPath}`;

const military = (name) => `/Game/MilitaryTrench/Assets/3D/${name}/StaticMeshes/SM_${name}`;
const junk = (folder, mesh = folder) => `/Game/Scene_Junkyard/Assets/MS/3D/${folder}/SM_${mesh}`;
const vehicle = (folder, mesh) => `/Game/CitySampleVehicles/${folder}/Mesh/${mesh}`;

const selections = {
  OT_ARCH_001: [mapOwned("MOD_WALL_01"), mapOwned("MOD_WALL_02"), mapOwned("MOD_WALL_03"), mapOwned("MOD_WALL_04")],
  OT_ARCH_002: [mapOwned("MOD_OPEN_01"), mapOwned("MOD_OPEN_02"), mapOwned("MOD_DOOR_01"), mapOwned("MOD_WIN_01"), source("FAB_P1B_001", "old_wooden_door_wbmgdcpdw_high")],
  OT_ARCH_003: [mapOwned("MOD_ROOF_01"), mapOwned("MOD_ROOF_02"), mapOwned("MOD_ROOF_03"), mapOwned("MOD_ROOF_04"), mapOwned("MOD_ROOF_05")],
  OT_ARCH_004: [mapOwned("MOD_FENCE_01"), mapOwned("MOD_FENCE_02"), mapOwned("MOD_GATE_01"), mapOwned("MOD_GATE_02")],
  OT_ARCH_005: [mapOwned("MOD_BAZ_01"), mapOwned("MOD_BAZ_02"), mapOwned("MOD_BAZ_03"), mapOwned("MOD_BAZ_04"), mapOwned("MOD_BAZ_05")],
  OT_TAC_001: [project("/Game/Maps/Sunscar/Art/Quixel/Sandbags/SM_ydxlcck_tier_2/StaticMeshes/SM_ydxlcck_tier_2")],
  OT_TAC_002: [project("/Game/Maps/Sunscar/Art/Quixel/SandbagsSquare/SM_ydznbff_tier_2/StaticMeshes/SM_ydznbff_tier_2")],
  OT_TAC_003: [
    vehicle("vehicle01_Van", "SM_vehVan_vehicle01_LOD"),
    vehicle("vehicle04_Truck", "SM_vehTruck_vehicle04_LOD"),
    vehicle("vehicle09_Van", "SM_vehVan_vehicle09_LOD"),
    vehicle("vehicle11_Truck", "SM_vehTruck_vehicle11_LOD"),
    vehicle("vehicle13_Car", "SM_vehCar_vehicle13_LOD"),
  ],
  OT_TAC_004: [
    military("Mil_Trench_Equipment_Sandbag_Canvas_Stack_01"),
    military("Mil_Trench_Equipment_Sandbag_Canvas_Stack_02"),
    military("Mil_Trench_Equipment_Sandbag_Canvas_Stack_03"),
  ],
  OT_TAC_005: [
    military("Mil_Trench_Storage_Crate_Wood_M_01"),
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Storage_Crate_Wood_M_02/StaticMeshes/SM_Mil_Trench_Storage_Crate_Wood_M_02_A",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Storage_Crate_Wood_M_02/StaticMeshes/SM_Mil_Trench_Storage_Crate_Wood_M_02_B",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Storage_Crate_Wood_S_01/StaticMeshes/SM_Mil_Trench_Storage_Crate_Wood_S_01_A",
    military("Mil_Trench_Storage_Crate_Wood_S_02"),
  ],
  OT_TAC_006: [
    junk("Ind_Jun_Tank_Metal_Rusty_01"),
    junk("Ind_Fac_Tank_Gas_Metal_Worn_01"),
    junk("Ind_Aba_Tank_Gas_Metal_Worn_02", "Ind_Aban_Tank_Gas_Metal_Worn_02"),
    junk("Ind_Jun_Scrap_Cover_Metal_Weathered_01"),
    junk("Urb_Str_Bin_Trash_Metal_Worn_01", "Urb_Str_Bin_Trash_Metal_Worn_01_A"),
  ],
  OT_TAC_007: [mapOwned("APPROVED_COVER_SKIN_01"), mapOwned("APPROVED_COVER_SKIN_02")],
  OT_UTIL_001: [source("FAB_P1A_002", "electrical_box_tdgecegda_high")],
  OT_UTIL_002: [source("FAB_P1A_003", "electric_box_ullibjd_high")],
  OT_UTIL_003: [source("FAB_P1A_004", "electrical_cabinet_ujzfde2_high")],
  OT_UTIL_004: [mapOwned("MOD_UTIL_01"), mapOwned("MOD_UTIL_02")],
  OT_UTIL_005: [mapOwned("MOD_UTIL_03")],
  OT_UTIL_006: [source("FAB_P1A_005", "round_drain_cover_sdus0qk_4k"), mapOwned("MOD_UTIL_02")],
  OT_UTIL_007: [mapOwned("MOD_ROOF_03"), mapOwned("MOD_ROOF_04"), mapOwned("MOD_ROOF_05")],
  OT_UTIL_008: [source("FAB_P0_021", "metal_water_tank_wdklears_high"), junk("Ind_Jun_Tank_Metal_Rusty_01")],
  OT_UTIL_009: [mapOwned("OT_LAMP_01"), mapOwned("OT_POLE_01"), mapOwned("OT_FIXTURE_01")],
  OT_FURN_001: [source("FAB_P1B_009", "wooden_table_veigfjmaw_high")],
  OT_FURN_002: [source("FAB_P1B_008", "old_metal_stool_ukknbeyaw_high")],
  OT_FURN_003: [source("FAB_P1B_010", "wooden_bench_vlroadt_high")],
  OT_FURN_004: [mapOwned("MOD_BAZ_03"), mapOwned("MOD_BAZ_04"), project("/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Canvas")],
  OT_FURN_005: [mapOwned("MOD_BAZ_05")],
  OT_FURN_006: [
    military("Mil_Trench_Storage_Box_Wood_S"),
    military("Mil_Trench_Storage_Box_Metal_S"),
    junk("Ind_War_Storage_Tray_Plastic_Green_01"),
    junk("Ind_War_Container_Jerrycan_Metal_Red_03"),
    junk("Ind_Con_Oil_Plastic_Pack_02", "Ind_Con_Oil_Plastic_Pack_02_A"),
  ],
  OT_SCRAP_001: [
    junk("Ind_Jun_Exhaust_Car_Metal_Rusty_05"),
    junk("Ind_Jun_Exhaust_Metal_Rusty_01"),
    junk("Ind_Jun_Exhaust_Metal_Rusty_02"),
    junk("Ind_Jun_Fan_Metal_Rusty_01"),
    junk("Ind_Jun_Spring_Metal_Rusty_01"),
    junk("Ind_Jun_Wheel_Hub_Metal_Rusty_01"),
  ],
  OT_SCRAP_002: [
    junk("Ind_Jun_Wheel_Hub_Metal_Rusty_01"),
    junk("Res_Jun_Wheel_Metal_Weathered_01"),
  ],
  OT_SCRAP_003: [
    source("FAB_P1A_018", "rusty_metal_barrel_teufceuda_high"),
    junk("Ind_Aba_Storage_Barrel_Metal_Blue_01"),
    junk("Ind_Aba_Storage_Barrel_Metal_Buckled_01"),
    junk("Ind_Aba_Storage_Barrel_Metal_Green_01"),
  ],
  OT_SCRAP_004: [
    source("FAB_P1A_019", "old_shovel_uckmaibfa_high"),
    military("Ind_Mine_Tool_Shovel_Old_01"),
    junk("Ind_Jun_Gear_Metal_Rusty_02"),
    junk("Ind_Jun_Support_Stand_Metal_Rusty_01"),
  ],
  OT_SCRAP_005: [
    junk("Ind_Jun_Storage_Pallet_Wood_Trap_01"),
    junk("Ind_Jun_Storage_Crate_Metal_Rusty_01"),
    military("Mil_Trench_Storage_Crate_Wood_M_01"),
  ],
  OT_SCRAP_006: [
    junk("Ind_Jun_Cover_Metal_Painted_05"),
    junk("Ind_Jun_Exhaust_Metal_Rusty_06"),
    junk("Ind_Jun_Spring_Metal_Rusty_01"),
    junk("Ind_Sto_PaintCan_Metal_Worn_03"),
  ],
  OT_DECAL_001: [project("/Game/Maps/Sunscar/Art/Quixel/Damage/DamagedPlaster/vdekajsfw_tier_2/StaticMeshes/vdekajsfw_tier_2")],
  OT_DECAL_002: [source("FAB_SUP_001", "military_trenches_decal_metal_rust_01_ydzmbgd_4k"), source("FAB_SUP_002", "mud_stain_wbhtagkv_4k")],
  OT_DECAL_003: [source("FAB_P1B_013", "cracked_asphalt_tjmgfelew_4k"), source("FAB_P1B_014", "asphalt_debris_pack_tlhjacuva_high")],
  OT_DECAL_004: [mapOwned("MOD_SIGN_01"), mapOwned("MOD_SIGN_02")],
  OT_DECAL_005: [mapOwned("OT_SPAWN_MARKING_01"), mapOwned("OT_SERVICE_MARKING_01")],
  OT_DECAL_006: [source("FAB_SUP_003", "oil_stain_sdjmigi_4k")],
  OT_GROUND_001: [project("/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_04_yd0lfcq/Medium/SM_yd0lfcq_tier_2/StaticMeshes/SM_yd0lfcq_tier_2")],
  OT_GROUND_002: [source("FAB_P1A_012", "military_trenches_debris_patch_rock_corner_ydyqbjds_high"), military("Mil_Trench_Debris_Patch_Rock_Corner")],
  OT_GROUND_003: [source("FAB_P1B_014", "asphalt_debris_pack_tlhjacuva_high")],
  OT_GROUND_004: [
    mapOwned("OT_DESERT_DEBRIS_CARD_01"), mapOwned("OT_DESERT_DEBRIS_CARD_02"),
    mapOwned("OT_DESERT_DEBRIS_CARD_03"), mapOwned("OT_DESERT_DEBRIS_CARD_04"),
  ],
  OT_GROUND_005: [source("FAB_P1A_014", "desert_western_rock_medium_08_uk4cdch_high")],
  OT_GROUND_006: [project("/Game/Fab/Megascans/3D/Sandstone_Rocky_Ground_vmjjfiv/Medium/vmjjfiv_tier_2/StaticMeshes/vmjjfiv_tier_2")],
  OT_GROUND_007: [
    military("Mil_Trench_Scatter_Rock_S_01"), military("Mil_Trench_Scatter_Rock_S_02"),
    military("Mil_Trench_Scatter_Rock_S_03"), military("Mil_Trench_Scatter_Rock_S_04"),
    military("Mil_Trench_Scatter_Rock_S_05"), military("Mil_Trench_Scatter_Rock_S_06"),
  ],
  OT_VEG_001: [
    source("FAB_P1A_015", "dry_grass_tbbqejqr_high"),
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/SM_Urb_Street_Grass_Dry_01_A",
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/SM_Urb_Street_Grass_Dry_01_B",
  ],
  OT_VEG_002: [
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/SM_Urb_Street_Grass_Dry_01_C",
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/SM_Urb_Street_Grass_Dry_01_D",
  ],
  OT_VEG_003: [
    "/Game/MilitaryTrench/Assets/3D/Plants/Des_West_Grass_Wild_01/StaticMeshes/SM_Des_West_Grass_Wild_01_A",
    "/Game/MilitaryTrench/Assets/3D/Plants/Des_West_Grass_Wild_01/StaticMeshes/SM_Des_West_Grass_Wild_01_B",
  ],
};

const bomPolicy = {
  OT_TAC_003: { status: "offline_candidate_ue_visual_and_bounds_validation_required", exclusion: "No Blueprints, Chaos, traffic, Mass AI, audio, VFX or sample maps" },
  OT_TAC_004: { status: "offline_candidate_collision_validation_required", exclusion: "Do not create continuous impassable sandbag walls" },
  OT_TAC_005: { status: "offline_candidate_stack_and_collision_validation_required", exclusion: "No climb chains into protected roofs" },
  OT_TAC_006: { status: "offline_candidate_visual_bounds_and_collision_validation_required", exclusion: "Maximum five large families; graybox cover remains authoritative" },
  OT_FURN_004: { status: "map_owned_fallback_selected", exclusion: "Two paid tarp listings remain excluded; canopy underside at least 2.5 m" },
  OT_VEG_002: { status: "corrected_surface_underlay_plus_pack_mesh_candidates", exclusion: "The downloaded Dried Grass listing is a surface, not an instanced plant mesh" },
};

function localPathForGameRef(ref) {
  if (!ref.startsWith("/Game/")) return null;
  const relative = ref.slice("/Game/".length) + ".uasset";
  if (ref.startsWith("/Game/MilitaryTrench/")) return path.join(downloads, "UnrealPacks", "MilitaryTrenchMegascansSa", "Content", relative);
  if (ref.startsWith("/Game/CitySampleVehicles/") || ref.startsWith("/Game/Scene_Junkyard/")) return path.join(downloads, "UnrealPacks", "OfficialAssetStaging", "Content", relative);
  return null;
}

const candidates = JSON.parse(fs.readFileSync(candidatesPath, "utf8"));
const inventory = JSON.parse(fs.readFileSync(inventoryPath, "utf8"));
const availableRecords = new Set(inventory.directAssets.map((item) => item.recordId));
const unresolved = [];
for (const [bomId, refs] of Object.entries(selections)) {
  for (const ref of refs) {
    const local = localPathForGameRef(ref);
    if (local && !fs.existsSync(local)) unresolved.push({ bomId, ref, reason: "staged_uasset_missing" });
    if (ref.startsWith("source://")) {
      const recordId = ref.split("/")[2];
      if (!availableRecords.has(recordId)) unresolved.push({ bomId, ref, reason: "downloaded_source_record_missing" });
    }
  }
}
const missingBomMappings = [...new Set(candidates.records.map((record) => record.bom_id))].filter((bomId) => !selections[bomId]);
if (missingBomMappings.length || unresolved.length) {
  throw new Error(JSON.stringify({ missingBomMappings, unresolved }, null, 2));
}

const records = candidates.records.map((record, index) => {
  const refs = selections[record.bom_id];
  const variantIndex = (index + Number(record.site_id.slice(-3)) + Number(record.candidate_id.match(/(\d+)$/)?.[1] ?? 0)) % refs.length;
  const plannedAssetRef = refs[variantIndex];
  const sourceState = plannedAssetRef.startsWith("/Game/") ? "staged_pack_asset" : plannedAssetRef.startsWith("source://") ? "downloaded_source_import_pending" : plannedAssetRef.startsWith("project://") ? "existing_project_asset" : "map_owned_definition";
  return {
    ...record,
    planned_asset_ref: plannedAssetRef,
    planned_variant_index: variantIndex,
    source_state: sourceState,
    resolution_status: "asset_candidate_resolved_transform_still_candidate",
    ue_required: "Resolve terrain/facade Z, pivot, bounds, dependencies, collision and final visual acceptance",
  };
});

const siteAssignments = {};
for (const record of records) {
  const key = `${record.site_id}|${record.bom_id}|${record.planned_asset_ref}`;
  siteAssignments[key] = (siteAssignments[key] ?? 0) + 1;
}
const matrix = Object.entries(siteAssignments).map(([key, count]) => {
  const [siteId, bomId, assetRef] = key.split("|");
  const sample = records.find((record) => record.site_id === siteId && record.bom_id === bomId && record.planned_asset_ref === assetRef);
  return {
    siteId,
    siteName: sample.site_name,
    bomId,
    role: sample.asset_role,
    assetRef,
    plannedInstances: count,
    sourceState: sample.source_state,
    validationStatus: bomPolicy[bomId]?.status ?? "offline_resolved_ue_validation_required",
    exclusion: bomPolicy[bomId]?.exclusion ?? "Preserve graybox gameplay, clearance and collision until validated",
  };
}).sort((left, right) => left.siteId.localeCompare(right.siteId) || left.bomId.localeCompare(right.bomId) || left.assetRef.localeCompare(right.assetRef));

const connectedSliceSites = new Set(["SS_007", "SS_008", "SS_004", "SS_017", "SS_010"]);
const queueByAsset = new Map();
for (const record of records) {
  if (!queueByAsset.has(record.planned_asset_ref)) {
    queueByAsset.set(record.planned_asset_ref, {
      assetRef: record.planned_asset_ref,
      sourceState: record.source_state,
      plannedInstances: 0,
      sites: new Set(),
      bomIds: new Set(),
      classes: new Set(),
      connectedSlice: false,
    });
  }
  const item = queueByAsset.get(record.planned_asset_ref);
  item.plannedInstances += 1;
  item.sites.add(record.site_id);
  item.bomIds.add(record.bom_id);
  item.classes.add(record.class);
  if (connectedSliceSites.has(record.site_id)) item.connectedSlice = true;
}
const importAction = {
  staged_pack_asset: "Migrate selected asset and dependency closure from clean UE 5.8 staging copy",
  downloaded_source_import_pending: "Import exact downloaded archive source into clean UE 5.8 staging; then migrate accepted asset",
  existing_project_asset: "Verify existing project path and reuse; do not duplicate",
  map_owned_definition: "Resolve or assemble from existing map-owned modules/primitives",
};
const importQueue = [...queueByAsset.values()].map((item) => ({
  ...item,
  priority: item.connectedSlice ? "P0_connected_slice" : "P1_remaining_sites",
  sites: [...item.sites].sort(),
  bomIds: [...item.bomIds].sort(),
  classes: [...item.classes].sort(),
  action: importAction[item.sourceState],
  requiredChecks: item.sourceState === "map_owned_definition"
    ? "Dimensions; gameplay clearance; collision authority; naming"
    : "Rendered appearance; bounds; pivot; material slots; dependencies; collision; Nanite; scale",
})).sort((left, right) => left.priority.localeCompare(right.priority) || left.sourceState.localeCompare(right.sourceState) || left.assetRef.localeCompare(right.assetRef));

const nonInstanceDependencies = [
  [source("FAB_P1B_015", "wall_paint_qj2luvs0_4k"), "Facade source for shared Old Town material instances"],
  [source("FAB_P1B_016", "stucco_wall_vigrejf_4k"), "Facade source for shared Old Town material instances"],
  [source("FAB_P1B_017", "flaked_paint_wall_vhqkeff_4k"), "Localized facade weathering source"],
  [source("FAB_P1B_011", "asphalt_fresh_sfrofg0a_4k"), "Road-base material source"],
  [source("FAB_P1B_004", "garage_door_tmnobhhya_4k"), "Garage and shutter material source"],
  [source("FAB_P1A_016", "dried_grass_xbrgaba_4k"), "Ground underlay beneath sparse dry-grass meshes"],
  [source("FAB_P1A_017", "desert_debris_pblacidh2_4k"), "Material atlas for map-owned low-profile debris cards"],
  [project("/Game/Fab/Megascans/Surfaces/Weathered_Concrete_Wall_vi4idbm/Medium/vi4idbm_tier_2/Materials/MI_vi4idbm"), "Reuse existing concrete material"],
  [project("/Game/Fab/Megascans/Surfaces/Crushed_Asphalt_Ground_sjyjcbja/Medium/sjyjcbja_tier_2/Materials/MI_sjyjcbja"), "Reuse existing worn-ground material"],
  [project("/Game/Maps/Sunscar/Art/Quixel/CorrugatedBarrier/SM_ydxnbdns_tier_2/StaticMeshes/SM_ydxnbdns_tier_2"), "Reuse existing corrugated panel"],
];
for (const [assetRef, purpose] of nonInstanceDependencies) {
  if (importQueue.some((item) => item.assetRef === assetRef)) continue;
  const sourceState = assetRef.startsWith("source://") ? "downloaded_source_import_pending" : "existing_project_asset";
  importQueue.push({
    priority: "P0_connected_slice",
    assetRef,
    sourceState,
    plannedInstances: "material_or_dependency",
    sites: ["connected_visual_slice"],
    bomIds: ["NON_INSTANCE_DEPENDENCY"],
    classes: ["material_or_support"],
    action: importAction[sourceState],
    requiredChecks: `${purpose}; physical scale; channel packing; rendered result; dependency scope`,
  });
}
importQueue.sort((left, right) => left.priority.localeCompare(right.priority) || left.sourceState.localeCompare(right.sourceState) || left.assetRef.localeCompare(right.assetRef));

const result = {
  schemaVersion: 1,
  generated: "2026-08-01",
  scope: "Old Town first complete environment-art round",
  sourceCandidateManifest: "OldTown_PropCandidatePlacements_v1.json",
  recordCount: records.length,
  warning: "Every XY/yaw/scale and asset choice is deterministic planning data, not a final Unreal placement. Z, pivots, bounds, dependencies, collision and visual approval remain Unreal gates.",
  selectionPolicy: {
    exactDownloadedSourceAssigned: true,
    fullSampleMigrationAllowed: false,
    protectedGameplayGeometryRemainsAuthoritative: true,
    thirdPartyAssetsAllowed: false,
    paidTarpAssetsIncluded: false,
  },
  correction: "FAB_P1A_016 Dried Grass is a surface archive. It is assigned as an underlay material only; actual plant instances use verified downloaded Military Trench grass mesh candidates.",
  selections,
  policies: bomPolicy,
  records,
  validation: {
    missingBomMappings,
    unresolvedLocalSources: unresolved,
    countsBySourceState: Object.fromEntries([...new Set(records.map((record) => record.source_state))].map((state) => [state, records.filter((record) => record.source_state === state).length])),
    countsBySite: Object.fromEntries([...new Set(records.map((record) => record.site_id))].sort().map((siteId) => [siteId, records.filter((record) => record.site_id === siteId).length])),
  },
};

function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

fs.writeFileSync(jsonOut, JSON.stringify(result, null, 2) + "\n");
const recordHeaders = ["candidate_id", "site_id", "site_name", "bom_id", "class", "asset_role", "planned_asset_ref", "source_state", "cluster_id", "x_m", "y_m", "z_resolution", "yaw_deg", "scale", "band", "placement_policy", "resolution_status", "collision", "nanite", "hard_rule", "ue_required"];
fs.writeFileSync(csvOut, [recordHeaders, ...records.map((record) => recordHeaders.map((header) => record[header] ?? ""))].map((row) => row.map(csvEscape).join(",")).join("\n") + "\n");
const matrixHeaders = ["site_id", "site_name", "bom_id", "role", "asset_ref", "planned_instances", "source_state", "validation_status", "exclusion"];
fs.writeFileSync(selectionOut, [matrixHeaders, ...matrix.map((row) => [row.siteId, row.siteName, row.bomId, row.role, row.assetRef, row.plannedInstances, row.sourceState, row.validationStatus, row.exclusion])].map((row) => row.map(csvEscape).join(",")).join("\n") + "\n");
const queueHeaders = ["priority", "asset_ref", "source_state", "planned_instances", "sites", "bom_ids", "classes", "action", "required_checks"];
fs.writeFileSync(importQueueOut, [queueHeaders, ...importQueue.map((item) => [item.priority, item.assetRef, item.sourceState, item.plannedInstances, item.sites.join(";"), item.bomIds.join(";"), item.classes.join(";"), item.action, item.requiredChecks])].map((row) => row.map(csvEscape).join(",")).join("\n") + "\n");

console.log(JSON.stringify({ recordCount: result.recordCount, selectionRows: matrix.length, importQueueRows: importQueue.length, ...result.validation }, null, 2));
