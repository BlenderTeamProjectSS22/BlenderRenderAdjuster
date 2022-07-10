"""
author: Romain Carl
created on: 20/05/2022
edited by: Alexander Ritter

description:
Some basic functionalities common to all tasks.
Will need to be expanded and adapted as the project progresses.
"""

import bpy
import os
from math import radians
import fnmatch
from PIL import Image, ImageOps
import sys
import gui.properties as props
from contextlib import contextmanager, redirect_stdout
import enum


# Disable console output if verbose flag is not set
# Output redirection adapted from https://blender.stackexchange.com/a/44563
@contextmanager
def hide_output():
    logfile = "assets/blender_render.log"
    open(logfile, "a").close()
    old = os.dup(sys.stdout.fileno())
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    fd = os.open(logfile, os.O_WRONLY)
    yield
    os.close(fd)
    os.dup(old)
    os.close(old)


# basic camera capable of orbiting around central cube
# uses track-to-constraint, limit-distance-constraint
class OrbitCam:
    
    def __init__(self):
        
        bpy.ops.object.camera_add(location=(1, 0, 0))
        self.camera = bpy.context.object
        self.camera.data.lens = 25
        bpy.ops.object.empty_add(type='CUBE', location=(0, 0, 0), scale=(1, 1, 1))
        self.controller = bpy.context.object
        self.controller.name = self.camera.name + "_controller"

        # add limit_distance_constraint to control distance from camera to center cube
        self.distance_constraint = self.camera.constraints.new(type='LIMIT_DISTANCE')
        self.distance_constraint.target = self.controller
        self.distance_constraint.limit_mode = 'LIMITDIST_ONSURFACE'

        # add track_to_constraint to point camera at center cube
        self.track_constraint = self.camera.constraints.new(type='TRACK_TO')
        self.track_constraint.target = self.controller
        self.track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        self.track_constraint.up_axis = 'UP_Y'

        # add parenting to control camera's rotation
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        self.camera.parent = bpy.context.object

        #put camera in default position
        self.reset_position()
    
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

    # pan camera along global Z axis, changing its position by distance
    def pan_vertical(self, distance: float) -> None:
        self.controller.location[2] += distance

    # pan camera along local Y axis, chaning its position by distance
    # relies on bpy.ops.tranform because of the use of local axis
    def pan_horizontal(self, distance: float) -> None:
        bpy.ops.object.select_all(action = 'DESELECT')
        self.controller.select_set(True)
        bpy.context.view_layer.objects.active = self.controller
        bpy.ops.transform.translate(value=(0, distance, 0), orient_axis_ortho='X', orient_type='LOCAL')

    
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

    # resets camera to default position
    def reset_position(self) -> None:
        self.distance_constraint.distance = 5
        self.controller.rotation_euler[1] = radians(-30)
        self.controller.rotation_euler[2] = radians(45)


# basic renderer
class Renderer:
    def __init__(self, 
                 camera: bpy.types.Object):
        self.scene = bpy.context.scene
        self.camera = camera
        self.scene.camera = self.camera
        self.frame_count  = self.scene.frame_end

    # render image/video to configured output destination 
    def render(self, animation: bool) -> None:
        self.scene.render.image_settings.file_format = "AVI_JPEG" if animation else "PNG"
        if props.VERBOSE:
            bpy.ops.render.render(write_still=True, animation=animation)
        else:
            with hide_output():
                bpy.ops.render.render(write_still=True, animation=animation)
    
    # apply settings for preview rendering
    def set_preview_render(self,
                           file_path: str = "assets/gui/preview.png",
                           use_transparent_bg: bool = False,
                           num_samples: int = 8) -> None:

        self.scene.render.engine = 'CYCLES'
        self.scene.render.filepath = bpy.path.relpath(file_path)
        self.scene.render.film_transparent = use_transparent_bg
        self.scene.view_layers[0].cycles.use_denoising = False
        self.scene.cycles.use_adaptive_sampling = True
        self.scene.cycles.samples = num_samples
        self.scene.render.use_persistent_data = False
        self.scene.cycles.max_bounces = 4
        self.scene.cycles.tile_size = 4096
        self.scene.cycles.time_limit = 0.3

    # apply settings for final rendering
    def set_final_render(self,
                         file_path: str,
                         use_transparent_bg: bool = False,
                         num_samples: int = 64) -> None:

        self.scene.render.engine = 'CYCLES'
        self.scene.render.filepath = file_path
        self.scene.render.film_transparent = use_transparent_bg
        self.scene.view_layers[0].cycles.use_denoising = True
        self.scene.cycles.use_adaptive_sampling = True
        self.scene.cycles.samples = num_samples
        self.scene.render.use_persistent_data = False
        self.scene.cycles.max_bounces = 12
        self.scene.cycles.tile_size = 2048
        self.scene.cycles.use_fast_gi = False
        self.scene.cycles.time_limit = 0
   
    # set aspect ratio
    def set_aspect_ratio(self, w: int, h: int) -> None:
        self.scene.render.resolution_y = int(self.scene.render.resolution_x / (w / h))
    
    # Set the amount of frames from 1 to frame_count
    def set_frame_count(self, frame_count: int) -> None:
        self.frame_count = frame_count
        self.scene.frame_end = frame_count


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

def generate_hdri_thumbnail(filepath):
    filename = os.path.basename(filepath)
    img = bpy.data.images.load(bpy.path.relpath(filepath))
    thumb_width, thumb_height = (256, 256)
    
    # May be a good idea to use the module "tempfile" here
    # But haven't figured out how to make blender save to this tempfile yet
    temp_file = "assets/temp.png"
    
    # blender doesn't support saving to buffer, so we write to file and then load it with PIL
    img.save_render(temp_file, scene=bpy.context.scene)
    image = Image.open(temp_file)

    w, h = image.size
    CROP_FACTOR = h / 5
    area = (0, CROP_FACTOR, h-2*CROP_FACTOR, h-CROP_FACTOR)
    cropped = image.crop(area)

    thumb = ImageOps.fit(cropped, (256, 256), Image.ANTIALIAS)
    
    thumb_folder = "assets/hdri_thumbs/"
    if not os.path.exists(thumb_folder):
        os.mkdir(thumb_folder)
    thumb.save(thumb_folder + filename + ".png", "PNG")

# rotate obj around Z axis and angle
def rotate_object(obj: bpy.types.Object, angle: float) -> None:
    obj.rotation_euler[2] += radians(angle)

# Enum containing all possible textures
class Handler(enum.Enum):
    PER_FRAME = enum.auto()
    FINISHED  = enum.auto()

def unregister_handler(render_handler, handlertype: Handler):
    if handlertype == Handler.PER_FRAME:
        bpy.app.handlers.frame_change_pre.remove(render_handler)
    elif handlertype == Handler.FINISHED:
        bpy.app.handlers.render_complete.remove(render_handler)

def register_handler(render_handler, handlertype: Handler):
    if handlertype == Handler.PER_FRAME:
        bpy.app.handlers.frame_change_pre.append(render_handler)
    elif handlertype == Handler.FINISHED:
        bpy.app.handlers.render_complete.append(render_handler)
