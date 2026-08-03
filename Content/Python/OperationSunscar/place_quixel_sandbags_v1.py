import unreal

LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TAG = "SunscarQuixelSandbagPassV1"
ROOT = "OldTown_QuixelPass/Sandbags"
CM = 100.0
MESH_PATH = "/Game/Maps/Sunscar/Art/Quixel/Sandbags/SM_ydxlcck_tier_2/StaticMeshes/SM_ydxlcck_tier_2"
CUBE_PATH = "/Game/LevelPrototyping/Meshes/SM_Cube"

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if level.get_current_level().get_outermost().get_name() != LEVEL:
    raise RuntimeError("Wrong level: " + level.get_current_level().get_outermost().get_name())

mesh = unreal.EditorAssetLibrary.load_asset(MESH_PATH)
cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
if not mesh or not cube:
    raise RuntimeError("Required mesh missing")

try:
    nanite = mesh.get_editor_property("nanite_settings")
    nanite.enabled = True
    mesh.set_editor_property("nanite_settings", nanite)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
except Exception as exc:
    unreal.log_warning("SUNSCAR_NANITE_SETUP " + str(exc))

for actor in list(actors.get_all_level_actors()):
    if any(str(t) == TAG for t in actor.tags):
        actors.destroy_actor(actor)

# Remove only the graybox fortification shapes now replaced by Quixel render meshes.
for actor in list(actors.get_all_level_actors()):
    label = actor.get_actor_label()
    if label.startswith("Detention_Fort_") or label.startswith("NorthSpawn_Fort_"):
        if any(str(t) == "SunscarMapOwned" for t in actor.tags):
            actors.destroy_actor(actor)

specs = {
    "SS_010": ("DetentionAnnex", 22.0, 91.0, 34.0, 28.0, 6.4),
    "SS_011": ("CheckpointOffice", 74.0, 51.0, 20.0, 17.0, 6.4),
    "SS_020": ("NorthDefender", 118.0, 97.0, 20.0, 16.0, 0.2),
}
all_actors = actors.get_all_level_actors()
sites = {}
for sid, (folder, cx, cy, width, depth, height) in specs.items():
    marker = next((a for a in all_actors if a.get_actor_label().startswith(sid + "_")), None)
    if marker is None:
        raise RuntimeError("Missing marker " + sid)
    sites[sid] = {
        "folder": folder,
        "base": marker.get_actor_location().z - height * 50.0,
    }

bounds = mesh.get_bounds()
local_min_z = bounds.origin.z - bounds.box_extent.z
cube_size = cube.get_bounds().box_extent * 2.0

placements = [
    ("SS_010", "Detention_West_A", 8.5, 75.0, 0.0),
    ("SS_010", "Detention_West_Return", 6.9, 76.7, 90.0),
    ("SS_010", "Detention_East_A", 35.5, 75.0, 0.0),
    ("SS_010", "Detention_East_Return", 37.1, 76.7, 90.0),
    ("SS_011", "Checkpoint_West_A", 63.5, 42.0, 0.0),
    ("SS_011", "Checkpoint_West_B", 66.7, 42.0, 0.0),
    ("SS_020", "North_West_A", 108.8, 90.5, 0.0),
    ("SS_020", "North_West_B", 112.0, 90.5, 0.0),
    ("SS_020", "North_East_A", 124.0, 90.5, 0.0),
    ("SS_020", "North_East_B", 127.2, 90.5, 0.0),
]

created = []
for sid, name, x_m, y_m, yaw in placements:
    base_z = sites[sid]["base"]
    render = actors.spawn_actor_from_object(
        mesh,
        unreal.Vector(x_m * CM, y_m * CM, base_z - local_min_z),
        unreal.Rotator(0.0, yaw, 0.0),
        transient=False,
    )
    render.set_actor_label("QX_Sandbag_" + name)
    render.tags = [unreal.Name(TAG), unreal.Name(sid), unreal.Name("SunscarMapOwned"), unreal.Name("QuixelMegascans")]
    render.set_folder_path(unreal.Name(ROOT + "/" + sites[sid]["folder"]))
    render.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    created.append(render)

    proxy_dims = (3.05, 0.45, 0.82) if yaw == 0.0 else (0.45, 3.05, 0.82)
    proxy = actors.spawn_actor_from_object(
        cube,
        unreal.Vector(x_m * CM, y_m * CM, base_z + 41.0),
        unreal.Rotator(),
        transient=False,
    )
    proxy.set_actor_label("COL_Sandbag_" + name)
    proxy.tags = [unreal.Name(TAG), unreal.Name(sid), unreal.Name("SunscarMapOwned"), unreal.Name("SimpleCollisionProxy")]
    proxy.set_folder_path(unreal.Name(ROOT + "/" + sites[sid]["folder"] + "/Collision"))
    proxy.set_actor_scale3d(unreal.Vector(
        proxy_dims[0] * CM / cube_size.x,
        proxy_dims[1] * CM / cube_size.y,
        proxy_dims[2] * CM / cube_size.z,
    ))
    proxy.static_mesh_component.set_visibility(False)
    proxy.static_mesh_component.set_hidden_in_game(True)
    proxy.static_mesh_component.set_collision_profile_name("BlockAll")
    created.append(proxy)

level.save_current_level()
unreal.log("SUNSCAR_QX_SANDBAGS actors=%d render=%d collision=%d" % (len(created), len(placements), len(placements)))
print("SUNSCAR_QX_SANDBAGS", len(created))
