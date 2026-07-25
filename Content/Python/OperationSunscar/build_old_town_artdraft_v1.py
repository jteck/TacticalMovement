import unreal

LEVEL="/Game/Maps/Blockout/Lvl_Blockout_01"
TAG="SunscarOldTownArtDraftV1"
ROOT="OldTown_ArtDraft"
CM=100.0
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if level.get_current_level().get_outermost().get_name()!=LEVEL:
    raise RuntimeError("Wrong level; expected "+LEVEL)

cube=unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_Cube")
chamfer=unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_ChamferCube")
cylinder=unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_Cylinder")
src="/Game/LevelPrototyping/Materials/MI_DefaultColorway"
mat_root="/Game/Maps/Sunscar/Art/Materials/Instances"
unreal.EditorAssetLibrary.make_directory(mat_root)
colors={
"WarmStucco":(0.50,0.34,0.19,0.0,0.78),
"PaleStucco":(0.68,0.58,0.42,0.0,0.74),
"Stone":(0.34,0.29,0.23,0.0,0.88),
"Timber":(0.12,0.075,0.045,0.0,0.72),
"Glass":(0.08,0.18,0.22,0.15,0.34),
"Canvas":(0.38,0.24,0.12,0.0,0.94),
"RustCanvas":(0.38,0.11,0.045,0.0,0.90),
"Metal":(0.23,0.25,0.25,0.72,0.43),
"Detention":(0.22,0.29,0.22,0.0,0.82),
"Accent":(0.055,0.31,0.31,0.0,0.63)}
mats={}
for key,v in colors.items():
    path=mat_root+"/MI_OT_"+key
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.duplicate_asset(src,path)
    mi=unreal.EditorAssetLibrary.load_asset(path)
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi,"Base Color",unreal.LinearColor(v[0],v[1],v[2],1))
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,"Metallic",v[3])
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,"Roughness",v[4])
    unreal.EditorAssetLibrary.save_loaded_asset(mi,only_if_is_dirty=False)
    mats[key]=mi

for a in list(actors.get_all_level_actors()):
    if any(str(t)==TAG for t in a.tags):
        actors.destroy_actor(a)

sizes={}
def msize(mesh):
    p=mesh.get_path_name()
    if p not in sizes:
        e=mesh.get_bounds().box_extent
        sizes[p]=unreal.Vector(e.x*2,e.y*2,e.z*2)
    return sizes[p]

created=[]
def spawn(name,site,folder,x,y,z,dims,mat,mesh=None):
    if mesh is None: mesh=cube
    a=actors.spawn_actor_from_object(mesh,unreal.Vector(x*CM,y*CM,z),unreal.Rotator(),transient=False)
    s=msize(mesh)
    a.set_actor_scale3d(unreal.Vector(dims[0]*CM/s.x,dims[1]*CM/s.y,dims[2]*CM/s.z))
    a.set_actor_label(name)
    a.tags=[unreal.Name(TAG),unreal.Name(site),unreal.Name("SunscarMapOwned")]
    try: a.set_folder_path(unreal.Name(ROOT+"/"+folder))
    except Exception: pass
    a.static_mesh_component.set_material(0,mats[mat])
    created.append(a)
    return a

specs={
"SS_004":("TeaHouse",-88.,-29.,18.,16.,3.2),
"SS_007":("MunicipalHotel",-14.,27.,28.,22.,9.6),
"SS_008":("CentralCourtyard",-18.,-31.,34.,28.,0.2),
"SS_010":("DetentionAnnex",22.,91.,34.,28.,6.4),
"SS_017":("CoveredBazaar",28.,-93.,36.,17.,3.4)}
data={}
all_actors=actors.get_all_level_actors()
for sid,(name,cx,cy,w,d,h) in specs.items():
    marker=next((a for a in all_actors if a.get_actor_label().startswith(sid+"_")),None)
    if marker is None: raise RuntimeError("Missing loaded marker "+sid)
    data[sid]={"name":name,"cx":cx,"cy":cy,"w":w,"d":d,"h":h,"base":marker.get_actor_location().z-h*50.0}

def box(name,sid,x,y,zc,dims,mat,mesh=None):
    s=data[sid]
    return spawn(name,sid,s["name"],x,y,s["base"]+zc*CM,dims,mat,mesh)

def parapet(sid,mat):
    s=data[sid]; z=s["h"]+.4
    box(sid+"_Parapet_N",sid,s["cx"],s["cy"]+s["d"]/2,z,(s["w"],.3,.8),mat)
    box(sid+"_Parapet_S",sid,s["cx"],s["cy"]-s["d"]/2,z,(s["w"],.3,.8),mat)
    box(sid+"_Parapet_E",sid,s["cx"]+s["w"]/2,s["cy"],z,(.3,s["d"],.8),mat)
    box(sid+"_Parapet_W",sid,s["cx"]-s["w"]/2,s["cy"],z,(.3,s["d"],.8),mat)

def win_y(sid,name,x,y,z,out):
    box(name+"_Frame",sid,x,y,z,(1.65,.16,1.45),"Timber")
    box(name+"_Glass",sid,x,y+out*.1,z,(1.28,.08,1.08),"Glass")
def win_x(sid,name,x,y,z,out):
    box(name+"_Frame",sid,x,y,z,(.16,1.65,1.45),"Timber")
    box(name+"_Glass",sid,x+out*.1,y,z,(.08,1.28,1.08),"Glass")
def door(sid,name,x,y,out,mat="Timber"):
    box(name,sid,x,y+out*.12,1.2,(1.25,.18,2.4),mat)

