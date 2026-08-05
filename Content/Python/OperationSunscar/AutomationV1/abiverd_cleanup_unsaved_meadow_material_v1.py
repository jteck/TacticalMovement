"""Remove only the unsaved partial Abiverd Landscape V3 material shell."""

import unreal


TARGET = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd"
dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if dirty != [TARGET]:
    raise RuntimeError("ABIVERD_MEADOW_MATERIAL_CLEANUP_SCOPE " + "|".join(dirty))
if not unreal.EditorAssetLibrary.does_asset_exist(TARGET):
    raise RuntimeError("ABIVERD_MEADOW_MATERIAL_CLEANUP_MISSING")
if not unreal.EditorAssetLibrary.delete_asset(TARGET):
    raise RuntimeError("ABIVERD_MEADOW_MATERIAL_CLEANUP_FAILED")
remaining = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if remaining:
    raise RuntimeError("ABIVERD_MEADOW_MATERIAL_CLEANUP_DIRTY_AFTER " + "|".join(remaining))
unreal.log("ABIVERD_MEADOW_MATERIAL_CLEANUP complete")
print("ABIVERD_MEADOW_MATERIAL_CLEANUP")
