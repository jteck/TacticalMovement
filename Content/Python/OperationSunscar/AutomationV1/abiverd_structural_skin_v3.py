"""Apply the first complete Abiverd structural skin to Old Town buildings.

The playable blockout shells remain authoritative for collision and layout.
This pass changes only their visible materials and adds simple, grounded caps:
foundation skirts, roof parapets, restrained buttresses, and a few non-colliding
Quixel erosion accents.
"""

import hashlib
import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = unreal.Name("SunscarAbiverdStructuralSkinV3")
FOLDER_ROOT = "OperationSunscar/AbiverdStructuralSkinV3"
REPORT_NAME = "abiverd_structural_skin_v3.json"

CUBE_PATH = "/Engine/BasicShapes/Cube"
MUD_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned"
BRICK_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned"
STUCCO_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_WorldAligned"
FLAKED_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_WorldAligned"
DETENTION_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Detention"
METAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal"
STONE_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone"
WALL_SCAN_PATH = "/Game/Maps/Sunscar/Art/Heritage/Architecture/WallModularSet04/Historic_Desert_Ruin_Wall_Modular_Set_04_yjxsbaqyx_High"

RESIDENTIAL_SITES = {
    "SS_004", "SS_005", "SS_007", "SS_012", "SS_017",
    "CentralCourtyard", "WaterTowerCompound",
}
SECURED_SITES = {"SS_010", "DetentionYard"}
INDUSTRIAL_SITES = {"SS_003", "SS_013", "SS_015", "SS_016", "SS_018", "SalvageYard"}
PARAPET_SITES = {"SS_004", "SS_005", "SS_007", "SS_010", "SS_011", "SS_012", "SS_017", "SS_018"}
BUTTRESS_SITES = {"SS_004", "SS_005", "SS_012"}
SCAN_ACCENT_SITES = {"SS_004", "SS_005", "SS_007", "SS_010", "SS_012", "SS_017"}


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


def load_asset(path, expected_class):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, expected_class):
        raise RuntimeError("ABIVERD_SKIN_V3_MISSING_ASSET " + path)
    return asset


def stable_choice(label, values):
    digest = hashlib.sha1(label.encode("utf-8")).digest()
    return values[int.from_bytes(digest[:2], "big") % len(values)]


def actor_site(actor):
    for tag in actor.tags:
        value = str(tag)
        if value.startswith("Building_"):
            return value[len("Building_"):]
    return ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_SKIN_V3_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_SKIN_V3_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_SKIN_V3_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_SKIN_V3_DIRTY_BEFORE " + "|".join(dirty_packages()))

# Load only Old Town and its immediate playable edge.
working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_SKIN_V3_LOAD_DIRTY")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = list(actor_subsystem.get_all_level_actors())
if any(PASS_TAG in list(actor.tags) for actor in actors):
    raise RuntimeError("ABIVERD_SKIN_V3_DUPLICATE")

cube = load_asset(CUBE_PATH, unreal.StaticMesh)
mud = load_asset(MUD_PATH, unreal.MaterialInterface)
brick = load_asset(BRICK_PATH, unreal.MaterialInterface)
stucco = load_asset(STUCCO_PATH, unreal.MaterialInterface)
flaked = load_asset(FLAKED_PATH, unreal.MaterialInterface)
detention = load_asset(DETENTION_PATH, unreal.MaterialInterface)
metal = load_asset(METAL_PATH, unreal.MaterialInterface)
stone = load_asset(STONE_PATH, unreal.MaterialInterface)
wall_scan = load_asset(WALL_SCAN_PATH, unreal.StaticMesh)

landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
trace_ignored = [actor for actor in actors if actor not in landscapes]


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        trace_ignored,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return None
    data = hit.to_dict()
    if not data.get("blocking_hit") or data.get("location") is None:
        return None
    return float(data["location"].z)


building_actors = []
roof_actors = []
modified_packages = set()
material_changes = []

