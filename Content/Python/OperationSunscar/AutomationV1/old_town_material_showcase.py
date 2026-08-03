"""Spawn a transient material-review lineup; never saves level actors."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
common.require_safe_context(config, write_requested=False)
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]
for actor in actors:
    if actor.get_actor_label().startswith("TEMP_OT_MAT_"):
        actor_system.destroy_actor(actor)

specs = [
    ("Door", "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_001_wbmgdcpdw/Old_Wooden_Door_wbmgdcpdw_High"),
    ("Stool", "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_008_ukknbeyaw/Old_Metal_Stool_ukknbeyaw_High"),
    ("Table", "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_009_veigfjmaw/Wooden_Table_veigfjmaw_High"),
    ("Bench", "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_010_vlroadt/Wooden_Bench_vlroadt_High"),
    ("Electrical", "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_002_tdgecegda/Electrical_Box_tdgecegda_High"),
]
created = []
for index, (name, path) in enumerate(specs):
    x = -13200.0 + index * 280.0
    y = -12500.0
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        non_landscapes,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None or not hit.to_dict().get("blocking_hit"):
        raise RuntimeError("SUNSCAR_MAT_SHOWCASE_TERRAIN_TRACE_FAILED " + name)
    support_z = hit.to_dict()["location"].z
    mesh = unreal.EditorAssetLibrary.load_asset(path)
    actor = actor_system.spawn_actor_from_object(
        mesh, unreal.Vector(x, y, support_z), unreal.Rotator(0.0, 0.0, 0.0), transient=True
    )
    actor.set_actor_label("TEMP_OT_MAT_" + name)
    origin, extent = actor.get_actor_bounds(False)
    actor.add_actor_world_offset(
        unreal.Vector(0.0, 0.0, support_z - (origin.z - extent.z)), False, False
    )
    actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    created.append(actor.get_actor_label())

unreal.log("SUNSCAR_MATERIAL_SHOWCASE transient=%d" % len(created))
print("SUNSCAR_MATERIAL_SHOWCASE", len(created))
