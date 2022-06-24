import bpy 
import math

#camera animation 




class Camera:

    def __init__(self, name: str, x: float, y: float, z: float):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.camera = bpy.data.cameras.new(name)
        self.setCameraPosition(x, y, z)
        

    def setCameraPosition(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.camera.location = (x, y, z)

    def getCameraPosition(self):
        return self.x, self.y, self.z


    def deleteAllCameras():
        bpy.ops.object.select_all(action="DESELECT")
        for ob in bpy.data.objects:
            if ob.type == 'CAMERA':
                ob.select_set(True)
        bpy.ops.object.delete()
    
    def deleteCamera(self):
        bpy.data.objects[self.name].select_set(True)
        bpy.ops.object.delete()

    def getCameraRotation(self):
        return self.camera.rotation_euler
    
    def setCameraRotation(self, x_rotation: float, y_rotation: float, z_rotation: float):
        self.camera.rotation_euler = (x_rotation, y_rotation, z_rotation)


