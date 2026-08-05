"""Dry-run/apply the first terrain-conformed Abiverd heritage composition."""

import json
import math
import os

import unreal


APPLY_CHANGES = True
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = unreal.Name("SunscarAbiverdHeritageCompositionV1")
FOLDER_ROOT = "OperationSunscar/AbiverdHeritageV1"
REPORT_NAME = (
    "abiverd_heritage_architecture_composition_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_heritage_architecture_composition_dry_run_v1.json"
)

CUBE_PATH = "/Engine/BasicShapes/Cube"
SPHERE_PATH = "/Engine/BasicShapes/Sphere"
CYLINDER_PATH = "/Engine/BasicShapes/Cylinder"
MASTER_PATH = "/Game/Maps/Sunscar/Art/Materials/Facade/M_OT_WorldAlignedFacade"
MATERIAL_FOLDER = "/Game/Maps/Sunscar/Art/Heritage/Materials"
MUD_MI_PATH = MATERIAL_FOLDER + "/MI_ABV_CrackedMud_WorldAligned"
BRICK_MI_PATH = MATERIAL_FOLDER + "/MI_ABV_RuinBrick_WorldAligned"

MUD_BASE = "/Game/Maps/Sunscar/Art/Heritage/Surfaces/CrackedMudWall/Cracked_Mud_Wall_th5kcijn_4K_BaseColor"
MUD_NORMAL = "/Game/Maps/Sunscar/Art/Heritage/Surfaces/CrackedMudWall/Cracked_Mud_Wall_th5kcijn_4K_Normal"
BRICK_BASE = "/Game/Maps/Sunscar/Art/Heritage/Surfaces/RuinWallBrick03/xboibiu_4K_Basecolor"
BRICK_NORMAL = "/Game/Maps/Sunscar/Art/Heritage/Surfaces/RuinWallBrick03/xboibiu_4K_Normal"

ARCH_PATH = "/Game/Maps/Sunscar/Art/Heritage/Architecture/ArchStoneCarved08/Historic_Desert_Ruin_Arch_Stone_Carved_08_xbkobbd_High"
WALL_SCAN_PATH = "/Game/Maps/Sunscar/Art/Heritage/Architecture/WallModularSet04/Historic_Desert_Ruin_Wall_Modular_Set_04_yjxsbaqyx_High"
STONE_PATH = "/Game/Maps/Sunscar/Art/Heritage/Architecture/StructureStoneS06/Historic_Desert_Ruin_Structure_Stone_S_06_xblnbfv_High"


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_COMPOSITION_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_COMPOSITION_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_COMPOSITION_DIRTY_BEFORE " + repr(dirty_packages()))

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = list(actor_subsystem.get_all_level_actors())
landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
if len(landscapes) < 3:
    raise RuntimeError("ABIVERD_COMPOSITION_REGION_NOT_LOADED landscapes=%d" % len(landscapes))
if any(PASS_TAG in list(actor.tags) for actor in actors):
    raise RuntimeError("ABIVERD_COMPOSITION_DUPLICATE_TAG")
non_landscapes = [actor for actor in actors if actor not in landscapes]


def load_mesh(path):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        raise RuntimeError("ABIVERD_COMPOSITION_MISSING_MESH " + path)
    return asset


def load_asset(path):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset is None:
        raise RuntimeError("ABIVERD_COMPOSITION_MISSING_ASSET " + path)
    return asset


cube_mesh = load_mesh(CUBE_PATH)
sphere_mesh = load_mesh(SPHERE_PATH)
cylinder_mesh = load_mesh(CYLINDER_PATH)
arch_mesh = load_mesh(ARCH_PATH)
wall_scan_mesh = load_mesh(WALL_SCAN_PATH)
stone_mesh = load_mesh(STONE_PATH)
master = load_asset(MASTER_PATH)
mud_base = load_asset(MUD_BASE)
mud_normal = load_asset(MUD_NORMAL)
brick_base = load_asset(BRICK_BASE)
brick_normal = load_asset(BRICK_NORMAL)


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        non_landscapes,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return None
    data = hit.to_dict()
    if not data.get("blocking_hit") or data.get("location") is None:
        return None
    return float(data["location"].z)


def core(label, site, x, y, yaw, length, thickness, height, material_key="mud", visible=True):
    return {
        "kind": "core",
        "label": label,
        "site": site,
        "mesh": CUBE_PATH,
        "x": x,
        "y": y,
        "yaw": yaw,
        "dimensions_cm": [length, thickness, height],
        "scale": [length / 100.0, thickness / 100.0, height / 100.0],
        "material_key": material_key,
        "collision": "QueryAndPhysics",
        "visible": visible,
    }


