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
        

    def drive_by(self, frames: int, points: list, rotation: list, track: bool, object: bpy.types.Object,):
        #
        frame = 0
        rot = 0
        frames = frames / (len(points) - 1)
        for i in range(len(points)):
            self.set_camera_position(points[i][0], points[i][1], points[i][2])
            try:
                self.set_camera_rotation(rotation[rot], rotation[rot + 1], rotation[rot + 2])
            except:
                pass
            self.add_keyframe(frame)
            rot += 3
            
            print("Before: "+str(frame))
            frame = frame + frames
            print("After: "+str(frame))
            


    def set_mode(self, mode: str, object: bpy.types.Object):
        if mode == "track":
            self.cam.constraints.new(type="TRACK_TO")
            self.cam.constraints["Track To"].target = object
        else:
            self.cam.constraints.remove(self.cam.constraints["Track To"])

    def preset_1(self, frames: int, object: bpy.types.Object, track: bool):
        #left to right drive by
        self.drive_by(
            frames,
            [[5, -3, 0],[5, 3, 0]],
            [90, 0, 90],
            track,
            object,
        )

    def preset_2(self, frames: int, object: bpy.types.Object, track: bool):

        self.drive_by(
            # get closer to the object/zoom in
            frames,
            [[100, 0, 0],[7, 0, 0],[3, 0, 0]],
            [90, 0, 90],
            track,
            object,
        )

    def preset_3(self, frames: int, object: bpy.types.Object, track: bool):
        self.drive_by(
            frames,
            [[5, -3, 0],[5, 3, 0],[5, 0, 0],[5, -3, 0]],
            [90, 0, 90, 90, 90, 90, 90, 0, 90],
            track,
            object,
        )