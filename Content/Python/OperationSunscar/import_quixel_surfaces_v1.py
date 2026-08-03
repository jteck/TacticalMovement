import unreal

ITEMS = [
    (
        r"/var/folders/l5/kcv4w0k15w3dbktdr2jkmp3h0000gn/T/FabLibrary/9485cd8b-02f5-42c0-9cfd-097b5b7b7f55/weathered_concrete_wall_vi4idbm_2k_ue_mid_extracted/vi4idbm_tier_2.gltf",
        "/Game/Maps/Sunscar/Art/Quixel/Surfaces/WeatheredConcrete",
    ),
    (
        r"/var/folders/l5/kcv4w0k15w3dbktdr2jkmp3h0000gn/T/FabLibrary/261cf6b0-2810-4482-9c90-a0a175c7815f/damaged_plaster_patch_vdekajsfw_2k_ue_mid_extracted/vdekajsfw_tier_2.gltf",
        "/Game/Maps/Sunscar/Art/Quixel/Damage/DamagedPlaster",
    ),
]
tasks = []
for source, dest in ITEMS:
    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = dest
    task.automated = True
    task.replace_existing = False
    task.save = True
    tasks.append(task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for task in tasks:
    unreal.log("SUNSCAR_QUX_SURFACE_IMPORT=" + repr(list(task.imported_object_paths)))
print("SUNSCAR_QUX_SURFACE_IMPORT", sum(len(task.imported_object_paths) for task in tasks))