def scan(label, site, mesh_path, x, y, yaw, scale=1.0):
    return {
        "kind": "scan",
        "label": label,
        "site": site,
        "mesh": mesh_path,
        "x": x,
        "y": y,
        "yaw": yaw,
        "scale": [scale, scale, scale],
        "material_key": "source",
        "collision": "NoCollision",
        "visible": True,
    }


placements = []

# SS_021: mosque shell shifted 6 m east from the initial planning center so
# the west wall clears the preserved north arterial by roughly 2 m.
placements.extend(
    [
        core("ABV_SS021_SouthWall_Left", "SS_021", 1062.5, 15700.0, 0.0, 725.0, 60.0, 450.0),
        core("ABV_SS021_SouthWall_Right", "SS_021", 2137.5, 15700.0, 0.0, 725.0, 60.0, 450.0),
        core("ABV_SS021_WestWall_South", "SS_021", 700.0, 16100.0, 90.0, 740.0, 60.0, 450.0),
        core("ABV_SS021_WestWall_North", "SS_021", 700.0, 16850.0, 90.0, 650.0, 60.0, 390.0, "brick"),
        core("ABV_SS021_EastWall_South", "SS_021", 2500.0, 16050.0, 90.0, 640.0, 60.0, 450.0),
        core("ABV_SS021_EastWall_North", "SS_021", 2500.0, 16850.0, 90.0, 650.0, 60.0, 360.0, "brick"),
        core("ABV_SS021_NorthWall_West", "SS_021", 1000.0, 17300.0, 0.0, 600.0, 60.0, 320.0, "brick"),
        core("ABV_SS021_NorthWall_East", "SS_021", 2200.0, 17300.0, 0.0, 600.0, 60.0, 240.0),
        core("ABV_SS021_Roof_South", "SS_021", 1600.0, 16100.0, 0.0, 1680.0, 650.0, 30.0),
        core("ABV_SS021_Roof_North", "SS_021", 1600.0, 16900.0, 0.0, 1680.0, 500.0, 30.0, "brick"),
        scan("ABV_SS021_Portal", "SS_021", ARCH_PATH, 1600.0, 15665.0, 0.0, 1.0),
    ]
)

# The dome uses simple opaque primitives because they are cheaper than Nanite
# at this triangle count. The imported 4K mud texture remains world aligned.
placements.append(
    {
        "kind": "dome_drum",
        "label": "ABV_SS021_Dome_Drum",
        "site": "SS_021",
        "mesh": CYLINDER_PATH,
        "x": 1600.0,
        "y": 16600.0,
        "yaw": 0.0,
        "dimensions_cm": [600.0, 600.0, 300.0],
        "scale": [6.0, 6.0, 3.0],
        "material_key": "mud",
        "collision": "NoCollision",
        "visible": True,
        "base_offset_cm": 390.0,
    }
)
placements.append(
    {
        "kind": "dome",
        "label": "ABV_SS021_Dome",
        "site": "SS_021",
        "mesh": SPHERE_PATH,
        "x": 1600.0,
        "y": 16600.0,
        "yaw": 0.0,
        "dimensions_cm": [600.0, 600.0, 600.0],
        "scale": [6.0, 6.0, 6.0],
        "material_key": "mud",
        "collision": "NoCollision",
        "visible": True,
        "base_offset_cm": 390.0,
    }
)

# Terrain-cover walls on both sides of the central north route.
hard_walls = [
    ("E01", 3300.0, 18150.0, 24.0, 560.0, 210.0),
    ("E02", 5250.0, 18700.0, 104.0, 460.0, 190.0),
    ("E03", 3000.0, 19850.0, 88.0, 380.0, 175.0),
    ("E04", 5100.0, 20700.0, 16.0, 600.0, 220.0),
    ("W01", -3500.0, 16950.0, 158.0, 520.0, 205.0),
    ("W02", -5450.0, 18150.0, 82.0, 450.0, 185.0),
    ("W03", -3350.0, 19600.0, 8.0, 600.0, 220.0),
    ("W04", -5250.0, 20700.0, 126.0, 520.0, 205.0),
]
for index, (suffix, x, y, yaw, length, height) in enumerate(hard_walls):
    placements.append(
        core(
            "ABV_SS022_HardWall_" + suffix,
            "SS_022",
            x,
            y,
            yaw,
            length,
            55.0,
            height,
            "brick" if index % 3 == 1 else "mud",
        )
    )
    placements.append(
        scan(
            "ABV_SS022_FoundationDress_" + suffix,
            "SS_022",
            WALL_SCAN_PATH,
            x + math.cos(math.radians(yaw + 90.0)) * 75.0,
            y + math.sin(math.radians(yaw + 90.0)) * 75.0,
            yaw + 12.0,
            0.9 + (index % 3) * 0.05,
        )
    )

