"""
Some basic functionalities common to all tasks.
Will need to be expanded and adapted as the project progresses.
"""

import bpy
import os
from math import radians

#remove default objects
#keepLight: If false, default light source is deleted
def clear_scene(keepLight: bool = True) -> None:
    for o in bpy.data.objects:
        if not(o.name == "Light" and keepLight):
            bpy.data.objects.remove(o)
    
#add camera locked to object
#returns the created camera
def add_camera(target_object: bpy.types.Object, distance: float = 10) -> bpy.types.Object:
    #create camera object 1 y unit in front of target object
    bpy.ops.object.camera_add(location=(target_object.location[0], target_object.location[1] + distance, target_object.location[2]))
    camera = bpy.context.object
    
    #add limit_distance_constraint to control distance from camera to object
    constraint = camera.constraints.new(type='LIMIT_DISTANCE')
    constraint.target = target_object
    constraint.limit_mode = 'LIMITDIST_ONSURFACE'
    constraint.distance = distance
    
    #add track_to_constraint to point camera at target object
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = target_object
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    #add empty box to control the camera's rotation
    bpy.ops.object.empty_add(type='CUBE', location=target_object.location, scale=(1, 1, 1))
    bpy.context.object.name = camera.name + "_controller"
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    camera.parent = bpy.context.object

    return camera

#configure output parameters
def set_output_properties(scene: bpy.types.Scene,
                          resolution_percentage: int = 100,
                          output_file_path: str = os.getcwd() + "/renders/result.png",
                          res_x: int = 1920,
                          res_y: int = 1080) -> None:
    scene.render.resolution_percentage = resolution_percentage
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y

    scene.render.filepath = output_file_path
        
#configure cycles renderer parameters
def set_cycles_renderer(scene: bpy.types.Scene,
                        camera_object: bpy.types.Object,
                        num_samples: int = 64,
                        use_denoising: bool = True,
                        use_transparent_bg: bool = False) -> None:
    scene.camera = camera_object

    scene.render.image_settings.file_format = 'PNG'
    scene.render.engine = 'CYCLES'

    scene.render.film_transparent = use_transparent_bg
    scene.view_layers[0].cycles.use_denoising = use_denoising

    scene.cycles.use_adaptive_sampling = True
    scene.cycles.samples = num_samples
    
#rotate camera position around object and global z axis
#angle: degrees
def rotate_view_z(camera: bpy.types.Object, angle: float) -> None:
    camera.parent.rotation_euler[2] += radians(angle)

#rotate camera position around object and local (relative to camera) x axis 
#angle: degrees
def rotate_view_x(camera: bpy.types.Object, angle: float) -> None:
    camera.parent.rotation_euler[0] += radians(angle)
  
#set distance between camera and object  
#distance: meters
def set_distance(camera: bpy.types.Object, distance: float) -> None:
    if distance <= 0:
        distance = 0.1 # setting distance to zero oddly resets it to 10
    camera.constraints["Limit Distance"].distance = distance
        
#increase / decrease distance between camera and object
#delta: meters
def change_distance(camera: bpy.types.Object, delta: float) -> None:
    newDist = camera.constraints["Limit Distance"].distance + delta
    if newDist <= 0:
        newDist = 0.1 
    camera.constraints["Limit Distance"].distance = newDist

#render image to configured output destination    
def render() -> None:
    bpy.ops.render.render(write_still=True)
