"""
Example script which creates a simple scene.
To run, execute 

blender --background --python ./utils_example.py

in shell.

"""

import bpy
import os
import sys
import importlib

sys.path.append(os.getcwd())

from utils import *

clear_scene()

tower = import_mesh("assets/STL samples/eiffel_tower.stl")

myScene = bpy.context.scene
myCamera = OrbitCam(tower)
myCamera.set_distance(6)
myCamera.rotate_z(150)
myCamera.rotate_x(30)

myRenderer = Renderer(myScene, myCamera.camera)
myRenderer.set_output_properties()
myRenderer.set_eevee()

myRenderer.render()
