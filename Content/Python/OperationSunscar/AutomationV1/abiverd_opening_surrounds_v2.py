"""Dry-run-first V2 surround pass for verified Old Town openings.

Extends the existing two-component HISM actor to the Hotel's verified main
door and open side passages plus the Bazaar's three open passages. Two Hotel
door props that sit against solid gameplay shell are hidden and made
non-colliding; no gameplay shell actor is changed.
"""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
MATERIAL_PATHS = {
    "mud": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
    "brick": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
}
DOOR_SITES = {
    "Tea_MainDoor": ("SS_004", "mud"),
    "Clinic_MainDoor": ("SS_005", "brick"),
    "Clinic_ServiceDoor": ("SS_005", "brick"),
    "Hotel_Door_-20": ("SS_007", "brick"),
    "Detention_Door_12": ("SS_010", "brick"),
    "Detention_Door_22": ("SS_010", "brick"),
    "Detention_Door_32": ("SS_010", "brick"),
    "Consulate_Door_A": ("SS_012", "mud"),
    "Consulate_Door_B": ("SS_012", "mud"),
}
PASSAGE_LINTELS = {
    "Core_SS_007_F1_E_Lintel": ("SS_007", "brick"),
    "Core_SS_007_F2_W_Lintel": ("SS_007", "brick"),
    "Core_SS_017_F1_E_Lintel": ("SS_017", "mud"),
    "Core_SS_017_F1_N_Lintel": ("SS_017", "mud"),
    "Core_SS_017_F1_W_Lintel": ("SS_017", "mud"),
}
FALSE_HOTEL_DOORS = {"Hotel_Door_-14", "Hotel_Door_-8"}
PASS_TAG = unreal.Name("SunscarAbiverdDoorSurroundsV1")
ACTOR_LABEL = "ABV_OldTown_DoorSurrounds_HISM_V1"
JAMB_WIDTH = 22.0
SURROUND_DEPTH = 34.0
JAMB_OVERHEAD = 18.0
LINTEL_HEIGHT = 28.0
REPORT_NAME = (
    "abiverd_opening_surrounds_v2_apply.json"
    if APPLY_CHANGES
    else "abiverd_opening_surrounds_v2_dry_run.json"
)


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


def actor_site(actor):
    for tag in actor.tags:
        value = str(tag)
        if value.startswith("Building_"):
            return value[len("Building_"):]
        if value.startswith("SS_") and len(value) == 6:
            return value
    return ""


def make_transform(location, dimensions):
    transform = unreal.Transform()
    transform.translation = location
    transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(unreal.Rotator())
    transform.scale3d = unreal.Vector(dimensions.x / 100.0, dimensions.y / 100.0, dimensions.z / 100.0)
    return transform


