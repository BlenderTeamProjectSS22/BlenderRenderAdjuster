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

# basic camera capable of orbiting around central cube
# uses track-to-constraint, limit-distance-constraint
class OrbitCam:
    
    def __init__(self):
        default_distance = 6 # chosen so that camera frame approx. corresponds to center unit box

        bpy.ops.object.camera_add(location=(default_distance, 0, 0))
        self.camera = bpy.context.object
        bpy.ops.object.empty_add(type='CUBE', location=(0, 0, 0), scale=(1, 1, 1))
        self.controller = bpy.context.object
        self.controller.name = self.camera.name + "_controller"

        # add limit_distance_constraint to control distance from camera to center cube
        self.distance_constraint = self.camera.constraints.new(type='LIMIT_DISTANCE')
        self.distance_constraint.target = self.controller
        self.distance_constraint.limit_mode = 'LIMITDIST_ONSURFACE'
        self.distance_constraint.distance = default_distance

        # add track_to_constraint to point camera at center cube
        self.track_constraint = self.camera.constraints.new(type='TRACK_TO')
        self.track_constraint.target = self.controller
        self.track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        self.track_constraint.up_axis = 'UP_Y'

        # add parenting to control camera's rotation
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        self.camera.parent = bpy.context.object
  
    
    # returns cube object which controlls rotation
    def get_controller(self) -> bpy.types.Object:
        return self.controller
    
    def get_location(self) -> (float, float, float):
        return self.camera.location
    
    # rotate camera position around object and global z axis
    # angle: degrees
    def rotate_z(self, angle: float) -> None:
        self.controller.rotation_euler[2] += radians(angle)
    
    # rotate camera position around object and local (relative to camera) x axis 
    # angle: degrees
    def rotate_x(self, angle: float) -> None:
        self.controller.rotation_euler[1] += radians(angle)
    
    def get_distance(self) -> float:
        return self.distance_constraint.distance
    
    # set distance between camera and object  
    # distance: meters
    def set_distance(self, distance: float) -> None:
        if distance <= 0:
            distance = 0.1 # setting distance to zero oddly resets it to 10
        self.distance_constraint.distance = distance
        
    # increase / decrease distance between camera and object
    # delta: meters
    def change_distance(self, delta: float) -> None:
        newDist = self.distance_constraint.distance + delta
        if newDist <= 0:
            newDist = 0.1 
        self.distance_constraint.distance = newDist


# basic renderer
class Renderer:
    def __init__(self, 
                 camera: bpy.types.Object):
        self.scene = bpy.context.scene
        self.camera = camera
        self.scene.camera = self.camera

    # render image to configured output destination 
    def render(self) -> None:
        bpy.ops.render.render(write_still=True, animation=self.animation)

    # apply settings for preview rendering
    def set_preview_render(self,
                           file_path: str = "assets/gui/preview.png",
                           use_transparent_bg: bool = False,
                           num_samples: int = 8) -> None:

        self.scene.render.engine = 'CYCLES'
        self.animation = False
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.filepath = bpy.path.relpath(file_path)
        self.scene.render.film_transparent = use_transparent_bg
        self.scene.view_layers[0].cycles.use_denoising = False
        self.scene.cycles.use_adaptive_sampling = True
        self.scene.cycles.samples = num_samples
        self.scene.render.use_persistent_data = True
        self.scene.cycles.max_bounces = 4
        self.scene.cycles.tile_size = 4096
        self.scene.cycles.use_fast_gi = True
        self.scene.cycles.fast_gi_method = "ADD" # refer to issue #10 for why this is set
        self.scene.cycles.time_limit = 0.3

    # apply settings for final rendering
    def set_final_render(self,
                         file_path: str,
                         animation: bool = False,
                         use_transparent_bg: bool = False,
                         num_samples: int = 64) -> None:

        self.scene.render.engine = 'CYCLES'
        self.animation = animation
        if animation:
            self.scene.render.image_settings.file_format = 'AVI_JPEG'
        else:
            self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.filepath = file_path
        self.scene.render.film_transparent = use_transparent_bg
        self.scene.view_layers[0].cycles.use_denoising = True
        self.scene.cycles.use_adaptive_sampling = True
        self.scene.cycles.samples = num_samples
        self.scene.render.use_persistent_data = True
        self.scene.cycles.max_bounces = 12
        self.scene.cycles.tile_size = 2048
        self.scene.cycles.use_fast_gi = False
        self.scene.cycles.time_limit = 0
   
    # set aspect ratio
    def set_aspect_ratio(self, w: int, h: int) -> None:
        self.scene.render.resolution_y = int(self.scene.render.resolution_x / (w / h))

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
            self.scene.render.image_settings.file_format = 'AVI_JPEG'
        else:
            self.scene.render.image_settings.file_format = 'PNG'    
    
    def set_eevee(self,
                  num_samples: int = 32,
                  use_transparent_bg: bool = False) -> None:

        self.scene.render.engine = 'BLENDER_EEVEE'
        self.scene.render.film_transparent = use_transparent_bg
        self.scene.eevee.taa_render_samples = num_samples

        

#some other useful functions:

#remove default objects
#keepLight: If false, default light source is deleted
def clear_scene(keepLight: bool = True) -> None:
    for o in bpy.data.objects:
        if not(o.name == "Light" and keepLight):
            bpy.data.objects.remove(o)

def remove_object(obj: bpy.types.Object) -> None:
   bpy.data.objects.remove(obj)

#import .ply, .stl or .obj file
def import_mesh(filepath: str) -> bpy.types.Object:
    if fnmatch.fnmatch(filepath.lower(), '*.ply'):
        bpy.ops.import_mesh.ply(filepath=filepath)
    elif fnmatch.fnmatch(filepath.lower(), '*.stl'):
        bpy.ops.import_mesh.stl(filepath=filepath)
    elif fnmatch.fnmatch(filepath.lower(), '*.obj'):
        bpy.ops.wm.obj_import(filepath=filepath)
    else:
        raise ImportError("can only import .ply, .stl or .obj files")
    newObj = bpy.context.object
    scale_to_unit_cube(newObj)
    return newObj

def export_blend(filepath: str) -> None:
    bpy.ops.wm.save_mainfile(filepath=filepath)

#scale obj down so that its bounding box fits into the unit cube (2 x 2 x 2)
def scale_to_unit_cube(obj: bpy.types.Object) -> None:
    obj.dimensions = obj.dimensions / max(obj.dimensions) * 2 #downscaling
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS') #align object's bounding box' center and origin
