import bpy
import sys
import os

##Der SpeicherPfad
print(os.getcwd())
##Speicher die Licht_Klasse.py Datei in diesem Pfad rein
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    

from utils import *
from camera_animation import *


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