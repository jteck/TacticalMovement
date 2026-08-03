"""Read-only probe of Unreal Python Rotator positional constructor order."""

import unreal

r = unreal.Rotator(1.0, 2.0, 3.0)
unreal.log("SUNSCAR_ROTATOR_PROBE roll=%.1f pitch=%.1f yaw=%.1f" % (r.roll, r.pitch, r.yaw))
print("SUNSCAR_ROTATOR_PROBE", r.roll, r.pitch, r.yaw)
