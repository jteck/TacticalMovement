import unreal

LEVEL="/Game/Maps/Blockout/Lvl_Blockout_01"
TAG="SunscarOldTownArtDraftV1B"
ROOT="OldTown_ArtDraft"
CM=100.0
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if level.get_current_level().get_outermost().get_name()!=LEVEL:
    raise RuntimeError("Wrong level")

cube=unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_Cube")
chamfer=unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_ChamferCube")
cylinder=unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_Cylinder")
mat_root="/Game/Maps/Sunscar/Art/Materials/Instances"
mat_names=("WarmStucco","PaleStucco","Stone","Timber","Glass","Canvas","RustCanvas","Metal","Detention","Accent")
mats={n:unreal.EditorAssetLibrary.load_asset(mat_root+"/MI_OT_"+n) for n in mat_names}
for a in list(actors.get_all_level_actors()):
    if any(str(t)==TAG for t in a.tags): actors.destroy_actor(a)

sizes={}
def msize(mesh):
    p=mesh.get_path_name()
    if p not in sizes:
        e=mesh.get_bounds().box_extent
        sizes[p]=unreal.Vector(e.x*2,e.y*2,e.z*2)
    return sizes[p]

created=[]
def spawn(name,sid,folder,x,y,z,dims,mat,mesh=None):
    if mesh is None: mesh=cube
    a=actors.spawn_actor_from_object(mesh,unreal.Vector(x*CM,y*CM,z),unreal.Rotator(),transient=False)
    s=msize(mesh)
    a.set_actor_scale3d(unreal.Vector(dims[0]*CM/s.x,dims[1]*CM/s.y,dims[2]*CM/s.z))
    a.set_actor_label(name)
    a.tags=[unreal.Name(TAG),unreal.Name(sid),unreal.Name("SunscarMapOwned")]
    try:a.set_folder_path(unreal.Name(ROOT+"/"+folder))
    except Exception:pass
    a.static_mesh_component.set_material(0,mats[mat])
    created.append(a)
    return a

specs={
"SS_001":("AttackerSpawn",-130.,-99.,20.,18.,.2),
"SS_002":("DryCanalEntrance",-126.,-19.,7.,24.,1.5),
"SS_003":("CanalPumpStation",-106.,-63.,18.,15.,3.2),
"SS_005":("OldClinic",-56.,-1.,24.,19.,6.4),
"SS_006":("WaterTowerCompound",-62.,45.,16.,16.,15.),
"SS_009":("TransitPlaza",6.,-5.,32.,26.,.2),
"SS_011":("CheckpointOffice",74.,51.,20.,17.,6.4),
"SS_012":("ConsulateResidence",118.,49.,21.,18.,6.4),
"SS_013":("FreightDepot",108.,1.,30.,24.,4.2),
"SS_014":("SalvageYard",74.,-17.,44.,35.,2.4),
"SS_015":("MotorPool",128.,-47.,24.,20.,4.2),
"SS_016":("PowerSubstation",60.,-70.,26.,20.,3.2),
"SS_018":("TelecomWorkshop",-56.,-91.,21.,18.,6.4),
"SS_019":("SouthDefender",112.,-105.,20.,16.,.2),
"SS_020":("NorthDefender",118.,97.,20.,16.,.2)}
all_actors=actors.get_all_level_actors()
D={}
for sid,(name,cx,cy,w,d,h) in specs.items():
    marker=next((a for a in all_actors if a.get_actor_label().startswith(sid+"_")),None)
    if marker is None:raise RuntimeError("Missing marker "+sid)
    D[sid]={"name":name,"cx":cx,"cy":cy,"w":w,"d":d,"h":h,"base":marker.get_actor_location().z-h*50.0}

def box(name,sid,x,y,zc,dims,mat,mesh=None):
    s=D[sid];return spawn(name,sid,s["name"],x,y,s["base"]+zc*CM,dims,mat,mesh)
def parapet(sid,mat):
    s=D[sid];z=s["h"]+.4
    box(sid+"_Parapet_N",sid,s["cx"],s["cy"]+s["d"]/2,z,(s["w"],.3,.8),mat)
    box(sid+"_Parapet_S",sid,s["cx"],s["cy"]-s["d"]/2,z,(s["w"],.3,.8),mat)
    box(sid+"_Parapet_E",sid,s["cx"]+s["w"]/2,s["cy"],z,(.3,s["d"],.8),mat)
    box(sid+"_Parapet_W",sid,s["cx"]-s["w"]/2,s["cy"],z,(.3,s["d"],.8),mat)
def window_y(sid,name,x,y,z,out,frame="Timber"):
    box(name+"_Frame",sid,x,y,z,(1.65,.16,1.45),frame)
    box(name+"_Glass",sid,x,y+out*.1,z,(1.28,.08,1.08),"Glass")
def door_y(sid,name,x,y,out,mat="Timber",w=1.25,h=2.4):
    box(name,sid,x,y+out*.12,h/2,(w,.18,h),mat)
def barrier(sid,name,x,y,yaw90=False):
    dims=(.55,2.3,.95) if yaw90 else (2.3,.55,.95)
    box(name,sid,x,y,.48,dims,"Stone",chamfer)
