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
import camera_animation.camera_animation_module as cam
import HDRI.hdri as hdri

clear_scene()

tower = import_mesh("assets/STL samples/Eiffel_tower.STL")

myScene = bpy.context.scene
myCamera = cam.Camera("cam1", 6, 0, 0.5)

startp = [6,-1,0.5]
endP = [6,1,0.5]
rot = [90,0,90]
myCamera.driveBy(100, startp, endP, rot)


myRenderer = Renderer(myCamera.cam)
myRenderer.set_output_properties(animation=False)    # animation=True would render video
myRenderer.set_eevee()



hdri.initialize_world_texture()
path = bpy.path.relpath("assets/HDRIs/green_point_park_2k.hdr")
hdri.set_background_image(path)
hdri.pan_background_vertical(10)
hdri.pan_background_horizontal(-20)
export_blend(os.path.abspath("renders/export.blend"))
myRenderer.render()

print(myCamera.getCameraPosition())
print(myCamera.getCameraRotation())