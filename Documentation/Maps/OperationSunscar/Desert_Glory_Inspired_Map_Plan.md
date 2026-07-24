# Desert Glory–Inspired Map Plan

Working title: **Operation Sunscar**
Graybox level: `/Game/Maps/Graybox/L_GB_Sunscar`
Target engine: Unreal Engine 5.8

## 1. Intent

Build an original desert-town tactical map that captures the combat grammar that
made SOCOM's Desert Glory memorable:

- asymmetric attacker/defender territory;
- a rescue objective deep in defender territory;
- three readable macro routes with frequent cross-connections;
- a central exposed fight space;
- a protected but slower edge route;
- a wide flank through scattered cover;
- a small number of powerful vertical positions;
- distinct landmarks that support fast team callouts;
- meaningful travel back through the map after securing the objective.

This is an homage, not a one-for-one reconstruction. The final map should use a
different overall silhouette, original building plans, different proportions,
new landmark names, and altered route connections.

Primary reference lock: use the **SOCOM Confrontation version of Desert Glory**
for spatial density, architecture, street proportions, verticality, cover rhythm,
and atmosphere. Use the PlayStation 2 version only to clarify the original
extraction flow, landmark roles, and broad three-route structure.

Expansion lock: Operation Sunscar will be a substantially larger reinterpretation,
not a compact remake. Preserve Confrontation's human-scale architecture and
combat texture while expanding the town into multiple connected districts.

Location lock: Operation Sunscar is a fictional abandoned road, canal, and rail
service town on the **Kaka–Abiverd corridor in Ahal Province**, between the
Kopet-Dag foothills to the south and the Karakum Desert to the north.

Topography lock: use
`Sunscar_Topography_and_Site_Spec.md` as the terrain, elevation, drainage,
georeferencing, and Unreal Landscape source of truth.

## 2. Reference findings

The original Desert Glory appears in SOCOM and SOCOM II as a daytime Extraction
map set in a Turkmenistan desert town. SEALs advance through the town, enter the
hostage/prison area, and return rescued hostages toward their side.

The widely circulated Sea Snipers tactical map labels these important spaces:

- Prison and Prison Grounds
- Hotel
- Prison Tower
- Guard House
- Guest House
- Cafe
- Courtyard
- Junkyard
- Garage
- The Strip and Strip Tower
- SEAL Pass

The original layout supports three broad approaches:

1. West edge: SEAL Pass to Cafe, Prison Tower, and Prison Grounds.
2. Center: Courtyard and Hotel to the Prison Deck.
3. East edge: The Strip to Garage, Junkyard, Guard House, and Prison.

The Hotel is repeatedly described as a three-floor overwatch position. Community
guides also identify playable roofs and rocks around the Prison, Strip Tower,
Guest House, and Cafe. A later Confrontation version retained the compact scale,
central explosive hazards, and strong sniper pressure from edge buildings.

Reference links:

- https://www.darksidealliance.com/articles/gaming-maps/258066-socom-maps
- https://gamefaqs.gamespot.com/ps2/914813-socom-ii-us-navy-seals/faqs/32202
- https://gamefaqs.gamespot.com/ps2/516240-socom-us-navy-seals/faqs/22671
- https://giantbomb.com/wiki/Games/SOCOM_U_S_Navy_SEALs
- https://wikiwiki.jp/socom/Desert%20Glory
- Primary — SOCOM Confrontation flythrough:
  https://www.youtube.com/watch?v=W-TRYD3mOBs
- Secondary — original SOCOM II gameplay:
  https://www.youtube.com/watch?v=rQ-oHvLd2-4

### Confrontation calibration notes

The SOCOM Confrontation flythrough is the primary reference for this project.
Its rebuilt version has the stronger architectural language and vertical combat
spaces we want: dense low-rise construction, broad exterior stairs, balconies,
roof edges, utility poles, shallow channels, vehicle courts, and tight cliff
boundaries.

The original PlayStation 2 gameplay remains a secondary reference. It can
clarify the extraction objective and the recognizable relationship between the
Hotel, Prison, Courtyard, edge routes, and attacker side, but it must not
override the Confrontation version's architecture or spatial presentation.

The videos do not contain survey data, so apparent measurements are calibrated
against ordinary human-scale objects:

- character height: approximately 1.75–1.85 m;
- doorway: approximately 0.9–1.1 m wide and 2.05–2.2 m high;
- exterior stair: approximately 0.17–0.19 m rise and 0.28–0.32 m tread;
- passenger vehicle: approximately 4.3–4.8 m long;
- typical floor-to-floor height: approximately 3.0–3.3 m.