for actor in actors:
    tags = list(actor.tags)
    if unreal.Name("CoreCategory_Building") not in tags:
        continue
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    site = actor_site(actor)
    if not site:
        continue
    label = actor.get_actor_label()
    component = actor.static_mesh_component
    building_actors.append(actor)

    if "_Roof" in label:
        roof_actors.append((actor, site))

    # Floors stay on their existing hard-surface materials. Industrial walls
    # retain their metal/stone language; other zones receive a coherent local
    # mud-brick/plaster hierarchy.
    target = None
    if "_Floor" in label:
        target = None
    elif site in RESIDENTIAL_SITES:
        if "_Lintel" in label:
            target = brick
        elif "_Roof" in label:
            target = mud
        elif site in {"SS_005", "SS_007"}:
            target = stable_choice(label, [stucco, stucco, mud, brick])
        elif site == "SS_017":
            target = stable_choice(label, [mud, mud, flaked])
        else:
            target = stable_choice(label, [mud, mud, mud, brick])
    elif site in SECURED_SITES:
        target = brick if "_Lintel" in label else stable_choice(label, [detention, brick, mud])
    elif site in INDUSTRIAL_SITES:
        if "_Roof" in label:
            target = metal
        elif site in {"SS_003", "SS_013", "SS_018"}:
            target = stable_choice(label, [stone, stone, flaked])
        else:
            target = stable_choice(label, [metal, flaked])
    elif site == "SS_011":
        target = brick if "_Lintel" in label else stable_choice(label, [flaked, stucco, brick])

    if target is not None:
        old = component.get_material(0)
        old_path = old.get_path_name() if old else ""
        new_path = target.get_path_name()
        if old_path != new_path:
            component.set_material(0, target)
            modified_packages.add(package_name(actor.get_package()))
            material_changes.append({"actor": label, "site": site, "from": old_path, "to": new_path})


created = []
created_packages = set()


def spawn_cube(label, site, location, scale, material, collision):
    actor = actor_subsystem.spawn_actor_from_object(cube, location, unreal.Rotator(), transient=False)
    if actor is None:
        raise RuntimeError("ABIVERD_SKIN_V3_SPAWN " + label)
    actor.set_actor_scale3d(scale)
    actor.set_actor_label(label)
    actor.set_folder_path(unreal.Name(FOLDER_ROOT + "/" + site))
    actor.tags = [PASS_TAG, unreal.Name(site), unreal.Name("AbiverdStructuralSkinV3")]
    component = actor.static_mesh_component
    component.set_material(0, material)
    component.set_collision_enabled(
        unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision else unreal.CollisionEnabled.NO_COLLISION
    )
    component.set_cast_shadow(True)
    created.append(label)
    created_packages.add(package_name(actor.get_package()))
    return actor


def spawn_scan(label, site, location, yaw, scale):
    bounds = wall_scan.get_bounds()
    local_bottom = (bounds.origin.z - bounds.box_extent.z) * scale
    actor = actor_subsystem.spawn_actor_from_object(
        wall_scan,
        unreal.Vector(location.x, location.y, location.z - local_bottom),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw),
        transient=False,
    )
    if actor is None:
        raise RuntimeError("ABIVERD_SKIN_V3_SCAN " + label)
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    actor.set_actor_label(label)
    actor.set_folder_path(unreal.Name(FOLDER_ROOT + "/" + site))
    actor.tags = [PASS_TAG, unreal.Name(site), unreal.Name("AbiverdStructuralSkinV3"), unreal.Name("QuixelMegascans")]
    actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    created.append(label)
    created_packages.add(package_name(actor.get_package()))
    return actor


