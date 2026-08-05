"""Read-only probe of World Partition descriptors intersecting Old Town/Abiverd."""

import json
import os
import traceback

import unreal


REPORT_PATH = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar",
    "Reports",
    "abiverd_world_partition_descriptor_probe_v1.json",
)

payload = {"status": "started"}
try:
    box = unreal.Box(
        min=unreal.Vector(-7000.0, 10000.0, -100000.0),
        max=unreal.Vector(7000.0, 25000.0, 100000.0),
    )
    result = unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(box)
    payload.update(
        {
            "status": "complete",
            "result_type": str(type(result)),
            "result_repr_prefix": repr(result)[:4000],
            "result_length": len(result) if hasattr(result, "__len__") else None,
        }
    )
    if isinstance(result, tuple):
        payload["tuple_element_types"] = [str(type(value)) for value in result]
        for value in result:
            if isinstance(value, (list, tuple)):
                payload["descriptor_count"] = len(value)
                payload["descriptor_sample"] = []
                for desc in value[:10]:
                    payload["descriptor_sample"].append(
                        {
                            "type": str(type(desc)),
                            "repr": repr(desc),
                            "dir_filtered": [
                                name for name in dir(desc)
                                if name in ("guid", "label", "name", "bounds", "actor_package", "is_spatially_loaded")
                            ],
                        }
                    )
    else:
        values = list(result)
        payload["descriptor_count"] = len(values)
        payload["descriptor_sample"] = []
        for desc in values[:10]:
            sample = {
                "type": str(type(desc)),
                "repr": repr(desc),
                "dir_filtered": [
                    name for name in dir(desc)
                    if name in ("guid", "label", "name", "bounds", "actor_package", "is_spatially_loaded")
                ],
            }
            for name in sample["dir_filtered"]:
                try:
                    sample[name] = str(getattr(desc, name))
                except Exception as prop_exc:
                    sample[name] = {"error": str(prop_exc)}
            payload["descriptor_sample"].append(sample)
except Exception as exc:
    payload = {
        "status": "failed",
        "exception": repr(exc),
        "traceback": traceback.format_exc(),
    }

os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, default=str)
    handle.write("\n")
unreal.log("ABIVERD_WP_DESCRIPTOR_PROBE " + payload["status"] + " " + REPORT_PATH)
