"""Start a local PIE session for Old Town player-height review."""

import unreal


subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
available = sorted(name for name in dir(subsystem) if "play" in name.lower())
unreal.log("SUNSCAR_PIE_METHODS " + " | ".join(available))
if subsystem.is_in_play_in_editor():
    subsystem.editor_request_end_play()
if hasattr(subsystem, "editor_request_begin_play"):
    subsystem.editor_request_begin_play()
else:
    raise RuntimeError("SUNSCAR_PIE_START_BLOCKED editor_request_begin_play unavailable")
unreal.log("SUNSCAR_PIE_START_REQUESTED")
print("SUNSCAR_PIE_START_REQUESTED")