for roof_actor, site in roof_actors:
    if site not in PARAPET_SITES:
        continue
    bounds = roof_actor.get_actor_bounds(False)
    origin = bounds[0]
    extent = bounds[1]
    top_z = origin.z + extent.z
    x_len = max(200.0, extent.x * 2.0)
    y_len = max(200.0, extent.y * 2.0)
    parapet_height = 72.0 if site not in {"SS_007", "SS_010"} else 88.0
    parapet_thickness = 28.0
    parapet_material = brick if site in {"SS_005", "SS_010", "SS_011", "SS_018"} else mud
    z = top_z + parapet_height * 0.5

    for suffix, x, y, sx, sy in (
        ("North", origin.x, origin.y + extent.y - parapet_thickness * 0.5, x_len / 100.0, parapet_thickness / 100.0),
        ("South", origin.x, origin.y - extent.y + parapet_thickness * 0.5, x_len / 100.0, parapet_thickness / 100.0),
        ("East", origin.x + extent.x - parapet_thickness * 0.5, origin.y, parapet_thickness / 100.0, y_len / 100.0),
        ("West", origin.x - extent.x + parapet_thickness * 0.5, origin.y, parapet_thickness / 100.0, y_len / 100.0),
    ):
        spawn_cube(
            "ABV_%s_RoofParapet_%s" % (site, suffix),
            site,
            unreal.Vector(x, y, z),
            unreal.Vector(sx, sy, parapet_height / 100.0),
            parapet_material,
            True,
        )

    # Four 35 cm high masonry skirts visually join the existing shell to the
    # terrain. They are render-only so movement collision remains unchanged.
    ground = terrain_z(origin.x, origin.y)
    if ground is None:
        raise RuntimeError("ABIVERD_SKIN_V3_TERRAIN " + site)
    skirt_height = 35.0
    skirt_thickness = 24.0
    skirt_material = brick if site in {"SS_005", "SS_010", "SS_011", "SS_018"} else mud
    skirt_z = ground + skirt_height * 0.5 - 4.0
    for suffix, x, y, sx, sy in (
        ("North", origin.x, origin.y + extent.y, x_len / 100.0, skirt_thickness / 100.0),
        ("South", origin.x, origin.y - extent.y, x_len / 100.0, skirt_thickness / 100.0),
        ("East", origin.x + extent.x, origin.y, skirt_thickness / 100.0, y_len / 100.0),
        ("West", origin.x - extent.x, origin.y, skirt_thickness / 100.0, y_len / 100.0),
    ):
        spawn_cube(
            "ABV_%s_FoundationSkirt_%s" % (site, suffix),
            site,
            unreal.Vector(x, y, skirt_z),
            unreal.Vector(sx, sy, skirt_height / 100.0),
            skirt_material,
            False,
        )

    # Residential/civic corners get restrained low buttresses. These are
    # decorative and never become an unintended climb/collision surface.
    if site in BUTTRESS_SITES:
        buttress_height = 220.0
        for suffix, x, y in (
            ("NE", origin.x + extent.x, origin.y + extent.y),
            ("SW", origin.x - extent.x, origin.y - extent.y),
        ):
            corner_ground = terrain_z(x, y)
            if corner_ground is None:
                continue
            spawn_cube(
                "ABV_%s_Buttress_%s" % (site, suffix),
                site,
                unreal.Vector(x, y, corner_ground + buttress_height * 0.5),
                unreal.Vector(0.55, 0.55, buttress_height / 100.0),
                mud,
                False,
            )

    # One scan accent on selected buildings is enough to break the perfect
    # cuboid silhouette without obscuring doors, windows, or combat lanes.
    if site in SCAN_ACCENT_SITES:
        accent_x = origin.x + extent.x + 32.0
        accent_y = origin.y + extent.y * 0.58
        accent_ground = terrain_z(accent_x, accent_y)
        if accent_ground is not None:
            spawn_scan(
                "ABV_%s_ErodedCornerAccent" % site,
                site,
                unreal.Vector(accent_x, accent_y, accent_ground),
                -90.0,
                0.58,
            )

expected_dirty = modified_packages | created_packages
dirty_before_save = dirty_packages()
unexpected = [
    name for name in dirty_before_save
    if name not in expected_dirty
    and not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")
]
if unexpected:
    raise RuntimeError("ABIVERD_SKIN_V3_UNEXPECTED_DIRTY " + "|".join(unexpected))

packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_SKIN_V3_SAVE_FAILED")
remaining = dirty_packages()
if remaining:
    raise RuntimeError("ABIVERD_SKIN_V3_DIRTY_AFTER " + "|".join(remaining))

report = {
    "schema_version": 3,
    "status": "abiverd_structural_skin_saved",
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "world_partition_descriptors_loaded": len(descriptors),
    "building_actor_count": len(building_actors),
    "roof_actor_count": len(roof_actors),
    "material_change_count": len(material_changes),
    "created_actor_count": len(created),
    "created_actors": created,
    "modified_actor_packages": sorted(modified_packages),
    "created_actor_packages": sorted(created_packages),
    "dirty_before_save": dirty_before_save,
    "dirty_after_save": remaining,
    "policies": {
        "gameplay_shells_preserved": True,
        "foundation_skirts_collision": "NoCollision",
        "parapet_collision": "QueryAndPhysics",
        "scan_collision": "NoCollision",
        "nanite_scan_policy": "Reuse configured Nanite source mesh",
        "replication": "Static non-replicated actors",
    },
}

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)

unreal.log(
    "ABIVERD_SKIN_V3_COMPLETE materials=%d created=%d saved=%d"
    % (len(material_changes), len(created), len(packages))
)
