"""
Example script which creates a simple scene with a monkey.
To run, execute 

blender --background --python ./utils_example.py

in shell.

"""

import bpy
import os
import sys

sys.path.append(os.getcwd())

from utils import *

clear_scene()

bpy.ops.mesh.primitive_monkey_add()
monkey = bpy.context.object

scene = bpy.context.scene
camera = add_camera(monkey, 6)

set_output_properties(scene)
set_cycles_renderer(scene, camera)

rotate_view_z(camera, 150)
rotate_view_x(camera, 30)

render()
