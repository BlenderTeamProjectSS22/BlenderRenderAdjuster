import bpy 
import math

#camera animation 

def deleteAllCameras():
    bpy.ops.object.select_all(action="DESELECT")
    for ob in bpy.data.objects:
        if ob.type == 'CAMERA':
            ob.select_set(True)
    bpy.ops.object.delete()



