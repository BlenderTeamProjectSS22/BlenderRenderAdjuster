import bpy
import math
import sys
import os
import random

##Der SpeicherPfad
#print(os.getcwd())
##Speicher die Licht_Klasse.py Datei in diesem Pfad rein
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    
from Licht_Klasse import *
from utils import *


#delete all lights
def deleteAllLights():
    bpy.ops.object.select_all(action="DESELECT")
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT':
            ob.select_set(True)
    bpy.ops.object.delete()
           
#delete the lights in "lights"-array (the elements are objects)
def deleteLights(lights):
    bpy.ops.object.select_all(action='DESELECT')
    for light in lights:
        if bpy.context.scene.objects.get(light.getName()):
            bpy.data.objects[light.getName()].select_set(True)
    bpy.ops.object.delete()

#creating fill- and rim-light
#-radius_rim = the distance of the rim light
#-brightness_rim = the brightness of the rim light
#-brightness_fill = the brightness of the fill light
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def creatingFillAndRimLight(radius_rim, brightness_rim, brightness_fill, cameraObject):
    #if camera is used
    if not cameraObject == None:
        rimLightAngle = math.asin(cameraObject.get_location()[0]/cameraObject.get_distance())
        #creating Lights
        rim=PointLight("rim",-radius_rim*math.sin(rimLightAngle),
                    -radius_rim*math.cos(rimLightAngle),
                    radius_rim*math.sin(math.radians(170)),
                    brightness_rim,0.25)
        fill=PointLight("fill",20*math.sin(rimLightAngle),
                    20*math.cos(rimLightAngle),
                    20*math.sin(math.radians(170)),
                    brightness_fill,5)
    #if camera is not used
    else:
        #creating Lights
        fill=PointLight("fill",-14,16,0.3,brightness_fill,5)
        rim=PointLight("rim", 0, -radius_rim,
                    radius_rim*math.sin(math.radians(170)),
                    brightness_rim,0.25)
    return [fill, rim]

###not good tested
#applies the new location of the camera and the lights
def fitLightLocation(cameraObject, rimLight, fillLight):
    #values
    rimLightAngle = math.asin(cameraObject.get_location()[0]/cameraObject.get_distance())
    oldPosition = rimLight.getPosition()
    radius_rim = math.sqrt(math.pow(oldPosition[0],2)+math.pow(oldPosition[1],2))
    #creating lights
    rimLight.setPosition(-radius_rim*math.sin(rimLightAngle),
                         -radius_rim*math.cos(rimLightAngle),
                         oldPosition[2])
    fillLight.setPosition(20*math.sin(rimLightAngle),
                          20*math.cos(rimLightAngle),
                          fillLight.getPosition()[2])

###is this function necessary?
#adding an array with random constalations of stars
#-radius: the distance of the stars
#-brightness: the brightness of the starts (the type is "Point")
#-amounth: the amounth of stars (this number has to be 0 or more)
def addingStars(radius :float, brightness: float, amounth: int):
    #check valid amounth value
    if amounth >= 0:
        stars = []
        for star in range(amounth):
            #creating randomnumbers
            randomNumbers=[random.randint(10, 170),random.randint(10, 170)]
            #creating star
            stars.append(PointLight("Star", radius*math.sin(math.radians(randomNumbers[0])),
                        radius*math.cos(math.radians(randomNumbers[1])),
                        radius*math.sin(math.radians(randomNumbers[1])),
                        brightness*200,0.25))
        return stars
    else:
        print("addingStars: amounth has to be 0 or more")
        return None

