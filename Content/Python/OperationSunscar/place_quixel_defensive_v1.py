import unreal

LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TAG = "SunscarQuixelDefensivePassV1"
ROOT = "OldTown_QuixelPass/DefensiveV1"
CM = 100.0
SQUARE_PATH = "/Game/Maps/Sunscar/Art/Quixel/SandbagsSquare/SM_ydznbff_tier_2/StaticMeshes/SM_ydznbff_tier_2"
CORR_PATH = "/Game/Maps/Sunscar/Art/Quixel/CorrugatedBarrier/SM_ydxnbdns_tier_2/StaticMeshes/SM_ydxnbdns_tier_2"
CUBE_PATH = "/Game/LevelPrototyping/Meshes/SM_Cube"
STONE_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Stone"

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if level.get_current_level().get_outermost().get_name() != LEVEL:
    raise RuntimeError("Wrong level")

square = unreal.EditorAssetLibrary.load_asset(SQUARE_PATH)
corr = unreal.EditorAssetLibrary.load_asset(CORR_PATH)
cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
stone = unreal.EditorAssetLibrary.load_asset(STONE_PATH)
if not square or not corr or not cube or not stone:
    raise RuntimeError("Missing defensive pass asset")

for mesh in (square, corr):
    try:
        ns = mesh.get_editor_property("nanite_settings")
        ns.enabled = True
        mesh.set_editor_property("nanite_settings", ns)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    except Exception as exc:
        unreal.log_warning("SUNSCAR_DEF_NANITE " + str(exc))

for actor in list(actors.get_all_level_actors()):
    if any(str(t) == TAG for t in actor.tags):
        actors.destroy_actor(actor)

specs = {
    "SS_010": ("DetentionAnnex", 6.4),
    "SS_011": ("CheckpointOffice", 6.4),
    "SS_014": ("SalvageYard", 2.4),
    "SS_017": ("CoveredBazaar", 3.4),
    "SS_020": ("NorthDefender", 0.2),
}
all_actors = actors.get_all_level_actors()
sites = {}
for sid, (folder, height) in specs.items():
    marker = next((a for a in all_actors if a.get_actor_label().startswith(sid + "_")), None)
    if not marker:
        raise RuntimeError("Missing marker " + sid)
    sites[sid] = {"folder": folder, "base": marker.get_actor_location().z - height * 50.0}

cube_size = cube.get_bounds().box_extent * 2.0
created = []

def mesh_ground_z(mesh, base):
    b = mesh.get_bounds()
    return base - (b.origin.z - b.box_extent.z)

def add_render(mesh, sid, name, x, y, yaw):
    actor = actors.spawn_actor_from_object(
        mesh,
        unreal.Vector(x * CM, y * CM, mesh_ground_z(mesh, sites[sid]["base"])),
        unreal.Rotator(0.0, yaw, 0.0),
        transient=False,
    )
    actor.set_actor_label(name)
    actor.tags = [unreal.Name(TAG), unreal.Name(sid), unreal.Name("SunscarMapOwned"), unreal.Name("QuixelMegascans")]
    actor.set_folder_path(unreal.Name(ROOT + "/" + sites[sid]["folder"]))
    actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    created.append(actor)
    return actor

def add_proxy(sid, name, x, y, yaw, dims):
    proxy = actors.spawn_actor_from_object(
        cube,
        unreal.Vector(x * CM, y * CM, sites[sid]["base"] + dims[2] * 50.0),
        unreal.Rotator(0.0, yaw, 0.0),
        transient=False,
    )
    proxy.set_actor_label(name)
    proxy.tags = [unreal.Name(TAG), unreal.Name(sid), unreal.Name("SunscarMapOwned"), unreal.Name("SimpleCollisionProxy")]
    proxy.set_folder_path(unreal.Name(ROOT + "/" + sites[sid]["folder"] + "/Collision"))
    proxy.set_actor_scale3d(unreal.Vector(dims[0] * CM / cube_size.x, dims[1] * CM / cube_size.y, dims[2] * CM / cube_size.z))
    proxy.static_mesh_component.set_visibility(False)
    proxy.static_mesh_component.set_hidden_in_game(True)
    proxy.static_mesh_component.set_collision_profile_name("BlockAll")
    created.append(proxy)

square_places = [
    ("SS_010", "QX_Square_Detention_West_End", 6.4, 74.9, 0.0),
    ("SS_010", "QX_Square_Detention_East_End", 37.6, 74.9, 180.0),
    ("SS_011", "QX_Square_Checkpoint_West_End", 61.4, 42.0, 0.0),
    ("SS_011", "QX_Square_Checkpoint_Gate_End", 68.6, 42.0, 180.0),
    ("SS_020", "QX_Square_North_West_End", 107.0, 90.5, 0.0),
    ("SS_020", "QX_Square_North_East_End", 129.0, 90.5, 180.0),
]
for sid, name, x, y, yaw in square_places:
    add_render(square, sid, name, x, y, yaw)
    add_proxy(sid, "COL_" + name, x, y, yaw, (1.60, 0.95, 0.52))

corr_bounds = corr.get_bounds().box_extent * 2.0
dominant_x = corr_bounds.x >= corr_bounds.y
yaw_along_x = 0.0 if dominant_x else 90.0
yaw_along_y = 90.0 if dominant_x else 0.0

# Salvage south edge: intermittent patched panels over the existing readable perimeter.
for idx, x in enumerate((56.0, 61.0, 66.0, 71.0, 77.0, 82.0, 87.0, 92.0), 1):
    sid = "SS_014"
    base = actors.spawn_actor_from_object(
        cube,
        unreal.Vector(x * CM, -34.2 * CM, sites[sid]["base"] + 30.0),
        unreal.Rotator(0.0, yaw_along_x, 0.0),
        transient=False,
    )
    base.set_actor_label("QX_Corr_Base_Salvage_%02d" % idx)
    base.tags = [unreal.Name(TAG), unreal.Name(sid), unreal.Name("SunscarMapOwned"), unreal.Name("SimpleCollisionProxy")]
    base.set_folder_path(unreal.Name(ROOT + "/SalvageYard/Bases"))
    base.set_actor_scale3d(unreal.Vector(2.1 * CM / cube_size.x, 0.42 * CM / cube_size.y, 0.60 * CM / cube_size.z))
    base.static_mesh_component.set_material(0, stone)
    created.append(base)
    panel = add_render(corr, sid, "QX_Corr_Salvage_S_%02d" % idx, x, -34.2, yaw_along_x)
    panel.add_actor_world_offset(unreal.Vector(0.0, 0.0, 60.0), False, False)

# Bazaar stall backs: visual panels only; existing stall geometry remains tactical collision.
for idx, (x, y) in enumerate(((16.0,-86.1),(24.0,-86.1),(32.0,-99.9),(40.0,-99.9)), 1):
    add_render(corr, "SS_017", "QX_Corr_Bazaar_%02d" % idx, x, y, yaw_along_x)

level.save_current_level()
unreal.log("SUNSCAR_QX_DEFENSIVE actors=%d square=%d corrugated=%d" % (len(created), len(square_places), 12))
print("SUNSCAR_QX_DEFENSIVE", len(created))