def crate(sid,name,x,y,z=.55,dims=(1.1,1.1,1.1),mat="Timber"):
    box(name,sid,x,y,z,dims,mat,chamfer)
def fence_rect(sid,mat="Metal",height=2.4):
    s=D[sid];z=height/2
    box(sid+"_Fence_N",sid,s["cx"],s["cy"]+s["d"]/2,z,(s["w"],.12,height),mat)
    box(sid+"_Fence_S",sid,s["cx"],s["cy"]-s["d"]/2,z,(s["w"],.12,height),mat)
    box(sid+"_Fence_E",sid,s["cx"]+s["w"]/2,s["cy"],z,(.12,s["d"],height),mat)
    box(sid+"_Fence_W",sid,s["cx"]-s["w"]/2,s["cy"],z,(.12,s["d"],height),mat)

# Attacker spawn: edge barriers only.
for i,(x,y,r) in enumerate(((-138,-105,0),(-135,-105,0),(-125,-105,0),(-122,-105,0)),1):barrier("SS_001","Attacker_Barrier_%02d"%i,x,y,bool(r))

# Dry canal entrance: edge trims and rubble, clear central channel.
box("Canal_Edge_W","SS_002",-130,-19,.75,(1.,24.,1.5),"Stone")
box("Canal_Edge_E","SS_002",-122,-19,.75,(1.,24.,1.5),"Stone")
for i,(x,y) in enumerate(((-130,-27),(-122,-27),(-130,-12),(-122,-12),(-129,-8),(-123,-30)),1):
    crate("SS_002","Canal_Rubble_%02d"%i,x,y,.35,(1.3,.9,.7),"Stone")

# Pump station.
parapet("SS_003","Stone");s=D["SS_003"];sy=s["cy"]-s["d"]/2-.16
door_y("SS_003","Pump_Door_A",-111,sy,-1,"Metal");door_y("SS_003","Pump_Door_B",-101,sy,-1,"Metal")
for i,x in enumerate((-108,-104),1):window_y("SS_003","Pump_Window_%02d"%i,x,sy,1.7,-1,"Metal")
for i,(x,y,z,d) in enumerate(((-113,-59,.7,(1.2,.5,1.4)),(-99,-66,.5,(.8,.5,1.)),(-106,-70,1.2,(.18,.18,2.4))),1):
    box("Pump_Utility_%02d"%i,"SS_003",x,y,z,d,"Metal")

# Old Clinic.
parapet("SS_005","PaleStucco");s=D["SS_005"];sy=s["cy"]-s["d"]/2-.16
for floor,z in enumerate((1.85,5.05),1):
    for i,x in enumerate((-65,-59,-53,-47),1):window_y("SS_005","Clinic_F%d_Win_%02d"%(floor,i),x,sy,z,-1)
door_y("SS_005","Clinic_MainDoor",-59,sy,-1,"Accent");door_y("SS_005","Clinic_ServiceDoor",-50,sy,-1,"Metal")

# Hero water tower assembly.
sid="SS_006";s=D[sid]
for i,(x,y) in enumerate(((-64.2,42.8),(-59.8,42.8),(-64.2,47.2),(-59.8,47.2)),1):
    box("WaterTower_Leg_%02d"%i,sid,x,y,5.5,(.45,.45,11.),"Metal")
box("WaterTower_Platform",sid,-62,45,10.8,(5.8,5.8,.3),"Metal")
box("WaterTower_Tank",sid,-62,45,12.7,(6.,6.,3.2),"Accent",cylinder)
box("WaterTower_Ladder",sid,-65,45,5.5,(.25,1.,11.),"Metal")
for i,(x,y) in enumerate(((-67,39),(-57,39),(-67,51),(-57,51)),1):crate(sid,"Tower_Utility_%02d"%i,x,y,.55,(1.,.8,1.1),"Metal")

# Transit plaza: lamps and edge benches.
for i,(x,y) in enumerate(((-6,-14),(18,-14),(-6,4),(18,4)),1):
    box("Plaza_Lamp_%02d"%i,"SS_009",x,y,2.4,(.14,.14,4.8),"Metal")
    box("Plaza_LampHead_%02d"%i,"SS_009",x,y,4.75,(.8,.35,.22),"Accent")
for i,(x,y,sx,sy2) in enumerate(((-7,-9,3,.55),(19,-9,3,.55),(-7,0,3,.55),(19,0,3,.55)),1):
    box("Plaza_Bench_%02d"%i,"SS_009",x,y,.42,(sx,sy2,.84),"Timber")

# Checkpoint office: readable facade and open vehicle gate.
parapet("SS_011","Stone");s=D["SS_011"];sy=s["cy"]-s["d"]/2-.16
for i,x in enumerate((68,74,80),1):window_y("SS_011","Checkpoint_Win_%02d"%i,x,sy,1.8,-1,"Metal")
door_y("SS_011","Checkpoint_Door",68,sy,-1,"Accent")
for i,(x,y) in enumerate(((64,39),(67,39),(81,39),(84,39)),1):barrier("SS_011","Checkpoint_Barrier_%02d"%i,x,y,False)
box("Checkpoint_GatePost_W","SS_011",70,39,1.5,(.45,.45,3.),"Metal")
box("Checkpoint_GatePost_E","SS_011",78,39,1.5,(.45,.45,3.),"Metal")