#creating the daylight (plus rim- and fill-Licht if addFillAndRimLight=True)
#returns an array of all objects
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def Daylight(brightness: float, angle, addFillAndRimLight: bool, cameraObject):
    if angle >= 180:
        angle = 180
    elif angle < 0:
        angle = 0
    #the distance of the lights
    radius_main=20
    radius_rim=50
    #the brightness of the lights
    brightness_main=3*brightness
    brightness_rim=6500
    brightness_fill=1500
    #to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #color of the sun
    color=[0.945, 0.855, 0.643]
    #dawnlight
    if angle >150:
        color[1] -= (angle-140)*0.021
        color[2] -= (angle-140)*0.016
    #creating the lights
    sonne=RotateLight("Sonne", "SUN",radius_main*math.sin(math.radians(10)),
                radius_main*math.cos(math.radians(angle)),
                radius_main*math.sin(math.radians(angle)),
                -math.cos(math.radians(angle)),math.sin(math.radians(10)),0,
                brightness_main)
    sonne.setColor(color[0],color[1],color[2])
    if addFillAndRimLight:
        list = [sonne]
        list.extend(creatingFillAndRimLight(
                                radius_rim, brightness_rim, brightness_fill, cameraObject))
        return list
    else:
        return [sonne]

#creating the nightlight (plus rim- and fill-Licht if addFillAndRimLight=True)
#returns an array of all objects
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def Nightlight(brightness: float, angle, addFillAndRimLight: bool, cameraObject):
    if angle > 180:
        angle = 180
    elif angle < 0:
        angle = 0
    #the distance of the lights
    radius_main=40
    radius_rim=30
    #the brightness of the lights
    brightness_main=6*brightness
    brightness_rim=2000
    brightness_fill=700
    #to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #color of the moon
    color=[0.001,0.044,0.107]
    #creating the light
    mond=RotateLight("Mond", "SUN",radius_main*math.sin(math.radians(10)),
                radius_main*math.cos(math.radians(angle)),
                radius_main*math.sin(math.radians(angle)),
                -math.cos(math.radians(angle)),math.sin(math.radians(10)),0,
                brightness_main)
    mond.setColor(color[0],color[1],color[2])
    #creating return array
    list = [mond]
    list.extend(addingStars(radius_main,brightness_main,5))
    #if adding fill and rim light
    if addFillAndRimLight:
        list.extend(creatingFillAndRimLight(
                                radius_rim, brightness_rim, brightness_fill, cameraObject))
    return list

#creating the laternlight (plus rim- and fill-Licht if addFillAndRimLight=True)
#returns an array of all objects
#-cameraObject = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def Laternlight(brightness: float, height, addFillAndRimLight: bool, cameraObject):
    #the distance of the lights
    radius_rim=40
    #the brightness of the lights
    brightness_main=4500*brightness
    brightness_rim=2500
    brightness_fill=850
    #to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    #color of the spot light
    color=[1,0.35,0]
    #creating the lights
    spot=Light("Laterne", "SPOT", 0, 0, height, brightness_main)
    spot.setColor(color[0],color[1],color[2])
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
def DayNightCircle(startingTime: int, brightness: float, addFillAndRimLight: bool, cameraObject):
    if startingTime > 24 or startingTime < 0:
        currentTime = 0
    else:
        currentTime = startingTime
    if currentTime > 6 and startingTime <= 18:
        lights = Daylight(brightness, angle, addFillAndRimLight, cameraObject)
    else:
        lights = Nightlight(brightness, angle, addFillAndRimLight, cameraObject)
    
    #in loop with currentTime++
    currentAngle = ((currentTime % 12) * 15 + 90) % 180
    if currentTime == 19:
        deleteLights(lights)
        Nightlight(brightness, 0, addFillAndRimLight, cameraObject)
    if currentTime == 7:
        deleteLights(lights)
        Daylight(brightness, 0, addFillAndRimLight, cameraObject)
    else:
        lights[0].setPosition(radius_main*math.sin(math.radians(10)),
                              radius_main*math.cos(math.radians(currentAngle)),
                              radius_main*math.sin(math.radians(currentAngle)))   

##Testfunktionen

##create camera
#myCamera = OrbitCam(bpy.data.objects['Kopf'])
#myCamera.set_distance(6)

##test functions
#deleteAllLights()
#Nightlight(1, 50, True, None)
#deleteLights(Nightlight(1, 90, True, None))
#lights = Daylight(1, 180, True, myCamera)
#Laternlight(1, 20, True, None)

##not good tested
#myCamera.rotate_z(2)
#fitLightLocation(myCamera, lights[2])
#myCamera.rotate_x(90)

# update scene, if needed
dg = bpy.context.evaluated_depsgraph_get() 
dg.update()