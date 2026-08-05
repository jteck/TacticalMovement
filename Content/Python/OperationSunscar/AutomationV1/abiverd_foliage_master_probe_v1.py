import json
import os

import unreal


REPORT_PATH = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar",
    "Reports",
    "abiverd_foliage_master_probe_v1.json",
)

MASTER_PATHS = [
    "/Game/Fab/Materials/Standard/M_MS_Foliage",
    "/Game/Fab/Materials/VT/M_MS_Foliage_VT",
]

DRY_GRASS_MESH_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_015_tbbqejqr/"
    "Dry_Grass_tbbqejqr_High_tbbqejqr_VarA_LOD0"
)


def object_path(value):
    return value.get_path_name() if value else None


def safe_call(callable_value, default=None):
    try:
        return callable_value()
    except Exception as exc:
        return {"error": str(exc)} if default is None else default


def material_parameters(material):
    library = unreal.MaterialEditingLibrary
    return {
        "texture_parameters": [str(v) for v in safe_call(
            lambda: library.get_texture_parameter_names(material), []
        )],
        "scalar_parameters": [str(v) for v in safe_call(
            lambda: library.get_scalar_parameter_names(material), []
        )],
        "vector_parameters": [str(v) for v in safe_call(
            lambda: library.get_vector_parameter_names(material), []
        )],
        "static_switch_parameters": [str(v) for v in safe_call(
            lambda: library.get_static_switch_parameter_names(material), []
        )],
    }


report = {
    "status": "complete",
    "project_dir": unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()),
    "level": object_path(unreal.EditorLevelLibrary.get_editor_world()),
    "masters": [],
    "existing_dry_grass": {},
}

for path in MASTER_PATHS:
    material = unreal.load_asset(path)
    entry = {
        "path": path,
        "exists": bool(material),
        "class": material.get_class().get_name() if material else None,
    }
    if material:
        entry.update(material_parameters(material))
        for property_name in ("blend_mode", "two_sided", "shading_model"):
            try:
                entry[property_name] = str(material.get_editor_property(property_name))
            except Exception as exc:
                entry[property_name] = {"error": str(exc)}
    report["masters"].append(entry)

mesh = unreal.load_asset(DRY_GRASS_MESH_PATH)
mesh_entry = {
    "path": DRY_GRASS_MESH_PATH,
    "exists": bool(mesh),
    "class": mesh.get_class().get_name() if mesh else None,
}
if mesh:
    bounds = mesh.get_bounds()
    mesh_entry["bounds"] = {
        "origin": [bounds.origin.x, bounds.origin.y, bounds.origin.z],
        "box_extent": [bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z],
        "sphere_radius": bounds.sphere_radius,
    }
    mesh_entry["lod_count"] = safe_call(
        lambda: unreal.EditorStaticMeshLibrary.get_lod_count(mesh), -1
    )
    mesh_entry["nanite_enabled"] = safe_call(
        lambda: bool(mesh.get_editor_property("nanite_settings").enabled), False
    )
    mesh_entry["materials"] = []
    for index, static_material in enumerate(mesh.get_editor_property("static_materials")):
        assigned = static_material.material_interface
        material_entry = {
            "slot_index": index,
            "slot_name": str(static_material.material_slot_name),
            "material_path": object_path(assigned),
            "material_class": assigned.get_class().get_name() if assigned else None,
        }
        if assigned:
            try:
                parent = assigned.get_editor_property("parent")
                material_entry["parent"] = object_path(parent)
            except Exception:
                material_entry["parent"] = None
            material_entry.update(material_parameters(assigned))
            material_entry["resolved_textures"] = {}
            for parameter_name in material_entry["texture_parameters"]:
                texture = safe_call(
                    lambda n=parameter_name: unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(
                        assigned, n
                    ),
                    None,
                )
                material_entry["resolved_textures"][parameter_name] = object_path(texture)
            material_entry["resolved_scalars"] = {}
            for parameter_name in material_entry["scalar_parameters"]:
                value = safe_call(
                    lambda n=parameter_name: unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(
                        assigned, n
                    ),
                    None,
                )
                material_entry["resolved_scalars"][parameter_name] = value
        mesh_entry["materials"].append(material_entry)

report["existing_dry_grass"] = mesh_entry

os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2, sort_keys=True)

unreal.log("ABIVERD_FOLIAGE_MASTER_PROBE_V1_COMPLETE " + REPORT_PATH)
