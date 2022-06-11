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

sys.path.append(os.getcwd())

from utils import *
import HDRI.hdri as hdri

clear_scene()

tower = import_mesh("assets/STL samples/Eiffel_tower.stl")

myScene = bpy.context.scene
myCamera = OrbitCam(tower)
myCamera.set_distance(6)

myRenderer = Renderer(myScene, myCamera.camera)
myRenderer.set_output_properties()    # animation=True would render video
myRenderer.set_cycles()

myCamera.rotate_z(150)
myCamera.rotate_x(30)

hdri.initialize_world_texture()
path = bpy.path.relpath("assets/HDRIs/green_point_park_2k.hdr")
hdri.set_background_image(path)
hdri.pan_background_vertical(10)
hdri.pan_background_horizontal(-20)
export_blend("renders/export.blend")
myRenderer.render()

print(myCamera.get_location())
