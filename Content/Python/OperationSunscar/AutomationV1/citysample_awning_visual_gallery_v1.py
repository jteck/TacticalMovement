"""Unsaved neutral-material viewport gallery for seven owned City Sample awnings."""

import os

import unreal


EXPECTED_PROJECT = "OfficialAssetStaging"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_SampleAudit/OfficialAssetStaging"
ROOT = "/Game/CitySampleBuildings/Building/NY/A/Kit_PROP_NYA/Mesh"
SUFFIXES = ("01", "02", "03", "05", "07", "08", "10")
PASS_TAG = unreal.Name("CitySampleAwningVisualGalleryV1")


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("CITYSAMPLE_AWNING_GALLERY_WRONG_PROJECT")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
existing = [actor for actor in actor_subsystem.get_all_level_actors() if PASS_TAG in list(actor.tags)]
if existing:
    raise RuntimeError("CITYSAMPLE_AWNING_GALLERY_ALREADY_EXISTS %d" % len(existing))

default_material = unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial")
if default_material is None:
    raise RuntimeError("CITYSAMPLE_AWNING_GALLERY_DEFAULT_MATERIAL")

mesh_actors = []
for index, suffix in enumerate(SUFFIXES):
    path = ROOT + "/SM_PROP_NYA_A_Awning_%s_N1" % suffix
    mesh = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(mesh, unreal.StaticMesh):
        raise RuntimeError("CITYSAMPLE_AWNING_GALLERY_MISSING " + path)
    bounds = mesh.get_bounds()
    y = -900.0 + index * 300.0
    z = bounds.box_extent.z - bounds.origin.z
    actor = actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0.0, y, z),
        unreal.Rotator(),
        transient=False,
    )
    if actor is None:
        raise RuntimeError("CITYSAMPLE_AWNING_GALLERY_SPAWN " + suffix)
    actor.set_actor_label("Gallery_Awning_%s" % suffix)
    actor.tags = [PASS_TAG]
    actor.set_folder_path(unreal.Name("CitySampleAwningGallery/Geometry"))
    component = actor.static_mesh_component
    component.set_static_mesh(mesh)
    component.set_material(0, default_material)
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    mesh_actors.append(actor)

    label = actor_subsystem.spawn_actor_from_class(
        unreal.TextRenderActor,
        unreal.Vector(-115.0, y, 145.0),
        unreal.Rotator(0.0, 0.0, 0.0),
        transient=False,
    )
    if label is None:
        raise RuntimeError("CITYSAMPLE_AWNING_GALLERY_LABEL " + suffix)
    label.set_actor_label("Gallery_Label_%s" % suffix)
    label.tags = [PASS_TAG]
    label.set_folder_path(unreal.Name("CitySampleAwningGallery/Labels"))
    text_component = label.text_render
    text_component.set_text(unreal.Text("Awning %s" % suffix))
    text_component.set_world_size(34.0)
    text_component.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    text_component.set_text_render_color(unreal.Color(255, 210, 80, 255))

unreal.get_editor_subsystem(unreal.EditorActorSubsystem).set_selected_level_actors(mesh_actors)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(-1750.0, 0.0, 430.0),
    unreal.Rotator(-11.0, 0.0, 0.0),
)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world, "VIEWMODE UNLIT")
unreal.log("CITYSAMPLE_AWNING_GALLERY_READY meshes=7 unsaved=true")
print("CITYSAMPLE_AWNING_GALLERY_READY", len(mesh_actors))
