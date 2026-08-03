import unreal

LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TAG = "SunscarQuixelSurfacePassV1"
ROOT = "OldTown_QuixelPass/SurfaceV1"
CM = 100.0
CONCRETE_MAT = "/Game/Maps/Sunscar/Art/Quixel/Surfaces/WeatheredConcrete/vi4idbm_tier_2/Materials/MI_vi4idbm"
PLASTER_MESH = "/Game/Maps/Sunscar/Art/Quixel/Damage/DamagedPlaster/vdekajsfw_tier_2/StaticMeshes/vdekajsfw_tier_2"

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if level.get_current_level().get_outermost().get_name() != LEVEL:
    raise RuntimeError("Wrong level")

concrete = unreal.EditorAssetLibrary.load_asset(CONCRETE_MAT)
plaster = unreal.EditorAssetLibrary.load_asset(PLASTER_MESH)
if not concrete or not plaster:
    raise RuntimeError("Missing surface pass assets")

try:
    ns = plaster.get_editor_property("nanite_settings")
    ns.enabled = True
    plaster.set_editor_property("nanite_settings", ns)
    unreal.EditorAssetLibrary.save_loaded_asset(plaster)
except Exception as exc:
    unreal.log_warning("SUNSCAR_PLASTER_NANITE " + str(exc))

for actor in list(actors.get_all_level_actors()):
    if any(str(t) == TAG for t in actor.tags):
        actors.destroy_actor(actor)

# Apply concrete only to selected structural shells and canal edges.
prefixes = ("Core_SS_003_", "Core_SS_009_", "Core_SS_011_", "Core_SS_015_", "Canal_Edge_")
exclude_terms = ("Window", "Door", "Glass", "Interior", "RoofVent", "Vehicle", "Antenna", "Sign")
materialized = []
for actor in actors.get_all_level_actors():
    label = actor.get_actor_label()
    if not label.startswith(prefixes) or any(term in label for term in exclude_terms):
        continue
    comp = getattr(actor, "static_mesh_component", None)
    if not comp:
        continue
    comp.set_material(0, concrete)
    if not any(str(t) == TAG for t in actor.tags):
        actor.tags = list(actor.tags) + [unreal.Name(TAG), unreal.Name("QuixelConcreteApplied")]
    materialized.append(actor)

specs = {
    "SS_005": ("OldClinic", 6.4),
    "SS_010": ("DetentionAnnex", 6.4),
}
all_actors = actors.get_all_level_actors()
sites = {}
for sid, (folder, height) in specs.items():
    marker = next((a for a in all_actors if a.get_actor_label().startswith(sid + "_")), None)
    if not marker:
        raise RuntimeError("Missing marker " + sid)
    sites[sid] = {"folder": folder, "base": marker.get_actor_location().z - height * 50.0}

b = plaster.get_bounds()
dims = b.box_extent * 2.0
thin_x = dims.x <= dims.y
yaw_for_south_wall = 90.0 if thin_x else 0.0
placements = [
    ("SS_005", "Clinic_A", -63.0, -10.62, 1.65, 0.75),
    ("SS_005", "Clinic_B", -55.0, -10.62, 4.75, 0.85),
    ("SS_005", "Clinic_C", -48.0, -10.62, 1.90, 0.65),
    ("SS_010", "Detention_A", 12.5, 76.88, 1.70, 0.80),
    ("SS_010", "Detention_B", 22.0, 76.88, 4.85, 0.90),
    ("SS_010", "Detention_C", 31.5, 76.88, 2.10, 0.70),
]
created = []
for sid, name, x, y, center_z_m, scale in placements:
    loc_z = sites[sid]["base"] + center_z_m * CM - b.origin.z * scale
    patch = actors.spawn_actor_from_object(
        plaster,
        unreal.Vector(x * CM, y * CM, loc_z),
        unreal.Rotator(0.0, yaw_for_south_wall, 0.0),
        transient=False,
    )
    patch.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    patch.set_actor_label("QX_PlasterDamage_" + name)
    patch.tags = [unreal.Name(TAG), unreal.Name(sid), unreal.Name("SunscarMapOwned"), unreal.Name("QuixelMegascans"), unreal.Name("NoCollision")]
    patch.set_folder_path(unreal.Name(ROOT + "/Damage/" + sites[sid]["folder"]))
    patch.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    created.append(patch)

level.save_current_level()
unreal.log("SUNSCAR_QX_SURFACE concrete_actors=%d plaster=%d plaster_dims=%s" % (len(materialized), len(created), str(dims)))
print("SUNSCAR_QX_SURFACE", len(materialized), len(created))
