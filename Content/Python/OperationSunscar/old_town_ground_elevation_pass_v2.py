import math
import unreal


LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TAG = "SunscarGroundElevationPassV2"
ROOT = "OldTown_GroundElevationPassV2"
CM = 100.0

CUBE_PATH = "/Game/LevelPrototyping/Meshes/SM_Cube"
GROUND_MATERIAL_ROOT = "/Game/Maps/Sunscar/Art/Materials/Ground"
QUIXEL_ASPHALT_PATH = (
    "/Game/Fab/Megascans/Surfaces/Crushed_Asphalt_Ground_sjyjcbja/"
    "Medium/sjyjcbja_tier_2/Materials/MI_sjyjcbja"
)

SITES = {
    "SS_002": (-126.0, -19.0, 7.0, 24.0),
    "SS_003": (-106.0, -63.0, 18.0, 15.0),
    "SS_004": (-88.0, -29.0, 18.0, 16.0),
    "SS_005": (-56.0, -1.0, 24.0, 19.0),
    "SS_006": (-62.0, 45.0, 16.0, 16.0),
    "SS_007": (-14.0, 27.0, 28.0, 22.0),
    "SS_008": (-18.0, -31.0, 34.0, 28.0),
    "SS_009": (6.0, -5.0, 32.0, 26.0),
    "SS_010": (22.0, 91.0, 34.0, 28.0),
    "SS_011": (74.0, 51.0, 20.0, 17.0),
    "SS_012": (118.0, 49.0, 21.0, 18.0),
    "SS_013": (108.0, 1.0, 30.0, 24.0),
    "SS_014": (74.0, -17.0, 44.0, 35.0),
    "SS_015": (128.0, -47.0, 24.0, 20.0),
    "SS_016": (60.0, -70.0, 26.0, 20.0),
    "SS_017": (28.0, -93.0, 36.0, 17.0),
    "SS_018": (-56.0, -91.0, 21.0, 18.0),
}

# Primary vehicle-readable routes. Each long segment is subdivided so the
# visual surface follows the macro terrain rather than floating as one slab.
ROAD_PATHS = {
    "SouthRoute": [
        (-142.0, -108.0),
        (-82.0, -108.0),
        (-22.0, -104.0),
        (40.0, -107.0),
        (100.0, -109.0),
        (142.0, -103.0),
    ],
    "MarketRoute": [
        (-136.0, -58.0),
        (-82.0, -51.0),
        (-28.0, -44.0),
        (20.0, -46.0),
        (72.0, -43.0),
        (138.0, -43.0),
    ],
    "NorthRoute": [
        (-92.0, 61.0),
        (-34.0, 70.0),
        (24.0, 78.0),
        (82.0, 71.0),
        (138.0, 62.0),
    ],
    "ClinicConnector": [(-58.0, -103.0), (-57.0, -50.0), (-56.0, -4.0), (-60.0, 48.0)],
    "CourtyardConnector": [(10.0, -105.0), (8.0, -48.0), (4.0, -4.0), (12.0, 76.0)],
    "FreightConnector": [(110.0, -106.0), (112.0, -44.0), (110.0, 2.0), (116.0, 62.0)],
}

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

if level.get_current_level().get_outermost().get_name() != LEVEL:
    raise RuntimeError("Wrong level")

cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
materials = {
    name: unreal.EditorAssetLibrary.load_asset(
        GROUND_MATERIAL_ROOT + "/MI_OT_Ground_" + name
    )
    for name in ("Asphalt", "Silt", "Stone")
}
quixel_asphalt = unreal.EditorAssetLibrary.load_asset(QUIXEL_ASPHALT_PATH)
if quixel_asphalt:
    materials["Asphalt"] = quixel_asphalt
if not cube or any(material is None for material in materials.values()):
    raise RuntimeError("Missing ground-pass source assets")

all_actors = list(actors_subsystem.get_all_level_actors())
for actor in list(all_actors):
    if any(str(tag) == TAG for tag in actor.tags):
        actors_subsystem.destroy_actor(actor)
all_actors = list(actors_subsystem.get_all_level_actors())

world = editor.get_editor_world()
cube_size = cube.get_bounds().box_extent * 2.0
created = []

# Trace only against Landscape. This keeps roads and skirts from recursively
# snapping to earlier visual overlays or prototype architecture.
landscape_ignore = [
    actor for actor in all_actors if "Landscape" not in actor.get_class().get_name()
]


def landscape_z(x_m, y_m):
    result = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x_m * CM, y_m * CM, 45000.0),
        unreal.Vector(x_m * CM, y_m * CM, 30000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        landscape_ignore,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    data = result.to_dict()
    return data["location"].z if data["blocking_hit"] else None


def spawn_box(
    label,
    folder,
    location,
    dimensions_m,
    material,
    yaw=0.0,
    collision=unreal.CollisionEnabled.NO_COLLISION,
    extra_tags=(),
):
    actor = actors_subsystem.spawn_actor_from_object(
        cube,
        unreal.Vector(location[0], location[1], location[2]),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw),
        transient=False,
    )
    actor.set_actor_scale3d(
        unreal.Vector(
            dimensions_m[0] * CM / cube_size.x,
            dimensions_m[1] * CM / cube_size.y,
            dimensions_m[2] * CM / cube_size.z,
        )
    )
    actor.set_actor_label(label)
    actor.tags = [
        unreal.Name(TAG),
        unreal.Name("SunscarMapOwned"),
        *[unreal.Name(value) for value in extra_tags],
    ]
    actor.set_folder_path(unreal.Name(ROOT + "/" + folder))
    actor.static_mesh_component.set_material(0, material)
    actor.static_mesh_component.set_collision_enabled(collision)
    created.append(actor)
    return actor


