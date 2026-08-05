"""Read-only sampling of the Grass Landscape paint layer at planned meadow centers."""

import json
import os

import unreal


LAYER = unreal.Name("Grass")
POINTS = [
    (-4500.0, 16300.0),
    (-4500.0, 18700.0),
    (-4300.0, 21100.0),
    (4400.0, 16900.0),
    (4300.0, 19400.0),
    (4400.0, 21600.0),
    (0.0, 0.0),
]

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
components = [
    component
    for actor in actors if isinstance(actor, unreal.LandscapeProxy)
    for component in actor.get_components_by_class(unreal.LandscapeComponent)
]

rows = []
for x, y in POINTS:
    values = []
    for component in components:
        try:
            value = component.editor_get_paint_layer_weight_by_name_at_location(
                unreal.Vector(x, y, 0.0),
                LAYER,
            )
        except Exception as exc:
            value = "ERROR: " + repr(exc)
        if not isinstance(value, (int, float)) or value >= 0.0:
            values.append({"component": component.get_name(), "value": value})
    rows.append({"point": [x, y], "values": values})

payload = {
    "schema_version": 1,
    "status": "read_only_grass_sample_probe_complete",
    "method_doc": str(
        unreal.LandscapeComponent.editor_get_paint_layer_weight_by_name_at_location.__doc__
    ),
    "samples": rows,
    "changes_made": False,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_grass_sample_probe_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_GRASS_SAMPLE_PROBE_COMPLETE")
