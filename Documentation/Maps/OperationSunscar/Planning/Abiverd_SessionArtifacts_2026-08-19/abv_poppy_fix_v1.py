# ABV poppy field — repair instance coords to actor-local space.
# Runs INSIDE the Unreal editor (Output Log -> Python), NOT over the MCP bridge.
# Bridge set_properties on perInstanceSMData is the documented OOM bomb (handoff s14).
import unreal, json, math

LABEL   = "ABV_Abiverd_PoppyField_South_V1"
SRC     = "/tmp/poppy_fixed_instances.json"   # local-space transforms, precomputed
CHUNK   = 500

def log(m): unreal.log("[ABV_POPPY] %s" % m)

# ---- 1. locate the actor -------------------------------------------------
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == LABEL:
        actor = a; break
if actor is None:
    log("FAIL: actor %s not found (is the WP region loaded?)" % LABEL); raise SystemExit

org = actor.get_actor_location()
log("actor found. origin = (%.1f, %.1f, %.1f)" % (org.x, org.y, org.z))

hisms = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
if not hisms:
    log("FAIL: no HISM component on actor"); raise SystemExit
h = hisms[0]
log("HISM '%s' currently holds %d instances" % (h.get_name(), h.get_instance_count()))

b_min, b_max = actor.get_actor_bounds(False)
log("bounds BEFORE: centre=(%.1f,%.1f,%.1f) extent=(%.1f,%.1f,%.1f)"
    % (b_min.x, b_min.y, b_min.z, b_max.x, b_max.y, b_max.z))

# ---- 2. load + decompose precomputed local transforms --------------------
raw = json.load(open(SRC))
log("loaded %d local-space transforms from %s" % (len(raw), SRC))

transforms = []
non_yaw = 0
for e in raw:
    t  = e["transform"]
    xp, yp, zp, wp = t["xPlane"], t["yPlane"], t["zPlane"], t["wPlane"]
    sx = math.sqrt(xp["x"]**2 + xp["y"]**2 + xp["z"]**2)
    sy = math.sqrt(yp["x"]**2 + yp["y"]**2 + yp["z"]**2)
    sz = math.sqrt(zp["x"]**2 + zp["y"]**2 + zp["z"]**2)
    if abs(xp["z"]) > 1e-6 or abs(yp["z"]) > 1e-6 or abs(zp["x"]) > 1e-6 or abs(zp["y"]) > 1e-6:
        non_yaw += 1
    yaw = math.degrees(math.atan2(xp["y"] / sx, xp["x"] / sx))
    transforms.append(unreal.Transform(
        location = unreal.Vector(wp["x"], wp["y"], wp["z"]),
        rotation = unreal.Rotator(0.0, 0.0, yaw),
        scale    = unreal.Vector(sx, sy, sz)))

if non_yaw:
    log("WARN: %d instances had non-yaw rotation; yaw-only decomposition is lossy for those" % non_yaw)
else:
    log("all instances are yaw-only - decomposition is exact")

zs = [t.translation.z for t in transforms]
log("local Z range %.1f .. %.1f (expect roughly -115 .. +13)" % (min(zs), max(zs)))

# ---- 3. rewrite, batched -------------------------------------------------
h.clear_instances()
log("cleared. adding %d in chunks of %d ..." % (len(transforms), CHUNK))
added = 0
for i in range(0, len(transforms), CHUNK):
    batch = transforms[i:i + CHUNK]
    h.add_instances(batch, False, False)   # world_space=False -> ACTOR-LOCAL
    added += len(batch)
    log("  %d / %d" % (added, len(transforms)))

log("final instance count = %d" % h.get_instance_count())

# ---- 4. verify -----------------------------------------------------------
b_min2, b_max2 = actor.get_actor_bounds(False)
log("bounds AFTER: min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)"
    % (b_min2.x, b_min2.y, b_min2.z, b_max2.x, b_max2.y, b_max2.z))
ok = (b_max2.z < 35200.0)
log("VERDICT: %s (max Z %.1f; broken version was 69885)" % ("FIXED" if ok else "STILL BROKEN", b_max2.z))
log("NOT saved by this script - save via the bridge (AssetTools.save_assets) after verifying.")
