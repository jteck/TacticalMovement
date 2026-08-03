"""Read-only probe for dirty-state methods on in-memory Unreal packages."""

import unreal

maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
methods = sorted(name for name in dir(maps[0]) if "dirty" in name.lower()) if maps else []
existence = {package.get_name(): unreal.EditorAssetLibrary.does_asset_exist(package.get_name()) for package in maps}
unreal.log("SUNSCAR_PACKAGE_DIRTY_API %s" % ",".join(methods))
unreal.log("SUNSCAR_PACKAGE_EXISTENCE %s" % existence)
print("SUNSCAR_PACKAGE_DIRTY_API", methods, existence)
