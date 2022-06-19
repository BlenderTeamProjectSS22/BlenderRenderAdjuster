"""
author: Romain Carl
created on: 20/05/2022
edited by:

description:
Some basic functionalities common to all tasks.
Will need to be expanded and adapted as the project progresses.
"""

import bpy
import os
from math import radians
import fnmatch

#basic camera capable of orbiting around target
#uses track-to-constraint, limit-distance-constraint
class OrbitCam:
    
    def __init__(self, target: bpy.types.Object):
        default_distance = 6 #chosen so that camera frame approx. corresponds to center unit box

        self.target = target
        bpy.ops.object.camera_add(location=(target.location[0] + default_distance, target.location[1], target.location[2]))
        self.camera = bpy.context.object

        #add limit_distance_constraint to control distance from camera to object
        self.distance_constraint = self.camera.constraints.new(type='LIMIT_DISTANCE')
        self.distance_constraint.target = target
        self.distance_constraint.limit_mode = 'LIMITDIST_ONSURFACE'
        self.distance_constraint.distance = default_distance

        #add track_to_constraint to point camera at target object
        self.track_constraint = self.camera.constraints.new(type='TRACK_TO')
        self.track_constraint.target = target
        self.track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        self.track_constraint.up_axis = 'UP_Y'

        #add empty box to control the camera's rotation
        bpy.ops.object.empty_add(type='CUBE', location=target.location, scale=(1, 1, 1))
        self.controller = bpy.context.object
        self.controller.name = self.camera.name + "_controller"
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        self.camera.parent = bpy.context.object
  
    
    #returns cube object which controlls rotation
    def get_controller(self) -> bpy.types.Object:
        return self.controller
    
    def get_location(self) -> (float, float, float):
        return self.camera.location
    
    #rotate camera position around object and global z axis
    #angle: degrees
    def rotate_z(self, angle: float) -> None:
        self.controller.rotation_euler[2] += radians(angle)
    
    #rotate camera position around object and local (relative to camera) x axis 
    #angle: degrees
    def rotate_x(self, angle: float) -> None:
        self.controller.rotation_euler[0] += radians(angle)
    
    def get_distance(self) -> float:
        return self.distance_constraint.distance
    
    #set distance between camera and object  
    #distance: meters
    def set_distance(self, distance: float) -> None:
        if distance <= 0:
            distance = 0.1 # setting distance to zero oddly resets it to 10
        self.distance_constraint.distance = distance
        
    #increase / decrease distance between camera and object
    #delta: meters
    def change_distance(self, delta: float) -> None:
        newDist = self.distance_constraint.distance + delta
        if newDist <= 0:
            newDist = 0.1 
        self.distance_constraint.distance = newDist


#basic renderer
class Renderer:
    def __init__(self, 
                 scene: bpy.types.Scene, 
                 camera: bpy.types.Object):
        self.scene = scene
        self.camera = camera
        self.scene.camera = self.camera
    

    #configure output parameters
    def set_output_properties(self,
                              resolution_percentage: int = 100,
                              output_file_path: str = os.getcwd() + "/renders/result",
                              res_x: int = 1920,
                              res_y: int = 1080,
                              animation: bool = False) -> None:
        self.scene.render.resolution_percentage = resolution_percentage
        self.scene.render.resolution_x = res_x
        self.scene.render.resolution_y = res_y
        self.scene.render.filepath = output_file_path
        self.animation = animation
        if animation:
            self.scene.render.image_settings.file_format = 'FFMPEG'
        else:
            self.scene.render.image_settings.file_format = 'PNG'
            
            
    #choose cycles engine and configure parameters
    def set_cycles(self,
                   num_samples: int = 64,
                   use_denoising: bool = True,
                   use_transparent_bg: bool = False) -> None:
        
        self.scene.render.engine = 'CYCLES'
        self.scene.render.film_transparent = use_transparent_bg
        self.scene.view_layers[0].cycles.use_denoising = use_denoising
        self.scene.cycles.use_adaptive_sampling = True
        self.scene.cycles.samples = num_samples
    
    #choose eevee engine and configure parameters
    def set_eevee(self,
                  num_samples: int = 32,
                  use_transparent_bg: bool = False) -> None:

        self.scene.render.engine = 'BLENDER_EEVEE'
        self.scene.render.film_transparent = use_transparent_bg
        self.scene.eevee.taa_render_samples = num_samples

    #render image to configured output destination 
    def render(self) -> None:
        bpy.ops.render.render(write_still=True, animation=self.animation)



        
                     
                 


#some other useful functions:

#remove default objects
#keepLight: If false, default light source is deleted
def clear_scene(keepLight: bool = True) -> None:
    for o in bpy.data.objects:
        if not(o.name == "Light" and keepLight):
            bpy.data.objects.remove(o)

#import .ply or .stl file
def import_mesh(filepath: str) -> bpy.types.Object:
    if fnmatch.fnmatch(filepath.lower(), '*.ply'):
        bpy.ops.import_mesh.ply(filepath=filepath)
    elif fnmatch.fnmatch(filepath.lower(), '*.stl'):
        bpy.ops.import_mesh.stl(filepath=filepath)
    else:
        raise ImportError("can only import .ply and .stl files")
    newObj = bpy.context.object
    scale_to_unit_cube(newObj)
    return newObj

#scale obj down so that its bounding box fits into the unit cube (2 x 2 x 2)
def scale_to_unit_cube(obj: bpy.types.Object) -> None:
    obj.dimensions = obj.dimensions / max(obj.dimensions) * 2 #downscaling
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS') #align object's bounding box' center and origin
