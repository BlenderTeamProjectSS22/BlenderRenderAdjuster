"""
Example script which creates a simple scene.
To run, execute 

blender --background --python ./utils_example.py

in shell.o

"""

import bpy
import os
import sys
import importlib

from utils import *
import HDRI.hdri as hdri

clear_scene()

tower = import_mesh("assets/STL samples/Eiffel_tower.STL")

myScene = bpy.context.scene
myCamera = OrbitCam()
myCamera.set_distance(6)

myRenderer = Renderer(myCamera.camera)
myRenderer.set_final_render(
    file_path = bpy.path.relpath("result.png"),
    animation = False,
    use_transparent_bg = False,
    num_samples = 32
)

myCamera.rotate_z(150)
myCamera.rotate_x(30)

hdri.initialize_world_texture()
path = bpy.path.abspath(os.getcwd() + "/" + "assets/HDRIs/green_point_park_2k.hdr")
hdri.set_background_image(path)
hdri.pan_background_vertical(10)
hdri.pan_background_horizontal(-20)
export_blend(os.path.abspath(os.getcwd() + "/renders/export.blend"))
myRenderer.render()

print(myCamera.get_location())
