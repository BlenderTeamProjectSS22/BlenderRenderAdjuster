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
import camera_animation.camera_animation_module as cammod
import HDRI.hdri as hdri

clear_scene()

tower = import_mesh("assets/STL samples/Eiffel_tower.STL")

myScene = bpy.context.scene
myCamera = cammod.Camera("cam1", 6, 0, 0.5)
path = cammod.CameraPath("camera_animation/testpath.obj", myCamera)


startp = [-3,-5,0.5]
endP = [6,5,0.5]
rot = [90,0,90]

myCamera.set_mode("track", tower)
path.follow_path(path.pathObj, 50)

myRenderer = Renderer(myCamera.cam)
myRenderer.set_output_properties(animation=True)    # animation=True would render video
myRenderer.set_eevee()




export_blend(os.path.abspath("renders/export.blend"))
myRenderer.render()

print(myCamera.get_camera_position())
print(myCamera.get_camera_rotation())