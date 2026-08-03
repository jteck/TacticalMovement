import unreal


LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TAG = "SunscarQuixelGroundPassV1"
ROOT = "OldTown_QuixelPass/GroundV1"
CM = 100.0

ASPHALT_MATERIAL_PATH = (
    "/Game/Fab/Megascans/Surfaces/Crushed_Asphalt_Ground_sjyjcbja/"
    "Medium/sjyjcbja_tier_2/Materials/MI_sjyjcbja"
)
SANDSTONE_MESH_PATH = (
    "/Game/Fab/Megascans/3D/Sandstone_Rocky_Ground_vmjjfiv/"
    "Medium/vmjjfiv_tier_2/StaticMeshes/vmjjfiv_tier_2"
)
TRENCH_PATCH_MESH_PATH = (
    "/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_04_yd0lfcq/"
    "Medium/SM_yd0lfcq_tier_2/StaticMeshes/SM_yd0lfcq_tier_2"
)

EXPECTED_DIRTY_PREFIXES = (
    "/Game/Fab/Megascans/Surfaces/Crushed_Asphalt_Ground_sjyjcbja/",
    "/Game/Fab/Megascans/3D/Sandstone_Rocky_Ground_vmjjfiv/",
    "/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_04_yd0lfcq/",
)

# Deliberately sparse placements at district edges and broad dead-ground
# pockets. These meshes are visual-only; cover and traversal remain governed
# by the tested graybox.
PLACEMENTS = (
    ("Sandstone", "WestApproach_A", -137.0, -76.0, 0.78, 18.0),
    ("Sandstone", "WestApproach_B", -121.0, 18.0, 0.62, 96.0),
    ("Sandstone", "NorthWest_A", -82.0, 69.0, 0.90, 205.0),
    ("Sandstone", "NorthEdge_A", -29.0, 88.0, 0.70, 12.0),
    ("Sandstone", "NorthEast_A", 75.0, 88.0, 0.86, 142.0),
    ("Sandstone", "EastApproach_A", 141.0, 28.0, 0.72, 271.0),
    ("Sandstone", "SouthEast_A", 142.0, -84.0, 0.82, 331.0),
    ("Sandstone", "SouthWest_A", -102.0, -118.0, 0.66, 44.0),
    ("TrenchPatch", "MarketDeadGround_A", -38.0, -55.0, 1.10, 15.0),
    ("TrenchPatch", "MarketDeadGround_B", 41.0, -55.0, 0.92, 188.0),
    ("TrenchPatch", "CourtyardEdge_A", -39.0, -17.0, 0.82, 72.0),
    ("TrenchPatch", "FreightEdge_A", 95.0, -18.0, 1.05, 247.0),
    ("TrenchPatch", "ClinicEdge_A", -77.0, 3.0, 0.80, 316.0),
    ("TrenchPatch", "HotelEdge_A", 2.0, 47.0, 0.88, 138.0),
    ("TrenchPatch", "CheckpointEdge_A", 90.0, 61.0, 0.76, 29.0),
    ("TrenchPatch", "BazaarEdge_A", 3.0, -93.0, 0.98, 202.0),
)

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if level.get_current_level().get_outermost().get_name() != LEVEL:
    raise RuntimeError("Wrong level")

asphalt = unreal.EditorAssetLibrary.load_asset(ASPHALT_MATERIAL_PATH)
sandstone = unreal.EditorAssetLibrary.load_asset(SANDSTONE_MESH_PATH)
trench_patch = unreal.EditorAssetLibrary.load_asset(TRENCH_PATCH_MESH_PATH)
if not asphalt or not sandstone or not trench_patch:
    raise RuntimeError("Missing imported Quixel ground assets")

# Save only packages imported in this approved ground batch. Stop if another
# content package is dirty so the pass never turns into an accidental Save All.
dirty_content = unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
unexpected_dirty = []
saved_imports = 0
for package in dirty_content:
    package_name = package.get_name()
    if package_name.startswith(EXPECTED_DIRTY_PREFIXES):
        if unreal.EditorAssetLibrary.save_asset(
            package_name, only_if_is_dirty=True
        ):
            saved_imports += 1
    else:
        unexpected_dirty.append(package_name)
if unexpected_dirty:
    raise RuntimeError("Unexpected dirty content: " + repr(unexpected_dirty))

for mesh in (sandstone, trench_patch):
    try:
        settings = mesh.get_editor_property("nanite_settings")
        settings.enabled = True
        mesh.set_editor_property("nanite_settings", settings)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    except Exception as exc:
        unreal.log_warning("SUNSCAR_QX_GROUND_NANITE " + str(exc))

all_actors = list(actors_subsystem.get_all_level_actors())
for actor in list(all_actors):
    if any(str(tag) == TAG for tag in actor.tags):
        actors_subsystem.destroy_actor(actor)
all_actors = list(actors_subsystem.get_all_level_actors())

# Replace every current asphalt overlay while preserving its actor, transform,
# tags, collision and World Partition identity.
asphalt_applied = 0
for actor in all_actors:
    tags = {str(tag) for tag in actor.tags}
    if "Asphalt" not in tags and not actor.get_actor_label().startswith(
        "Ground_Asphalt_"
    ):
        continue
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        continue
    component.set_material(0, asphalt)
    if not any(str(tag) == "QuixelAsphaltApplied" for tag in actor.tags):
        actor.tags = list(actor.tags) + [
            unreal.Name("QuixelAsphaltApplied"),
            unreal.Name("QuixelMegascans"),
        ]
    asphalt_applied += 1

world = editor.get_editor_world()
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


meshes = {"Sandstone": sandstone, "TrenchPatch": trench_patch}
created = []
for asset_type, name, x_m, y_m, scale, yaw in PLACEMENTS:
    mesh = meshes[asset_type]
    terrain = landscape_z(x_m, y_m)
    if terrain is None:
        continue
    bounds = mesh.get_bounds()
    bottom_local = bounds.origin.z - bounds.box_extent.z
    location_z = terrain + 1.0 - bottom_local * scale
    actor = actors_subsystem.spawn_actor_from_object(
        mesh,
        unreal.Vector(x_m * CM, y_m * CM, location_z),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw),
        transient=False,
    )
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    actor.set_actor_label("QX_Ground_%s_%s" % (asset_type, name))
    actor.tags = [
        unreal.Name(TAG),
        unreal.Name("SunscarMapOwned"),
        unreal.Name("QuixelMegascans"),
        unreal.Name("NoCollision"),
        unreal.Name(asset_type),
    ]
    actor.set_folder_path(unreal.Name(ROOT + "/" + asset_type))
    actor.static_mesh_component.set_collision_enabled(
        unreal.CollisionEnabled.NO_COLLISION
    )
    created.append(actor)

level.save_current_level()
unreal.log(
    "SUNSCAR_QX_GROUND imports_saved=%d asphalt=%d patches=%d"
    % (saved_imports, asphalt_applied, len(created))
)
print(
    "SUNSCAR_QX_GROUND",
    saved_imports,
    asphalt_applied,
    len(created),
)