The most reliable findings are proportional. These describe the Confrontation
reference; Sunscar will repeat this density at a larger district scale:

- each combat district is compact and wider than it is deep;
- the major landmarks are separated by short streets rather than empty terrain;
- most streets are about one vehicle wide, with only a few broader courts;
- most buildings are one or two floors, with selected multi-floor anchors;
- balconies, exterior stairs, windows, and roof edges create layered fights;
- the Hotel remains the strongest multi-floor landmark;
- the cliffs and exterior walls sit close to playable routes;
- exterior stairs are broad enough for two characters to pass, but alleys are
  deliberately tighter.

All dimensions below are therefore **calibrated starting values**, not claims
about the original source files. Final dimensions must be accepted through
timed traversal tests with this project's player movement.

## 3. Proposed map identity

Operation Sunscar is a partially abandoned desert customs town built around a
detention annex and municipal hotel. A militia holds captives in the annex.
Attackers enter from a dry flood channel in the southwest. Defenders can stage
from either a northern command post or a southern market district.

Original landmark names:

| Reference role | Sunscar landmark |
| --- | --- |
| Prison / hostage room | Detention Annex |
| Hotel | Municipal Hotel |
| Prison Tower | Water Tower Compound |
| Cafe | Tea House |
| Guard House | Checkpoint Office |
| Guest House | Consulate Residence |
| Junkyard | Salvage Yard |
| Garage | Motor Pool |
| The Strip | Covered Bazaar |
| Strip Tower | Telecom Workshop |
| SEAL Pass | Dry Canal |

## 4. Scale targets

The existing layout becomes the reusable **Old Town / Detention Core**. The
previous 640 m × 500 m expansion becomes the **Inner Service Town**. Both remain
intact inside a much larger regional battlefield.

- Existing core footprint: approximately **320 m × 250 m**
- Inner Service Town footprint: approximately **640 m × 500 m**
- Full playable footprint: approximately **2,000 m × 1,600 m**
- Full playable area: approximately **3.2 km²**
- Full terrain and skyline envelope: approximately **2,520 m × 2,520 m**
- Outer terrain buffer: approximately **260 m east/west** and **460 m north/south**
- Attacker spawn to first meaningful decision: **8–12 seconds**
- Attacker spawn to first likely contact: **18–30 seconds**
- Core-only fast route to Detention Annex: approximately **45–60 seconds**
- Core-only cautious route to Detention Annex: approximately **65–95 seconds**
- Inner-town infantry traversal: approximately **110–160 seconds**
- Full-map direct infantry traversal: approximately **6–10 minutes**
- Regular street width: **4.5–7.0 m**
- Broad vehicle street or court: **7–10 m**
- Major court or yard crossing: **16–36 m**
- Exterior alley width: **2.2–3.5 m**
- Tight interior corridor width: **1.5–2.0 m**
- Main building ceiling height: **2.8–3.2 m**
- Typical exterior stair clear width: **2.4–3.0 m**
- Exterior wall height: **2.2–2.8 m**
- Parapet height: **1.0–1.2 m**
- Rooftop floor separation: approximately **3.0–3.3 m**

The full map should support multi-stage co-op, 16v16 or larger objective modes,
AI patrol space, vehicles, forward spawns, and mission phases. The Inner Service
Town and Old Town Core remain separately closeable for compact round-based modes.

### 4.1 Geographic influence

Use south-central Turkmenistan—especially the Kaka–Abiverd corridor along the
northern edge of the Kopet-Dag Mountains—as the realistic geographic basis.
This is a deliberate location for Operation Sunscar, not a claim that SOCOM
assigned Desert Glory to a real city.

This combination supports the Confrontation visual language while giving the
expanded map believable variety:

- Karakum sand ridges, fixed dunes, dry depressions, and sparse scrub to the
  north;
- irrigation canals, collector ditches, pump houses, small bridges, and
  rectilinear fields primarily east of town;
- orchard walls and small irrigated compounds along the settled corridor;
- Abiverd-inspired fortified ruins, caravan infrastructure, and earthen walls
  west of the core;
- east–west freight roads, rail service, power distribution, and water
  infrastructure;
- Kopet-Dag foothill cuts, quarry faces, and rocky ridges to the south that
  justify Confrontation-like cliffs and elevated approaches.

Geographic references:

