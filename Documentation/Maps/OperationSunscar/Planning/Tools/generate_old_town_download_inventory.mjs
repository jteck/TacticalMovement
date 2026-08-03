import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const root = path.basename(scriptDirectory) === "Tools" && path.basename(path.dirname(scriptDirectory)) === "Planning"
  ? path.resolve(scriptDirectory, "..", "..")
  : path.resolve(scriptDirectory, "..");
const planning = path.join(root, "Planning");
const downloads = path.join(root, "Assets", "FabDownloads");
const libraryCsv = path.join(planning, "OLD_TOWN_FAB_LIBRARY_STATUS_2026-08-01.csv");
const jsonOut = path.join(planning, "OldTown_DownloadedAssetInventory_v1.json");
const csvOut = path.join(planning, "OLD_TOWN_DOWNLOADED_ASSET_INVENTORY_V1.csv");

function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (char === '"') {
      if (quoted && text[index + 1] === '"') { field += '"'; index += 1; }
      else quoted = !quoted;
    } else if (char === "," && !quoted) { row.push(field); field = ""; }
    else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && text[index + 1] === "\n") index += 1;
      row.push(field);
      if (row.some((value) => value !== "")) rows.push(row);
      row = []; field = "";
    } else field += char;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const [headers, ...values] = rows;
  return values.map((fields) => Object.fromEntries(headers.map((header, index) => [header, fields[index] ?? ""])));
}

function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function normalized(value) {
  return value.toLowerCase().replaceAll(/[^a-z0-9]+/g, "");
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function directoryStats(directory) {
  let bytes = 0, files = 0, uassets = 0, staticMeshes = 0;
  const visit = (current) => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) visit(full);
      else {
        const size = fs.statSync(full).size;
        bytes += size; files += 1;
        if (entry.name.endsWith(".uasset")) uassets += 1;
        if (entry.name.startsWith("SM_") && entry.name.endsWith(".uasset")) staticMeshes += 1;
      }
    }
  };
  visit(directory);
  return { bytes, files, uassets, staticMeshes };
}

const libraryRows = parseCsv(fs.readFileSync(libraryCsv, "utf8"));
const acquiredRows = libraryRows.filter((row) => row.verified_library_status === "added_to_library");
const directRows = acquiredRows.filter((row) => !["FAB_P0_001", "FAB_P0_002", "FAB_P1A_001"].includes(row.record_id));
const rowByName = new Map(directRows.map((row) => [normalized(row.listing_name), row]));

const zipDirectories = ["Quixel_High_FBX", "Quixel_4K_Textures"];
const directAssets = [];
for (const directoryName of zipDirectories) {
  const directory = path.join(downloads, directoryName);
  for (const filename of fs.readdirSync(directory).filter((name) => name.endsWith(".zip")).sort()) {
    const archivePath = path.join(directory, filename);
    const entries = execFileSync("unzip", ["-Z1", archivePath], { encoding: "utf8" }).trim().split("\n").filter(Boolean);
    const jsonEntry = entries.find((entry) => entry.endsWith(".json"));
    if (!jsonEntry) throw new Error(`Missing Megascans metadata JSON in ${filename}`);
    const metadata = JSON.parse(execFileSync("unzip", ["-p", archivePath, jsonEntry], { encoding: "utf8", maxBuffer: 16 * 1024 * 1024 }));
    const sourceStem = filename.replace(new RegExp(`_${metadata.id}_(high|4k)\\.zip$`, "i"), "");
    const source = rowByName.get(normalized(sourceStem));
    if (!source) throw new Error(`No acquisition record matched ${filename} (${sourceStem})`);
    const meta = Object.fromEntries((metadata.meta ?? []).map((item) => [item.key, item.value]));
    const tier1 = (metadata.models ?? []).find((model) => model.tier === 1 && model.mimeType === "application/x-fbx");
    const extensionCounts = {};
    for (const entry of entries) {
      const extension = path.extname(entry).slice(1).toLowerCase() || "none";
      extensionCounts[extension] = (extensionCounts[extension] ?? 0) + 1;
    }
    directAssets.push({
      recordId: source.record_id,
      listingName: source.listing_name,
      listingId: source.listing_id,
      publisher: source.publisher,
      packageKind: entries.some((entry) => entry.endsWith(".fbx")) ? "megascans_3d_high_fbx" : "megascans_surface_or_decal_4k",
      localArchive: path.relative(root, archivePath),
      archiveBytes: fs.statSync(archivePath).size,
      sha256: sha256(archivePath),
      megascansId: metadata.id,
      metadataName: metadata.name,
      dimensionsMeters: {
        length: meta.length ?? null,
        width: meta.width ?? null,
        height: meta.height ?? null,
        semanticMin: metadata.semanticTags?.minSize ?? null,
        semanticMax: metadata.semanticTags?.maxSize ?? null,
      },
      highFbxTriangles: tier1?.tris ?? null,
      includedFileCount: entries.length,
      extensionCounts,
      highestAvailableResolution: metadata.highest_available_res ?? null,
      ueFnCompatible: metadata.is_uefn_compatible ?? null,
      status: "downloaded_archive_metadata_verified",
      remainingGate: "Import into UE 5.8 staging; verify bounds, pivot, material result, Nanite and collision before production placement",
    });
  }
}
directAssets.sort((left, right) => Number(left.recordId.match(/\d+/)?.[0] ?? 999) - Number(right.recordId.match(/\d+/)?.[0] ?? 999) || left.recordId.localeCompare(right.recordId));

