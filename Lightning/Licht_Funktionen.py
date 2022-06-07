import bpy
import math
import sys
import os
import random
from typing import Union

##Der SpeicherPfad
#print(os.getcwd())
##Speicher die Licht_Klasse.py Datei in diesem Pfad rein
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    
from Licht_Klasse import *
from utils import *
from camera_animation_module import *


#delete all lights
def deleteAllLights() -> None:
    bpy.ops.object.select_all(action = "DESELECT")
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT':
            ob.select_set(True)
    bpy.ops.object.delete()
           
#delete the lights in "lights"-array (the elements are objects)
def deleteLights(lights: list[Light]) -> None:
    bpy.ops.object.select_all(action = 'DESELECT')
    for light in lights:
        if bpy.context.scene.objects.get(light.getName()):
            bpy.data.objects[light.getName()].select_set(True)
    bpy.ops.object.delete()
    
#calculates the distance of the light object "object" from the center
def radiusOfLightObject(object: Light) -> float:
    result = 0
    for position in object.getPosition():
        result += math.pow(position, 2)
    return math.sqrt(result)

#creating fill- and rim-light
#-radius_rim = the distance of the rim light
#-brightness_rim = the brightness of the rim light
#-brightness_fill = the brightness of the fill light
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def creatingFillAndRimLight(radius_rim: float, brightness_rim: float,
                            brightness_fill: float, cameraObject: OrbitCam) -> list[Light]:
    #if camera is used
    if not cameraObject == None:
        rimLightAngle = math.asin(cameraObject.get_location()[0] / cameraObject.get_distance())
        #creating Lights
        rim = PointLight("rim", -radius_rim * math.sin(rimLightAngle),
                    -radius_rim * math.cos(rimLightAngle),
                    radius_rim * math.sin(math.radians(170)),
                    brightness_rim, 0.25)
        fill = PointLight("fill", 20 * math.sin(rimLightAngle),
                    20 * math.cos(rimLightAngle),
                    20 * math.sin(math.radians(170)),
                    brightness_fill, 5)
        #link lights to controller
        rim.getDatas()[1].parent = cameraObject.get_controller()  
        fill.getDatas()[1].parent = cameraObject.get_controller()     
    #if camera is not used
    else:
        #creating Lights
        fill = PointLight("fill", -14, 16, 0.3, brightness_fill, 5)
        rim = PointLight("rim", 0, -radius_rim,
                        radius_rim*math.sin(math.radians(170)),
                        brightness_rim, 0.25)
    return [fill, rim]

#creating the daylight (plus rim- and fill-Licht if addFillAndRimLight = True)
#returns an array of all objects
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def Daylight(brightness: float, angle: int, addFillAndRimLight: bool, cameraObject: OrbitCam) -> list[Light]:
    #precondition
    if angle >= 180:
        angle = 180
    elif angle < 0:
        angle = 0
    #the distance of the lights
    radius_main = 20
    radius_rim = 50
    #the brightness of the lights
    brightness_main = 3 * brightness
    brightness_rim = 6500
    brightness_fill = 1500
    #to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #color of the sun
    color = [0.945, 0.855, 0.643]
    #dawnlight
    if angle > 150:
        color[1] -= (angle-140) * 0.021
        color[2] -= (angle-140) * 0.016
    #creating the lights
    sonne = RotateLight("Sonne", "SUN", radius_main * math.sin(math.radians(10)),
                    radius_main * math.cos(math.radians(angle)),
                    radius_main * math.sin(math.radians(angle)),
                    -math.cos(math.radians(angle)), math.sin(math.radians(10)), 0,
                    brightness_main)
    sonne.setColor(color[0], color[1], color[2])
    if addFillAndRimLight:
        list = [sonne]
        list.extend(creatingFillAndRimLight(
                                radius_rim, brightness_rim, brightness_fill, cameraObject))
        return list
    else:
        return [sonne]

#creating the nightlight (plus rim- and fill-Licht if addFillAndRimLight = True)
#returns an array of all objects
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def Nightlight(brightness: float, angle: int, addFillAndRimLight: bool, cameraObject: OrbitCam) -> list[Light]:
    #precondition
    if angle > 180:
        angle = 180
    elif angle < 0:
        angle = 0
    #the distance of the lights
    radius_main = 40
    radius_rim = 30
    #the brightness of the lights
    brightness_main = 6 * brightness
    brightness_rim = 2000
    brightness_fill = 700
    #to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #color of the moon
    color = [0.001, 0.044, 0.107]
    #creating the light
    mond = RotateLight("Mond", "SUN", radius_main * math.sin(math.radians(10)),
                      radius_main * math.cos(math.radians(angle)),
                      radius_main * math.sin(math.radians(angle)),
                      -math.cos(math.radians(angle)), math.sin(math.radians(10)), 0,
                      brightness_main)
    mond.setColor(color[0], color[1], color[2])
    list = [mond]
    #if adding fill and rim light
    if addFillAndRimLight:
        list.extend(creatingFillAndRimLight(
                                radius_rim, brightness_rim, brightness_fill, cameraObject))
    return list