# Consulate residence.
parapet("SS_012","WarmStucco");s=D["SS_012"];sy=s["cy"]-s["d"]/2-.16
for floor,z in enumerate((1.85,5.05),1):
    for i,x in enumerate((111,116,121,126),1):window_y("SS_012","Consulate_F%d_Win_%02d"%(floor,i),x,sy,z,-1)
door_y("SS_012","Consulate_Door_A",114,sy,-1,"Timber");door_y("SS_012","Consulate_Door_B",123,sy,-1,"Accent")

# Freight depot: loading openings, crates and roof vents.
s=D["SS_013"];sy=s["cy"]-s["d"]/2-.16
door_y("SS_013","Depot_LoadingDoor",108,sy,-1,"Metal",5.,4.)
door_y("SS_013","Depot_PedDoor",96,sy,-1,"Accent")
for i,(x,y) in enumerate(((96,-7),(100,-7),(116,-7),(120,-7),(102,9),(114,9)),1):crate("SS_013","Depot_Crate_%02d"%i,x,y,.65,(1.4,1.2,1.3),"Timber")
for i,x in enumerate((102,110,118),1):box("Depot_RoofVent_%02d"%i,"SS_013",x,1,4.55,(1.,.8,.7),"Metal")

# Salvage yard: fence, vehicle silhouettes and scrap clusters.
fence_rect("SS_014","Metal",2.4)
for i,(x,y) in enumerate(((58,-26),(72,-18),(88,-8)),1):
    box("Salvage_Vehicle_%02d"%i,"SS_014",x,y,.8,(4.6,2.,1.6),"RustCanvas",chamfer)
for i,(x,y) in enumerate(((55,-10),(64,-30),(81,-31),(91,-22),(83,-4),(61,-4)),1):
    crate("SS_014","Salvage_Scrap_%02d"%i,x,y,.8,(2.2,1.6,1.6),"Metal")

# Motor pool: garage doors, two vehicles and repair clusters.
s=D["SS_015"];sy=s["cy"]-s["d"]/2-.16
door_y("SS_015","MotorPool_Garage_A",122,sy,-1,"Metal",4.,3.5)
door_y("SS_015","MotorPool_Garage_B",134,sy,-1,"Metal",4.,3.5)
box("MotorPool_Vehicle_A","SS_015",123,-39,.8,(4.5,2.,1.6),"Detention",chamfer)
box("MotorPool_Vehicle_B","SS_015",134,-52,.8,(4.5,2.,1.6),"RustCanvas",chamfer)
for i,(x,y) in enumerate(((119,-54),(126,-54),(137,-40),(139,-51)),1):crate("SS_015","MotorPool_Repair_%02d"%i,x,y,.5,(1.,1.,1.),"Timber")

# Power substation.
fence_rect("SS_016","Metal",2.4)
for i,(x,y,sx,sy2,sz) in enumerate(((52,-75,2.2,1.5,2.5),(58,-75,2.2,1.5,3.),(64,-75,2.2,1.5,2.3),(70,-75,2.2,1.5,2.8),(55,-66,1.4,1.2,1.8),(66,-66,1.4,1.2,1.8)),1):
    box("Substation_Equipment_%02d"%i,"SS_016",x,y,sz/2,(sx,sy2,sz),"Metal")

# Telecom workshop.
parapet("SS_018","Stone");s=D["SS_018"];sy=s["cy"]-s["d"]/2-.16
for floor,z in enumerate((1.85,5.05),1):
    for i,x in enumerate((-63,-57,-51),1):window_y("SS_018","Telecom_F%d_Win_%02d"%(floor,i),x,sy,z,-1,"Metal")
door_y("SS_018","Telecom_MainDoor",-57,sy,-1,"Accent")
for i,(x,y,h) in enumerate(((-62,-88,2.5),(-56,-91,3.2),(-50,-94,2.1)),1):
    box("Telecom_Antenna_%02d"%i,"SS_018",x,y,6.4+h/2,(.12,.12,h),"Metal")
    box("Telecom_RoofBox_%02d"%i,"SS_018",x,y,6.7,(1.,.8,.6),"Metal")

# South and north insertion edges.
for i,(x,y) in enumerate(((104,-111),(107,-111),(117,-111),(120,-111)),1):barrier("SS_019","SouthSpawn_Barrier_%02d"%i,x,y)
box("NorthSpawn_HistoricWall","SS_020",118,104,1.5,(20.,.5,3.),"WarmStucco")
for i,(x,y) in enumerate(((111,90),(114,90),(122,90),(125,90)),1):
    box("NorthSpawn_Fort_%02d"%i,"SS_020",x,y,.22,(1.1,.48,.44),"Canvas",chamfer)

unreal.log("SUNSCAR_ARTDRAFT_V1B actors=%d"%len(created))
print("SUNSCAR_ARTDRAFT_V1B",len(created))
