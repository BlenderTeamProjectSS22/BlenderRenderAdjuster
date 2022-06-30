import bpy
import math
from Lightning.light_class import *
from utils import *
#from camera_animation_module import *

# delete all lights
def delete_all_lights() -> None:
    bpy.ops.object.select_all(action = "DESELECT")
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT':
            ob.select_set(True)
    bpy.ops.object.delete()
           
# delete the lights in "lights"-array (the elements are objects)
def delete_lights(lights: list[Light]) -> None:
    bpy.ops.object.select_all(action = 'DESELECT')
    for light in lights:
        if bpy.context.scene.objects.get(light.get_name()):
            bpy.data.objects[light.get_name()].select_set(True)
    bpy.ops.object.delete()
    
# calculates the distance of the light object "object" from the center
def radius_of_light_object(object: Light) -> float:
    result = 0
    for position in object.get_position():
        result += math.pow(position, 2)
    return math.sqrt(result)

# creating fill- and rim-light
# - radius_rim = the distance of the rim light
# - brightness_rim = the brightness of the rim light
# - brightness_fill = the brightness of the fill light
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def creating_fill_and_rim_light(radius_rim: float, brightness_rim: float,
                                brightness_fill: float, camera_object: OrbitCam) -> list[Light]:
    # if camera is used
    if not camera_object == None:
        camera_angle_diff = camera_object.get_location()[0] / camera_object.get_distance()
        if camera_angle_diff > 1:
            camera_angle_diff = 1
        camera_angle = math.asin(camera_angle_diff)
        # creating Lights
        rim = PointLight("rim", -radius_rim * math.sin(camera_angle),
                    -radius_rim * math.cos(camera_angle),
                    radius_rim * math.sin(math.radians(170)),
                    brightness_rim, 0.25)
        fill = PointLight("fill", 20 * math.sin(camera_angle),
                    20 * math.cos(camera_angle),
                    20 * math.sin(math.radians(170)),
                    brightness_fill, 5)
        # link lights to controller
        rim.get_datas()[1].parent = camera_object.get_controller()  
        fill.get_datas()[1].parent = camera_object.get_controller()     
    # if camera is not used
    else:
        # creating Lights
        fill = PointLight("fill", -14, 16, 0.3, brightness_fill, 5)
        rim = PointLight("rim", 0, -radius_rim,
                        radius_rim * math.sin(math.radians(170)),
                        brightness_rim, 0.25)
    return [fill, rim]

# creating the daylight (plus rim- and fill-light if add_fill_and_rim_light = True)
# returns an array of all objects
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def day_light(brightness: float, angle: int, add_fill_and_rim_light: bool, camera_object: OrbitCam) -> list[Light]:
    # precondition
    if angle >= 180:
        angle = 180
    elif angle < 0:
        angle = 0
    # the distance of the lights
    radius_main = 20
    radius_rim = 50
    # the brightness of the lights
    brightness_main = 3 * brightness
    brightness_rim = 6500
    brightness_fill = 1500
    # to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    # color of the sun
    color = [0.945, 0.855, 0.643]
    # dawnlight
    if angle > 150:
        color[1] -= (angle-140) * 0.021
        color[2] -= (angle-140) * 0.016
    # creating the lights
    sonne = RotateLight("Sonne", "SUN", radius_main * math.sin(math.radians(10)),
                        radius_main * math.cos(math.radians(angle)),
                        radius_main * math.sin(math.radians(angle)),
                        -math.cos(math.radians(angle)), math.sin(math.radians(10)), 0,
                        brightness_main)
    sonne.set_color(color[0], color[1], color[2])
    if add_fill_and_rim_light:
        list = [sonne]
        list.extend(creating_fill_and_rim_light(
                                    radius_rim, brightness_rim, brightness_fill, camera_object))
        return list
    else:
        return [sonne]

# creating the nightlight (plus rim- and fill-light if add_fill_and_rim_light = True)
# returns an array of all objects
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def night_light(brightness: float, angle: int, add_fill_and_rim_light: bool, camera_object: OrbitCam) -> list[Light]:
    # precondition
    if angle > 180:
        angle = 180
    elif angle < 0:
        angle = 0
    # the distance of the lights
    radius_main = 40
    radius_rim = 30
    # the brightness of the lights
    brightness_main = 6 * brightness
    brightness_rim = 2000
    brightness_fill = 700
    # to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    # color of the moon
    color = [0.001, 0.044, 0.107]
    # creating the light
    mond = RotateLight("Mond", "SUN", radius_main * math.sin(math.radians(10)),
                      radius_main * math.cos(math.radians(angle)),
                      radius_main * math.sin(math.radians(angle)),
                      -math.cos(math.radians(angle)), math.sin(math.radians(10)), 0,
                      brightness_main)
    mond.set_color(color[0], color[1], color[2])
    list = [mond]
    # if adding fill and rim light
    if add_fill_and_rim_light:
        list.extend(creating_fill_and_rim_light(
                                    radius_rim, brightness_rim, brightness_fill, camera_object))
    return list

