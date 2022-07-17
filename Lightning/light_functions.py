import bpy
import math
from Lightning.light_class import *
from utils import OrbitCam
from HDRI.hdri import background_brightness_affects_objects

# delete all lights
def delete_all_lights() -> None:
    bpy.ops.object.select_all(action = "DESELECT")
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT':
            ob.select_set(True)
    bpy.ops.object.delete()

# if "is_light" is active, enabling lights and disabling background lightning
# else deleting all lights and enabling background lightning
def lights_enabled(is_light: bool) -> None:
    if is_light:
        print("Enabling lights, disabling background lighting")
        background_brightness_affects_objects(False)
    else:
        delete_all_lights()
        print("Deleting all lights, enabling background lighting")
        background_brightness_affects_objects(True)
           
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

# returns the angle-value between 0 and 180 degrees
def precondition_angle_check(angle : int) -> int:
    if angle >= 180:
        return 180
    elif angle < 0:
        return 0
    else:
        return angle

# creating fill- and rim-light
# - radius_rim = the distance of the rim light
# - brightness_rim = the brightness of the rim light
# - brightness_fill = the brightness of the fill light
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def creating_fill_and_rim_light(radius_rim: float, brightness_rim: float,
                                brightness_fill: float, camera_object: OrbitCam) -> list[Light]:
    # constants
    POINT_LIGHT_RADIUS_OF_RIM = 0.25
    POINT_LIGHT_RADIUS_OF_FILL = 5
    DISTANCE_FILL_LIGHT = 20
    STANDARD_FILL_LIGHT_POS = [-14, -16, 0.3]
    Z_ANGLE : int = 170
    # if camera is used
    if not camera_object == None:
        camera_angle_diff = camera_object.get_location()[0] / camera_object.get_distance()
        if camera_angle_diff > 1:
            camera_angle_diff = 1
        camera_angle = math.asin(camera_angle_diff)
        # creating Lights
        rim = PointLight("rim", -radius_rim * math.sin(camera_angle),
                    -radius_rim * math.cos(camera_angle),
                    radius_rim * math.sin(math.radians(Z_ANGLE)),
                    brightness_rim, POINT_LIGHT_RADIUS_OF_RIM)
        fill = PointLight("fill", DISTANCE_FILL_LIGHT * math.sin(camera_angle),
                    DISTANCE_FILL_LIGHT * math.cos(camera_angle),
                    DISTANCE_FILL_LIGHT * math.sin(math.radians(Z_ANGLE)),
                    brightness_fill, POINT_LIGHT_RADIUS_OF_FILL)
        # link lights to controller
        rim.get_datas()[1].parent = camera_object.get_controller()  
        fill.get_datas()[1].parent = camera_object.get_controller()     
    # if camera is not used
    else:
        # creating Lights
        fill = PointLight("fill", STANDARD_FILL_LIGHT_POS[0], STANDARD_FILL_LIGHT_POS[1],
                         STANDARD_FILL_LIGHT_POS[2], brightness_fill, POINT_LIGHT_RADIUS_OF_FILL)
        rim = PointLight("rim", 0, -radius_rim,
                        radius_rim * math.sin(math.radians(Z_ANGLE)),
                        brightness_rim, POINT_LIGHT_RADIUS_OF_RIM)
    return [fill, rim]

