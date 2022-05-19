import bpy
import math

#Lichtklasse mit Attributen:
#---name=Name des Lichts
#---type=Typ des Lichts(POINT,SUN,SPOT,AREA)
#---xLoxation=Die x-Koordinate
#---yLoxation=Die y-Koordinate
#---zLoxation=Die z-Koordinate
#---brightness=Die Lichtstärke
#------color=Die Farbe des Lichts in rgb (Wertebereich [0;1]) (default ist [1,1,1])
class Light:
    def __init__(self, name , type, xLocation, yLocation, zLocation, brightness):
        self._name = name
        self._type = type
        self._xLocation = xLocation
        self._yLocation = yLocation
        self._zLocation = zLocation
        self._brightness = brightness
        self._color = [1, 1, 1]
        self._light_data=bpy.data.lights.new(name=name,type=self._type)
        self._light_data.energy=self._brightness
        self._light_data.color=(self._color[0],self._color[1],self._color[2])
        self._Licht = bpy.data.objects.new(name,object_data=self._light_data)
        bpy.context.collection.objects.link(self._Licht)
        bpy.context.view_layer.objects.active = self._Licht
        #setzt die Position des lichts
        self._Licht.location = (self._xLocation, self._yLocation, self._zLocation)  
    
    #gibt die Position des Lichts als [x,y,z]-Array zurück
    def getPosition(self):
        return [self._xLocation, self._yLocation, self._zLocation]

    #setzt die Position des Lichts in (x,y,z)
    def setPosition(self, xLocation, yLocation, zLocation):
        self._xLocation = xLocation
        self._yLocation = yLocation
        self._zLocation = zLocation
        self._Licht.location = (self._xLocation, self._yLocation, self._zLocation)

    #gibt den Namen des Lichts zurück
    def getName(self):
        return self._name

    #bennent das Licht in "name" um
    def rename(self, name):
        self._name=name
        self._light_data.name=name
        self._Licht.name=name

    #gibt den Typ des Lichts zurück
    def getType(self):
        return self._type

    #setzt den Typ des Lichts
    def setType(self, newType):
        if newType == "SUN" or newType == "POINT" or newType == "AREA" or newType == "SPOT":
            self._type = newType
            self._light_data.type=newType
        else:
            print(" Typ: "+ newType + " is not a valid type")
    
    #gibt die Lichtstärke zurück
    def getBrightness(self):
        return self._type

    #setzt die Lichtstärke
    def setBrightness(self, newBrigthness):
        if newBrigthness >= 0:
            self._brightness = newBrigthness
            self._light_data.energy=self._brightness
        else:
            print(" Helligkeit: "+ newBrigthness + " is not a valid")
    
    #setzt die Farbe (Wertebereich [0;1])
    def setColor(self, red, green, blue):
        if (red < 0 or red > 1 or green < 0 or
            green > 1 or blue < 0 or blue > 1):
            print(" Farbe: nur Werte im Wertebereich [0;1] erlaubt")
        else:
            self._color = [red, green, blue]
            self._light_data.color=(self._color[0],self._color[1],self._color[2])
    
    #gibt die Farbe zurück
    def getColor(self):
        return self._color

#PointLight = eine Subklasse von Licht mit zusätzlichen Attributen
#---radius=der Radius des Punktes
#Typ wird nicht angegeben
class PointLight(Light):
    def __init__(self, name, xLocation, yLocation, zLocation, brightness, radius):
        super().__init__(name, "POINT", xLocation, yLocation, zLocation, brightness)
        self._radius = radius
        self._light_data.shadow_soft_size=radius
    
    #setzt den Radius (nur positive Werte erlaubt)
    def setRadius(self, newRadius):
        if (newRadius < 0):
            print(" Radius: nur positive Werte erlaubt")
        else:
            self._radius = newRadius
            self._light_data.shadow_soft_size=newRadius

    #gibt den Radius zurück
    def getRadius(self):
        return self._color

###Zu Testzwecken

##Variabeln
#
##Einschlagswinkel des Sonnenlichts
#winkel=80
##Entfernung des Sonnenlichts
#radius=20
##Lichtstärke des Sonnenlichts
#sun_brightness=3
##Farbe
#color=[0.001,0.044,0.107]

##Lösche alle Testlichter
#bpy.ops.object.select_all(action='DESELECT')
#if bpy.context.scene.objects.get('Sonne'):
#    bpy.data.objects['Sonne'].select_set(True)
#if bpy.context.scene.objects.get('fill'):
#    bpy.data.objects['fill'].select_set(True)
## delete all selected objects
#bpy.ops.object.delete()

##Testlichter
#l1=Light("Sonne", "SUN",radius*math.sin(math.radians(10)),
#         radius*math.cos(math.radians(winkel)),
#         radius*math.sin(math.radians(winkel)),
#         sun_brightness)
#l1.setType("s")
#l1.setColor(color[0],color[1],color[2])
#l1.setPosition(0,0,10)
#l1.rename("Ilios")
#l1.setBrightness(100)
#l1.setType("POINT")
#l2=PointLight("fill",-14,16,0.3,3000,2)
#l2.setRadius(5)

## update scene, if needed
#dg = bpy.context.evaluated_depsgraph_get() 
#dg.update()