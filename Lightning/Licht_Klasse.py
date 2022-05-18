import bpy
import math

###Zu Testzwecken
##Variabeln
#
##Einschlagswinkel des Sonnenlichts
#winkel=80
##Entfernung des Sonnenlichts
#radius=20
##Lichtstärke des Sonnenlichts
#sun_brightness=3

#Lichtklasse mit Attributen:
#---type=Typ des Lichts(POINT,SUN,SPOT,AREA)
#---xLoxation=Die x-Koordinate
#---yLoxation=Die y-Koordinate
#---zLoxation=Die z-Koordinate
#---brightness=Die Lichtstärke
class Light:
    def __init__(self, type, xLocation, yLocation, zLocation, brightness):
        self._type = type
        self._xLocation = xLocation
        self._yLocation = yLocation
        self._zLocation = zLocation
        self._brightness = brightness

    #die Position des Lichts als [x,y,z]-Array gegeben
    def getPosition(self):
        return [self._xLocation, self._yLocation, self._zLocation]

    #setzt die Position des Lichts in (x,y,z)
    def setPosition(self, xLocation, yLocation, zLocation):
        self._xLocation = xLocation
        self._yLocation = yLocation
        self._zLocation = zLocation

    #der Typ des Lichts
    def getType(self):
        return self._type

    #setzt den Typ des Lichts
    def setType(self, newType):
        if newType == "SUN" or newType == "POINT" or newType == "AREA" or newType == "SPOT":
            self._type = newType
        else:
            print(newType + " is not a valid type")
    
    #die Lichtstärke
    def getBrightness(self):
        return self._type

    #setzt die Lichtstärke
    def setBrightness(self, newBrigthness):
        if newBrigthness >= 0:
            self._brightness = newBrigthness
        else:
            print(newBrigthness + " is not a valid")
            
    #erstellt das Licht (Name ist erforderlich)
    def creatingLight(self, name):
        light_data=bpy.data.lights.new(name=name,type=self._type)
        light_data.energy=self._brightness
        Licht = bpy.data.objects.new(name,object_data=light_data)
        bpy.context.collection.objects.link(Licht)
        bpy.context.view_layer.objects.active = Licht
        #setzt die Position des lichts
        Licht.location = (self._xLocation, self._yLocation, self._zLocation)

###Zu Testzwecken
##Testlicht
#l1=Light("SUN",radius*math.sin(math.radians(10)),
#         radius*math.cos(math.radians(winkel)),
#         radius*math.sin(math.radians(winkel)),
#         sun_brightness)
#l1.setType("s")
#l1.creatingLight("Sonne")

## update scene, if needed
#dg = bpy.context.evaluated_depsgraph_get() 
#dg.update()