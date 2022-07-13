from calendar import c
from os import set_inheritable
import bpy
import math
from math import radians
from utils import *

# .venv-blender\Scripts\activate.bat

# Camera class with most important controll methods to move around the scene
class Camera:
    def __init__(self, name: str, x: float, y: float, z: float):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        bpy.ops.object.camera_add(location=(x, y, z))
        self.cam = bpy.context.object
        self.cam.data.lens = 25
        self.set_camera_rotation(90, 0, 90)

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

    def set_handles(self, mode: str):

        # ensure the action is still available
        if self.cam.animation_data.action:
        # and store it in a convenience variable
            my_action = bpy.data.actions.get(self.cam.animation_data.action.name)
        bpy.ops.object.select_all(action="DESELECT")
        my_fcu_rot = my_action.fcurves.find("rotation_euler", index=1)
        my_fcu_pos = my_action.fcurves.find("location", index=1)
        for pt in my_fcu_rot.keyframe_points:
            pt.select_control_point
            pt.handle_left_type = mode
            pt.handle_right_type = mode
            print(pt.handle_left_type)
        for pt in my_fcu_pos.keyframe_points:
            pt.select_control_point
            pt.handle_left_type = type=mode
            pt.handle_right_type = mode
        



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
            try:
                self.set_camera_rotation(Rotation[0], Rotation[1], Rotation[2])
                self.set_mode("dont_track", object)
            except:
                pass
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

    def preset_1(self, frames: int, object: bpy.types.Object):



        self.drive_by(
            frames,
            [5, -3, 0],
            [5, 3, 0],
            [90, 0, 90],
            False,
            object,
        )

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
        #path to curve
        bpy.ops.object.select_all(action="DESELECT")

        pathObj.select_set(True)
        bpy.ops.object.convert(target="CURVE")

        bpy.ops.object.select_all(action="DESELECT")
        self.cam.select_set(True)
        bpy.ops.object.constraint_add(type='FOLLOW_PATH')
        bpy.context.object.constraints["Follow Path"].target = bpy.data.objects["NurbsPath_NurbsPath.001"]
        bpy.context.object.constraints["Follow Path"].use_curve_follow = True
        bpy.ops.constraint.followpath_path_animate(constraint="Follow Path", owner='OBJECT')

        