#creating the laternlight (plus rim- and fill-Licht if addFillAndRimLight = True)
#returns an array of all objects
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def Laternlight(brightness: float, height: float,
                addFillAndRimLight: bool, cameraObject: OrbitCam) -> list[Light]:
    #the distance of the lights
    radius_rim = 40
    #the brightness of the lights
    brightness_main = 4500 * brightness
    brightness_rim = 2500
    brightness_fill = 850
    #to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #color of the spot light
    color = [1, 0.35, 0]
    #creating the lights
    spot = Light("Laterne", "SPOT", 0, 0, height, brightness_main)
    spot.setColor(color[0], color[1], color[2])
    if addFillAndRimLight:
        list = [spot]
        list.extend(creatingFillAndRimLight(
                                radius_rim, brightness_rim, brightness_fill, cameraObject))
        return list
    else:
        return [spot]


###work in progress
#makes a day-night-circle
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def DayNightCircle(startingTime: int, brightness: float,
                    addFillAndRimLight: bool, cameraObject: OrbitCam) -> None:
    #before starting time
    deleteAllLights()
    first_element = True
    #color of the sun (important for the dawn light)
    dayColor = [0.945, 0.855, 0.643]
    #preconditions
    if startingTime > 24 or startingTime < 0:
        currentTime = 0
    else:
        currentTime = startingTime
    #setting starting values
    currentAngle = ((currentTime % 12) * 15 + 89) % 180
    currentTime *= 10
    if currentTime > 60 and startingTime <= 180:
        isDay = True
        lights = Daylight(brightness, currentAngle,
                          addFillAndRimLight, cameraObject)
        lightcollection = [lights[0]]
        lightcollection.extend(Nightlight(brightness, 0, False, cameraObject))
    else:
        isDay = False
        lights = Nightlight(brightness, currentAngle,
                          addFillAndRimLight, cameraObject)
        lightcollection = [lights[0]]
        lightcollection.extend(Daylight(brightness, 0, False, cameraObject))
    #brightnesses: for saving the energies of the light sources
    brightnesses = [lightcollection[0].getBrightness(), lightcollection[1].getBrightness()]
    assert len(lightcollection) == 2 and len(brightnesses) == 2
    lightcollection[1].setBrightness(0)
    radius = radiusOfLightObject(lights[0])
    scene = bpy.context.scene
    frame_current = scene.frame_current
    
    #setting per frame
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        #day and night change
        if currentAngle >= 180:
            lights[0].setBrightness(0)
            if first_element:
                 lights[0] = lightcollection[1]
                 lights[0].setBrightness(brightnesses[1])
                 assert lightcollection[0].getBrightness() == 0
            else:
                 lights[0] = lightcollection[0]
                 lights[0].setBrightness(brightnesses[0])
                 assert lightcollection[1].getBrightness() == 0
            first_element = not first_element
            isDay = not isDay
            if isDay:
                lights[0].setColor(dayColor[0], dayColor[1], dayColor[2])
            currentAngle = 0
            radius = radiusOfLightObject(lights[0])
            assert lights[0].getType() == "SUN" 
        #day and night dont change
        else:
            #dawnlight
            if isDay and currentAngle >= 140:               
                lights[0].setColor(dayColor[0],
                                   dayColor[1] - (currentAngle-140) * 0.021,
                                   dayColor[2] - (currentAngle-140) * 0.016)
            #fit position and rotation 
            lights[0].setPosition(radius * math.sin(math.radians(10)),
                                  radius * math.cos(math.radians(currentAngle)),
                                  radius * math.sin(math.radians(currentAngle))) 
            lights[0].setRotation(-math.cos(math.radians(currentAngle)), math.sin(math.radians(10)), 0)
        #increment angle and saving datas in frames
        currentAngle += 1
        lights[0].getDatas()[1].keyframe_insert(data_path="rotation_euler", frame=f)
        lights[0].getDatas()[1].keyframe_insert(data_path="location", frame=f)
        for light in lightcollection:
            light.getDatas()[0].keyframe_insert(data_path="energy", frame=f)
            light.getDatas()[0].keyframe_insert(data_path="color", frame=f)
    scene.frame_set(frame_current) 

###for testing

##create camera
#deleteAllCameras()
#myCamera = OrbitCam(bpy.data.objects['Kopf'])
#myCamera.set_distance(6)

##test functions
#deleteAllLights()
#Nightlight(1, 50, True, myCamera)
#deleteLights(Nightlight(1, 90, True, None))
#lights = Daylight(1, 180, True, None)
#Laternlight(1, 20, True, None)
#DayNightCircle(12, 1, True, None)
#myCamera.rotate_z(270)

# update scene, if needed
dg = bpy.context.evaluated_depsgraph_get() 
dg.update()