# creating the daylight (plus rim- and fill-light if add_fill_and_rim_light = True)
# returns an array of all objects
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def day_light(brightness: float, angle: int, add_fill_and_rim_light: bool, camera_object: OrbitCam) -> list[Light]:
    # constants
    BRIGHTNESS_OF_MAIN = 2
    BRIGHTNESS_OF_RIM = 6500
    BRIGHTNESS_OF_FILL = 1500
    RADIUS_OF_RIM = 50
    RADIUS_OF_MAIN = 20
    DAWN_ANGLE : int = 30
    HALF_CYCLE_ANGLE : int = 180
    # precondition
    angle = precondition_angle_check(angle)
    # the distance of the lights
    radius_main = RADIUS_OF_MAIN
    radius_rim = RADIUS_OF_RIM
    # the brightness of the lights
    brightness_main = BRIGHTNESS_OF_MAIN * brightness
    brightness_rim = BRIGHTNESS_OF_RIM
    brightness_fill = BRIGHTNESS_OF_FILL
    # to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    # color of the sun
    color = [0.945, 0.855, 0.643]
    # dawnlight
    if angle > (HALF_CYCLE_ANGLE - DAWN_ANGLE):
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
    # constants
    BRIGHTNESS_OF_MAIN = 2
    BRIGHTNESS_OF_RIM = 2000
    BRIGHTNESS_OF_FILL = 700
    RADIUS_OF_RIM = 30
    RADIUS_OF_MAIN = 40
    RGB_COLOR_OF_MOON_LIGHT = [0.001, 0.044, 0.107]
    # precondition
    angle = precondition_angle_check(angle)
    # the distance of the lights
    radius_main = RADIUS_OF_MAIN
    radius_rim = RADIUS_OF_RIM
    # the brightness of the lights
    brightness_main = BRIGHTNESS_OF_MAIN * brightness
    brightness_rim = BRIGHTNESS_OF_RIM
    brightness_fill = BRIGHTNESS_OF_FILL
    # to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    # creating the light
    mond = RotateLight("Mond", "SUN", radius_main * math.sin(math.radians(10)),
                      radius_main * math.cos(math.radians(angle)),
                      radius_main * math.sin(math.radians(angle)),
                      -math.cos(math.radians(angle)), math.sin(math.radians(10)), 0,
                      brightness_main)
    mond.set_color(RGB_COLOR_OF_MOON_LIGHT[0], RGB_COLOR_OF_MOON_LIGHT[1], RGB_COLOR_OF_MOON_LIGHT[2])
    list = [mond]
    # if adding fill and rim light
    if add_fill_and_rim_light:
        list.extend(creating_fill_and_rim_light(
                                    radius_rim, brightness_rim, brightness_fill, camera_object))
    return list

# creating the lanternlight (plus rim- and fill-Licht if add_fill_and_rim_light = True)
# returns an array of all objects
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
def lantern_light(brightness: float, height: float,
                add_fill_and_rim_light: bool, camera_object: OrbitCam) -> list[Light]:
    # constants
    BRIGHTNESS_OF_MAIN = 3500
    BRIGHTNESS_OF_RIM = 2500
    BRIGHTNESS_OF_FILL = 850
    RADIUS_OF_RIM = 40
    RGB_COLOR_OF_LANTERN_LIGHT = [1, 0.35, 0]
    # the distance of the lights
    radius_rim = RADIUS_OF_RIM
    # the brightness of the lights
    brightness_main = BRIGHTNESS_OF_MAIN * brightness
    brightness_rim = BRIGHTNESS_OF_RIM
    brightness_fill = BRIGHTNESS_OF_FILL
    # to fit brightness
    if brightness < 1:
        brightness_rim *= brightness
        brightness_fill *= brightness
    # creating the lights
    spot = Light("Laterne", "SPOT", 0, 0, height, brightness_main)
    spot.set_color(RGB_COLOR_OF_LANTERN_LIGHT[0], RGB_COLOR_OF_LANTERN_LIGHT[1], RGB_COLOR_OF_LANTERN_LIGHT[2])
    if add_fill_and_rim_light:
        list = [spot]
        list.extend(creating_fill_and_rim_light(
                                        radius_rim, brightness_rim, brightness_fill, camera_object))
        return list
    else:
        return [spot]

# private method
# puts the rotate light in the sky with "radius" and "angle" 
def put_rotate_light_in_cyrcle(light: Light, radius: float, angle : int):
    light.set_position(radius * math.sin(math.radians(10)),
                        radius * math.cos(math.radians(angle)),
                        radius * math.sin(math.radians(angle))) 
    light.set_rotation(-math.cos(math.radians(angle)), math.sin(math.radians(10)), 0)

