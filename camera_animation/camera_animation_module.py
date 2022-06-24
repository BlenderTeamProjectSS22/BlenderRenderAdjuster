import bpy 
import math
from math import radians
#camera animation 




class Camera:

    def __init__(self, name: str, x: float, y: float, z: float):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        bpy.ops.object.camera_add(location=(x, y, z))
        self.cam = bpy.context.object
        
    def setCameraPosition(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.cam.location = (x, y, z)

    def getCameraPosition(self):
        return self.x, self.y, self.z

    def deleteAllCameras(self):
        bpy.ops.object.select_all(action="DESELECT")
        for ob in bpy.data.objects:
            if ob.type == 'CAMERA':
                ob.select_set(True)
                bpy.ops.object.delete()

    def getCameraRotation(self):
        return self.cam.rotation_euler
    
    def setCameraRotation(self, x_rotation: float, y_rotation: float, z_rotation: float):
        self.cam.rotation_euler = (radians(x_rotation), radians(y_rotation), radians(z_rotation))

    def addKeyframe(self, frame: int):
        self.cam.keyframe_insert(data_path="location", frame=frame)
        self.cam.keyframe_insert(data_path="rotation_euler", frame=frame)

    def driveBy(self, frames: int, startPoint: list, endPoint: list, Rotation: list):
        self.setCameraPosition(startPoint[0], startPoint[1], startPoint[2])
        self.setCameraRotation(Rotation[0], Rotation[1], Rotation[2])
        self.addKeyframe(0)
        self.setCameraPosition(endPoint[0], endPoint[1], endPoint[2])
        self.setCameraRotation(Rotation[0], Rotation[1], Rotation[2])
        self.addKeyframe(frames)

    

    
             