- NASA, Murgab and Tedzhen agricultural fans:
  https://science.nasa.gov/earth/earth-observatory/agriculture-fans-out-in-turkmenistan-149577/
- NASA, Mary oasis:
  https://www.nasa.gov/image-article/oasis-city-of-mary-karakum-desert-turkmenistan/
- UNESCO, Parthian Fortresses of Nisa and Kopet-Dag setting:
  https://whc.unesco.org/en/list/1242/
- UNESCO, Ancient Merv:
  https://whc.unesco.org/en/list/886
- UNESCO, Dehistan/Mishrian abandoned fortified city:
  https://whc.unesco.org/en/tentativelists/967/
- UNESCO, Turkmenistan Silk Roads sites and infrastructure:
  https://whc.unesco.org/en/tentativelists/5521
- UNESCO, Repetek/Karakum dune landscape:
  https://whc.unesco.org/en/tentativelists/5435/

### 4.2 Expansion master plan

Do not scale or rebuild the existing 320 m × 250 m core. Place it in the center
of the battlefield as a reusable Level Instance with a global offset of
`(+840 m, +675 m)`. Preserve the 640 m × 500 m expansion around it as the Inner
Service Town at X 680–1320 and Y 550–1050.

| Region | Expanded coordinates | Primary identity | Combat role |
| --- | --- | --- | --- |
| Old Town / Detention Core | X 840–1160, Y 675–925 | Existing Sunscar layout | Dense central objective district |
| Inner Service Town | X 680–1320, Y 550–1050 | Original four expansion districts | Close tactical ring and core access |
| West — Abiverd March | X 0–680, Y 400–1200 | Ruins, caravan road, kiln village | Broken-wall fighting, caves, historic approach |
| East — Canal Agricultural Belt | X 1320–2000, Y 350–1250 | Canal, fields, freight spur | Infrastructure fights, bridges, field compounds |
| South — Kopet Foothills | X 400–1600, Y 0–550 | Quarry complex, ridge road, gullies | High ground, caves, switchbacks, objective chain |
| North — Karakum Expanse | X 350–1650, Y 1050–1600 | Dunes, depressions, desert road | Long flank, convoy route, concealed approaches |
| Southwest approach | X 0–400, Y 0–550 | Wadi fan and border trail | Infiltration, vehicle bypass, hidden staging |
| Southeast works | X 1600–2000, Y 0–350 | Reservoir, rail yard, industrial edge | Logistics objective and vehicle access |
| Northwest approach | X 0–350, Y 1200–1600 | Caravan track and ruined wells | Recon route and desert spawn |
| Northeast approach | X 1650–2000, Y 1250–1600 | Checkpoint highway and salt flats | Convoy spawn and open-fire corridor |

Expansion rules:

- Break every 400–700 m outer region into two or three 120–220 m combat pockets.
- Separate pockets with 60–180 m transition zones such as fields, dry wadis,
  berms, canals, road cuts, and vehicle routes.
- Give every outer district at least three connections: one to the core, one to
  an adjacent outer district, and one local alternate route.
- Keep the original core playable as a standalone “classic” map by closing its
  expansion gates.
- Use the 640 m × 500 m Inner Service Town for medium objective and large
  round-based modes.
- Use the full 2,000 m × 1,600 m battlefield for multi-stage co-op, territory,
  convoy, raid, or high-player-count modes.
- Full-map modes require vehicles, forward spawns, phase changes, or a
  combination of all three.
- Preserve realistic directional silhouettes: old ruins west, green irrigation
  east, Kopet-Dag ridge south, and open Karakum desert north.

Outer-district landmarks:

| District | Major landmarks |
| --- | --- |
| Abiverd Road | Ruined Gate, Caravan Court, Kiln Yard, Old Road Checkpoint |
| Kopet Ridge | Quarry Bowl, Qala Wall, Cave Store, Ridge Road, Signal Mast |
| Karakum Pass | Caravanserai Ruin, Dune Cut, Well Compound, Desert Checkpoint |
| Canal Works | Main Canal, Pump Hall, Narrow Bridge, Field Sluices, Freight Platform |

## 5. Coordinate layout

Coordinates below remain local to the preserved 320 m × 250 m core. In the
full battlefield, add `(840, 675)` to each X/Y value. This keeps the existing
layout unchanged while placing it at the center of the Inner Service Town and
the 2,000 m × 1,600 m map.

