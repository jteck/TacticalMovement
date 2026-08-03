import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const planning = path.join(root, "Planning");
const placementPath = path.join(planning, "OldTown_PropPlacementManifest_v1.json");
const bomPath = path.join(planning, "OLD_TOWN_PROP_MASTER_BOM.csv");
const jsonOutput = path.join(planning, "OldTown_PropCandidatePlacements_v1.json");
const csvOutput = path.join(planning, "OLD_TOWN_PROP_CANDIDATE_PLACEMENTS_V1.csv");
const reportOutput = path.join(planning, "OLD_TOWN_PROP_CANDIDATE_VALIDATION_V1.json");

const classKey = {
  architecture: "architecture_caps",
  tactical: "tactical_cover",
  utility: "utilities",
  furniture: "furniture_market",
  industrial: "industrial_scrap",
  decal: "decals_signs",
  ground: "rubble_ground",
  vegetation: "vegetation",
};

const placementPolicy = {
  architecture: "socket_or_manual",
  tactical: "manual_only",
  utility: "socket_or_manual",
  furniture: "manual_cluster",
  industrial: "large_manual_small_seeded",
  decal: "socket_or_projected",
  ground: "seeded_scatter",
  vegetation: "seeded_pcg",
};

const clusterSize = {
  architecture: 6,
  tactical: 3,
  utility: 3,
  furniture: 4,
  industrial: 5,
  decal: 4,
  ground: 5,
  vegetation: 6,
};

// Eligibility comes from OLD_TOWN_EXACT_SITE_ASSIGNMENTS.csv and the site
// recipes. It prevents a globally correct budget from producing locally
// nonsensical results such as hotel parapets at a spawn or market furniture
// inside the canal.
const eligibleSites = {
  OT_ARCH_001: ["SS_002","SS_003","SS_004","SS_005","SS_006","SS_007","SS_008","SS_010","SS_011","SS_012","SS_013","SS_014","SS_015","SS_016","SS_017","SS_018"],
  OT_ARCH_002: ["SS_003","SS_004","SS_005","SS_006","SS_007","SS_010","SS_011","SS_012","SS_013","SS_015","SS_016","SS_017","SS_018"],
  OT_ARCH_003: ["SS_003","SS_004","SS_005","SS_006","SS_007","SS_010","SS_011","SS_012","SS_013","SS_015","SS_016","SS_017","SS_018"],
  OT_ARCH_004: ["SS_001","SS_006","SS_009","SS_010","SS_011","SS_012","SS_014","SS_016","SS_019","SS_020"],
  OT_ARCH_005: ["SS_017"],
  OT_TAC_001: ["SS_001","SS_010","SS_011","SS_019","SS_020"],
  OT_TAC_002: ["SS_001","SS_010","SS_011","SS_019","SS_020"],
  OT_TAC_003: ["SS_014","SS_015","SS_019"],
  OT_TAC_004: ["SS_001","SS_011","SS_019","SS_020"],
  OT_TAC_005: ["SS_004","SS_008","SS_010","SS_011","SS_013","SS_014","SS_015","SS_017"],
  OT_TAC_006: ["SS_014","SS_015"],
  OT_UTIL_001: ["SS_003","SS_005","SS_007","SS_011","SS_013","SS_015","SS_016","SS_018"],
  OT_UTIL_002: ["SS_003","SS_011","SS_016","SS_018"],
  OT_UTIL_003: ["SS_003","SS_016"],
  OT_UTIL_004: ["SS_002","SS_003","SS_006","SS_013","SS_015","SS_016","SS_018"],
  OT_UTIL_005: ["SS_003","SS_004","SS_005","SS_006","SS_007","SS_010","SS_011","SS_012","SS_013","SS_014","SS_015","SS_016","SS_017","SS_018"],
  OT_UTIL_006: ["SS_002","SS_003","SS_008","SS_009","SS_016"],
  OT_UTIL_007: ["SS_003","SS_006","SS_007","SS_013","SS_015","SS_018"],
  OT_UTIL_008: ["SS_003","SS_006","SS_015","SS_016","SS_018"],
  OT_UTIL_009: ["SS_001","SS_004","SS_008","SS_009","SS_011","SS_017","SS_019","SS_020"],
  OT_FURN_001: ["SS_004","SS_005","SS_007","SS_008","SS_009","SS_010","SS_012","SS_013","SS_017","SS_018"],
  OT_FURN_002: ["SS_004","SS_017"],
  OT_FURN_003: ["SS_004","SS_005","SS_007","SS_008","SS_010","SS_012","SS_017"],
  OT_FURN_004: ["SS_004","SS_017"],
  OT_FURN_005: ["SS_004","SS_017"],
  OT_FURN_006: ["SS_004","SS_005","SS_007","SS_008","SS_009","SS_010","SS_012","SS_013","SS_017","SS_018"],
  OT_SCRAP_001: ["SS_013","SS_014","SS_015"],
  OT_SCRAP_002: ["SS_014","SS_015"],
  OT_SCRAP_003: ["SS_003","SS_011","SS_013","SS_014","SS_015","SS_016","SS_017","SS_018"],
  OT_SCRAP_004: ["SS_003","SS_011","SS_013","SS_014","SS_015","SS_016","SS_017","SS_018"],
  OT_SCRAP_005: ["SS_013","SS_014","SS_015","SS_017"],
  OT_SCRAP_006: ["SS_003","SS_011","SS_013","SS_014","SS_015","SS_016","SS_017","SS_018"],
  OT_DECAL_001: ["SS_003","SS_004","SS_005","SS_007","SS_010","SS_012","SS_018"],
  OT_DECAL_002: ["SS_002","SS_003","SS_006","SS_011","SS_013","SS_014","SS_015","SS_016","SS_017","SS_018"],
  OT_DECAL_003: ["SS_001","SS_002","SS_008","SS_009","SS_014","SS_015","SS_019","SS_020"],
  OT_DECAL_004: ["SS_001","SS_003","SS_004","SS_005","SS_007","SS_009","SS_010","SS_011","SS_012","SS_013","SS_016","SS_017","SS_018","SS_019","SS_020"],
  OT_DECAL_005: ["SS_001","SS_009","SS_015","SS_019"],
  OT_DECAL_006: ["SS_002","SS_003","SS_006","SS_013","SS_014","SS_015","SS_016","SS_018"],
  OT_GROUND_001: ["SS_002","SS_006","SS_008","SS_010","SS_020"],
  OT_GROUND_002: ["SS_002","SS_003","SS_004","SS_005","SS_007","SS_008","SS_010","SS_012","SS_018","SS_020"],
  OT_GROUND_003: ["SS_001","SS_009","SS_014","SS_015","SS_019"],
  OT_GROUND_004: ["SS_001","SS_002","SS_003","SS_006","SS_008","SS_013","SS_014","SS_015","SS_016","SS_017","SS_018","SS_019","SS_020"],
  OT_GROUND_005: ["SS_002","SS_006","SS_014","SS_020"],
  OT_GROUND_006: ["SS_002","SS_006","SS_020"],
};