# creating the laternlight (plus rim- and fill-Licht if add_fill_and_rim_light = True)
# returns an array of all objects
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def latern_light(brightness: float, height: float,
                add_fill_and_rim_light: bool, camera_object: OrbitCam) -> list[Light]:
    # the distance of the lights
    radius_rim = 40
    # the brightness of the lights
    brightness_main = 3500 * brightness
    brightness_rim = 2500
    brightness_fill = 850
    # to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    # color of the spot light
    color = [1, 0.35, 0]
    # creating the lights
    spot = Light("Laterne", "SPOT", 0, 0, height, brightness_main)
    spot.set_color(color[0], color[1], color[2])
    if add_fill_and_rim_light:
        list = [spot]
        list.extend(creating_fill_and_rim_light(
                                        radius_rim, brightness_rim, brightness_fill, camera_object))
        return list
    else:
        return [spot]

# private method
# set the value for every frame of the day-night circle function
# function should only be used in day_night_circle()
def frame_setting_of_day_night_circle(frame_current: int, lights: list[Light], scene, current_angle: int, day_color: list[float],
                                        brightnesses: list[float], is_day: bool,
                                        lightcollection: list[Light], radius: float, first_element : bool) -> None:
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        # day and night change
        if current_angle >= 180:
            lights[0].set_brightness(0)
            if first_element:
                lights[0] = lightcollection[1]
                lights[0].set_brightness(brightnesses[1])
                assert lightcollection[0].get_brightness() == 0
            else:
                lights[0] = lightcollection[0]
                lights[0].set_brightness(brightnesses[0])
                assert lightcollection[1].get_brightness() == 0
            first_element = not first_element
            is_day = not is_day
            if is_day:
                lights[0].set_color(day_color[0], day_color[1], day_color[2])
            current_angle = 0
            radius = radius_of_light_object(lights[0])
            assert lights[0].get_type() == "SUN" 
        # day and night dont change
        else:
            # dawnlight
            if is_day and current_angle >= 140:               
                lights[0].set_color(day_color[0],
                                day_color[1] - (current_angle-140) * 0.021,
                                day_color[2] - (current_angle-140) * 0.016)
            # fit position and rotation 
            lights[0].set_position(radius * math.sin(math.radians(10)),
                                radius * math.cos(math.radians(current_angle)),
                                radius * math.sin(math.radians(current_angle))) 
            lights[0].set_rotation(-math.cos(math.radians(current_angle)), math.sin(math.radians(10)), 0)
        # increment angle and saving datas in frames
        current_angle += 1
        lights[0].get_datas()[1].keyframe_insert(data_path = "rotation_euler", frame = f)
        lights[0].get_datas()[1].keyframe_insert(data_path = "location", frame = f)
        for light in lightcollection:
            light.get_datas()[0].keyframe_insert(data_path = "energy", frame = f)
            light.get_datas()[0].keyframe_insert(data_path = "color", frame = f)
    scene.frame_set(frame_current) 

# makes a day-night-circle
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
# all light objects will be deleted
def day_night_circle(starting_time: int, brightness: float,
                     add_fill_and_rim_light: bool, camera_object: OrbitCam) -> list[Light]:
    # before starting time
    delete_all_lights()
    lightcollection : list[Light] = []
    # color of the sun (important for the dawn light)
    day_color = [0.945, 0.855, 0.643]
    # preconditions
    if starting_time > 24 or starting_time < 0:
        current_time = 0
    else:
        current_time = starting_time
    # setting starting values
    current_angle = ((current_time % 12) * 15 + 89) % 180
    current_time *= 10
    if current_time > 60 and starting_time <= 180:
        is_day = True
        lights = day_light(brightness, current_angle,
                           add_fill_and_rim_light, camera_object)
        lightcollection = [lights[0]]
        lightcollection.extend(night_light(brightness, 0, False, camera_object))
    else:
        is_day = False
        lights = night_light(brightness, current_angle,
                             add_fill_and_rim_light, camera_object)
        lightcollection = [lights[0]]
        lightcollection.extend(day_light(brightness, 0, False, camera_object))
    # bightnesses: for saving the energies of the light sources
    brightnesses = [lightcollection[0].get_brightness(), lightcollection[1].get_brightness()]
    assert len(lightcollection) == 2 and len(brightnesses) == 2
    lightcollection[1].set_brightness(0)
    first_element = True
    radius = radius_of_light_object(lights[0])
    scene = bpy.context.scene
    frame_current = scene.frame_current
    
    # setting per frame
    frame_setting_of_day_night_circle(frame_current, lights, scene, current_angle, day_color,
                                    brightnesses, is_day,
                                    lightcollection, radius, first_element)
    
    # postconditions
    assert len(lightcollection) == 2
    if add_fill_and_rim_light == False:
        return lightcollection
    assert len(lights) == 3
    lightcollection.append(lights[1])
    lightcollection.append(lights[2])
    return lightcollection

# deletes the animation of all lights in "lights"
def delete_light_animation(lights : list[Light]):
    for light in lights:
        light.get_datas()[0].animation_data_clear()
        light.get_datas()[1].animation_data_clear()

### for testing

## create camera
# deleteAllCameras()
# myCamera = OrbitCam(bpy.data.objects['Kopf'])
# myCamera.set_distance(6)

## test functions
# delete_all_lights()
# night_light(1, 50, True, myCamera)
# delete_lights(night_light(1, 90, True, None))
# lights = day_light(1, 180, True, None)
# latern_light(1, 20, True, None)
# delete_light_animation(day_night_circle(12, 1, True, None))
# myCamera.rotate_z(270)

# update scene, if needed
# dg = bpy.context.evaluated_depsgraph_get() 
# dg.update()