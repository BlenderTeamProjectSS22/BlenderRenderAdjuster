import bpy
import math

# light class with attributes:
# --- name = name of the light
# --- type = type of the light (POINT, SUN, SPOT, AREA) (default POINT)
# --- x_loxation = the x-coordinate
# --- y_loxation = the y-coordinate
# --- z_loxation = the z-coordinate
# --- brightness = the strength of the light
# --- color = the color of the light in RGB (values are [0;1]) (default is [1,1,1])
class Light:
    def __init__(self, name: str, type: str, x_Location: float,
                 y_Location: float, z_Location: float, brightness: float) -> None:
        self._name = name
        self._color = [1, 1, 1]
        # set type
        if type == "SUN" or type == "POINT" or type == "AREA" or type == "SPOT":
            self._type = type
            self._light_data.type = type
        else:
            print(str(self._name) + ": type: " + str(type) + " is not a valid type")
            self._type = "POINT"
            self._light_data.type = "POINT"
            print(str(self._name) + ": type: type is set to POINT")
        # apply settings
        self._light_data = bpy.data.lights.new(name = name, type = self._type)
        self.set_brightness(brightness)
        self._light_data.color = (self._color[0],self._color[1],self._color[2])
        self._light_object = bpy.data.objects.new(name, object_data = self._light_data)
        bpy.context.collection.objects.link(self._light_object)
        bpy.context.view_layer.objects.active = self._light_object
        # set the light position
        self.set_position(x_Location, y_Location, z_Location)  
    
    # get the position in [x,y,z]-array 
    def get_position(self) -> list[float]:
        return [self._x_location, self._y_location, self._z_location]

    # set the position in (x,y,z)
    def set_position(self, x_location: float, y_location: float, z_location: float) -> None:
        self._x_location = x_location
        self._y_location = y_location
        self._z_location = z_location
        self._light_object.location = (self._x_location, self._y_location, self._z_location)

    # get the name
    def get_name(self) -> str:
        return self._name

    # rename the light to "name"
    def rename(self, name: str) -> None:
        self._name = name
        self._light_data.name = name
        self._light_object.name = name

    # get the typ of light
    def get_type(self) -> str:
        return self._type
    
    # get the brightness
    def get_brightness(self) -> float:
        return self._brightness

    # set the brightness
    def set_brightness(self, new_brigthness: float) -> None:
        if new_brigthness >= 0:            
            self._brightness = new_brigthness           
        else:
            print(str(self._name) + ": brightness: only positiv values allowed")
            self._brightness = 0
        self._light_data.energy = self._brightness
            
    
    # set the color (values are [0;1])
    def set_color(self, red: float, green: float, blue: float) -> None:
        if (red < 0 or red > 1 or green < 0 or
            green > 1 or blue < 0 or blue > 1):
            print(str(self._name) + ": color: only values in [0;1] allowed")
        else:
            self._color = [red, green, blue]
            self._light_data.color = (self._color[0], self._color[1], self._color[2])
    
    # get the color as [r,g,b]-array with values [0;1]
    def get_color(self) -> list[float]:
        return self._color

    # get the datas of the light object (first is the light settings; second the object data)
    def get_datas(self) -> list[any]:
        return [self._light_data, self._light_object]

# PointLight = a subclass of light with extra attributes
# --- radius = the Radius of the point
# type is not an input
class PointLight(Light):
    def __init__(self, name: str, x_location: float, y_location: float,
                 z_location: float, brightness: float, radius: float) -> None:
        super().__init__(name, "POINT", x_location, y_location, z_location, brightness)
        self.set_radius(radius)
    
    # set the radius (only positiv values allowed)
    def set_radius(self, new_radius: float) -> None:
        if (new_radius < 0):
            print(str(self._name)+": radius: only positiv values allowed")
            self._radius = 0.25
        else:
            self._radius = new_radius
        self._light_data.shadow_soft_size = new_radius

    # get the radius
    def get_radius(self) -> float:
        return self._radius

# RotateLight = a subclass of light with rotation
# --- x_rotation = the x-rotation
# --- y_rotation = the y-rotation
# --- z_rotation = the z-rotation
class RotateLight(Light):
    def __init__(self, name: str, type: str, x_location: float, y_location: float, z_location: float,
                 x_rotation: float, y_rotation: float, z_rotation: float, brightness: float) -> None:
        super().__init__(name, type, x_location, y_location, z_location, brightness)
        self.set_rotation(x_rotation, y_rotation, z_rotation)
    
    # set the rotation
    def set_rotation(self, x_rotation: float, y_rotation: float, z_rotation: float) -> None:
        self._x_rotation = x_rotation
        self._y_rotation = y_rotation
        self._z_rotation = z_rotation
        self._light_object.rotation_euler = (self._x_rotation, self._y_rotation, self._z_rotation)

    # get the rotation as [x,y,z]-array
    def get_rotation(self) -> list[int]:
        return [self._x_rotation, self._y_rotation, self._z_rotation]

### for testing

## variables
#
## angle of the light
# angle = 10
## distance of the light
# radius = 20
## brightness of the light
# sun_brightness = 3
## color
# color = [0.001, 0.044, 0.107]

## delete all test lights
# bpy.ops.object.select_all(action = 'DESELECT')
# if bpy.context.scene.objects.get('Sonne'):
#     bpy.data.objects['Sonne'].select_set(True)
# if bpy.context.scene.objects.get('fill'):
#     bpy.data.objects['fill'].select_set(True)
## delete all selected objects
# bpy.ops.object.delete()

## test lights
# l1 = Light("Sonne", "SUN", radius * math.sin(math.radians(10)),
#            radius * math.cos(math.radians(angle)),
#            radius * math.sin(math.radians(angle)),
#            sun_brightness)
# l1.set_color(color[0], color[1], color[2])
# l1.set_position(0, 0, 10)
# l1.rename("Ilios")
# l1.set_brightness(100)
# print(l1.get_color())
# l2 = PointLight("fill", -14, 16, 0.3, 3000, 2)
# l2.set_radius(5)
# l3 = RotateLight("Sonne", "SUN", radius * math.sin(math.radians(10)),
#               radius * math.cos(math.radians(angle)),
#               radius * math.sin(math.radians(angle)),
#               0, 0, 0, -4)
# l3.set_rotation(-math.cos(math.radians(angle)), math.sin(math.radians(10)), 0)

## update scene, if needed
# dg = bpy.context.evaluated_depsgraph_get() 
# dg.update()