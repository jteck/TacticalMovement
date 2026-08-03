import unreal

ITEMS = [
    (
        r"/var/folders/l5/kcv4w0k15w3dbktdr2jkmp3h0000gn/T/FabLibrary/1cc000de-5422-4ae9-8b54-ed0e53cdbb94/military_trenches_barrier_sandbag_canvas_square_02_ydznbff_ue_mid_extracted/SM_ydznbff_tier_2.gltf",
        "/Game/Maps/Sunscar/Art/Quixel/SandbagsSquare",
    ),
    (
        r"/var/folders/l5/kcv4w0k15w3dbktdr2jkmp3h0000gn/T/FabLibrary/b303f5a1-42da-460c-a14c-4022f447f8dd/military_trenches_wall_metal_corrugated_06_ydxnbdns_ue_mid_extracted/SM_ydxnbdns_tier_2.gltf",
        "/Game/Maps/Sunscar/Art/Quixel/CorrugatedBarrier",
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
    unreal.log("SUNSCAR_QUX_MULTI_IMPORT=" + repr(list(task.imported_object_paths)))
print("SUNSCAR_QUX_MULTI_IMPORT", sum(len(task.imported_object_paths) for task in tasks))
