import json
import os

import unreal


MASTER_PATH = "/Game/Fab/Materials/Standard/M_MS_Foliage"
REPORT_PATH = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar",
    "Reports",
    "abiverd_foliage_master_graph_probe_v1.json",
)


def prop(value, name):
    try:
        result = value.get_editor_property(name)
        if hasattr(result, "get_path_name"):
            return result.get_path_name()
        return str(result)
    except Exception:
        return None


def describe(expression):
    if not expression:
        return None
    entry = {
        "name": expression.get_name(),
        "class": expression.get_class().get_name(),
        "path": expression.get_path_name(),
        "text": str(expression),
    }
    for name in (
        "parameter_name",
        "desc",
        "r",
        "g",
        "b",
        "a",
        "default_value",
        "const_input",
        "channel_names",
        "sampler_type",
    ):
        value = prop(expression, name)
        if value is not None:
            entry[name] = value
    return entry


def trace(expression, seen=None, depth=0):
    if not expression or depth > 24:
        return None
    if seen is None:
        seen = set()
    path = expression.get_path_name()
    if path in seen:
        return {"reference": path}
    seen.add(path)
    entry = describe(expression)
    entry["inputs"] = []
    if expression.get_class().get_name() == "MaterialExpressionNamedRerouteUsage":
        try:
            declaration = expression.get_editor_property("declaration")
            entry["declaration"] = describe(declaration)
            if declaration:
                entry["declaration"]["reroute_name"] = prop(declaration, "name")
                input_value = declaration.get_editor_property("input")
                upstream = input_value.get_editor_property("expression")
                if upstream:
                    entry["inputs"].append(trace(upstream, seen, depth + 1))
        except Exception as exc:
            entry["declaration_error"] = str(exc)
    else:
        try:
            for upstream in unreal.MaterialEditingLibrary.get_inputs_for_material_expression(
                master, expression
            ):
                if upstream:
                    entry["inputs"].append(trace(upstream, seen, depth + 1))
        except Exception as exc:
            entry["input_error"] = str(exc)
    return entry


master = unreal.load_asset(MASTER_PATH)
library = unreal.MaterialEditingLibrary
properties = {
    "base_color": unreal.MaterialProperty.MP_BASE_COLOR,
    "normal": unreal.MaterialProperty.MP_NORMAL,
    "roughness": unreal.MaterialProperty.MP_ROUGHNESS,
    "ambient_occlusion": unreal.MaterialProperty.MP_AMBIENT_OCCLUSION,
    "opacity_mask": unreal.MaterialProperty.MP_OPACITY_MASK,
    "world_position_offset": unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET,
    "subsurface_color": unreal.MaterialProperty.MP_SUBSURFACE_COLOR,
}

report = {
    "status": "complete",
    "master": MASTER_PATH,
    "exists": bool(master),
    "properties": {},
    "master_dir_filtered": [],
    "editor_only_data": {},
    "texture_group_values": [name for name in dir(unreal.TextureGroup) if name.isupper()],
    "static_mesh_subsystem_methods": [
        name for name in dir(unreal.StaticMeshEditorSubsystem)
        if any(token in name for token in ("lod", "collision", "nanite"))
    ],
}

if master:
    report["master_dir_filtered"] = [
        name for name in dir(master)
        if "expression" in name.lower() or "editor" in name.lower()
    ]
    try:
        editor_data = master.get_editor_property("editor_only_data")
        report["editor_only_data"] = {
            "class": editor_data.get_class().get_name() if editor_data else None,
            "dir_filtered": [
                name for name in dir(editor_data)
                if "expression" in name.lower() or "collection" in name.lower()
            ] if editor_data else [],
        }
        for candidate in ("expression_collection", "expressions"):
            try:
                value = editor_data.get_editor_property(candidate)
                report["editor_only_data"][candidate] = str(value)
            except Exception as exc:
                report["editor_only_data"][candidate] = {"error": str(exc)}
    except Exception as exc:
        report["editor_only_data"] = {"error": str(exc)}
    for label, material_property in properties.items():
        try:
            node = library.get_material_property_input_node(master, material_property)
            entry = {"input_node": describe(node), "direct_inputs": [], "trace": trace(node)}
            if node:
                try:
                    entry["direct_inputs"] = [
                        describe(value)
                        for value in library.get_inputs_for_material_expression(master, node)
                    ]
                except Exception as exc:
                    entry["input_error"] = str(exc)
            report["properties"][label] = entry
        except Exception as exc:
            report["properties"][label] = {"error": str(exc)}

os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2, sort_keys=True)

unreal.log("ABIVERD_FOLIAGE_MASTER_GRAPH_PROBE_V1_COMPLETE " + REPORT_PATH)