# private method
# set the value for every frame of the day-night circle function
# function should only be used in day_night_circle()
def frame_setting_of_day_night_cycle(frame_current: int, lights: list[Light], scene, current_angle: int, day_color: list[float],
                                        brightnesses: list[float], is_day: bool,
                                        lightcollection: list[Light], radius: float, speed: int) -> None:
    # constants
    DAWN_ANGLE : int = 35
    HALF_CYCLE_ANGLE : int = 180
    # loop
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        # day and night change
        if current_angle >= HALF_CYCLE_ANGLE:
            is_day = not is_day
            if is_day:
                lights[0] = lightcollection[0]
            else:
                lights[0] = lightcollection[1]
            current_angle = 0
            radius = radius_of_light_object(lights[0])
            assert lights[0].get_type() == "SUN" 
        # day and night dont change
        else:
            # dawnlight
            if current_angle > (HALF_CYCLE_ANGLE - DAWN_ANGLE):  
                if is_day:       
                    lightcollection[0].set_color(day_color[0],
                                                day_color[1] - (current_angle-(HALF_CYCLE_ANGLE - DAWN_ANGLE)) * 0.021,
                                                day_color[2] - (current_angle-(HALF_CYCLE_ANGLE - DAWN_ANGLE)) * 0.016)
                lightcollection[not is_day].set_brightness(((HALF_CYCLE_ANGLE - current_angle) * brightnesses[not is_day]) / (2 * DAWN_ANGLE)
                                                        + (brightnesses[not is_day] / 2))
                lightcollection[is_day].set_brightness(((DAWN_ANGLE-(HALF_CYCLE_ANGLE -current_angle)) * brightnesses[is_day]) / (2 * DAWN_ANGLE))
            elif current_angle >= ((HALF_CYCLE_ANGLE - DAWN_ANGLE) - speed):
                put_rotate_light_in_cyrcle(lightcollection[is_day], radius_of_light_object(lightcollection[is_day]), 0)
                lightcollection[is_day].get_datas()[1].keyframe_insert(data_path = "rotation_euler", frame = f)
                lightcollection[is_day].get_datas()[1].keyframe_insert(data_path = "location", frame = f)
                if not is_day:
                    lightcollection[is_day].set_color(day_color[0], day_color[1], day_color[2])
            elif current_angle < DAWN_ANGLE:
                lightcollection[not is_day].set_brightness((current_angle * brightnesses[not is_day]) / (2 * DAWN_ANGLE) + (brightnesses[not is_day] / 2))
                lightcollection[is_day].set_brightness(((DAWN_ANGLE-1-current_angle) * brightnesses[is_day]) / (2 * DAWN_ANGLE))
            elif current_angle < (DAWN_ANGLE + speed):
                lightcollection[is_day].set_brightness(0)
                lightcollection[not is_day].set_brightness(brightnesses[not is_day])
            # fit position and rotation  
            put_rotate_light_in_cyrcle(lights[0], radius, current_angle)
        # increment angle and saving datas in frames
        current_angle += speed
        lights[0].get_datas()[1].keyframe_insert(data_path = "rotation_euler", frame = f)
        lights[0].get_datas()[1].keyframe_insert(data_path = "location", frame = f)
        for light in lightcollection:
            light.get_datas()[0].keyframe_insert(data_path = "energy", frame = f)
            light.get_datas()[0].keyframe_insert(data_path = "color", frame = f)
    scene.frame_set(frame_current) 

# makes a day-night-cycle
# - camera_object = the camera object if the light need to be fit ("None" if the camera shouldnt be used)
# - speed = a full day needs 360 frames on speed = 1 (only values from 1 to 5 allowed)
# all light objects will be deleted
def day_night_cycle(starting_time: int, brightness: float,
                     add_fill_and_rim_light: bool, camera_object: OrbitCam, speed : int) -> list[Light]:
    # constants
    HALF_CYCLE_ANGLE : int = 180
    STARTING_TIME_OF_DAY : int = 6
    STARTING_TIME_OF_NIGHT : int = 18
    # before starting time
    delete_all_lights()
    lightcollection : list[Light] = []
    # color of the sun (important for the dawn light)
    day_color = [0.945, 0.855, 0.643]
    # preconditions
    if starting_time > 24 or starting_time < 0:
        starting_time = 0
    else:
        starting_time = starting_time
    if speed < 1:
        speed = 1
    if speed > 5:
        speed = 5
    # setting starting values
    current_angle = ((starting_time % 12) * 15 + 89) % HALF_CYCLE_ANGLE # transforming time to angle
    lights = day_light(brightness, 0,
                       add_fill_and_rim_light, camera_object)
    lightcollection = [lights[0]]
    lightcollection.extend(night_light(brightness, 0, False, None))
    # lightcollection 0 = sun and 1 = moon
    # bightnesses: for saving the energies of the light sources
    brightnesses = [lightcollection[0].get_brightness(), lightcollection[1].get_brightness()] 
    if starting_time > STARTING_TIME_OF_DAY  and starting_time <= STARTING_TIME_OF_NIGHT:
        is_day = True
        lightcollection[1].set_brightness(0) 
    else:
        is_day = False
        lightcollection[0].set_brightness(0) 
        lights[0] = lightcollection[1]
    assert len(lightcollection) == 2 and len(brightnesses) == 2
    radius = radius_of_light_object(lights[0])
    put_rotate_light_in_cyrcle(lights[0], radius, current_angle)
    scene = bpy.context.scene
    frame_current = scene.frame_current
    
    # setting per frame
    frame_setting_of_day_night_cycle(frame_current, lights, scene, current_angle, day_color,
                                    brightnesses, is_day,
                                    lightcollection, radius, speed)
    
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

# creating a default light source
def create_default_light() -> list[Light]:
    default_light = Light("light", "POINT", 4.0762, 1.0055, 5.9039, 1000)
    return [default_light]