def add_surround(transforms_by_material, rows, source_label, site, material_key, origin, extent, base_z, kind, site_center):
    dimensions = extent * 2.0
    along_x = extent.x >= extent.y
    opening_width = dimensions.x if along_x else dimensions.y
    top_z = origin.z + extent.z
    opening_height = top_z - base_z
    jamb_height = opening_height + JAMB_OVERHEAD
    jamb_z = base_z + jamb_height * 0.5
    lintel_z = top_z + JAMB_OVERHEAD + LINTEL_HEIGHT * 0.5
    placements = []
    if along_x:
        outward = 1.0 if origin.y >= site_center.y else -1.0
        facade_y = origin.y + outward * (extent.y + SURROUND_DEPTH * 0.5 - 4.0)
        side_offset = extent.x + JAMB_WIDTH * 0.5 - 2.0
        placements = [
            (unreal.Vector(origin.x - side_offset, facade_y, jamb_z), unreal.Vector(JAMB_WIDTH, SURROUND_DEPTH, jamb_height), "left_jamb"),
            (unreal.Vector(origin.x + side_offset, facade_y, jamb_z), unreal.Vector(JAMB_WIDTH, SURROUND_DEPTH, jamb_height), "right_jamb"),
            (unreal.Vector(origin.x, facade_y, lintel_z), unreal.Vector(opening_width + JAMB_WIDTH * 2.0 - 4.0, SURROUND_DEPTH, LINTEL_HEIGHT), "lintel"),
        ]
    else:
        outward = 1.0 if origin.x >= site_center.x else -1.0
        facade_x = origin.x + outward * (extent.x + SURROUND_DEPTH * 0.5 - 4.0)
        side_offset = extent.y + JAMB_WIDTH * 0.5 - 2.0
        placements = [
            (unreal.Vector(facade_x, origin.y - side_offset, jamb_z), unreal.Vector(SURROUND_DEPTH, JAMB_WIDTH, jamb_height), "left_jamb"),
            (unreal.Vector(facade_x, origin.y + side_offset, jamb_z), unreal.Vector(SURROUND_DEPTH, JAMB_WIDTH, jamb_height), "right_jamb"),
            (unreal.Vector(facade_x, origin.y, lintel_z), unreal.Vector(SURROUND_DEPTH, opening_width + JAMB_WIDTH * 2.0 - 4.0, LINTEL_HEIGHT), "lintel"),
        ]
    for location, piece_dimensions, role in placements:
        transforms_by_material[material_key].append(make_transform(location, piece_dimensions))
        rows.append(
            {
                "source": source_label,
                "site": site,
                "opening_kind": kind,
                "material_key": material_key,
                "role": role,
                "location_cm": [round(location.x, 3), round(location.y, 3), round(location.z, 3)],
                "dimensions_cm": [round(piece_dimensions.x, 3), round(piece_dimensions.y, 3), round(piece_dimensions.z, 3)],
                "collision": "NoCollision",
            }
        )


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_WRONG_PROJECT")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(min=unreal.Vector(-12500.0, -11500.0, -100000.0), max=unreal.Vector(15500.0, 11500.0, 100000.0))
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_LOAD_DIRTY")

cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
materials = {key: unreal.EditorAssetLibrary.load_asset(path) for key, path in MATERIAL_PATHS.items()}
if not isinstance(cube, unreal.StaticMesh) or any(value is None for value in materials.values()):
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_ASSET_MISSING")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
missing = sorted((set(DOOR_SITES) | set(PASSAGE_LINTELS) | FALSE_HOTEL_DOORS) - set(by_label))
if missing:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_MISSING " + repr(missing))

