import bpy
import math
import random



#this is here to delete previous objects, so you dont have to manually deltete everything
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()


#controls
#size of objects in the cloud
pointcloudRadius = 0.02
#objects that will be spawned, choose between: "cube","circle","disk".
toSpawn = "circ"
#not enought verticies? Subdivide
subdivide = True
#watch out for vertex amount beeing to high
subAmount = 3
#random rotation for pointcloud objects
randomRot = False




def spawnCircle(x,y,z):
     bpy.ops.mesh.primitive_uv_sphere_add(radius=pointcloudRadius, enter_editmode=False, align='WORLD', location=(x, y, z), scale=(1, 1, 1))

def spawnCube(x,y,z):
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(x, y, z), scale=(pointcloudRadius, pointcloudRadius, pointcloudRadius))

def spawnDisk(x,y,z):
    bpy.ops.mesh.primitive_circle_add(radius=pointcloudRadius, enter_editmode=True, align='WORLD', location=(x, y, z), scale=(1, 1, 1))
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.editmode_toggle()
    

bpy.ops.object.select_all(action='DESELECT')
#toCloud = bpy.ops.mesh.primitive_monkey_add()
toCloud = bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

for obj in bpy.context.selected_objects:
    obj.name = "pointCloudObject"
if subdivide:
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=subAmount)
    bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.delete(type="EDGE_FACE")
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.editmode_toggle()

obj = bpy.context.view_layer.objects.active
mesh = obj.data
for vert in mesh.vertices:
    if toSpawn == "cube":
         spawnCube(vert.co.x,vert.co.y,vert.co.z)
    if toSpawn == "circ":
        spawnCircle(vert.co.x,vert.co.y,vert.co.z)
    if toSpawn == "disk":
        spawnDisk(vert.co.x,vert.co.y,vert.co.z)
        
    if randomRot:
        bpy.context.active_object.rotation_euler[0] = math.radians(random.randint(0,360))
        bpy.context.active_object.rotation_euler[1] = math.radians(random.randint(0,360))
        bpy.context.active_object.rotation_euler[2] = math.radians(random.randint(0,360))
        
bpy.data.objects["pointCloudObject"].select_set(True)
# delete all selected objects
bpy.ops.object.delete()


objects = bpy.context.scene.objects

for obj in objects:
    obj.select_set(obj.type == "MESH")


if toSpawn == "circ":
    activeObj = "Sphere"
elif toSpawn == "disk":
    activeObj = "Circle"
else:
    activeObj = "cube"
    

bpy.context.view_layer.objects.active = bpy.data.objects[activeObj]
bpy.ops.object.join()


        

    





 
