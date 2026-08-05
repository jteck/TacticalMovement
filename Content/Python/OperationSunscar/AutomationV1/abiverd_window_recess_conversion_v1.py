"""Dry-run-first conversion of placeholder cyan glass to opaque dusty recesses.

For this multiplayer FPS draft, opaque recessed-window cards are deliberately
preferred to translucent glass: they remove the bright prototype cue, avoid
translucency cost and sorting, and preserve the existing gameplay wall shells.
"""

import json
import os
import re

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
WINDOW_PATTERN = re.compile(r"^(.*(?:_Win_|_Window_).*)_(Frame|Glass)$", re.IGNORECASE)
MASTER_PATH = "/Game/LevelPrototyping/Materials/M_FlatCol"
MATERIAL_FOLDER = "/Game/Maps/Sunscar/Art/Materials/Facade"
MATERIAL_NAME = "MI_OT_DustyWindowRecess"
MATERIAL_PATH = MATERIAL_FOLDER + "/" + MATERIAL_NAME
REPORT_NAME = (
    "abiverd_window_recess_conversion_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_window_recess_conversion_dry_run_v1.json"
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


def asset_path(asset):
    return asset.get_outermost().get_name() if asset else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WINDOW_RECESS_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_WINDOW_RECESS_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_WINDOW_RECESS_LOAD_DIRTY")

master = unreal.EditorAssetLibrary.load_asset(MASTER_PATH)
if not isinstance(master, unreal.Material):
    raise RuntimeError("ABIVERD_WINDOW_RECESS_MASTER_MISSING")
existing_material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
if existing_material is not None and not isinstance(existing_material, unreal.MaterialInstanceConstant):
    raise RuntimeError("ABIVERD_WINDOW_RECESS_MATERIAL_CLASS")

records = []
pairs = {}
targets = []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    label = actor.get_actor_label()
    match = WINDOW_PATTERN.match(label)
    if not match:
        continue
    key, role = match.groups()
    role = role.lower()
    component = actor.static_mesh_component
    records.append(
        {
            "key": key.lower(),
            "label": label,
            "role": role,
            "source_material": asset_path(component.get_material(0)),
            "target_material": MATERIAL_PATH if role == "glass" else asset_path(component.get_material(0)),
            "source_collision": str(component.get_collision_enabled()),
            "target_collision": str(unreal.CollisionEnabled.NO_COLLISION),
            "visible": component.is_visible(),
            "hidden_in_game": bool(component.get_editor_property("hidden_in_game")),
        }
    )
    pairs.setdefault(key.lower(), set()).add(role)
    targets.append((actor, role))

records.sort(key=lambda item: item["label"].lower())
targets.sort(key=lambda item: item[0].get_actor_label().lower())
if len(records) != 80 or len(pairs) != 40:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_COUNTS records=%d pairs=%d" % (len(records), len(pairs)))
bad_pairs = sorted(key for key, roles in pairs.items() if roles != {"frame", "glass"})
if bad_pairs:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_PAIRS " + "|".join(bad_pairs))
if sum(role == "glass" for _actor, role in targets) != 40:
    raise RuntimeError("ABIVERD_WINDOW_RECESS_GLASS_COUNT")
if any(not row["visible"] or row["hidden_in_game"] for row in records):
    raise RuntimeError("ABIVERD_WINDOW_RECESS_VISIBILITY")

saved_packages = []
if APPLY_CHANGES:
    material = existing_material
    if material is None:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            MATERIAL_NAME,
            MATERIAL_FOLDER,
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew(),
        )
        if material is None:
            raise RuntimeError("ABIVERD_WINDOW_RECESS_CREATE_FAILED")
    material.set_editor_property("parent", master)
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
        material,
        "Base Color",
        unreal.LinearColor(r=0.018, g=0.022, b=0.018, a=1.0),
    )
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material, "Roughness", 0.92)
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material, "Metallic", 0.0)
    unreal.MaterialEditingLibrary.update_material_instance(material)
    for actor, role in targets:
        actor.modify()
        component = actor.static_mesh_component
        component.modify()
        if role == "glass":
            component.set_material(0, material)
        component.set_collision_profile_name("NoCollision")
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    before_save = dirty_packages()
    allowed_prefixes = (
        MATERIAL_PATH,
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_WINDOW_RECESS_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_WINDOW_RECESS_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_WINDOW_RECESS_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "record_count": len(records),
    "pair_count": len(pairs),
    "glass_count": sum(row["role"] == "glass" for row in records),
    "frame_count": sum(row["role"] == "frame" for row in records),
    "records": records,
    "material": {
        "path": MATERIAL_PATH,
        "parent": MASTER_PATH,
        "base_color_linear": [0.018, 0.022, 0.018, 1.0],
        "roughness": 0.92,
        "metallic": 0.0,
        "blend_mode": "opaque inherited from M_FlatCol",
    },
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "rendering": "opaque fake-interior recess; no translucent glass or scene capture",
        "collision": "all 80 decorative frame/recess actors use NoCollision; gameplay shells remain authoritative",
        "performance": "one shared material instance; no new actors, ticks, navigation or replication",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_WINDOW_RECESS_COMPLETE apply=%s records=80 pairs=40" % APPLY_CHANGES)
print("ABIVERD_WINDOW_RECESS_COMPLETE", report_path)