const packDefinitions = [
  {
    recordId: "FAB_P0_001",
    listingName: "Military Trench Megascans Sample",
    publisher: "Quixel Megascans",
    enginePackage: "launcher_project",
    selectedVersion: "Launcher-installed version; exact engine build requires Unreal inspection",
    directory: path.join(downloads, "UnrealPacks", "MilitaryTrenchMegascansSa"),
    contentRoot: "/Game/MilitaryTrench",
    purpose: "Selected sandbags, crates, corrugated pieces, rubble and sparse dry vegetation only",
  },
  {
    recordId: "FAB_P0_002",
    listingName: "City Sample Vehicles",
    publisher: "Epic Games",
    enginePackage: "launcher_content_pack",
    selectedVersion: "5.3 selection; Launcher manifest build labeled 5.4.0",
    directory: path.join(downloads, "UnrealPacks", "OfficialAssetStaging", "Content", "CitySampleVehicles"),
    contentRoot: "/Game/CitySampleVehicles",
    purpose: "Five static render-mesh candidates only; exclude traffic, Chaos, Mass AI, maps, audio and gameplay Blueprints",
  },
  {
    recordId: "FAB_P1A_001",
    listingName: "Junkyard",
    publisher: "Quixel Megascans",
    enginePackage: "launcher_content_pack",
    selectedVersion: "5.6",
    directory: path.join(downloads, "UnrealPacks", "OfficialAssetStaging", "Content", "Scene_Junkyard"),
    contentRoot: "/Game/Scene_Junkyard",
    purpose: "Maximum twenty selected salvage assets; exclude demo map, sequences, lighting and VisualFrameWork",
  },
];

const packs = packDefinitions.map((pack) => ({ ...pack, localDirectory: path.relative(root, pack.directory), ...directoryStats(pack.directory), status: "downloaded_local_staging_verified", remainingGate: "Open with UE 5.8 staging workflow and measure selected assets before dependency-safe migration" }));

const deferred = libraryRows.filter((row) => row.verified_library_status !== "added_to_library").map((row) => ({
  recordId: row.record_id,
  listingName: row.listing_name,
  publisher: row.publisher,
  status: row.verified_library_status,
  note: row.observed_note,
  replacement: "Use map-owned canopy plane with existing MI_OT_Canvas unless a verified-free official alternative is later selected",
}));

const inventory = {
  schemaVersion: 1,
  generated: "2026-08-01",
  scope: "Old Town approved Epic Games and Quixel acquisition set",
  facts: {
    approvedFreeListings: 38,
    downloadedDirectArchives: directAssets.length,
    downloadedOfficialPacks: packs.length,
    deferredPaidListings: deferred.length,
    directArchiveBytes: directAssets.reduce((sum, item) => sum + item.archiveBytes, 0),
    packLocalBytes: packs.reduce((sum, item) => sum + item.bytes, 0),
  },
  classificationPolicy: {
    verifiedFact: "Derived from local files, archive metadata, Launcher manifests/logs or explicit publisher records",
    offlineCandidate: "Selected from exact package paths and semantic naming; not yet visually approved",
    unrealRequired: "Bounds, pivot, rendered appearance, collision, dependency and Nanite state require UE 5.8 inspection",
  },
  directAssets,
  packs,
  deferred,
};

fs.writeFileSync(jsonOut, JSON.stringify(inventory, null, 2) + "\n");
const headers = ["record_id", "listing_name", "publisher", "package_kind", "status", "local_source", "bytes", "dimensions_m", "tier1_tris", "files", "remaining_gate"];
const csvRows = [headers];
for (const item of directAssets) {
  const dims = [item.dimensionsMeters.length, item.dimensionsMeters.width, item.dimensionsMeters.height].filter(Boolean).join(" x ");
  csvRows.push([item.recordId, item.listingName, item.publisher, item.packageKind, item.status, item.localArchive, item.archiveBytes, dims, item.highFbxTriangles ?? "", item.includedFileCount, item.remainingGate]);
}
for (const item of packs) csvRows.push([item.recordId, item.listingName, item.publisher, item.enginePackage, item.status, item.localDirectory, item.bytes, "UE inspection required", "", item.files, item.remainingGate]);
for (const item of deferred) csvRows.push([item.recordId, item.listingName, item.publisher, "not_downloaded", item.status, "", 0, "", "", 0, item.replacement]);
fs.writeFileSync(csvOut, csvRows.map((row) => row.map(csvEscape).join(",")).join("\n") + "\n");

console.log(JSON.stringify(inventory.facts, null, 2));