const forcedSiteCounts = {
  OT_ARCH_005: { SS_017: 30 },
  OT_TAC_003: { SS_014: 3, SS_015: 2 },
  OT_UTIL_001: { SS_003: 4, SS_005: 3, SS_007: 3, SS_011: 2, SS_013: 2, SS_015: 2, SS_016: 2, SS_018: 2 },
  OT_UTIL_002: { SS_003: 2, SS_011: 2, SS_016: 4, SS_018: 4 },
  OT_UTIL_003: { SS_003: 2, SS_016: 2 },
  OT_UTIL_007: { SS_003: 2, SS_006: 2, SS_007: 4, SS_013: 3, SS_015: 3, SS_018: 6 },
  OT_UTIL_008: { SS_003: 4, SS_006: 4, SS_015: 1, SS_016: 1, SS_018: 2 },
  OT_UTIL_009: { SS_001: 2, SS_004: 2, SS_008: 1, SS_009: 4, SS_011: 3, SS_017: 4, SS_019: 2, SS_020: 2 },
  OT_FURN_001: { SS_004: 3, SS_017: 6 },
  OT_FURN_002: { SS_004: 4, SS_017: 12 },
  OT_FURN_003: { SS_004: 2, SS_008: 2, SS_012: 2, SS_017: 4 },
  OT_FURN_004: { SS_004: 2, SS_017: 8 },
  OT_FURN_005: { SS_004: 4, SS_017: 16 },
  OT_FURN_006: { SS_004: 3, SS_017: 14 },
  OT_DECAL_005: { SS_001: 4, SS_009: 4, SS_015: 6, SS_019: 4 },
  OT_DECAL_006: { SS_003: 4, SS_013: 4, SS_014: 4, SS_015: 4, SS_016: 4 },
  OT_GROUND_005: { SS_002: 8, SS_006: 8, SS_014: 6, SS_020: 8 },
  OT_GROUND_006: { SS_002: 8, SS_006: 6, SS_020: 6 },
};

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (char === '"') {
      if (quoted && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else {
        quoted = !quoted;
      }
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && text[i + 1] === "\n") i += 1;
      row.push(field);
      if (row.some((value) => value !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field !== "" || row.length) {
    row.push(field);
    rows.push(row);
  }
  const [headers, ...data] = rows;
  return data.map((values) => Object.fromEntries(headers.map((key, index) => [key, values[index] ?? ""])));
}

function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function mulberry32(seed) {
  return function random() {
    let value = (seed += 0x6d2b79f5);
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffle(values, random) {
  for (let i = values.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    [values[i], values[j]] = [values[j], values[i]];
  }
}

function allocateRolesToSites(assetClass, roles, sites) {
  // Small integral max-flow: source -> BOM role -> eligible site -> sink.
  const source = 0;
  const roleStart = 1;
  const siteStart = roleStart + roles.length;
  const sink = siteStart + sites.length;
  const graph = Array.from({ length: sink + 1 }, () => []);
  function addEdge(from, to, capacity) {
    const forward = { to, rev: graph[to].length, capacity, flow: 0 };
    const reverse = { to: from, rev: graph[from].length, capacity: 0, flow: 0 };
    graph[from].push(forward);
    graph[to].push(reverse);
  }
  const forcedBySite = Object.fromEntries(sites.map((site) => [site.id, 0]));
  const residualByRole = new Map();
  roles.forEach((role) => {
    const forced = forcedSiteCounts[role.bom_id] ?? {};
    const forcedTotal = Object.values(forced).reduce((sum, value) => sum + Number(value), 0);
    const residual = Number(role.target_instances) - forcedTotal;
    if (residual < 0) throw new Error(`Forced count exceeds BOM target for ${role.bom_id}`);
    residualByRole.set(role.bom_id, residual);
    for (const [siteId, count] of Object.entries(forced)) {
      if (!(siteId in forcedBySite)) throw new Error(`Unknown forced site ${siteId}`);
      if (!(eligibleSites[role.bom_id] ?? sites.map((site) => site.id)).includes(siteId)) {
        throw new Error(`Forced site ${siteId} is not eligible for ${role.bom_id}`);
      }
      forcedBySite[siteId] += Number(count);
    }
  });
  roles.forEach((role, roleIndex) => {
    addEdge(source, roleStart + roleIndex, residualByRole.get(role.bom_id));
    const allowed = new Set(eligibleSites[role.bom_id] ?? sites.map((site) => site.id));
    sites.forEach((site, siteIndex) => {
      if (allowed.has(site.id)) addEdge(roleStart + roleIndex, siteStart + siteIndex, 1000000);
    });
  });
  sites.forEach((site, siteIndex) => {
    const residual = Number(site.counts[classKey[assetClass]]) - forcedBySite[site.id];
    if (residual < 0) throw new Error(`Forced counts exceed ${assetClass} budget at ${site.id}`);
    addEdge(siteStart + siteIndex, sink, residual);
  });

  let totalFlow = 0;
  while (true) {
    const parent = Array(sink + 1).fill(null);
    const queue = [source];
    parent[source] = { node: -1, edge: -1 };
    for (let cursor = 0; cursor < queue.length && parent[sink] === null; cursor += 1) {
      const node = queue[cursor];
      graph[node].forEach((edge, edgeIndex) => {
        if (parent[edge.to] === null && edge.flow < edge.capacity) {
          parent[edge.to] = { node, edge: edgeIndex };
          queue.push(edge.to);
        }
      });
    }
    if (parent[sink] === null) break;
    let amount = Infinity;
    for (let node = sink; node !== source; ) {
      const step = parent[node];
      const edge = graph[step.node][step.edge];
      amount = Math.min(amount, edge.capacity - edge.flow);
      node = step.node;
    }
    for (let node = sink; node !== source; ) {
      const step = parent[node];
      const edge = graph[step.node][step.edge];
      edge.flow += amount;
      graph[node][edge.rev].flow -= amount;
      node = step.node;
    }
    totalFlow += amount;
  }

  const expected = roles.reduce((sum, role) => sum + residualByRole.get(role.bom_id), 0);
  if (totalFlow !== expected) {
    const roleResidual = roles.map((role, index) => ({
      id: role.bom_id,
      remaining: graph[source][index].capacity - graph[source][index].flow,
    })).filter((entry) => entry.remaining > 0);
    const siteResidual = sites.map((site, index) => {
      const edge = graph[siteStart + index].find((candidate) => candidate.to === sink);
      return { id: site.id, remaining: edge.capacity - edge.flow };
    }).filter((entry) => entry.remaining > 0);
    throw new Error(`Eligibility cannot satisfy ${assetClass}: ${totalFlow}/${expected}; roles=${JSON.stringify(roleResidual)} sites=${JSON.stringify(siteResidual)}`);
  }
  const result = Object.fromEntries(sites.map((site) => [site.id, []]));
  for (const role of roles) {
    for (const [siteId, count] of Object.entries(forcedSiteCounts[role.bom_id] ?? {})) {
      for (let i = 0; i < count; i += 1) result[siteId].push(role);
    }
  }
  roles.forEach((role, roleIndex) => {
    graph[roleStart + roleIndex].forEach((edge) => {
      if (edge.to < siteStart || edge.to >= sink || edge.flow <= 0) return;
      const site = sites[edge.to - siteStart];
      for (let i = 0; i < edge.flow; i += 1) result[site.id].push(role);
    });
  });
  for (const site of sites) shuffle(result[site.id], mulberry32(site.seed + assetClass.length * 131));
  return result;
}

function edgePoint(site, random, insetMin = 0.55, insetMax = 1.8) {
  const [width, depth] = site.size;
  const [cx, cy] = site.center;
  const halfW = width / 2;
  const halfD = depth / 2;
  const edge = Math.floor(random() * 4);
  const inset = insetMin + random() * Math.min(insetMax - insetMin, Math.max(0.1, Math.min(halfW, halfD) - insetMin));
  const alongX = cx - halfW + 0.8 + random() * Math.max(0.1, width - 1.6);
  const alongY = cy - halfD + 0.8 + random() * Math.max(0.1, depth - 1.6);
  if (edge === 0) return { x: alongX, y: cy + halfD - inset, yaw: 180, band: "north_edge" };
  if (edge === 1) return { x: cx + halfW - inset, y: alongY, yaw: 270, band: "east_edge" };
  if (edge === 2) return { x: alongX, y: cy - halfD + inset, yaw: 0, band: "south_edge" };
  return { x: cx - halfW + inset, y: alongY, yaw: 90, band: "west_edge" };
}

function interiorPoint(site, random, centerClearFraction = 0.18) {
  const [width, depth] = site.size;
  const [cx, cy] = site.center;
  for (let attempt = 0; attempt < 40; attempt += 1) {
    const nx = -0.44 + random() * 0.88;
    const ny = -0.44 + random() * 0.88;
    if (Math.hypot(nx, ny) < centerClearFraction) continue;
    return { x: cx + nx * width, y: cy + ny * depth, yaw: random() * 360, band: "interior_authored" };
  }
  return edgePoint(site, random);
}

function candidatePoint(site, assetClass, random) {
  const edgeClasses = new Set(["architecture", "utility", "decal", "ground", "vegetation"]);

  // The canal is deliberately kept open down its long centerline.
  if (site.id === "SS_002") {
    const side = random() < 0.5 ? -1 : 1;
    return {
      x: site.center[0] + side * (site.size[0] * 0.5 - 0.65 - random() * 0.45),
      y: site.center[1] - site.size[1] * 0.43 + random() * site.size[1] * 0.86,
      yaw: side < 0 ? 90 : 270,
      band: side < 0 ? "canal_west_bank" : "canal_east_bank",
    };
  }

  // Bazaar placement stays in two stall bands with a clear central passage.
  if (site.id === "SS_017") {
    const side = random() < 0.5 ? -1 : 1;
    return {
      x: site.center[0] - site.size[0] * 0.44 + random() * site.size[0] * 0.88,
      y: site.center[1] + side * (site.size[1] * 0.5 - 1.0 - random() * 1.4),
      yaw: side < 0 ? 0 : 180,
      band: side < 0 ? "bazaar_south_stalls" : "bazaar_north_stalls",
    };
  }

  // Courtyard, transit plaza, and insertion areas receive edge-only candidates.
  if (["SS_001", "SS_008", "SS_009", "SS_019", "SS_020"].includes(site.id)) {
    return edgePoint(site, random, 0.65, 2.4);
  }

  if (edgeClasses.has(assetClass)) return edgePoint(site, random);
  return interiorPoint(site, random, assetClass === "tactical" ? 0.28 : 0.18);
}

const manifest = JSON.parse(fs.readFileSync(placementPath, "utf8"));
const bomRows = parseCsv(fs.readFileSync(bomPath, "utf8")).filter((row) => row.bom_id !== "TOTAL");

const assignments = {};
for (const assetClass of Object.keys(classKey)) {
  const roles = bomRows.filter((row) => row.class === assetClass);
  assignments[assetClass] = allocateRolesToSites(assetClass, roles, manifest.sites);
}

const records = [];
for (const site of manifest.sites) {
  const random = mulberry32(site.seed);
  for (const [assetClass, budgetKey] of Object.entries(classKey)) {
    const count = Number(site.counts[budgetKey]);
    for (let localIndex = 0; localIndex < count; localIndex += 1) {
      const bom = assignments[assetClass][site.id][localIndex];
      if (!bom) throw new Error(`BOM queue exhausted for ${assetClass}`);
      const point = candidatePoint(site, assetClass, random);
      const scaleMin = Number(bom.scale_min);
      const scaleMax = Number(bom.scale_max);
      const scale = scaleMin + random() * (scaleMax - scaleMin);
      const yawJitter = assetClass === "architecture" ? (random() - 0.5) * 2 : (random() - 0.5) * 20;
      const cluster = Math.floor(localIndex / clusterSize[assetClass]) + 1;
      records.push({
        candidate_id: `${site.id}_${assetClass.toUpperCase()}_${String(localIndex + 1).padStart(3, "0")}`,
        site_id: site.id,
        site_name: site.name,
        bom_id: bom.bom_id,
        class: assetClass,
        asset_role: bom.asset_role,
        source: bom.source_record_or_pack,
        cluster_id: `${site.id}_${assetClass.toUpperCase()}_C${String(cluster).padStart(2, "0")}`,
        x_m: Number(point.x.toFixed(3)),
        y_m: Number(point.y.toFixed(3)),
        z_resolution: ["architecture", "utility", "decal"].includes(assetClass) ? "socket_or_trace_in_ue" : "terrain_trace_in_ue",
        yaw_deg: Number(((point.yaw + yawJitter + 360) % 360).toFixed(2)),
        scale: Number(scale.toFixed(4)),
        band: point.band,
        placement_policy: placementPolicy[assetClass],
        transform_status: "candidate_not_final",
        collision: bom.collision,
        nanite: bom.nanite,
        hard_rule: site.rule,
      });
    }
  }
}

const headers = Object.keys(records[0]);
const csv = [headers.join(","), ...records.map((row) => headers.map((key) => csvEscape(row[key])).join(","))].join("\n") + "\n";
fs.writeFileSync(csvOutput, csv);
fs.writeFileSync(
  jsonOutput,
  JSON.stringify(
    {
      schemaVersion: 1,
      generatedFrom: [path.basename(placementPath), path.basename(bomPath)],
      status: "candidate_not_final",
      warning: "XY coordinates are deterministic planning candidates. Unreal must resolve Z, sockets, collision, route exclusions, and final transforms.",
      records,
    },
    null,
    2,
  ) + "\n",
);

const byClass = {};
const bySite = {};
const byBom = {};
for (const record of records) {
  byClass[record.class] = (byClass[record.class] ?? 0) + 1;
  bySite[record.site_id] = (bySite[record.site_id] ?? 0) + 1;
  byBom[record.bom_id] = (byBom[record.bom_id] ?? 0) + 1;
}
const expectedBySite = Object.fromEntries(manifest.sites.map((site) => [site.id, Object.values(site.counts).reduce((a, b) => a + Number(b), 0)]));
const expectedByBom = Object.fromEntries(bomRows.map((row) => [row.bom_id, Number(row.target_instances)]));
const report = {
  valid:
    records.length === manifest.totals.all &&
    JSON.stringify(bySite) === JSON.stringify(expectedBySite) &&
    Object.entries(expectedByBom).every(([key, value]) => byBom[key] === value),
  total: records.length,
  expectedTotal: manifest.totals.all,
  siteCount: Object.keys(bySite).length,
  bomRoleCount: Object.keys(byBom).length,
  byClass,
  bySite,
  mismatchedBomRoles: Object.entries(expectedByBom).filter(([key, value]) => byBom[key] !== value),
};
fs.writeFileSync(reportOutput, JSON.stringify(report, null, 2) + "\n");
if (!report.valid) throw new Error(`Validation failed: ${JSON.stringify(report)}`);
console.log(JSON.stringify(report, null, 2));