| Landmark | X | Y | Footprint / height |
| --- | ---: | ---: | --- |
| Attacker spawn / extraction | 30 | 26 | 20 × 18 m |
| Dry Canal entrance | 34 | 106 | 7 m wide |
| Canal Pump Station | 54 | 62 | 18 × 15 m, 1 floor |
| Tea House | 72 | 96 | 18 × 16 m, 1 floor |
| Old Clinic | 104 | 124 | 24 × 19 m, 2 floors |
| Water Tower Compound | 98 | 170 | 16 × 16 m, tower |
| Municipal Hotel | 146 | 152 | 28 × 22 m, 3 floors |
| Central Courtyard | 142 | 94 | 34 × 28 m |
| Transit Plaza | 166 | 120 | 32 × 26 m |
| Detention Annex | 182 | 216 | 34 × 28 m, 2 floors |
| Checkpoint Office | 234 | 176 | 20 × 17 m, 2 floors |
| Consulate Residence | 278 | 174 | 21 × 18 m, 2 floors |
| Freight Depot | 268 | 126 | 30 × 24 m, 1 floor |
| Salvage Yard | 234 | 108 | 44 × 35 m |
| Motor Pool | 288 | 78 | 24 × 20 m |
| Power Substation | 220 | 55 | 26 × 20 m |
| Covered Bazaar | 188 | 32 | 36 × 17 m |
| Telecom Workshop | 104 | 34 | 21 × 18 m, 2 floors |
| South defender insertion | 272 | 20 | 20 × 16 m |
| North defender insertion | 278 | 222 | 20 × 16 m |

## 6. Route design

### Route A — Dry Canal

Role: slower, covered, deliberate approach.

Sequence:

`Attacker Spawn → Canal Pump Station → Dry Canal → Tea House → Old Clinic →
Water Tower → Detention Yard`

Design rules:

- Organize the route as three compact combat pockets connected by short movement
  intervals.
- Broken sightlines every 12–24 m inside combat pockets.
- Two locations that force a readiness decision before turning a corner.
- One elevated defender angle from the Water Tower, with at least two counters.
- A breachable-looking service door into the Annex, initially fixed open.
- The route must not be completely invisible from the center.

### Route B — Courtyard

Role: fastest and most dangerous approach.

Sequence:

`Attacker Spawn → Central Courtyard → Transit Plaza → Hotel edge/interior →
Annex Deck`

Design rules:

- Strong exposure during the Courtyard and Transit Plaza crossings.
- Cover supports movement but never forms an uninterrupted safe chain.
- Hotel windows watch portions of the route, not the entire route.
- Players can enter the Hotel to remove overwatch at the cost of time.
- A smoke grenade should be valuable here once equipment exists.

### Route C — Bazaar Flank

Role: longest route with the most cross-route options.

Sequence:

`Attacker Spawn → Telecom Workshop → Covered Bazaar → Power Substation →
Motor Pool → Salvage Yard → Freight Depot → Checkpoint Office → Annex`

Design rules:

- Medium-range engagements with irregular cover.
- Vehicle and scrap placement creates pockets, not random visual noise.
- Use the Power Substation and Freight Depot as intermediate fight spaces so
  the enlarged flank never becomes an empty running lane.
- At least two exits from the Salvage Yard.
- One connector returns to the Courtyard.
- One connector reaches the Consulate Residence.
- Defender sightlines should be strong but require repositioning as attackers move.

## 7. Cross-connections

Cross-connections prevent the three routes from behaving like isolated tunnels.

- Tea House ↔ Courtyard through a narrow service lane.
- Old Clinic ↔ Transit Plaza through a covered street.
- Hotel ↔ Salvage Yard through a broken wall and loading alley.
- Courtyard ↔ Bazaar through a shaded arcade.
- Transit Plaza ↔ Freight Depot through a broad vehicle street.
- Power Substation ↔ Courtyard through a maintenance passage.
- Salvage Yard ↔ Checkpoint Office through two separated openings.
- Water Tower ↔ Hotel through an exposed northern road.
- Detention Yard ↔ Checkpoint Office through a controlled gate.

Each connector should create a decision, not merely shorten travel time.

## 8. Verticality rules

Keep vertical positions scarce enough that players can learn them:

- Municipal Hotel: three floors; roof inaccessible in the first graybox.
- Water Tower: one elevated platform.
- Telecom Workshop: accessible second floor.
- Detention Annex: second-floor catwalk overlooking only part of its yard.
- Checkpoint Office: accessible second-floor room.
- Consulate Residence: balcony, no full roof access.

Confrontation-specific vertical language:

