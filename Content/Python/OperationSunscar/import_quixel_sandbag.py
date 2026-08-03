import unreal
SOURCE = r"/var/folders/l5/kcv4w0k15w3dbktdr2jkmp3h0000gn/T/FabLibrary/a5ad6a23-7e37-4b3c-ae91-063e8a4e0fd2/military_trenches_barrier_sandbag_canvas_worn_ydxlcck_ue_mid_extracted/SM_ydxlcck_tier_2.gltf"
DEST = "/Game/Maps/Sunscar/Art/Quixel/Sandbags"
task = unreal.AssetImportTask()
task.filename = SOURCE
task.destination_path = DEST
task.automated = True
task.replace_existing = False
task.save = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
unreal.log("SUNSCAR_QUX_IMPORT=" + repr(list(task.imported_object_paths)))