# Low archaeological remnants. Each visual scan receives a slightly smaller,
# invisible simple collision core so crouched-cover behavior is dependable.
low_foundations = [
    ("L01", -4700.0, 15100.0, 12.0, 1.00),
    ("L02", -2750.0, 18100.0, 72.0, 0.92),
    ("L03", -5850.0, 19500.0, 146.0, 1.05),
    ("L04", -2850.0, 21100.0, 28.0, 0.90),
    ("L05", 3650.0, 15100.0, 178.0, 0.95),
    ("L06", 5000.0, 16800.0, 42.0, 1.05),
    ("L07", 2150.0, 19000.0, 116.0, 0.90),
    ("L08", 5900.0, 19800.0, 8.0, 1.00),
    ("L09", 3800.0, 21400.0, 84.0, 0.95),
    ("L10", -4300.0, 22600.0, 174.0, 1.05),
]
for suffix, x, y, yaw, scale in low_foundations:
    placements.append(scan("ABV_SS022_RuinScan_" + suffix, "SS_022", WALL_SCAN_PATH, x, y, yaw, scale))
    placements.append(
        core(
            "ABV_SS022_RuinCollision_" + suffix,
            "SS_022",
            x,
            y,
            yaw,
            260.0 * scale,
            245.0 * scale,
            52.0 * scale,
            "mud",
            False,
        )
    )

# Broken northern fortification with a 28 m central route gap.
fortification = [
    ("WOuter", -5000.0, 22150.0, 4.0, 1450.0, 215.0),
    ("WInner", -2500.0, 22050.0, -8.0, 900.0, 180.0),
    ("EInner", 2500.0, 22050.0, 8.0, 900.0, 190.0),
    ("EOuter", 5000.0, 22150.0, -4.0, 1450.0, 220.0),
]
for suffix, x, y, yaw, length, height in fortification:
    placements.append(core("ABV_SS024_Fortification_" + suffix, "SS_024", x, y, yaw, length, 70.0, height))

# S06 is physically a low stone element, so it is used only as debris/capping.
stone_points = [
    (-5050.0, 15750.0, 14.0), (-4200.0, 17550.0, 82.0),
    (-5850.0, 18750.0, 141.0), (-4200.0, 20250.0, 32.0),
    (-2950.0, 22500.0, 96.0), (3350.0, 15750.0, 176.0),
    (4650.0, 17500.0, 44.0), (5700.0, 19100.0, 11.0),
    (4050.0, 20450.0, 119.0), (5500.0, 22600.0, 6.0),
    (2950.0, 17350.0, 20.0), (2350.0, 17150.0, 165.0),
]
for index, (x, y, yaw) in enumerate(stone_points, 1):
    placements.append(scan("ABV_StoneDebris_%02d" % index, "SS_022", STONE_PATH, x, y, yaw, 0.9 + (index % 4) * 0.06))

terrain_failures = []
for item in placements:
    ground = terrain_z(item["x"], item["y"])
    if ground is None:
        terrain_failures.append(item["label"])
        continue
    item["terrain_z_cm"] = round(ground, 3)
if terrain_failures:
    raise RuntimeError("ABIVERD_COMPOSITION_TERRAIN_TRACE_FAILED " + "|".join(terrain_failures))

# Enforce the preserved central north route and confirmed defender insertion.
route_violations = []
for item in placements:
    if item["site"] in ("SS_022", "SS_024") and -1900.0 < item["x"] < 900.0:
        route_violations.append(item["label"])
if route_violations:
    raise RuntimeError("ABIVERD_COMPOSITION_ROUTE_VIOLATION " + "|".join(route_violations))
for item in placements:
    if math.hypot(item["x"] - 11400.0, item["y"] - 10400.0) < 2000.0:
        raise RuntimeError("ABIVERD_COMPOSITION_SPAWN_CLEARANCE_VIOLATION " + item["label"])


def make_material_instance(path, base_texture, normal_texture, size_cm, roughness):
    existing = unreal.EditorAssetLibrary.load_asset(path)
    if existing is not None:
        return existing
    name = path.rsplit("/", 1)[1]
    instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name,
        MATERIAL_FOLDER,
        unreal.MaterialInstanceConstant,
        unreal.MaterialInstanceConstantFactoryNew(),
    )
    if instance is None:
        raise RuntimeError("ABIVERD_COMPOSITION_MI_CREATE_FAILED " + path)
    instance.set_editor_property("parent", master)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
        instance, "BaseColorTexture", base_texture
    )
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
        instance, "NormalTexture", normal_texture
    )
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
        instance,
        "TextureSizeCm",
        unreal.LinearColor(r=size_cm, g=size_cm, b=size_cm, a=1.0),
    )
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
        instance, "Roughness", roughness
    )
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
        instance, "Specular", 0.18
    )
    unreal.MaterialEditingLibrary.update_material_instance(instance)
    return instance