- favor exterior stairs and balconies over hidden interior stairwells;
- use partial upper floors rather than full-height towers everywhere;
- let elevated routes overlook one street or court at a time;
- keep rooftops visually readable even when they are inaccessible;
- use cliff walls and building backs to prevent uncontrolled long-range views.

Every elevated position needs:

- at least two attack angles or one attack angle plus utility exposure;
- a limited field of view;
- a readable silhouette;
- a movement or escape cost;
- no direct view of both team spawns.

## 9. Objective flow

Initial graybox objective:

1. Attackers spawn in the southwest.
2. Attackers reach the Detention Annex.
3. Attackers interact with a placeholder objective marker.
4. Attackers return to the extraction zone.

Before a full objective system exists:

- use `PlayerStart` actors for insertions;
- use `TargetPoint` actors for objective and extraction markers;
- add debug signs and floor colors;
- time runs manually with a stopwatch;
- do not build a bespoke objective framework just for the graybox.

Later objective requirements:

- two to three hostage positions;
- escort-follow behavior;
- extraction volume;
- round win/loss rules;
- defender hostage safeguards;
- objective status UI;
- interruption and recovery rules.

## 10. Unreal content structure

```text
/Game/Maps/
  /Dev/
    L_Dev_MapMetrics
  /Graybox/
    L_GB_Sunscar
  /Sunscar/
    L_Sunscar
    /Lighting
    /LevelInstances

/Game/Environment/Sunscar/
  /Blockout
  /Architecture
  /Props
  /Materials
  /Decals
  /Foliage

/Game/Gameplay/Map/
  /Debug
  /Objectives
  /Spawns
```

Keep `Lvl_ThirdPerson` unchanged as a known-good gameplay regression map.

For the 2,000 m × 1,600 m footprint, use World Partition and Data Layers.
Convert the approved 320 m × 250 m core into a Level Instance before
building the Inner Service Town and outer battlefield. This preserves the classic layout, allows core-only
playtests, and prevents outer-district work from destabilizing the central map.
Use One File Per Actor only if the project already relies on it for team workflow.

## 11. Graybox kit

Build or reuse:

- 1 m, 2 m, 4 m, and 8 m wall modules;
- 10 cm, 20 cm, and 40 cm trim blocks;
- 1.0 m and 1.2 m doorway modules;
- 1.2 m and 1.8 m window modules;
- straight stair modules;
- parapets and railings;
- 0.9 m and 1.2 m cover blocks;
- vehicle-sized proxy blocks;
- rocks/cliff boundary proxies;
- route-colored floor decals;
- a metric grid material.

Use Epic's Modeling Mode and template-friendly primitives for the first blockout.
No final environment assets are required to validate the layout.

## 12. Build sequence

### MAP-0 — Metrics map

- Create `L_Dev_MapMetrics`.
- Add door, corridor, stair, window, cover, and ceiling test pieces.
- Verify first-person camera clearance and weapon framing.
- Record accepted dimensions.

Exit test: traversal feels comfortable at jog and sprint speeds.

### MAP-1 — Master boundary and preserved core

- Create `L_GB_Sunscar`.
- Block the 2,000 m × 1,600 m master boundary.
- Place the 640 m × 500 m Inner Service Town at `(680 m, 550 m)`.
- Place the 320 m × 250 m core at `(840 m, 675 m)`.
- Preserve its landmarks, three macro routes, spawn, and objective markers.
- Add temporary gates at every planned expansion connection.

Exit test: the core remains playable by closing the temporary gates.

### MAP-1A — Inner Service Town

- Block Abiverd Road, Canal Works, Kopet Ridge, and Karakum Pass as district
  proxy volumes.
- Establish the 30–60 m transition zones inside the Inner Service Town.
- Add terrain silhouettes: western ruins, eastern canal fields, southern
  foothills, and northern dunes.

Exit test: every district has a unique silhouette when viewed from the core.

### MAP-1B — Outer battlefield

- Block the four regional zones and four corner approaches.
- Break each regional zone into two or three 120–220 m combat pockets.
- Establish 60–180 m transitions using wadis, fields, berms, canals, roads, and
  terrain folds.
- Add the vehicle loop, forward-spawn sites, and mission-phase boundaries.

Exit test: the 3.2 km² map has purposeful movement space rather than empty scale.

### MAP-1C — Outer routes

- Give each outer district three connections.
- Create a continuous outer ring route without entering the core.
- Connect the outer ring to at least four separated core gates.
- Place large-mode spawns and multi-stage objective markers.

