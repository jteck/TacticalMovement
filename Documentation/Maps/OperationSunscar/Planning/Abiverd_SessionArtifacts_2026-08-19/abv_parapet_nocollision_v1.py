# Abiverd SS_* obsolete parapet collision neutralisation
# One-shot bounded script. Run from the Unreal Output Log in Python mode:
#   exec(open(r"/private/tmp/abv_parapet_nocollision_v1.py").read())
#
# Scope: exactly the 28 obsolete parapets already hidden, shadowless,
# nav-irrelevant and tagged SunscarOldTownObsoleteArchitectureHiddenV1.
# SS_003 is DELIBERATELY EXCLUDED - its four are visible, 0 cm overhang,
# and are that building's only parapets.

import unreal

SITES = ["SS_004", "SS_005", "SS_007", "SS_010", "SS_011", "SS_012", "SS_018"]
DIRS = ["N", "S", "E", "W"]
TARGETS = {f"{s}_Parapet_{d}" for s in SITES for d in DIRS}
GUARD_TAG = "SunscarOldTownObsoleteArchitectureHiddenV1"

subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
changed, skipped, packages = [], [], []

for actor in subsys.get_all_level_actors():
    label = actor.get_actor_label()
    if label not in TARGETS:
        continue
    # Safety gate: only touch actors carrying the obsolete tag
    if GUARD_TAG not in [str(t) for t in actor.tags]:
        skipped.append((label, "missing guard tag"))
        continue
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if comp is None:
        skipped.append((label, "no static mesh component"))
        continue
    if comp.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION:
        skipped.append((label, "already NoCollision"))
        continue
    actor.modify()
    comp.modify()
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    changed.append(label)
    packages.append(actor.get_outermost())

if packages:
    unreal.EditorLoadingAndSavingUtils.save_packages(packages, False)

unreal.log("ABV_PARAPET_NOCOLLISION changed=%d skipped=%d" % (len(changed), len(skipped)))
for l in changed:
    unreal.log("  CHANGED %s" % l)
for l, why in skipped:
    unreal.log("  SKIPPED %s (%s)" % (l, why))

# Verify by reading back
bad = []
for actor in subsys.get_all_level_actors():
    if actor.get_actor_label() in TARGETS:
        c = actor.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
            bad.append(actor.get_actor_label())
unreal.log("ABV_PARAPET_NOCOLLISION verify_remaining_with_collision=%d %s" % (len(bad), bad))
