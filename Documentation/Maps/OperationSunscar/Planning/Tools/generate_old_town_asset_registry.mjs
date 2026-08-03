import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const planning = path.join(root, "Planning");
const bomPath = path.join(planning, "OLD_TOWN_PROP_MASTER_BOM.csv");
const outputPath = path.join(planning, "OldTown_AssetPathRegistry_v1.json");

function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (char === '"') quoted = !quoted;
    else if (char === "," && !quoted) { row.push(field); field = ""; }
    else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && text[i + 1] === "\n") i += 1;
      row.push(field);
      if (row.some((value) => value !== "")) rows.push(row);
      row = []; field = "";
    } else field += char;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const [headers, ...data] = rows;
  return data.map((values) => Object.fromEntries(headers.map((key, index) => [key, values[index] ?? ""])));
}

const known = {
  OT_TAC_001: {
    status: "resolved_existing_project_asset",
    assetPaths: ["/Game/Maps/Sunscar/Art/Quixel/Sandbags/SM_ydxlcck_tier_2/StaticMeshes/SM_ydxlcck_tier_2"],
    verifiedFrom: "existing project files and place_quixel_sandbags_v1.py",
  },
  OT_TAC_002: {
    status: "resolved_existing_project_asset",
    assetPaths: ["/Game/Maps/Sunscar/Art/Quixel/SandbagsSquare/SM_ydznbff_tier_2/StaticMeshes/SM_ydznbff_tier_2"],
    verifiedFrom: "existing project files and place_quixel_defensive_v1.py",
  },
  OT_DECAL_001: {
    status: "resolved_existing_project_asset",
    assetPaths: ["/Game/Maps/Sunscar/Art/Quixel/Damage/DamagedPlaster/vdekajsfw_tier_2/StaticMeshes/vdekajsfw_tier_2"],
    verifiedFrom: "existing project files",
  },
  OT_GROUND_001: {
    status: "resolved_existing_project_asset",
    assetPaths: ["/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_04_yd0lfcq/Medium/SM_yd0lfcq_tier_2/StaticMeshes/SM_yd0lfcq_tier_2"],
    verifiedFrom: "existing project files and place_quixel_ground_v1.py",
  },
  OT_GROUND_006: {
    status: "resolved_existing_project_asset",
    assetPaths: ["/Game/Fab/Megascans/3D/Sandstone_Rocky_Ground_vmjjfiv/Medium/vmjjfiv_tier_2/StaticMeshes/vmjjfiv_tier_2"],
    verifiedFrom: "existing project files and place_quixel_ground_v1.py",
  },
};

const mapOwnedPrefixes = ["MOD_", "Map-owned", "map-owned"];
const rows = parseCsv(fs.readFileSync(bomPath, "utf8")).filter((row) => row.bom_id !== "TOTAL");
const entries = rows.map((row) => {
  if (known[row.bom_id]) return { bomId: row.bom_id, role: row.asset_role, source: row.source_record_or_pack, ...known[row.bom_id] };
  const isMapOwned = mapOwnedPrefixes.some((prefix) => row.source_record_or_pack.includes(prefix)) || row.publisher === "Map-owned";
  return {
    bomId: row.bom_id,
    role: row.asset_role,
    source: row.source_record_or_pack,
    status: isMapOwned ? "map_owned_definition_ready_asset_path_pending" : "acquisition_or_staging_required",
    assetPaths: [],
    verifiedFrom: isMapOwned ? "OLD_TOWN_MAP_OWNED_MODULAR_KIT.csv or existing primitive fallback" : "Exact Fab listing or approved official pack",
  };
});

const registry = {
  schemaVersion: 1,
  generated: "2026-08-01",
  project: "TacticalMovement map-development worktree",
  level: "/Game/Maps/Blockout/Lvl_Blockout_01",
  policy: {
    publisherAllowList: ["Epic Games", "Quixel Megascans", "Map-owned"],
    preserveGrayboxCollisionUntilVerified: true,
    unresolvedAssetPathStopsPlacement: true,
    fallbackPrimitive: "/Game/LevelPrototyping/Meshes/SM_Cube",
  },
  supportAssetsAlreadyPresent: [
    "/Game/Fab/Megascans/Surfaces/Crushed_Asphalt_Ground_sjyjcbja/Medium/sjyjcbja_tier_2/Materials/MI_sjyjcbja",
    "/Game/Fab/Megascans/Surfaces/Weathered_Concrete_Wall_vi4idbm/Medium/vi4idbm_tier_2/Materials/MI_vi4idbm",
    "/Game/Maps/Sunscar/Art/Quixel/CorrugatedBarrier/SM_ydxnbdns_tier_2/StaticMeshes/SM_ydxnbdns_tier_2",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_WarmStucco",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_PaleStucco",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal",
    "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Canvas"
  ],
  entries,
  summary: Object.fromEntries(
    [...new Set(entries.map((entry) => entry.status))].map((status) => [status, entries.filter((entry) => entry.status === status).length]),
  ),
};

fs.writeFileSync(outputPath, JSON.stringify(registry, null, 2) + "\n");
console.log(JSON.stringify(registry.summary, null, 2));