Exit test: players can rotate between adjacent outer districts without always
crossing the central objective area.

### MAP-2 — Landmark masses

- Preserve the Detention Annex, Hotel, Tea House, Motor Pool, Bazaar, and offices.
- Build outer-district proxy landmarks before adding small cover.
- Keep interiors minimal.
- Establish strong silhouettes and callouts.

Exit test: players can identify their location without a minimap.

### MAP-3 — Connections and verticality

- Add cross-route alleys.
- Add selected second and third floors.
- Add stairs, ladders, and catwalks.
- Close any unintended dominant sightlines.

Exit test: no elevated position controls more than two major spaces.

### MAP-4 — Tactical cover

- Place deliberate cover clusters.
- Add vehicle and scrap proxies.
- Add concealment separately from hard cover.
- Validate crouch-height cover when crouching exists.

Exit test: routes have push-and-pause rhythm without safe cover chains.

### MAP-5 — Gameplay instrumentation

- Add route timing markers.
- Add combat-distance signs.
- Add sightline and spawn-safety debug actors.
- Add navigation data when AI testing begins.

Exit test: the team can collect repeatable route and encounter measurements.

### MAP-6 — First playable objective

- Add the smallest possible rescue/extraction prototype.
- Populate with simple targets or AI only after combat systems support it.
- Test attacking, securing, and returning through the changed map state.

Exit test: the return trip produces different tactical decisions from the entry.

### MAP-7 — Art prototype

- Select an original architectural region and material language.
- Build one finished landmark and one street segment.
- Establish lighting, atmosphere, decals, and prop density.

Exit test: the art direction preserves callout clarity and does not obscure doors.

### MAP-8 — Production and optimization

- Convert approved blockout pieces into modular production assets.
- Add Nanite where suitable.
- Validate collision independently from render meshes.
- Create HLODs only if later scale and streaming justify them.
- Profile Lumen, shadows, foliage, and draw calls on target hardware.

## 13. Playtest questions

Run every question from both directions where applicable:

- Can an attacker identify three viable routes within 10 seconds?
- Is the center route fastest but visibly riskiest?
- Is the west route safer without becoming mandatory?
- Can defenders rotate without instantly covering every route?
- Does the Hotel create pressure without controlling the whole map?
- Are the Detention Annex entrances meaningfully different?
- Is the return journey vulnerable without becoming impossible?
- Does Low Ready feel useful while moving through alleys?
- Are there natural points to transition from sprint to Movement Ready or ADS?
- Do corners and door widths work with the current first-person weapon framing?
- Are there at least two counters to every elevated position?
- Can players make short, unambiguous callouts for every landmark?

## 14. Dependencies and deferrals

Needed now:

- a dedicated map folder;
- a blockout material;
- modeling primitives;
- PlayerStarts and TargetPoints;
- repeatable route-timing notes;
- regular Standalone playtests.

Not needed for the first graybox:

- final environment art;
- World Partition;
- procedural generation;
- full objective framework;
- functioning doors;
- finished AI;
- destructible cover;
- civilians;
- inventory or ammo economy.

Systems needed before a true combat playtest:

- firing and recoil;
- damage and health;
- ammo and production reload input;
- target or enemy actors;
- spawn/round handling;
- rescue and extraction logic.

## 15. First editor session checklist

1. Create a feature branch for the graybox after explicit approval.
2. Create `/Game/Maps/Dev` and `/Game/Maps/Graybox`.
3. Create `L_Dev_MapMetrics`.
4. Verify player scale, door clearance, stairs, and cover.
5. Create `L_GB_Sunscar`.
6. Mark the full 2,000 m × 1,600 m playable footprint.
7. Mark the Inner Service Town at X 680–1320 and Y 550–1050.
8. Place the unchanged 320 m × 250 m core at offset `(840 m, 675 m)`.
9. Mark the West Abiverd March, East Canal Belt, South Kopet Foothills, and
   North Karakum Expanse bounds.
10. Split each outer region into two or three combat pockets before adding detail.
11. Connect outer regions with infantry paths, vehicle roads, and bypass routes.
12. Add primary and intermediate landmark proxy volumes.
13. Run core-only, inner-town, and full-map traversal timing passes before
    adding interiors.
14. Target 110–160 seconds across the Inner Service Town and 6–10 minutes across
    the full battlefield on foot. Tune vehicles and forward spawns before
    compressing terrain.
15. Compare each combat district against the Confrontation flythrough at four
    reference conditions: canal, dense town block, alley/low wall, and vehicle
    court.
