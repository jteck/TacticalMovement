"""End the local PIE session after Old Town player-height review."""

import unreal


subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if subsystem.is_in_play_in_editor():
    subsystem.editor_request_end_play()
unreal.log("SUNSCAR_PIE_END_REQUESTED")
print("SUNSCAR_PIE_END_REQUESTED")