# Municipal Hotel
parapet("SS_007","PaleStucco")
s=data["SS_007"]; sy=s["cy"]-s["d"]/2-.16; ny=s["cy"]+s["d"]/2+.16
for floor,z in enumerate((1.85,5.05,8.25),1):
    for i,x in enumerate((-24.,-19.,-14.,-9.,-4.),1): win_y("SS_007","Hotel_F%d_S_%02d"%(floor,i),x,sy,z,-1)
    for i,x in enumerate((-22.,-14.,-6.),1): win_y("SS_007","Hotel_F%d_N_%02d"%(floor,i),x,ny,z,1)
    win_x("SS_007","Hotel_F%d_E"%floor,s["cx"]+s["w"]/2+.16,s["cy"],z,1)
    win_x("SS_007","Hotel_F%d_W"%floor,s["cx"]-s["w"]/2-.16,s["cy"],z,-1)
for x in (-20.,-14.,-8.): door("SS_007","Hotel_Door_"+str(int(x)),x,sy,-1)
box("Hotel_Balcony_Deck","SS_007",-14.,sy-.85,4.05,(13.,1.8,.22),"Metal")
box("Hotel_Balcony_Rail","SS_007",-14.,sy-1.65,4.65,(13.,.1,1.2),"Metal")
box("Hotel_Municipal_Sign","SS_007",-14.,sy-.18,6.95,(3.8,.14,.85),"Accent")

# Central Courtyard
s=data["SS_008"]
box("Courtyard_Low_Focus","SS_008",s["cx"],s["cy"],.28,(3.6,3.6,.56),"Stone",cylinder)
for i,(x,y,sx,sy2) in enumerate(((-31,-42,2.8,.55),(-5,-42,2.8,.55),(-31,-20,2.8,.55),(-5,-20,2.8,.55),(-34,-35,.7,2.2),(-2,-27,.7,2.2)),1):
    box("Courtyard_Bench_%02d"%i,"SS_008",x,y,.38,(sx,sy2,.76),"Timber")
for i,(x,y) in enumerate(((-32,-43),(-4,-43),(-32,-19),(-4,-19)),1):
    box("Courtyard_Planter_%02d"%i,"SS_008",x,y,.45,(1.2,1.2,.9),"WarmStucco",chamfer)

# Tea House
parapet("SS_004","WarmStucco")
s=data["SS_004"]; sy=s["cy"]-s["d"]/2-.16
for i,x in enumerate((-94.,-88.,-82.),1): win_y("SS_004","Tea_Window_%02d"%i,x,sy,1.75,-1)
door("SS_004","Tea_MainDoor",-88.,sy,-1)
box("Tea_House_Sign","SS_004",-88.,sy-.18,2.75,(3.0,.14,.7),"Accent")
box("Tea_Canopy","SS_004",-88.,sy-2.,2.78,(6.5,3.6,.1),"Canvas")
for i,(x,y) in enumerate(((-91,sy-3.5),(-85,sy-3.5),(-91,sy-.5),(-85,sy-.5)),1):
    box("Tea_Pole_%02d"%i,"SS_004",x,y,1.45,(.12,.12,2.9),"Metal")
for i,(x,y) in enumerate(((-90.5,sy-2.1),(-85.5,sy-2.1)),1):
    box("Tea_Table_%02d"%i,"SS_004",x,y,.72,(1.2,.75,.12),"Timber")
    box("Tea_Bench_%02dA"%i,"SS_004",x,y-.75,.45,(1.5,.42,.55),"Timber")
    box("Tea_Bench_%02dB"%i,"SS_004",x,y+.75,.45,(1.5,.42,.55),"Timber")

# Covered Bazaar, two rows and clear central passage
for row,y in (("N",-87.4),("S",-98.6)):
    for i,x in enumerate((16.,24.,32.,40.),1):
        canvas="Canvas" if (i+(row=="S"))%2 else "RustCanvas"
        box("Bazaar_%s_Stall_%02d"%(row,i),"SS_017",x,y,1.2,(3.2,2.5,2.4),"Timber")
        box("Bazaar_%s_Canopy_%02d"%(row,i),"SS_017",x,y,2.72,(3.7,3.,.1),canvas)
        box("Bazaar_%s_Sign_%02d"%(row,i),"SS_017",x,y+(1.36 if row=="N" else -1.36),2.05,(1.35,.1,.55),"Accent")
for i,(x,y) in enumerate(((14,-85.9),(42,-85.9),(14,-100.1),(42,-100.1)),1):
    box("Bazaar_Pole_%02d"%i,"SS_017",x,y,1.5,(.12,.12,3.),"Metal")

# Detention Annex
parapet("SS_010","Detention")
s=data["SS_010"]; sy=s["cy"]-s["d"]/2-.16
for floor,z in enumerate((1.85,5.05),1):
    for i,x in enumerate((10.,16.,22.,28.,34.),1): win_y("SS_010","Detention_F%d_Win_%02d"%(floor,i),x,sy,z,-1)
for x,mat in ((12.,"Timber"),(22.,"Accent"),(32.,"Metal")): door("SS_010","Detention_Door_"+str(int(x)),x,sy,-1,mat)
for c,(cx,cy) in enumerate(((8.,75.),(36.,75.)),1):
    for i in range(6):
        box("Detention_Fort_%d_%02d"%(c,i+1),"SS_010",cx+(i%3)*1.05,cy+(i//3)*.48,.22,(1.1,.48,.44),"Canvas",chamfer)

unreal.log("SUNSCAR_ARTDRAFT_V1 actors=%d materials=%d"%(len(created),len(mats)))
print("SUNSCAR_ARTDRAFT_V1",len(created),len(mats))
