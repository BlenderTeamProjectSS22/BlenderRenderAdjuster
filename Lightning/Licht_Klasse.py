import bpy
import math

#light class with attributes:
#---name = name of the light
#---type = type of the light (POINT, SUN, SPOT, AREA)
#---xLoxation = the x-coordinate
#---yLoxation = the y-coordinate
#---zLoxation = the z-coordinate
#---brightness = the strength of the light
#------color = the color of the light in RGB (values are [0;1]) (default is [1,1,1])
class Light:
    def __init__(self, name: str, type: str, xLocation: float,
                 yLocation: float, zLocation: float, brightness: float) -> None:
        self._name = name
        self._type = type
        self._color = [1, 1, 1]
        #apply settings
        self._light_data = bpy.data.lights.new(name = name, type = self._type)
        self.setBrightness(brightness)
        self._light_data.color = (self._color[0],self._color[1],self._color[2])
        self._Licht = bpy.data.objects.new(name, object_data = self._light_data)
        bpy.context.collection.objects.link(self._Licht)
        bpy.context.view_layer.objects.active = self._Licht
        #set the light position
        self.setPosition(xLocation, yLocation, zLocation)  
    
    #get the position in [x,y,z]-array 
    def getPosition(self) -> list[float]:
        return [self._xLocation, self._yLocation, self._zLocation]

    #set the position in (x,y,z)
    def setPosition(self, xLocation: float, yLocation: float, zLocation: float) -> None:
        self._xLocation = xLocation
        self._yLocation = yLocation
        self._zLocation = zLocation
        self._Licht.location = (self._xLocation, self._yLocation, self._zLocation)

    #get the name
    def getName(self) -> str:
        return self._name

    #rename the light to "name"
    def rename(self, name: str) -> None:
        self._name = name
        self._light_data.name = name
        self._Licht.name = name

    #get the typ of light
    def getType(self) -> str:
        return self._type

    #set the type of light
    def setType(self, newType: str) -> None:
        if newType == "SUN" or newType == "POINT" or newType == "AREA" or newType == "SPOT":
            self._type = newType
            self._light_data.type = newType
        else:
            print(str(self._name) + ": type: " + str(newType) + " is not a valid type")
    
    #get the brightness
    def getBrightness(self) -> float:
        return self._brightness

    #set the brightness
    def setBrightness(self, newBrigthness: float) -> None:
        if newBrigthness >= 0:            
            self._brightness = newBrigthness           
        else:
            print(str(self._name) + ": brightness: only positiv values allowed")
            self._brightness = 0
        self._light_data.energy = self._brightness
            
    
    #set the color (values are [0;1])
    def setColor(self, red: float, green: float, blue: float) -> None:
        if (red < 0 or red > 1 or green < 0 or
            green > 1 or blue < 0 or blue > 1):
            print(str(self._name) + ": color: only values in [0;1] allowed")
        else:
            self._color = [red, green, blue]
            self._light_data.color = (self._color[0], self._color[1], self._color[2])
    
    #get the color as [r,g,b]-array with values [0;1]
    def getColor(self) -> list[float]:
        return self._color

    #get the datas of the light object (first is the light settings; second the object data)
    def getDatas(self) -> list[any]:
        return [self._light_data, self._Licht]

#PointLight = a subclass of light with extra attributes
#---radius = the Radius of the point
#type is not an input
class PointLight(Light):
    def __init__(self, name: str, xLocation: float, yLocation: float,
                 zLocation: float, brightness: float, radius: float) -> None:
        super().__init__(name, "POINT", xLocation, yLocation, zLocation, brightness)
        self.setRadius(radius)
    
    #set the radius (only positiv values allowed)
    def setRadius(self, newRadius: float) -> None:
        if (newRadius < 0):
            print(str(self._name)+": radius: only positiv values allowed")
            self._radius = 0.25
        else:
            self._radius = newRadius
        self._light_data.shadow_soft_size = newRadius

    #get the radius
    def getRadius(self) -> float:
        return self._radius

#RotateLight = a subclass of light with rotation
#---xRotation = the x-rotation
#---yRotation = the y-rotation
#---zRotation = the z-rotation
class RotateLight(Light):
    def __init__(self, name: str, type: str, xLocation: float, yLocation: float, zLocation: float,
                 xRotation: float, yRotation: float, zRotation: float, brightness: float) -> None:
        super().__init__(name, type, xLocation, yLocation, zLocation, brightness)
        self.setRotation(xRotation, yRotation, zRotation)
    
    #set the rotation
    def setRotation(self, xRotation: float, yRotation: float, zRotation: float) -> None:
        self._xRotation = xRotation
        self._yRotation = yRotation
        self._zRotation = zRotation
        self._Licht.rotation_euler = (self._xRotation, self._yRotation, self._zRotation)

    #get the rotation as [x,y,z]-array
    def getRotation(self) -> list[int]:
        return [self._xRotation, self._yRotation, self._zRotation]

###for testing

##Variabeln
#
##angle of the light
#winkel = 10
##distance of the light
#radius = 20
##brightness of the light
#sun_brightness = 3
##color
#color=[0.001, 0.044, 0.107]

##delete all test lights
#bpy.ops.object.select_all(action = 'DESELECT')
#if bpy.context.scene.objects.get('Sonne'):
#    bpy.data.objects['Sonne'].select_set(True)
#if bpy.context.scene.objects.get('fill'):
#    bpy.data.objects['fill'].select_set(True)
## delete all selected objects
#bpy.ops.object.delete()

##test lights
#l1 = Light("Sonne", "SUN",radius * math.sin(math.radians(10)),
#           radius * math.cos(math.radians(winkel)),
#           radius * math.sin(math.radians(winkel)),
#           sun_brightness)
#l1.setType("s")
#l1.setColor(color[0], color[1], color[2])
#l1.setPosition(0, 0, 10)
#l1.rename("Ilios")
#l1.setBrightness(100)
#l1.setType("POINT")
#print(l1.getColor())
#l2 = PointLight("fill", -14, 16, 0.3, 3000, 2)
#l2.setRadius(5)
#l3 = RotateLight("Sonne", "SUN", radius * math.sin(math.radians(10)),
#              radius * math.cos(math.radians(winkel)),
#              radius * math.sin(math.radians(winkel)),
#              0, 0, 0, -4)
#l3.setRotation(-math.cos(math.radians(winkel)), math.sin(math.radians(10)), 0)

## update scene, if needed
#dg = bpy.context.evaluated_depsgraph_get() 
#dg.update()