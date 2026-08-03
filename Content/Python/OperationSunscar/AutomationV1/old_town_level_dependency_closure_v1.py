"""Read-only dependency closure for the saved Old Town World Partition level."""

import collections
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PACK_PREFIXES = (
    "/Game/CitySampleVehicles/",
    "/Game/Fab/",
    "/Game/MilitaryTrench/",
    "/Game/Scene_Junkyard/",
)
MAP_PREFIXES = (
    "/Game/Maps/Blockout/",
    "/Game/Maps/Sunscar/",
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
)


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
registry = unreal.AssetRegistryHelpers.get_asset_registry()
actors = list(common.actor_subsystem().get_all_level_actors())

dependency_options = unreal.AssetRegistryDependencyOptions(
    include_soft_package_references=True,
    include_hard_package_references=True,
    include_searchable_names=False,
    include_soft_management_references=True,
    include_hard_management_references=True,
)


def package_name(value):
    if value is None:
        return ""
    try:
        name = str(value.get_outermost().get_name())
    except Exception:
        try:
            name = str(value.get_path_name()).split(".", 1)[0]
        except Exception:
            name = str(value).split(".", 1)[0]
    return name if name.startswith("/") else ""


def dependencies(name):
    try:
        return sorted(str(item) for item in registry.get_dependencies(name, dependency_options))
    except Exception:
        try:
            return sorted(str(item) for item in registry.get_dependencies(unreal.Name(name), dependency_options))
        except Exception as exc:
            dependency_errors.append({"package": name, "error": str(exc)})
            return []


def add_object(target, value):
    name = package_name(value)
    if name:
        target.add(name)


def package_files(name):
    if not name.startswith("/Game/"):
        return []
    stem = os.path.join(unreal.Paths.project_content_dir(), name[len("/Game/"):])
    found = []
    for suffix in (".uasset", ".umap", ".uexp", ".ubulk", ".uptnl"):
        candidate = stem + suffix
        if os.path.isfile(candidate):
            found.append(candidate)
    return found


direct_packages = {common.current_level_path()}
actor_records = []
for actor in actors:
    actor_direct = set()
    add_object(actor_direct, actor.get_class())
    actor_package = package_name(actor)
    if actor_package:
        direct_packages.add(actor_package)

    try:
        components = actor.get_components_by_class(unreal.ActorComponent)
    except Exception:
        components = []
    for component in components:
        add_object(actor_direct, component.get_class())
        if isinstance(component, unreal.StaticMeshComponent):
            try:
                add_object(actor_direct, component.get_editor_property("static_mesh"))
            except Exception:
                pass
        if isinstance(component, unreal.SkeletalMeshComponent):
            try:
                add_object(actor_direct, component.get_editor_property("skeletal_mesh_asset"))
            except Exception:
                pass
        try:
            for material in component.get_materials():
                add_object(actor_direct, material)
        except Exception:
            pass

    for property_name in ("landscape_material", "landscape_hole_material"):
        try:
            add_object(actor_direct, actor.get_editor_property(property_name))
        except Exception:
            pass

    direct_packages.update(actor_direct)
    relevant = sorted(name for name in actor_direct if name.startswith(PACK_PREFIXES + MAP_PREFIXES))
    if relevant:
        actor_records.append(
            {
                "label": actor.get_actor_label(),
                "class": actor.get_class().get_name(),
                "actor_package": actor_package,
                "direct_references": relevant,
            }
        )

dependency_errors = []
queue = collections.deque(sorted(direct_packages))
visited = set()
all_dependencies = set(direct_packages)
edges = 0
while queue:
    current = queue.popleft()
    if current in visited:
        continue
    visited.add(current)
    for dependency in dependencies(current):
        edges += 1
        if not dependency.startswith("/Game/"):
            continue
        if dependency not in all_dependencies:
            all_dependencies.add(dependency)
        if dependency.startswith(PACK_PREFIXES + MAP_PREFIXES) and dependency not in visited:
            queue.append(dependency)

required_pack_packages = sorted(name for name in all_dependencies if name.startswith(PACK_PREFIXES))
required_map_packages = sorted(name for name in all_dependencies if name.startswith(MAP_PREFIXES))

file_records = []
missing_files = []
for name in required_pack_packages:
    files = package_files(name)
    if not files:
        missing_files.append(name)
        continue
    for filename in files:
        file_records.append(
            {
                "package": name,
                "file": os.path.relpath(filename, common.project_directory()).replace("\\", "/"),
                "bytes": os.path.getsize(filename),
            }
        )

summary_by_root = {}
for prefix in PACK_PREFIXES:
    records = [record for record in file_records if record["package"].startswith(prefix)]
    summary_by_root[prefix] = {
        "package_count": len({record["package"] for record in records}),
        "file_count": len(records),
        "bytes": sum(record["bytes"] for record in records),
        "files_over_100mb": sum(1 for record in records if record["bytes"] > 100_000_000),
    }

payload = {
    "schema_version": 1,
    "status": "read_only_level_dependency_closure_complete",
    "context": context,
    "actor_count": len(actors),
    "actors_with_relevant_direct_references": actor_records,
    "direct_package_count": len(direct_packages),
    "visited_package_count": len(visited),
    "dependency_edge_count": edges,
    "required_pack_package_count": len(required_pack_packages),
    "required_map_package_count": len(required_map_packages),
    "required_pack_packages": required_pack_packages,
    "required_map_packages": required_map_packages,
    "required_pack_files": sorted(file_records, key=lambda item: item["file"]),
    "required_pack_summary": summary_by_root,
    "missing_required_pack_files": missing_files,
    "dependency_errors": dependency_errors,
    "changes_made": False,
}

report = common.write_json_report(config, "old_town_level_dependency_closure_v1.json", payload)
unreal.log(
    "SUNSCAR_DEPENDENCY_CLOSURE actors=%d packages=%d files=%d bytes=%d over100=%d errors=%d report=%s"
    % (
        len(actors),
        len(required_pack_packages),
        len(file_records),
        sum(record["bytes"] for record in file_records),
        sum(1 for record in file_records if record["bytes"] > 100_000_000),
        len(dependency_errors),
        report,
    )
)
print("SUNSCAR_DEPENDENCY_CLOSURE", report)