surround_matches = [actor for actor in actors if PASS_TAG in list(actor.tags) or actor.get_actor_label() == ACTOR_LABEL]
if len(surround_matches) != 1:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_ACTOR_COUNT %d" % len(surround_matches))
surround_actor = surround_matches[0]
components = list(surround_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
components_by_name = {component.get_name(): component for component in components}
if set(components_by_name) != {"HISM_DoorSurround_Brick", "HISM_DoorSurround_Mud"}:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_COMPONENTS " + repr(sorted(components_by_name)))

all_sites = {site for site, _material in DOOR_SITES.values()} | {site for site, _material in PASSAGE_LINTELS.values()}
site_samples = {}
for actor in actors:
    if isinstance(actor, unreal.StaticMeshActor) and unreal.Name("CoreCategory_Building") in list(actor.tags):
        site = actor_site(actor)
        if site in all_sites:
            origin, _extent = actor.get_actor_bounds(False)
            site_samples.setdefault(site, []).append(origin)
site_centers = {
    site: unreal.Vector(
        sum(item.x for item in values) / len(values),
        sum(item.y for item in values) / len(values),
        sum(item.z for item in values) / len(values),
    )
    for site, values in site_samples.items()
}
if set(site_centers) != all_sites:
    raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_SITE_CENTERS " + repr(sorted(site_centers)))

transforms_by_material = {key: [] for key in materials}
rows = []
for label in sorted(DOOR_SITES):
    site, material_key = DOOR_SITES[label]
    actor = by_label[label]
    if not isinstance(actor, unreal.StaticMeshActor):
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_DOOR_CLASS " + label)
    origin, extent = actor.get_actor_bounds(False)
    dimensions = extent * 2.0
    if not (115.0 <= max(dimensions.x, dimensions.y) <= 135.0 and 230.0 <= dimensions.z <= 250.0):
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_DOOR_BOUNDS " + label)
    add_surround(transforms_by_material, rows, label, site, material_key, origin, extent, origin.z - extent.z, "door", site_centers[site])

for label in sorted(PASSAGE_LINTELS):
    site, material_key = PASSAGE_LINTELS[label]
    lintel = by_label[label]
    origin, extent = lintel.get_actor_bounds(False)
    left_label = label[:-len("_Lintel")] + "_Left"
    right_label = label[:-len("_Lintel")] + "_Right"
    sides = [by_label.get(left_label), by_label.get(right_label)]
    if any(side is None for side in sides):
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_PASSAGE_SIDES " + label)
    base_z = min(side.get_actor_bounds(False)[0].z - side.get_actor_bounds(False)[1].z for side in sides)
    add_surround(transforms_by_material, rows, label, site, material_key, origin, extent, base_z, "open_passage", site_centers[site])

if len(rows) != 42 or len(transforms_by_material["brick"]) != 24 or len(transforms_by_material["mud"]) != 18:
    raise RuntimeError(
        "ABIVERD_OPENING_SURROUNDS_V2_COUNTS total=%d brick=%d mud=%d"
        % (len(rows), len(transforms_by_material["brick"]), len(transforms_by_material["mud"]))
    )

saved_packages = []
if APPLY_CHANGES:
    surround_actor.modify()
    for material_key in sorted(materials):
        component = components_by_name["HISM_DoorSurround_%s" % material_key.title()]
        component.modify()
        component.clear_instances()
        component.set_static_mesh(cube)
        component.set_material(0, materials[material_key])
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        component.set_cast_shadow(True)
        component.set_editor_property("instance_start_cull_distance", 12000)
        component.set_editor_property("instance_end_cull_distance", 30000)
        try:
            component.set_editor_property("can_ever_affect_navigation", False)
        except Exception:
            pass
        for transform in transforms_by_material[material_key]:
            component.add_instance(transform, world_space=True)
        if component.get_instance_count() != len(transforms_by_material[material_key]):
            raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_INSTANCE_COUNT " + material_key)

    for label in sorted(FALSE_HOTEL_DOORS):
        false_door = by_label[label]
        false_door.modify()
        false_component = false_door.static_mesh_component
        false_component.modify()
        false_component.set_visibility(False, True)
        false_component.set_hidden_in_game(True)
        false_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_OPENING_SURROUNDS_V2_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 2,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "door_opening_count": len(DOOR_SITES),
    "open_passage_count": len(PASSAGE_LINTELS),
    "piece_count": len(rows),
    "material_instance_counts": {key: len(value) for key, value in sorted(transforms_by_material.items())},
    "false_hotel_doors": sorted(FALSE_HOTEL_DOORS),
    "false_hotel_door_action": "hidden_and_collision_disabled" if APPLY_CHANGES else "planned",
    "placements": rows,
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "gameplay_shells": "unchanged",
        "real_openings": "nine verified doors plus five verified open shell passages",
        "false_door_cues": "two Hotel door props against solid wall are hidden and made non-colliding",
        "collision": "all surround dressing uses NoCollision",
        "performance": "existing static non-replicated actor; two material-batched HISM components; 12m/30m culling",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_OPENING_SURROUNDS_V2_COMPLETE apply=%s pieces=%d brick=%d mud=%d"
    % (APPLY_CHANGES, len(rows), len(transforms_by_material["brick"]), len(transforms_by_material["mud"]))
)
print("ABIVERD_OPENING_SURROUNDS_V2_COMPLETE", report_path)
