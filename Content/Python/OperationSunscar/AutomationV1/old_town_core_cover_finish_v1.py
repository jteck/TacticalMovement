"""Finish Old Town core cover visuals while preserving every existing collision proxy, unsaved."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarCoreCoverFinishV1")
VISUAL_TAG = unreal.Name("SunscarCoreCoverVehicleVisualV1")
HARD_SOURCE = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray_02.MI_PrototypeGrid_Gray_02"
VEHICLE_SOURCE = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark.MI_PrototypeGrid_TopDark"
MATERIAL_PATHS = {
    "stone": "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/MI_OT_SandstoneStone_WorldAligned",
    "concrete": "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/MI_OT_WeatheredConcreteGround_WorldAligned",
    "metal": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal",
    "timber": "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Timber",
}
VEHICLE_VISUALS = {
    "CoreCover_MotorTruck1": (
        "/Game/CitySampleVehicles/vehicle09_Van/Mesh/SM_vehVan_vehicle09_LOD",
        0.86,
        "OldTown_ArtDraft/MotorPool",
    ),
    "CoreCover_MotorTruck2": (
        "/Game/CitySampleVehicles/vehicle01_Van/Mesh/SM_vehVan_vehicle01_LOD",
        1.148,
        "OldTown_ArtDraft/MotorPool",
    ),
    "CoreCover_SalvageCar1": (
        "/Game/CitySampleVehicles/vehicle13_Car/Mesh/SM_vehCar_vehicle13_LOD",
        0.90,
        "OldTown_ArtDraft/SalvageYard",
    ),
    "CoreCover_SalvageCar2": (
        "/Game/CitySampleVehicles/vehicle13_Car/Mesh/SM_vehCar_vehicle13_LOD",
        0.90,
        "OldTown_ArtDraft/SalvageYard",
    ),
    "CoreCover_SalvageScrap": (
        "/Game/CitySampleVehicles/vehicle13_Car/Mesh/SM_vehCar_vehicle13_LOD",
        0.75,
        "OldTown_ArtDraft/SalvageYard",
    ),
}


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
dirty_before = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if dirty_before:
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_DIRTY_BEFORE_REFUSED %s" % "|".join(dirty_before))
actors = list(common.actor_subsystem().get_all_level_actors())
proxies = sorted(
    [actor for actor in actors if common.actor_folder(actor).startswith("Sunscar/CorePlayable/Cover/")],
    key=lambda actor: actor.get_actor_label(),
)
if len(proxies) != 34:
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_PROXY_COUNT_REFUSED count=%d" % len(proxies))
existing_visuals = [actor for actor in actors if str(VISUAL_TAG) in common.actor_tags(actor)]
if existing_visuals:
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_DUPLICATE_VISUALS count=%d" % len(existing_visuals))

materials = {role: common.load_asset_checked(config, path) for role, path in MATERIAL_PATHS.items()}
vehicle_meshes = {
    label: common.load_asset_checked(config, definition[0])
    for label, definition in VEHICLE_VISUALS.items()
}
records = []
counts = collections.Counter()
vehicle_proxy_data = []
for proxy in proxies:
    label = proxy.get_actor_label()
    component = proxy.static_mesh_component
    source = component.get_material(0)
    source_path = source.get_path_name() if source else ""
    collision_before = str(component.get_collision_enabled())
    if collision_before != str(unreal.CollisionEnabled.QUERY_AND_PHYSICS):
        raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_COLLISION_REFUSED %s %s" % (label, collision_before))
    proxy.modify()
    component.modify()
    treatment = ""
    target_path = ""
    if label.startswith("CoreCover_A"):
        treatment, target = "stone", materials["stone"]
        if source_path != HARD_SOURCE:
            raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_HARD_SOURCE_REFUSED %s %s" % (label, source_path))
        component.set_material(0, target)
        target_path = target.get_path_name()
    elif label.startswith("CoreCover_B"):
        treatment, target = "concrete", materials["concrete"]
        if source_path != HARD_SOURCE:
            raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_HARD_SOURCE_REFUSED %s %s" % (label, source_path))
        component.set_material(0, target)
        target_path = target.get_path_name()
    elif label.startswith("CoreCover_C"):
        if source_path != HARD_SOURCE:
            raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_HARD_SOURCE_REFUSED %s %s" % (label, source_path))
        if label == "CoreCover_C11":
            treatment = "hidden_duplicate_checkpoint_visual"
            component.set_visibility(False, True)
        else:
            treatment, target = "metal", materials["metal"]
            component.set_material(0, target)
            target_path = target.get_path_name()
    elif label == "CoreCover_FreightCrates":
        treatment, target = "timber", materials["timber"]
        if source_path != VEHICLE_SOURCE:
            raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_FREIGHT_SOURCE_REFUSED %s" % source_path)
        component.set_material(0, target)
        target_path = target.get_path_name()
    elif label in VEHICLE_VISUALS:
        if source_path != VEHICLE_SOURCE:
            raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_VEHICLE_SOURCE_REFUSED %s %s" % (label, source_path))
        treatment = "hidden_vehicle_collision_proxy"
        component.set_visibility(False, True)
        origin, extent = proxy.get_actor_bounds(False)
        vehicle_proxy_data.append((proxy, origin, extent))
    else:
        raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_UNCLASSIFIED " + label)
    if PASS_TAG not in list(proxy.tags):
        proxy.tags = list(proxy.tags) + [PASS_TAG]
    counts[treatment] += 1
    records.append(
        {
            "kind": "existing_proxy",
            "label": label,
            "treatment": treatment,
            "source_material": source_path,
            "target_material": target_path,
            "collision_before": collision_before,
            "collision_after": str(component.get_collision_enabled()),
            "visible_after": bool(component.get_editor_property("visible")),
            "package": proxy.get_package().get_name(),
        }
    )

created = []
for proxy, proxy_origin, proxy_extent in vehicle_proxy_data:
    label = proxy.get_actor_label()
    mesh_path, scale, folder = VEHICLE_VISUALS[label]
    mesh = vehicle_meshes[label]
    rotation = proxy.get_actor_rotation()
    visual = common.actor_subsystem().spawn_actor_from_object(
        mesh,
        proxy_origin,
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=rotation.yaw),
        transient=False,
    )
    if not isinstance(visual, unreal.StaticMeshActor):
        raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_VISUAL_SPAWN_FAILED " + label)
    visual.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    origin, extent = visual.get_actor_bounds(False)
    proxy_bottom = proxy_origin.z - proxy_extent.z
    visual.add_actor_world_offset(
        unreal.Vector(proxy_origin.x - origin.x, proxy_origin.y - origin.y, proxy_bottom - (origin.z - extent.z)),
        False,
        False,
    )
    visual.set_actor_label("Visual_" + label)
    visual.set_folder_path(unreal.Name(folder))
    visual.tags = [PASS_TAG, VISUAL_TAG, unreal.Name("SunscarMapOwned"), unreal.Name("CitySampleStaticVehicle")]
    visual.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    final_origin, final_extent = visual.get_actor_bounds(False)
    created.append(visual)
    counts["city_sample_vehicle_visual"] += 1
    records.append(
        {
            "kind": "new_visual",
            "label": visual.get_actor_label(),
            "source_proxy": label,
            "target_mesh": mesh.get_path_name(),
            "scale": scale,
            "yaw": round(rotation.yaw, 3),
            "location_cm": [round(final_origin.x, 3), round(final_origin.y, 3), round(final_origin.z, 3)],
            "extent_cm": [round(final_extent.x, 3), round(final_extent.y, 3), round(final_extent.z, 3)],
            "bottom_error_cm": round((final_origin.z - final_extent.z) - proxy_bottom, 3),
            "collision": str(visual.static_mesh_component.get_collision_enabled()),
            "package": visual.get_package().get_name(),
        }
    )

expected_counts = {
    "stone": 8,
    "concrete": 8,
    "metal": 11,
    "hidden_duplicate_checkpoint_visual": 1,
    "timber": 1,
    "hidden_vehicle_collision_proxy": 5,
    "city_sample_vehicle_visual": 5,
}
if dict(counts) != expected_counts or len(records) != 39 or len(created) != 5:
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_SCOPE_REFUSED expected=%s actual=%s" % (expected_counts, dict(counts)))
dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
expected_maps = sorted({record["package"] for record in records})
if dirty_content or dirty_maps != expected_maps:
    raise RuntimeError("SUNSCAR_CORE_COVER_FINISH_DIRTY_SCOPE_REFUSED content=%s maps=%s" % ("|".join(dirty_content), "|".join(dirty_maps)))
payload = {
    "schema_version": 1,
    "status": "unsaved_core_cover_finish_ready",
    "context": context,
    "proxy_actor_count": len(proxies),
    "created_visual_count": len(created),
    "actor_count": len(records),
    "treatment_counts": dict(sorted(counts.items())),
    "records": records,
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_core_cover_finish_v1.json", payload)
unreal.log("SUNSCAR_CORE_COVER_FINISH proxies=%d visuals=%d report=%s" % (len(proxies), len(created), report))
print("SUNSCAR_CORE_COVER_FINISH", len(records), report)
