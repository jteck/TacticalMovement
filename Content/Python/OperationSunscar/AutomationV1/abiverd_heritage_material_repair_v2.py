"""Repair Abiverd scan and foliage materials using map-owned UE 5.8 masters."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
HERITAGE_ROOT = "/Game/Maps/Sunscar/Art/Heritage"
MATERIAL_ROOT = HERITAGE_ROOT + "/Materials"
SCAN_MASTER_PATH = MATERIAL_ROOT + "/M_ABV_HeritageScan_PBR"
FOLIAGE_MASTER_PATH = MATERIAL_ROOT + "/M_ABV_Foliage_Masked"
REPORT_NAME = "abiverd_heritage_material_repair_v2.json"

ARCHITECTURE = (
    {
        "folder": HERITAGE_ROOT + "/Architecture/ArchStoneCarved08",
        "material": "MI_ABV_ArchStoneCarved08",
        "max_size": 4096,
    },
    {
        "folder": HERITAGE_ROOT + "/Architecture/WallModularSet04",
        "material": "MI_ABV_WallModularSet04",
        "max_size": 2048,
    },
    {
        "folder": HERITAGE_ROOT + "/Architecture/StructureStoneS06",
        "material": "MI_ABV_StructureStoneS06",
        "max_size": 2048,
    },
)

FOLIAGE = (
    {
        "folder": HERITAGE_ROOT + "/Foliage/FieldPoppy",
        "slug": "FieldPoppy",
        "tint": (1.0, 1.0, 1.0),
    },
    {
        "folder": HERITAGE_ROOT + "/Foliage/WildGrass",
        "slug": "WildGrass",
        "tint": (0.82, 0.94, 0.76),
    },
)


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


def expression(material, expression_class, x, y):
    value = unreal.MaterialEditingLibrary.create_material_expression(material, expression_class, x, y)
    if value is None:
        raise RuntimeError("ABIVERD_MATERIAL_V2_EXPRESSION " + expression_class.__name__)
    return value


def connect(source, output_name, destination, input_name):
    if not unreal.MaterialEditingLibrary.connect_material_expressions(
        source, output_name, destination, input_name
    ):
        raise RuntimeError("ABIVERD_MATERIAL_V2_CONNECT " + input_name)


def output(source, output_name, material_property):
    if not unreal.MaterialEditingLibrary.connect_material_property(
        source, output_name, material_property
    ):
        raise RuntimeError("ABIVERD_MATERIAL_V2_OUTPUT " + str(material_property))


def load_texture(path):
    value = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(value, unreal.Texture2D):
        raise RuntimeError("ABIVERD_MATERIAL_V2_TEXTURE " + path)
    return value


def sampler(texture, ordinary, virtual):
    return virtual if bool(texture.get_editor_property("virtual_texture_streaming")) else ordinary


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_MATERIAL_V2_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_MATERIAL_V2_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_MATERIAL_V2_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_MATERIAL_V2_DIRTY_BEFORE " + "|".join(dirty_packages()))

unreal.EditorAssetLibrary.make_directory(MATERIAL_ROOT)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

architecture_records = []
architecture_assets = []
role_defaults = None
for definition in ARCHITECTURE:
    assets = [
        unreal.EditorAssetLibrary.load_asset(path)
        for path in unreal.EditorAssetLibrary.list_assets(definition["folder"], recursive=False)
    ]
    meshes = [item for item in assets if isinstance(item, unreal.StaticMesh)]
    textures = [item for item in assets if isinstance(item, unreal.Texture2D)]
    if len(meshes) != 1 or len(textures) != 4:
        raise RuntimeError(
            "ABIVERD_MATERIAL_V2_ARCH_SCOPE %s meshes=%d textures=%d"
            % (definition["folder"], len(meshes), len(textures))
        )
    roles = {}
    for texture in textures:
        lower = texture.get_name().lower()
        if "basecolor" in lower:
            roles["BaseColor"] = texture
        elif "_normal" in lower:
            roles["Normal"] = texture
        elif "roughness" in lower:
            roles["Roughness"] = texture
        elif "_ao" in lower:
            roles["AO"] = texture
    if set(roles) != {"BaseColor", "Normal", "Roughness", "AO"}:
        raise RuntimeError("ABIVERD_MATERIAL_V2_ARCH_ROLES " + definition["folder"])
    virtual_states = {role: bool(texture.get_editor_property("virtual_texture_streaming")) for role, texture in roles.items()}
    if role_defaults is None:
        role_defaults = roles
        default_virtual_states = virtual_states
    elif virtual_states != default_virtual_states:
        raise RuntimeError("ABIVERD_MATERIAL_V2_ARCH_VT_MISMATCH " + definition["folder"])
    architecture_assets.append((definition, meshes[0], roles))

scan_master = unreal.EditorAssetLibrary.load_asset(SCAN_MASTER_PATH)
if scan_master is None:
    scan_master = asset_tools.create_asset(
        SCAN_MASTER_PATH.rsplit("/", 1)[1], MATERIAL_ROOT, unreal.Material, unreal.MaterialFactoryNew()
    )
if not isinstance(scan_master, unreal.Material):
    raise RuntimeError("ABIVERD_MATERIAL_V2_SCAN_MASTER")
scan_master.modify()
unreal.MaterialEditingLibrary.delete_all_material_expressions(scan_master)
scan_master.set_editor_properties(
    {"blend_mode": unreal.BlendMode.BLEND_OPAQUE, "two_sided": False, "tangent_space_normal": True}
)

base = expression(scan_master, unreal.MaterialExpressionTextureSampleParameter2D, -650, -300)
base.set_editor_properties(
    {
        "parameter_name": unreal.Name("BaseColor"),
        "texture": role_defaults["BaseColor"],
        "sampler_type": sampler(
            role_defaults["BaseColor"],
            unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
            unreal.MaterialSamplerType.SAMPLERTYPE_VIRTUAL_COLOR,
        ),
    }
)
normal = expression(scan_master, unreal.MaterialExpressionTextureSampleParameter2D, -650, -80)
normal.set_editor_properties(
    {
        "parameter_name": unreal.Name("Normal"),
        "texture": role_defaults["Normal"],
        "sampler_type": sampler(
            role_defaults["Normal"],
            unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
            unreal.MaterialSamplerType.SAMPLERTYPE_VIRTUAL_NORMAL,
        ),
    }
)
roughness = expression(scan_master, unreal.MaterialExpressionTextureSampleParameter2D, -650, 140)
roughness.set_editor_properties(
    {
        "parameter_name": unreal.Name("Roughness"),
        "texture": role_defaults["Roughness"],
        "sampler_type": sampler(
            role_defaults["Roughness"],
            unreal.MaterialSamplerType.SAMPLERTYPE_MASKS,
            unreal.MaterialSamplerType.SAMPLERTYPE_VIRTUAL_MASKS,
        ),
    }
)
ao = expression(scan_master, unreal.MaterialExpressionTextureSampleParameter2D, -650, 360)
ao.set_editor_properties(
    {
        "parameter_name": unreal.Name("AO"),
        "texture": role_defaults["AO"],
        "sampler_type": sampler(
            role_defaults["AO"],
            unreal.MaterialSamplerType.SAMPLERTYPE_MASKS,
            unreal.MaterialSamplerType.SAMPLERTYPE_VIRTUAL_MASKS,
        ),
    }
)
output(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
output(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
output(roughness, "R", unreal.MaterialProperty.MP_ROUGHNESS)
output(ao, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
scan_compile = list(unreal.MaterialEditingLibrary.recompile_material(scan_master))
if scan_compile:
    raise RuntimeError("ABIVERD_MATERIAL_V2_SCAN_COMPILE " + "|".join(str(item) for item in scan_compile))

for definition, mesh, roles in architecture_assets:
    material_path = definition["folder"] + "/" + definition["material"]
    material = unreal.EditorAssetLibrary.load_asset(material_path)
    if not isinstance(material, unreal.MaterialInstanceConstant):
        raise RuntimeError("ABIVERD_MATERIAL_V2_ARCH_MI " + material_path)
    material.modify()
    material.set_editor_property("parent", scan_master)
    for role, texture in roles.items():
        texture.modify()
        texture.set_editor_property("max_texture_size", int(definition["max_size"]))
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, role, texture)
    unreal.MaterialEditingLibrary.update_material_instance(material)
    mesh.modify()
    nanite = mesh.get_editor_property("nanite_settings")
    nanite.enabled = True
    mesh.set_editor_property("nanite_settings", nanite)
    mesh.set_material(0, material)
    architecture_records.append(
        {
            "mesh": mesh.get_path_name(),
            "material": material.get_path_name(),
            "nanite": bool(mesh.get_editor_property("nanite_settings").enabled),
            "max_texture_size": definition["max_size"],
            "textures": {role: texture.get_path_name() for role, texture in roles.items()},
        }
    )

foliage_defaults = {
    "BaseColor": load_texture(FOLIAGE[0]["folder"] + "/T_FieldPoppy_BaseColor"),
    "Normal": load_texture(FOLIAGE[0]["folder"] + "/T_FieldPoppy_Normal"),
    "Mask": load_texture(FOLIAGE[0]["folder"] + "/T_FieldPoppy_Mask"),
}
foliage_master = unreal.EditorAssetLibrary.load_asset(FOLIAGE_MASTER_PATH)
if foliage_master is None:
    foliage_master = asset_tools.create_asset(
        FOLIAGE_MASTER_PATH.rsplit("/", 1)[1], MATERIAL_ROOT, unreal.Material, unreal.MaterialFactoryNew()
    )
if not isinstance(foliage_master, unreal.Material):
    raise RuntimeError("ABIVERD_MATERIAL_V2_FOLIAGE_MASTER")
foliage_master.modify()
unreal.MaterialEditingLibrary.delete_all_material_expressions(foliage_master)
foliage_master.set_editor_properties(
    {
        "blend_mode": unreal.BlendMode.BLEND_MASKED,
        "two_sided": True,
        "tangent_space_normal": True,
        "opacity_mask_clip_value": 0.42,
    }
)
f_base = expression(foliage_master, unreal.MaterialExpressionTextureSampleParameter2D, -650, -260)
f_base.set_editor_properties(
    {
        "parameter_name": unreal.Name("BaseColorTexture"),
        "texture": foliage_defaults["BaseColor"],
        "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,
    }
)
f_tint = expression(foliage_master, unreal.MaterialExpressionVectorParameter, -650, -60)
f_tint.set_editor_properties(
    {"parameter_name": unreal.Name("ColorTint"), "default_value": unreal.LinearColor(1.0, 1.0, 1.0, 1.0)}
)
f_multiply = expression(foliage_master, unreal.MaterialExpressionMultiply, -300, -220)
connect(f_base, "RGB", f_multiply, "A")
connect(f_tint, "", f_multiply, "B")
f_normal = expression(foliage_master, unreal.MaterialExpressionTextureSampleParameter2D, -650, 160)
f_normal.set_editor_properties(
    {
        "parameter_name": unreal.Name("NormalTexture"),
        "texture": foliage_defaults["Normal"],
        "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
    }
)
f_mask = expression(foliage_master, unreal.MaterialExpressionTextureSampleParameter2D, -650, 380)
f_mask.set_editor_properties(
    {
        "parameter_name": unreal.Name("Mask"),
        "texture": foliage_defaults["Mask"],
        "sampler_type": unreal.MaterialSamplerType.SAMPLERTYPE_MASKS,
    }
)
f_roughness = expression(foliage_master, unreal.MaterialExpressionConstant, -250, 350)
f_roughness.set_editor_property("r", 0.82)
output(f_multiply, "", unreal.MaterialProperty.MP_BASE_COLOR)
output(f_normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
output(f_mask, "R", unreal.MaterialProperty.MP_OPACITY_MASK)
output(f_roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
foliage_compile = list(unreal.MaterialEditingLibrary.recompile_material(foliage_master))
if foliage_compile:
    raise RuntimeError("ABIVERD_MATERIAL_V2_FOLIAGE_COMPILE " + "|".join(str(item) for item in foliage_compile))

foliage_records = []
for definition in FOLIAGE:
    slug = definition["slug"]
    textures = {
        "BaseColorTexture": load_texture(definition["folder"] + "/T_%s_BaseColor" % slug),
        "NormalTexture": load_texture(definition["folder"] + "/T_%s_Normal" % slug),
        "Mask": load_texture(definition["folder"] + "/T_%s_Mask" % slug),
    }
    for role, texture in textures.items():
        texture.modify()
        texture.set_editor_property("virtual_texture_streaming", False)
        texture.set_editor_property("max_texture_size", 2048)
    material_path = definition["folder"] + "/MI_%s" % slug
    material = unreal.EditorAssetLibrary.load_asset(material_path)
    if not isinstance(material, unreal.MaterialInstanceConstant):
        raise RuntimeError("ABIVERD_MATERIAL_V2_FOLIAGE_MI " + material_path)
    material.modify()
    material.set_editor_property("parent", foliage_master)
    for parameter, texture in textures.items():
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, parameter, texture)
    r, g, b = definition["tint"]
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
        material, "ColorTint", unreal.LinearColor(r, g, b, 1.0)
    )
    unreal.MaterialEditingLibrary.update_material_instance(material)
    meshes = []
    for variant in "ABCDEFGH":
        path = definition["folder"] + "/SM_%s_Var%s" % (slug, variant)
        mesh = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError("ABIVERD_MATERIAL_V2_FOLIAGE_MESH " + path)
        mesh.modify()
        nanite = mesh.get_editor_property("nanite_settings")
        nanite.enabled = False
        mesh.set_editor_property("nanite_settings", nanite)
        mesh.set_material(0, material)
        meshes.append(mesh.get_path_name())
    foliage_records.append({"slug": slug, "material": material.get_path_name(), "meshes": meshes})

dirty_before_save = dirty_packages()
unexpected = [name for name in dirty_before_save if not name.startswith(HERITAGE_ROOT + "/")]
if unexpected:
    raise RuntimeError("ABIVERD_MATERIAL_V2_UNEXPECTED_DIRTY " + "|".join(unexpected))
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_MATERIAL_V2_SAVE_FAILED")
remaining = dirty_packages()
if remaining:
    raise RuntimeError("ABIVERD_MATERIAL_V2_DIRTY_AFTER " + "|".join(remaining))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "schema_version": 2,
            "status": "heritage_material_repair_saved",
            "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
            "scan_master": SCAN_MASTER_PATH,
            "foliage_master": FOLIAGE_MASTER_PATH,
            "architecture": architecture_records,
            "foliage": foliage_records,
            "saved_packages": dirty_before_save,
            "dirty_packages_after": remaining,
        },
        handle,
        indent=2,
    )
    handle.write("\n")

unreal.log("ABIVERD_MATERIAL_V2_COMPLETE saved=%d report=%s" % (len(dirty_before_save), report_path))
print("ABIVERD_MATERIAL_V2_COMPLETE", len(dirty_before_save), report_path)
