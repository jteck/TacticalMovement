"""Read-only per-site coverage audit for the Old Town first-round art draft."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


OFFICIAL_PREFIXES = (
    "/Game/Fab/",
    "/Game/Maps/Sunscar/Art/Quixel/",
    "/Game/MilitaryTrench/",
    "/Game/CitySampleVehicles/",
    "/Game/Scene_Junkyard/",
)
CATEGORIES = {
    "door": ("door", "gate"),
    "window": ("window", "shutter"),
    "parapet": ("parapet",),
    "wall": ("wall", "facade", "fence"),
    "floor": ("floor", "courtyard", "plaza", "yard"),
    "roof_or_canopy": ("roof", "canopy", "awning", "tarp"),
    "utility": ("electrical", "cabinet", "utility", "tank", "pipe", "drain"),
    "furniture": ("bench", "table", "chair", "furn"),
    "vehicle_or_scrap": ("vehicle", "sedan", "van", "truck", "scrap", "junk"),
    "cover": ("sandbag", "barrier", "cover"),
    "ground_dressing": ("ground", "debris", "rubble", "rock", "grass"),
}

config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
sites = {"SS_%03d" % index: [] for index in range(1, 21)}

for actor in actors:
    label = actor.get_actor_label()
    tags = common.actor_tags(actor)
    candidates = {tag for tag in tags if tag in sites}
    prefix = label[:6]
    if prefix in sites:
        candidates.add(prefix)
    if not candidates:
        continue
    for site_id in candidates:
        sites[site_id].append(actor)

site_records = []
for site_id in sorted(sites):
    site_actors = sites[site_id]
    category_counts = {key: 0 for key in CATEGORIES}
    bom_counts = {}
    official_count = 0
    automation_count = 0
    art_draft_count = 0
    labels = []
    for actor in site_actors:
        label = actor.get_actor_label()
        folder = common.actor_folder(actor)
        mesh_path = common.actor_mesh_path(actor)
        tags = common.actor_tags(actor)
        search = " ".join([label, folder, mesh_path, *tags]).lower()
        labels.append(label)
        if mesh_path.startswith(OFFICIAL_PREFIXES):
            official_count += 1
        if label.startswith("OT_"):
            automation_count += 1
        if folder.startswith("OldTown_ArtDraft/"):
            art_draft_count += 1
        for category, terms in CATEGORIES.items():
            if any(term in search for term in terms):
                category_counts[category] += 1
        for tag in tags:
            if tag.startswith("OT_"):
                bom_counts[tag] = bom_counts.get(tag, 0) + 1
    site_records.append({
        "site_id": site_id,
        "actor_count": len(site_actors),
        "official_asset_actor_count": official_count,
        "automation_actor_count": automation_count,
        "art_draft_actor_count": art_draft_count,
        "category_counts": category_counts,
        "bom_tag_counts": dict(sorted(bom_counts.items())),
        "labels": sorted(set(labels)),
    })

payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "loaded_actor_count": len(actors),
    "site_count": len(site_records),
    "sites": site_records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_site_coverage_audit_v1.json", payload)
unreal.log("SUNSCAR_SITE_COVERAGE sites=%d report=%s" % (len(site_records), report))
print("SUNSCAR_SITE_COVERAGE", len(site_records), report)
