import bpy
import math
import sys
import os

##Der SpeicherPfad
#print(os.getcwd())
##Speicher die Licht_Klasse.py Datei in diesem Pfad rein
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    
from Licht_Klasse import Light, PointLight


#löscht alle Lichter
def deleteAllLights():
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT':
            ob.select_set(True)
    bpy.ops.object.delete()
            
#löscht alle lichter im "lights"-array (die Elemente sind Objekte)
def deleteLights(lights):
    bpy.ops.object.select_all(action='DESELECT')
    for light in lights:
        if bpy.context.scene.objects.get(light.getName()):
            bpy.data.objects[light.getName()].select_set(True)
    bpy.ops.object.delete()

#erstellt das rim- und fill-Licht
#-radius_rim = Die Entfernung des rim-Lichts
#-brightness_rim = Die Helligkeit des rim-Lichts
#-brightness_fill = die Helligkeit des fill-Lichtes
def creatingFillAndRimLight(radius_rim, brightness_rim, brightness_fill):
    fill=PointLight("fill",-14,16,0.3,brightness_fill,5)
    rim=PointLight("rim",radius_rim*math.sin(math.radians(0)),
                radius_rim*math.cos(math.radians(170)),
                radius_rim*math.sin(math.radians(170)),
                brightness_rim,0.25)
    return [fill, rim]

#erstellt das Tageslicht (plus rim- und fill-Licht wenn addFillAndRimLight=True gilt)
#gibt ein Array der Lichtobjekte zurück
def Tageslicht(brightness: float, angle, addFillAndRimLight: bool):
    if angle > 180:
        angle = 180
    elif angle < 0:
        angle = 0
    #Entfernung der Lichter
    radius_main=20
    radius_rim=50
    #Lichtstärke der Lichter
    brightness_main=3*brightness
    brightness_rim=6500
    brightness_fill=1500
    #Zur Anpassung
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #Farbe der Sonne
    color=[0.945, 0.855, 0.643]
    #erstellt die Lichter
    sonne=Light("Sonne", "SUN",radius_main*math.sin(math.radians(10)),
                radius_main*math.cos(math.radians(angle)),
                radius_main*math.sin(math.radians(angle)),
                brightness_main)
    sonne.setColor(color[0],color[1],color[2])
    if addFillAndRimLight:
        list = [sonne]
        list.extend(creatingFillAndRimLight(
                                radius_rim, brightness_rim, brightness_fill))
        return list
    else:
        return [sonne]

#erstellt das Nachtlicht (plus rim- und fill-Licht wenn addFillAndRimLight=True gilt)
#gibt ein Array der Lichtobjekte zurück
def Nachtlicht(brightness: float, angle, addFillAndRimLight: bool):
    if angle > 180:
        angle = 180
    elif angle < 0:
        angle = 0
    #Entfernung der Lichter
    radius_main=40
    radius_rim=30
    #Lichtstärke der Lichter
    brightness_main=6*brightness
    brightness_rim=2000
    brightness_fill=700
    #Zur Anpassung
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #Farbe des Mondes
    color=[0.001,0.044,0.107]
    #erstellt die Lichter
    mond=Light("Mond", "SUN",radius_main*math.sin(math.radians(10)),
                radius_main*math.cos(math.radians(angle)),
                radius_main*math.sin(math.radians(angle)),
                brightness_main)
    mond.setColor(color[0],color[1],color[2])
    if addFillAndRimLight:
        list = [mond]
        list.extend(creatingFillAndRimLight(
                                radius_rim, brightness_rim, brightness_fill))
        return list
    else:
        return [mond]

#erstellt das Laternenlicht (plus rim- und fill-Licht wenn addFillAndRimLight=True gilt)
#gibt ein Array der Lichtobjekte zurück
def Laternenlicht(brightness: float, height, addFillAndRimLight: bool):
    #Entfernung der Lichter
    radius_rim=40
    #Lichtstärke der Lichter
    brightness_main=4500*brightness
    brightness_rim=2500
    brightness_fill=850
    #Zur Anpassung
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #Farbe des spot-Lichtes
    color=[1,0.35,0]
    #erstellt die Lichter
    spot=Light("Laterne", "SPOT", 0, 0, height, brightness_main)
    spot.setColor(color[0],color[1],color[2])
    if addFillAndRimLight:
        list = [spot]
        list.extend(creatingFillAndRimLight(
                                radius_rim, brightness_rim, brightness_fill))
        return list
    else:
        return [spot]

##Testfunktion
#deleteAllLights()
#Nachtlicht(1, 90, True)
#deleteLights(Nachtlicht(1, 90, True))
#Tageslicht(1, 90, True)
#Laternenlicht(1, 10, False)

# update scene, if needed
dg = bpy.context.evaluated_depsgraph_get() 
dg.update()