created = []
created_packages = []
if APPLY_CHANGES:
    unreal.EditorAssetLibrary.make_directory(MATERIAL_FOLDER)
    mud_material = make_material_instance(MUD_MI_PATH, mud_base, mud_normal, 180.0, 0.90)
    brick_material = make_material_instance(BRICK_MI_PATH, brick_base, brick_normal, 160.0, 0.88)
    mesh_by_path = {
        CUBE_PATH: cube_mesh,
        SPHERE_PATH: sphere_mesh,
        CYLINDER_PATH: cylinder_mesh,
        ARCH_PATH: arch_mesh,
        WALL_SCAN_PATH: wall_scan_mesh,
        STONE_PATH: stone_mesh,
    }
    material_by_key = {"mud": mud_material, "brick": brick_material}
    for item in placements:
        mesh = mesh_by_path[item["mesh"]]
        scale = unreal.Vector(*item["scale"])
        ground = item["terrain_z_cm"]
        bounds = mesh.get_bounds()
        if "base_offset_cm" in item:
            z_value = ground + float(item["base_offset_cm"]) - (
                (bounds.origin.z - bounds.box_extent.z) * scale.z
            )
        else:
            local_bottom = (bounds.origin.z - bounds.box_extent.z) * scale.z
            z_value = ground - local_bottom
        actor = actor_subsystem.spawn_actor_from_object(
            mesh,
            unreal.Vector(item["x"], item["y"], z_value),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=item["yaw"]),
            transient=False,
        )
        if actor is None:
            raise RuntimeError("ABIVERD_COMPOSITION_SPAWN_FAILED " + item["label"])
        actor.set_actor_scale3d(scale)
        actor.set_actor_label(item["label"])
        actor.set_folder_path(unreal.Name(FOLDER_ROOT + "/" + item["site"]))
        actor.tags = [PASS_TAG, unreal.Name(item["site"]), unreal.Name("AbiverdHeritageV1")]
        component = actor.static_mesh_component
        if item["material_key"] in material_by_key:
            component.set_material(0, material_by_key[item["material_key"]])
        component.set_collision_enabled(
            unreal.CollisionEnabled.QUERY_AND_PHYSICS
            if item["collision"] == "QueryAndPhysics"
            else unreal.CollisionEnabled.NO_COLLISION
        )
        if not item["visible"]:
            component.set_visibility(False, True)
        created.append(item["label"])
        created_packages.append(package_name(actor.get_package()))

dirty_after = dirty_packages()
expected_new_materials = []
if APPLY_CHANGES:
    expected_new_materials = [MUD_MI_PATH, BRICK_MI_PATH]
    expected_scope = set(created_packages) | set(expected_new_materials)
    unexpected = sorted(
        name for name in dirty_after
        if name not in expected_scope
        and not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")
    )
    if unexpected:
        raise RuntimeError("ABIVERD_COMPOSITION_UNEXPECTED_DIRTY " + "|".join(unexpected))

payload = {
    "schema_version": 1,
    "status": "unsaved_composition_ready" if APPLY_CHANGES else "dry_run_complete",
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "apply_changes": APPLY_CHANGES,
    "placement_count": len(placements),
    "counts_by_kind": {
        kind: sum(1 for item in placements if item["kind"] == kind)
        for kind in sorted({item["kind"] for item in placements})
    },
    "counts_by_site": {
        site: sum(1 for item in placements if item["site"] == site)
        for site in sorted({item["site"] for item in placements})
    },
    "mosque_center_adjustment": {
        "planned_center_m": [10.0, 165.0],
        "validated_center_m": [16.0, 165.0],
        "reason": "clear preserved central north arterial and town-spine route",
    },
    "route_clearance_cm": {"min_x": -1900.0, "max_x": 900.0},
    "defender_spawn_reference_cm": [11400.0, 10400.0],
    "materials": [MUD_MI_PATH, BRICK_MI_PATH],
    "placements": placements,
    "created_actor_labels": created,
    "created_actor_packages": sorted(set(created_packages)),
    "dirty_packages_after": dirty_after,
    "changes_saved": False,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_COMPOSITION mode=%s placements=%d created=%d report=%s"
    % ("APPLY" if APPLY_CHANGES else "DRY_RUN", len(placements), len(created), report_path)
)
print("ABIVERD_COMPOSITION", len(placements), len(created), report_path)
