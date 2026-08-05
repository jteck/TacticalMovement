"""Read-only inspection of Landscape component weightmap allocations."""

import json
import os

import unreal


actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
proxies = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
rows = []
for proxy in proxies:
    for component in proxy.get_components_by_class(unreal.LandscapeComponent):
        row = {
            "proxy": proxy.get_actor_label(),
            "component": component.get_name(),
            "package": component.get_package().get_name(),
        }
        try:
            allocations = component.get_editor_property("weightmap_layer_allocations")
            allocation_rows = []
            for allocation in allocations:
                info = allocation.get_editor_property("layer_info")
                allocation_rows.append(
                    {
                        "layer_info": info.get_path_name() if info else "",
                        "weightmap_texture_index": allocation.get_editor_property("weightmap_texture_index"),
                        "weightmap_texture_channel": allocation.get_editor_property("weightmap_texture_channel"),
                    }
                )
            row["allocations"] = allocation_rows
        except Exception as exc:
            row["allocation_error"] = repr(exc)
            row["component_members"] = sorted(
                name for name in dir(component)
                if "weight" in name.lower() or "layer" in name.lower()
            )
        rows.append(row)

payload = {
    "schema_version": 1,
    "status": "read_only_component_weight_probe_complete",
    "component_count": len(rows),
    "components_with_allocations": sum(1 for row in rows if row.get("allocations")),
    "grass_allocation_count": sum(
        1 for row in rows for allocation in row.get("allocations", [])
        if allocation["layer_info"].endswith("LI_Meadow_NonWeight.LI_Meadow_NonWeight")
    ),
    "components": rows,
    "dirty_packages": sorted(
        {item.get_name() for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {item.get_name() for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    ),
    "changes_made": False,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_component_weight_probe_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_COMPONENT_WEIGHT_PROBE_COMPLETE components=%d" % len(rows))
