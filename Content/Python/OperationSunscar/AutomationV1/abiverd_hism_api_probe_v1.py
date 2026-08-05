"""Read-only UE 5.8 Python API probe for persistent HISM authoring."""

import json
import os

import unreal


REPORT_PATH = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar",
    "Reports",
    "abiverd_hism_api_probe_v1.json",
)


def selected_names(value, tokens):
    return sorted(
        name for name in dir(value)
        if any(token.lower() in name.lower() for token in tokens)
    )


payload = {
    "actor_methods": selected_names(unreal.Actor, ("component", "instance", "root")),
    "hism_methods": selected_names(
        unreal.HierarchicalInstancedStaticMeshComponent,
        ("instance", "mesh", "collision", "navigation", "cull", "shadow"),
    ),
    "subobject_methods": selected_names(
        unreal.SubobjectDataSubsystem,
        ("subobject", "handle", "gather", "rename"),
    ),
    "add_new_subobject_params": selected_names(
        unreal.AddNewSubobjectParams,
        ("parent", "class", "blueprint"),
    ),
    "changes_made": False,
}
os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_HISM_API_PROBE " + REPORT_PATH)
