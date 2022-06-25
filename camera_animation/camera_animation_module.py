import bpy
import math
from math import radians
from utils import *

# Camera class with most important controll methods to move around the scene
class Camera:
    def __init__(self, name: str, x: float, y: float, z: float):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        bpy.ops.object.camera_add(location=(x, y, z))
        self.cam = bpy.context.object

    def set_camera_position(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.cam.location = (x, y, z)

    def get_camera_position(self):
        return self.x, self.y, self.z

    def delete_all_cameras(self):
        bpy.ops.object.select_all(action="DESELECT")
        for ob in bpy.data.objects:
            if ob.type == "CAMERA":
                ob.select_set(True)
                bpy.ops.object.delete()

    def get_camera_rotation(self):
        return self.cam.rotation_euler

    def set_camera_rotation(
        self, x_rotation: float, y_rotation: float, z_rotation: float
    ):
        self.cam.rotation_euler = (
            radians(x_rotation),
            radians(y_rotation),
            radians(z_rotation),
        )

    def add_keyframe(self, frame: int):  # gets added at the given frame
        self.cam.keyframe_insert(data_path="location", frame=frame)
        self.cam.keyframe_insert(data_path="rotation_euler", frame=frame)

    def drive_by(
        self,
        frames: int,
        startPoint: list,
        endPoint: list,
        Rotation: list,
        track: bool,
        object: bpy.types.Object,
    ):
        #
        self.set_camera_position(startPoint[0], startPoint[1], startPoint[2])
        if track == False:
            self.set_mode("dont_track", object)
            self.set_camera_rotation(Rotation[0], Rotation[1], Rotation[2])
        else:
            self.set_mode("track", object)
        self.add_keyframe(0)
        self.set_camera_position(endPoint[0], endPoint[1], endPoint[2])
        if track == False:
            self.set_camera_rotation(Rotation[0], Rotation[1], Rotation[2])
        self.add_keyframe(frames)

    def set_mode(self, mode: str, object: bpy.types.Object):
        if mode == "track":
            self.cam.constraints.new(type="TRACK_TO")
            self.cam.constraints["Track To"].target = object
        else:
            self.cam.constraints["Track To"].delete()


class CameraPath:
    def __init__(self, path: str, cam: Camera):
        self.path = path
        self.cam = cam.cam
        self.camera = cam
        self.pathObj = self.import_path(path)

    def delete_path(self):
        bpy.ops.object.select_all(action="DESELECT")
        self.pathObj.select_set(True)
        bpy.ops.object.delete()

    def import_path(self, path: str):
        if fnmatch.fnmatch(path, "*.obj"):
            bpy.ops.wm.obj_import(filepath=path)
        else:
            raise ImportError("can only import .ply, .stl or .obj files")
        newObj = bpy.context.object
        scale_to_unit_cube(newObj)
        return newObj

    # not working yet
    def follow_path(self, pathObj: bpy.types.Object, frames: int):
        bpy.ops.object.convert(target="CURVE")

        self.cam.constraints.new(type="CLAMP_TO")
        self.cam.constraints.new(type="FOLLOW_PATH")
        self.cam.constraints["Clamp To"].target = pathObj
        self.cam.constraints["Follow Path"].target = pathObj
    
        #bpy.ops.constraint.followpath_path_animate(frame_start=0, frame_end=frames)