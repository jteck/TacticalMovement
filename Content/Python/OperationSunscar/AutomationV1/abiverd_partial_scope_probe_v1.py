"""Read-only scope probe after a failed unsaved Abiverd preview."""

import json
import os

import unreal


tags = {
    unreal.Name("SunscarAbiverdHeritageCompositionV1"),
    unreal.Name("SunscarAbiverdVegetationHISMV1"),
}
actors = [
    actor for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    if any(tag in list(actor.tags) for tag in tags)
]
dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "tagged_actors": [
        {"label": actor.get_actor_label(), "package": actor.get_package().get_name()}
        for actor in actors
    ],
    "dirty_packages": dirty,
    "changes_made": False,
}
path = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", "abiverd_partial_scope_probe_v1.json"
)
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_PARTIAL_SCOPE actors=%d dirty=%d" % (len(actors), len(dirty)))