def add_surface_segment(path_name, index, start, end, width_m, material_name, offset_m=0.0):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length < 0.1:
        return
    yaw = math.degrees(math.atan2(dy, dx))
    nx = -dy / length
    ny = dx / length
    subdivisions = max(1, int(math.ceil(length / 10.0)))
    for tile_index in range(subdivisions):
        t0 = tile_index / subdivisions
        t1 = (tile_index + 1) / subdivisions
        tm = (t0 + t1) * 0.5
        x = start[0] + dx * tm + nx * offset_m
        y = start[1] + dy * tm + ny * offset_m
        z = landscape_z(x, y)
        if z is None:
            continue
        tile_length = length / subdivisions + 0.20
        spawn_box(
            "%s_%02d_%02d" % (path_name, index, tile_index + 1),
            "Roads/" + path_name,
            (x * CM, y * CM, z + 1.25),
            (tile_length, width_m, 0.025),
            materials[material_name],
            yaw,
            unreal.CollisionEnabled.NO_COLLISION,
            ("VisualGroundOverlay", material_name),
        )


# Build connected road surfaces and narrow dry drainage strips along selected
# edges. They remain visual-only until final Landscape layers and splines land.
for path_name, points in ROAD_PATHS.items():
    for index in range(len(points) - 1):
        add_surface_segment(
            path_name,
            index + 1,
            points[index],
            points[index + 1],
            5.5,
            "Asphalt",
        )
        if path_name in ("MarketRoute", "ClinicConnector", "FreightConnector"):
            add_surface_segment(
                path_name + "_Drain",
                index + 1,
                points[index],
                points[index + 1],
                0.60,
                "Silt",
                offset_m=3.05,
            )


def find_primary_site_actor(site_id):
    candidates = []
    for actor in all_actors:
        if not actor.get_actor_label().startswith(site_id + "_"):
            continue
        tags = {str(tag) for tag in actor.tags}
        if (
            "SunscarOldTownArtDraftV1" in tags
            or "SunscarQuixelSandbagPassV1" in tags
            or "SunscarQuixelDefensivePassV1" in tags
        ):
            continue
        origin, extent = actor.get_actor_bounds(False)
        candidates.append((extent.x * extent.y * extent.z, actor, origin, extent))
    return max(candidates, key=lambda item: item[0]) if candidates else None


# Thin perimeter skirts bridge any visible daylight between the primary
# architecture datum and the sloped Landscape. They are visual-only so they do
# not alter movement routes or create invisible collision ledges.
foundation_count = 0
for site_id, (_, _, fallback_width, fallback_depth) in SITES.items():
    candidate = find_primary_site_actor(site_id)
    if candidate is None or site_id == "SS_010":
        continue
    _, actor, origin, extent = candidate
    top = origin.z - extent.z + 2.0
    width_m = min(fallback_width, max(2.0, extent.x * 2.0 / CM))
    depth_m = min(fallback_depth, max(2.0, extent.y * 2.0 / CM))
    center_x_m = origin.x / CM
    center_y_m = origin.y / CM
    sides = (
        ("North", center_x_m, center_y_m + depth_m * 0.5, width_m, 0.35),
        ("South", center_x_m, center_y_m - depth_m * 0.5, width_m, 0.35),
        ("East", center_x_m + width_m * 0.5, center_y_m, 0.35, depth_m),
        ("West", center_x_m - width_m * 0.5, center_y_m, 0.35, depth_m),
    )
    for side, x_m, y_m, side_width, side_depth in sides:
        terrain = landscape_z(x_m, y_m)
        if terrain is None or terrain >= top - 6.0:
            continue
        bottom = max(terrain - 8.0, top - 120.0)
        height_m = (top - bottom) / CM
        spawn_box(
            "Foundation_%s_%s" % (site_id, side),
            "Foundations/" + site_id,
            (x_m * CM, y_m * CM, (top + bottom) * 0.5),
            (side_width + 0.25, side_depth + 0.25, height_m),
            materials["Stone"],
            0.0,
            unreal.CollisionEnabled.NO_COLLISION,
            (site_id, "FoundationSkirt"),
        )
        foundation_count += 1


# The Detention Annex intentionally occupies a raised terrace. Four shallow,
# colliding steps make the south approach readable and traversable.
detention = find_primary_site_actor("SS_010")
step_count = 0
if detention is not None:
    _, actor, origin, extent = detention
    terrace_top = origin.z - extent.z + 2.0
    entry_x_m = origin.x / CM
    entry_y_m = origin.y / CM - min(14.0, extent.y / CM) - 0.9
    terrain = landscape_z(entry_x_m, entry_y_m - 1.0)
    if terrain is not None:
        rise = max(20.0, terrace_top - terrain)
        steps = max(3, min(6, int(math.ceil(rise / 18.0))))
        step_height = rise / steps
        for index in range(steps):
            height = step_height * (index + 1)
            y_m = entry_y_m + index * 0.45
            spawn_box(
                "Detention_SouthStep_%02d" % (index + 1),
                "Access/SS_010",
                (
                    entry_x_m * CM,
                    y_m * CM,
                    terrain + height * 0.5,
                ),
                (4.2, 0.55, height / CM),
                materials["Stone"],
                0.0,
                unreal.CollisionEnabled.QUERY_AND_PHYSICS,
                ("SS_010", "TraversalStep"),
            )
            step_count += 1

level.save_current_level()
unreal.log(
    "SUNSCAR_GROUND_ELEVATION_V2 actors=%d foundations=%d steps=%d"
    % (len(created), foundation_count, step_count)
)
print(
    "SUNSCAR_GROUND_ELEVATION_V2",
    len(created),
    foundation_count,
    step_count,
)
