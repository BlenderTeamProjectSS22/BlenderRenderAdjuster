# author: Alexander Ritter
# created on: 06/06/2022
# edited by:

# description:
# GUI element: Main program, renders the GUI and connects it to other function


from ctypes import pointer
import tkinter as tk
from tkinter import Frame, Label, Button, StringVar, BooleanVar, IntVar, Checkbutton, OptionMenu, Scale, Canvas, Entry, PhotoImage
from tkinter import ttk
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo, showerror
from tkinter import filedialog
from PIL import ImageTk, Image

from CreatePointcloudFromObject import convert,switchrandom,switchvertex,setSphere,setDisk,setCube,setInstanceObjectScale
import bpy
import webbrowser
import threading
import requests
import enum
#from CreatePointcloudFromObject import createBasicPointcloud
from gui.render_preview import RenderPreview
from gui.gui_options import SettingsWindow
from gui.panel_materials import MaterialWidgets
from gui.settings import Control
from mathutils import Vector
from gui.loading_screen import VideoLoadingScreen, ImageLoadingScreen
import gui.properties as props
from gui.properties import VERSION_PATCH, VERSION_MAJOR, VERSION_MINOR, UPDATE_URL


from Lightning.light_functions import day_light, night_light, delete_lights, lantern_light, create_default_light
from Lightning.light_functions import day_night_cycle, delete_all_lights, delete_light_animation, lights_enabled
from materials.materials import MaterialController
from Lightning.light_class import Light
from HDRI.hdri import set_background_brightness
import utils
import os

import HDRI.hdri as hdri

## for testing
if props.DEBUG:
    import bpy

class ProgramGUI(tk.Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
    
        # blender initialization
        utils.clear_scene()
        camera   = utils.OrbitCam()
        renderer = utils.Renderer(camera.camera)
        renderer.set_preview_render()
        self.max_frame = IntVar()
        frames = utils.FrameControl(self.max_frame)

        hdri.initialize_world_texture()

        #generate HDRI previews
        hdri_dir = os.fsencode("assets/HDRIs/")
        for file in os.listdir(hdri_dir):
            filename = os.fsdecode(file)
            utils.generate_hdri_thumbnail("assets/HDRIs/" + filename)
        
        master.title("Render adjuster")
        master.minsize(107+1135+184,507)
        icon = ImageTk.PhotoImage(Image.open("assets/gui/icon.ico"))
        master.iconphoto(True, icon)
        
        self.columnconfigure(0, weight=0, minsize=107)
        self.columnconfigure(1, weight=16, minsize=1135)
        self.columnconfigure(2, weight=0, minsize=184)
        self.rowconfigure(0, weight=15, minsize=307)
        self.rowconfigure(1, weight=1)
        
        # Create global control object
        mid = Frame(master=self)
        self.preview = RenderPreview(master=self)
        self.control = Control(renderer, self.preview, camera, frames)
        self.control.material = MaterialController()
        self.control.model = None
        
        # Load defaul cube if debug is enabled
        if props.DEBUG:
            self.control.model = utils.import_mesh("assets/STL samples/cube.obj")
            self.control.camera.rotate_z(45)
            self.control.camera.rotate_x(-20)
            self.control.camera.set_distance(10)
            self.control.re_render()

        left  = LeftPanel(self, self.control)
        self.right = RightPanel(self, self.control)
        camcontrols = CameraControls(mid, self.control)
        background_ctrl = BackgroundControl(mid, self.control)
        frm_frame = FrameWidgets(mid, self.control, self.max_frame)
        
        mid.rowconfigure(1, weight=1)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)
        camcontrols.grid(row=1, column=0, sticky="nsew")
        background_ctrl.grid(row=1, column=1, sticky="nwse")
        frm_frame.grid(row=0, columnspan=2, sticky="esw")
        
        left.grid(row=0, column=0, sticky="nw", rowspan=2)
        self.preview.grid(row=0, column=1, sticky="nwes")
        mid.grid(row=1, column=1, sticky="nwes")
        self.right.grid(row=0, column=2, sticky="ne", rowspan=2)


class LeftPanel(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master)
        self.master = master
        self.control = control
        lbl_spacer = Label(master=self, text="")

        lbl_fileop = Label(master=self, text="File operations", font="Arial 10 bold")
        btn_import = Button(master=self, text="Import model", command=self.import_model)
        btn_export = Button(master=self, text="Export model", command=self.export_model)
        btn_render = Button(master=self, text="Save render", command=self.render_image)
        btn_video  = Button(master=self, text="Save video", command=self.render_video)
        lbl_fileop.pack(fill=tk.X)
        btn_import.pack(fill=tk.X)
        btn_export.pack(fill=tk.X)
        btn_render.pack(fill=tk.X)
        btn_video.pack(fill=tk.X)
        
        sep = ttk.Separator(self,orient='horizontal')
        sep.pack(fill=tk.X)
        
        # All general program widgets
        frame_ops    = tk.Frame(master=self)
        lbl_ops      = tk.Label(master=frame_ops, text="Actions", font="Arial 10 bold")
        btn_settings = tk.Button(master=frame_ops, text="Settings", command=self.open_settings_window)
        btn_updates  = tk.Button(master=frame_ops, text="Check for updates", command=self.check_update)
        btn_help     = tk.Button(master=frame_ops, text="Help", command=self.open_help_page)
        lbl_ops.pack(fill=tk.X)
        btn_settings.pack(fill=tk.X)
        btn_updates.pack(fill=tk.X)
        btn_help.pack(fill=tk.X)
        frame_ops.pack()
        
        lbl_spacer3 = Label(master=self, text="")
        lbl_spacer3.pack()
        modelcontrols = ModelControls(self, self.control)
        modelcontrols.pack(fill=tk.X)
    
    def import_model(self):
        filetypes = [
            ("All model files", "*.ply *.stl *.obj"),
            ("PLY object", "*.ply"),
            ("STL file", "*.stl"),
            ("Wavefront OBJ", "*.obj")
        ]
        filename = filedialog.askopenfilename(title="Select model to import", filetypes=filetypes, initialdir="assets/model presets/")
        if filename == "":
            return
        if self.control.model != None:
            self.master.right.frm_point.reset()
            utils.remove_object(self.control.model)
           
        self.control.model = utils.import_mesh(filename)
        self.control.material.apply_material(self.control.model)
        self.control.camera.reset_position()

        self.control.re_render()
        
    
    def export_model(self):
        filename = filedialog.asksaveasfilename(
            title="Save model at",
            initialfile = "untitled.blend",
            defaultextension=".blend",
            filetypes=[("Blender project","*.blend")])
        if filename == "":
            return
        utils.export_blend(filename)
    
    def render_image(self):
        filename = filedialog.asksaveasfilename(
            title="Save image at",
            initialfile = "render.png",
            defaultextension=".png",
            filetypes=[("Portable Network Graphics","*.png")])
        if filename == "":
            return
        
        self.loading_image = ImageLoadingScreen(self)
        self.update_idletasks()
        
        def render_finished(scene):
            self.loading_image.close_window()
            utils.unregister_handler(render_finished, utils.Handler.FINISHED)
        utils.register_handler(render_finished, utils.Handler.FINISHED)
        
        def render():
            self.control.renderer.set_final_render(file_path=filename)
            self.control.renderer.render(animation=False)
            self.control.renderer.set_preview_render()
        
        renderthread = threading.Thread(target=render)
        renderthread.start()
    
    def render_video(self):
        filename = filedialog.asksaveasfilename(
            title="Save video at",
            initialfile = "render.avi",
            defaultextension=".avi",
            filetypes=[("Audio Video Interleave","*.avi")])
        if filename == "":
            return
        self.loading_video = VideoLoadingScreen(self, self.control, filename)
        
    def open_settings_window(self):
        SettingsWindow(self.master, self.control)
    
    def check_update(self):
        try:
            page = requests.get(UPDATE_URL, timeout=2)
        except requests.HTTPError:
            showerror(title="Version check", message="Something is wrong with the update server", detail="Please try again another time")
            return
        except (requests.ConnectionError, requests.Timeout):
            showerror(title="Version check", message="You propably aren't connected to the internet")
            return
        except Exception as e:
            showerror(title="Version check", message="Unknown error during update check")
            print(e)
            return
        
        versionlist = page.text.split(".")
        
        major = int(versionlist[0])
        minor = int(versionlist[1])
        patch = int(versionlist[2])
        
        update_available = False
        if major > VERSION_MAJOR:
            update_available = True
        elif minor > VERSION_MINOR:
            update_available = True
        elif patch > VERSION_PATCH:
            update_available = True
            
        if update_available:
            showinfo(title="Version check", message="Update available!", detail="Download it from Github releases")
        else:
            showinfo(title="Version check", message="No update available!", detail="You are using the latest version")
    
    def open_help_page(self):
        webbrowser.open_new_tab("https://github.com/garvita-tiwari/blender_render/wiki")
        

class CameraControls(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        
        self.control = control
        
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=4)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)
        
        lbl_controls = Label(master=self, text="Camera Controls", font="Arial 10 bold")
        
        light_gray = "#e6e6e6"
        frm_rot = Frame(master=self)
        frm_rot.columnconfigure(0, weight=1)
        frm_rot.columnconfigure(1, weight=1)
        frm_rot.columnconfigure(2, weight=1)
        frm_rot.rowconfigure(0, weight=1)
        frm_rot.rowconfigure(1, weight=4)
        frm_rot.rowconfigure(2, weight=4)
        frm_rot.rowconfigure(3, weight=4)
        lbl_rot = Label(master=frm_rot, text="Rotation")
        btn_up_rot = Button(master=frm_rot, text="↑", command=self.rotate_up, bg=light_gray)
        btn_down_rot = Button(master=frm_rot, text="↓", command=self.rotate_down, bg=light_gray)
        btn_right_rot = Button(master=frm_rot, text="→", command=self.rotate_right, bg=light_gray)
        btn_left_rot = Button(master=frm_rot, text="←", command=self.rotate_left, bg=light_gray)
        lbl_rot.grid(row=0, column=0, columnspan=3, pady=10)
        btn_up_rot.grid(row=1, column=1, sticky="news")
        btn_left_rot.grid(row=2, column=0, sticky="news")
        btn_right_rot.grid(row=2, column=2, sticky="news")
        btn_down_rot.grid(row=3, column=1, sticky="news")
        
        frm_pan = Frame(master=self)
        frm_pan.columnconfigure(0, weight=1)
        frm_pan.columnconfigure(1, weight=1)
        frm_pan.columnconfigure(2, weight=1)
        frm_pan.rowconfigure(0, weight=1)
        frm_pan.rowconfigure(1, weight=4)
        frm_pan.rowconfigure(2, weight=4)
        frm_pan.rowconfigure(3, weight=4)
        lbl_pan = Label(master=frm_pan, text="Panning")
        btn_up_pan = Button(master=frm_pan, text="↑", command=self.move_up, bg=light_gray)
        btn_down_pan = Button(master=frm_pan, text="↓", command=self.move_down, bg=light_gray)
        btn_right_pan = Button(master=frm_pan, text="→", command=self.move_right, bg=light_gray)
        btn_left_pan = Button(master=frm_pan, text="←", command=self.move_left, bg=light_gray)
        lbl_pan.grid(row=0, column=0, columnspan=3, pady=10)
        btn_up_pan.grid(row=1, column=1, sticky="news")
        btn_left_pan.grid(row=2, column=0, sticky="news")
        btn_right_pan.grid(row=2, column=2, sticky="news")
        btn_down_pan.grid(row=3, column=1, sticky="news")
        
        frm_dist = Frame(master=self)
        frm_dist.columnconfigure(0, weight=1)
        frm_dist.rowconfigure(0, weight=1)
        frm_dist.rowconfigure(1, weight=4)
        frm_dist.rowconfigure(2, weight=4)
        lbl_dist = Label(master=frm_dist, text="Distance")
        btn_in = Button(master=frm_dist, text="Pan in", command=self.pan_in, bg=light_gray)
        btn_out = Button(master=frm_dist, text="Pan out", command=self.pan_out, bg=light_gray)
        lbl_dist.grid(row=0, column=0, sticky="news")
        btn_in.grid(row=1, column=0, padx=8, sticky="ew")
        btn_out.grid(row=2, column=0, padx=8, sticky="ew")

        btn_reset = Button(master=self, text="Reset camera angle", command=self.reset_camera)
        
        lbl_controls.grid(row=0, column=0, columnspan=3)
        frm_rot.grid(row=1, column=0, padx=10, pady=10, sticky="news")
        frm_pan.grid(row=1, column=1, padx=10, pady=10, sticky="news")
        frm_dist.grid(row=1, column=2, padx=10, sticky="news")
        btn_reset.grid(row=2, column=0, columnspan=3)

    def rotate_up(self):
        self.control.camera.rotate_x(-10)
        self.control.re_render()
    
    def rotate_down(self):
        self.control.camera.rotate_x(10)
        self.control.re_render()

    def rotate_right(self):
        self.control.camera.rotate_z(10)
        self.control.re_render()

    def rotate_left(self):
        self.control.camera.rotate_z(-10)
        self.control.re_render()

    global step_size # relative size of panning steps 
    step_size = 1 / 5

    def move_up(self):
        self.control.camera.pan_vertical(self.control.camera.get_distance() * step_size)
        self.control.re_render()
    
    def move_down(self):
        self.control.camera.pan_vertical(self.control.camera.get_distance() * -step_size)
        self.control.re_render()

    def move_right(self):
        self.control.camera.pan_horizontal(self.control.camera.get_distance() * step_size)
        self.control.re_render()

    def move_left(self):
        self.control.camera.pan_horizontal(self.control.camera.get_distance() * -step_size)
        self.control.re_render()

    global zoom_factor # relative size of panning in / out steps
    zoom_factor = 1.5

    def pan_in(self):
        self.control.camera.set_distance(self.control.camera.get_distance() / zoom_factor)
        self.control.re_render()

    def pan_out(self):
        self.control.camera.set_distance(self.control.camera.get_distance() * zoom_factor)
        self.control.re_render()
    
    def reset_camera(self):
        self.control.camera.reset_position()
        self.control.re_render()
        
    
class ModelControls(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master)
        
        self.control = control
        lbl_controls = Label(master=self, text="Model Controls", font="Arial 10 bold")
        lbl_rot   = Label(master=self, text="Rotation:")
        lbl_controls.grid(row=0, column=0, columnspan=3)
        lbl_rot.grid(row=1, column=0)

        btn_right = Button(master=self, text="→", command=self.rotate_right)
        btn_left = Button(master=self, text="←", command=self.rotate_left)

        btn_left.grid(row=1, column=1, sticky="e")
        btn_right.grid(row=1, column=2, sticky="w")

    def rotate_right(self):
        utils.rotate_object(self.control.model, 10)
        self.control.re_render()

    def rotate_left(self):
        utils.rotate_object(self.control.model, -10)
        self.control.re_render()
        
class ColorMeshWidgets(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.control = control
        
        self.current_color = None
        
        lbl_look    = Label(master=self, text="Look", font="Arial 10 bold")
        lbl_color   = Label(master=self, text="Color")
        btn_picker  = Button(master=self, text="pick", command=self.pick_color)
        lbl_add    = Label(master=self, text="Add")
        self.vertc = BooleanVar()
        self.mesh  = BooleanVar()
        self.point = BooleanVar()
        check_vertc = Checkbutton(master=self, text="Vertex color", variable=self.vertc, anchor="w", command=self.switch_vertex_color)
        check_mesh  = Checkbutton(master=self, text="Plane", variable=self.mesh, anchor="w", command=self.add_plane)
        lbl_look.grid(row=0, column=0, columnspan=2)
        lbl_color.grid(row=1, column=0)
        lbl_add.grid(row=1, column=1)
        btn_picker.grid(row=2, column=0)
        check_vertc.grid(row=3, column=0, sticky="w")
        check_mesh.grid(row=2, column=1, sticky="w")
    
    def pick_color(self):
    
        color = askcolor(self.current_color)[0]
        
        if color is not None:
            self.current_color = color
            self.control.material.set_color(utils.convert_color_to_bpy(self.current_color))
            self.control.re_render()
    
    def switch_vertex_color(self):
        self.control.re_render()


    def add_plane(self):
        self.has_plane = False
        for obj in bpy.context.scene.objects:
            if obj.name == "Plane":
                self.has_plane = True
            
        if self.has_plane:
            bpy.ops.object.select_all(action = "DESELECT")
            bpy.data.objects["Plane"].select_set(True) 
            bpy.ops.object.delete()   
            
        else:
            bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, -1), scale=(1, 1, 1))
            bpy.ops.transform.resize(value=(15, 15, 15))
        
        bpy.ops.object.select_all(action = "DESELECT")
        bpy.data.objects[self.control.model.name].select_set(True) 
        self.control.re_render()


    



class TextureWidgets(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.control = control
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        tex_selected = StringVar(self)
        tex_selected.set("none")
        lbl_textures = Label(master=self, text="Texture selection:", font="Arial 10 bold")
        btn_import_texture = Button(master=self, text="Import", command=self.import_texture)
        lbl_sel_tex    = Label(master=self, text="Select:")
        textures = (Textures.NONE.value, Textures.WOOD.value, Textures.BRICKS.value)
        dropdown_textures = OptionMenu(self, tex_selected, *textures, command=self.set_texture)
        lbl_textures.grid(row=0, column=0, columnspan=2, sticky="we")
        btn_import_texture.grid(row=1, column=0, columnspan=2, sticky="")
        lbl_sel_tex.grid(row=2, column=0, sticky="w")
        dropdown_textures.grid(row=2, column=1, sticky="we")
    
    def set_texture(self, *args):
        tex = Textures(args[0])
        if tex == Textures.WOOD:
            pass
        elif tex == Textures.BRICKS:
            pass
        else: # NONE
            pass
        self.control.re_render()
    
    def import_texture(self):
        filetypes = [
            ("PNG image", "*.png"),
        ]
        filename = filedialog.askopenfilename(title="Select a texture", filetypes=filetypes)
        # TODO Apply the texure to the object
        self.control.re_render()
        
        
# Enum containing all possible textures
class Textures(enum.Enum):
    NONE = "none"
    WOOD = "wood"
    BRICKS = "bricks"

class LightingWidgets(Frame):
    # constants
    TIME_TO_ANGLE_CONSTANT : int = 15
    HIGH_OF_LATERN_LIGHT : int = 2
    STARTING_TIME_OF_DAY : int = 6

    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.control = control

        # variables
        self.light_objects : list[Light] = []
        self.use_light_type : int = 0 # int instead of bool for Modular Continuity reasons
        self.brightness : float = 4
        self.daytime : int = 0
        self.background_strength : float = 1
        self.is_day_night : bool = BooleanVar()
        self.is_brightness_changeble : bool = False
        
        # grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        # labels
        lbl_light = Label(master=self, text="Lighting", font="Arial 10 bold")
        self.lbl_brightness = Label(master=self, text="Brightness(inactive)")
        lbl_daytime = Label(master=self, text="Time of day/night")
        lbl_background = Label(master=self, text="Background Strength")
        # buttons
        btn_use_lights_switch = Button(master=self, text="Lights off", command=self.lights_off)
        btn_default_light = Button(master=self, text="Default", command=self.set_default_light)
        btn_day = Button(master=self, text="Day", command=self.set_day)
        btn_night = Button(master=self, text="Night", command=self.set_night)
        btn_lantern = Button(master=self, text="Lantern", command=self.set_lantern)
        # checkboxs
        check_day_night_circle = Checkbutton(master=self, text="Day Night Cycle Animation", variable=self.is_day_night, anchor="w", command=self.switch_day_night_circle)
        # slider
        self.slider_brightness = Scale(master=self, to = 8.0, orient="horizontal",
                                  resolution = 0.1, showvalue=False, command=lambda val: self.set_brightness(val, False))
        slider_daytime = Scale(master=self, from_= 0, to = 12, orient="horizontal", showvalue=True, command=lambda val: self.set_daytime(val, False))
        slider_background = Scale(master=self, from_= 0, to = 10, orient="horizontal",
                                  resolution = 0.1, showvalue=False, command=lambda val: self.set_background_strength(val, False))
        self.slider_brightness.bind("<ButtonRelease-1>", lambda event : self.set_brightness(self.get_brightness(), True)) 
        slider_daytime.bind("<ButtonRelease-1>", lambda event : self.set_daytime(self.get_daytime(), True)) 
        slider_background.bind("<ButtonRelease-1>", lambda event : self.set_background_strength(self.get_background_strength(), True)) 

        # packing
        lbl_light.grid(row=0, column=0, columnspan=2)
        self.lbl_brightness.grid(row=1, column=0, sticky="w")
        self.slider_brightness.grid(row=1, column=1,  sticky="we", columnspan=2)
        btn_use_lights_switch.grid(row=2, column=0, sticky="we",pady=1)
        btn_default_light.grid(row=2, column=1, sticky="we", pady=1, columnspan=2) 
        btn_day.grid(row=3, column=0, sticky="we",pady=1)
        btn_night.grid(row=3, column=1, sticky="we",pady=1)
        btn_lantern.grid(row=4, column=1, sticky="we",pady=1, columnspan=2)
        check_day_night_circle.grid(row=5, column=0, sticky="", pady=1, columnspan=2)
        lbl_daytime.grid(row=6, column=0, sticky="w")
        slider_daytime.grid(row=6, column=1,  sticky="we", columnspan=2)  
        lbl_background.grid(row=7, column=0,  sticky="w") 
        slider_background.grid(row=7, column=1,  sticky="we", columnspan=2) 

        # initialization   
        self.slider_brightness.set(self.get_brightness())  
        slider_background.set(self.get_background_strength())
        self.slider_brightness.configure(state="disable")
        

    # set the background strength and rerenders
    def set_background_strength(self, value, is_released : bool) -> None:
        self.background_strength = value
        set_background_brightness(float(value))
        if is_released:
            self.control.re_render()

    # returns the background strength
    def get_background_strength(self) -> None:
        return self.background_strength

    # lights will be deleted
    def lights_off(self) -> None:
        lights_enabled(False)
        self.activate_brightness_slider(False)
        self.control.re_render()

    # puts the brightness slider active or inactive
    def activate_brightness_slider(self, is_active : bool) -> None:
        if is_active:
            self.slider_brightness.configure(state="active")
            self.is_brightness_changeble = True
            self.lbl_brightness.configure(text="Brightness(active)")
        else:
            self.slider_brightness.configure(state="disable")
            self.is_brightness_changeble = False
            self.lbl_brightness.configure(text="Brightness(inactive)")

    # set daytime value to "value"
    def set_daytime(self, value : int, is_released : bool) -> None:
        self.daytime = value
        if is_released:
            self.fit_brightness_to_lights()

    # returns the daytime value
    def get_daytime(self) -> int:
        return int(self.daytime)

    # set the brightness
    def set_brightness(self, value, is_released : bool) -> None:
        self.brightness = float(value)
        if is_released and self.is_brightness_changeble:
            self.fit_brightness_to_lights()
        
    # recreate lights with new brightness
    def fit_brightness_to_lights(self) -> None:
        match self.use_light_type:
            case 1:
                self.set_day()
                return
            case 2:
                self.set_night()
                return
            case 3:
                self.set_lantern()
                return
            case _:
                self.set_default_light()

    # returns the brightness
    def get_brightness(self) -> float:
        return self.brightness
        
    # set default light
    def set_default_light(self) -> None:
        self.standard_light_settings(0)
        self.activate_brightness_slider(False)
        self.light_objects = create_default_light()
        self.control.re_render()
        
    # some setting that should be made before creating new lights
    def standard_light_settings(self, use_light_type: int) -> None:
        lights_enabled(True)
        if use_light_type != 0:
            self.activate_brightness_slider(True)
        self.use_light_type = use_light_type
        self.is_day_night.set(False)
        delete_all_lights()

    # set day light
    def set_day(self) -> None:
        self.standard_light_settings(1)
        self.light_objects = day_light(self.get_brightness(), self.get_daytime() * self.TIME_TO_ANGLE_CONSTANT, False, self.control.camera)
        self.control.re_render()
    
    # set night light
    def set_night(self) -> None:
        self.standard_light_settings(2)
        self.light_objects = night_light(self.get_brightness(), self.get_daytime() * self.TIME_TO_ANGLE_CONSTANT, True, self.control.camera)
        self.control.re_render()
        
    # set lantern light
    def set_lantern(self) -> None:
        self.standard_light_settings(3)
        self.light_objects = lantern_light(self.get_brightness(), self.HIGH_OF_LATERN_LIGHT, True, self.control.camera)
        self.control.re_render()
    
    # creates a day night circle if "self.is_day_night" = true
    # deletes the animations if "self.is_day_night" = false
    def switch_day_night_circle(self):
        if self.is_day_night.get():
            self.control.frames.add_animation(utils.Animation.DAYNIGHT)
            self.activate_brightness_slider(False)
            delete_lights(self.light_objects)
            self.light_objects = day_night_cycle(self.daytime + self.STARTING_TIME_OF_DAY, self.get_brightness(), True, self.control.camera, 3)
        else:
            self.control.frames.remove_animation(utils.Animation.DAYNIGHT)
            delete_light_animation(self.light_objects)
            self.use_light_type = 0
        self.control.re_render()
    
    
class BackgroundControl(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.control = control
        lbl_controls = Label(master=self, text="Background", font="Arial 10 bold")
        lbl_controls.grid(row=0, column=0, columnspan=5)

        empty_bg_lbl = Label(master=self, text="Empty", font="Arial 10 bold")
        empty_bg_lbl.grid(row=1, column=0)
        self.empty_bg = PhotoImage(file = "assets/gui/empty_bg.png").subsample(2,2)
        empty_bg_btn = Button(master=self, image=self.empty_bg, command=self.remove_background)
        empty_bg_btn.grid(row=2, column=0)

        bg1_lbl = Label(master=self, text="Green Park", font="Arial 10 bold")
        bg1_lbl.grid(row=1, column=1)
        self.bg1 = PhotoImage(file = "assets/hdri_thumbs/green_point_park_2k.hdr.png").subsample(2,2)
        bg1_btn = Button(master=self, image=self.bg1, command=lambda: self.load_hdri("assets/HDRIs/green_point_park_2k.hdr"))
        bg1_btn.grid(row=2, column=1)

        bg2_lbl = Label(master=self, text="Old Depot", font="Arial 10 bold")
        bg2_lbl.grid(row=1, column=2)
        self.bg2 = PhotoImage(file = "assets/hdri_thumbs/old_depot_2k.hdr.png").subsample(2,2)
        bg2_btn = Button(master=self, image=self.bg2, command=lambda: self.load_hdri("assets/HDRIs/old_depot_2k.hdr"))
        bg2_btn.grid(row=2, column=2)

        bg3_lbl = Label(master=self, text="Desert", font="Arial 10 bold")
        bg3_lbl.grid(row=1, column=3)
        self.bg3 = PhotoImage(file = "assets/hdri_thumbs/syferfontein_6d_clear_2k.hdr.png").subsample(2,2)
        bg3_btn = Button(master=self, image=self.bg3, command=lambda: self.load_hdri("assets/HDRIs/syferfontein_6d_clear_2k.hdr"))
        bg3_btn.grid(row=2, column=3)

        btn_import_hdri = Button(master=self, text="Import custom HDRI", command=self.import_hdri)
        btn_import_hdri.grid(row=2, column=4)

    def load_hdri(self, path: str):
        hdri.set_background_image(path)
        self.control.re_render()

    def import_hdri(self):
        filetypes = [
            ("High Dynamic Range Image", "*.hdr")
        ]
        filename = filedialog.askopenfilename(title="Select image to import", filetypes=filetypes)
        if filename == "":
            return
        hdri.set_background_image(filename)
        self.control.re_render()
    
    def remove_background(self):
        hdri.remove_background_image()
        self.control.re_render()

class FrameWidgets(Frame):

    def __init__(self, master, control, max_frame: IntVar):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.control = control
        self.max_frame = max_frame
        
        # variables
        self.frame : int = 0
        max_frame.trace_add("write", self.max_changed)

        # grid
        self.columnconfigure(0, weight=1)

        # labels and sliders
        lbl_frame_setting = Label(master=self, text="Frame", font="Arial 10 bold")
        self.slider_frame_setting = Scale(master=self, from_= 0, to=self.max_frame.get(), orient="horizontal", command=lambda val: self.set_frame(val, False))
        self.slider_frame_setting.bind("<ButtonRelease-1>", lambda event : self.set_frame(self.get_frame(), True)) 
        
        # packing
        lbl_frame_setting.grid(row=0)
        self.slider_frame_setting.grid(row=1,sticky="wse")

    # Update the slider length whenever the frame max is changed
    def max_changed(self, var, index, mode):
        self.slider_frame_setting.configure(to=self.max_frame.get())
    
    # returns the frame value
    def get_frame(self) -> int:
        return self.frame

    # set frame to "value" and rerenders on "is_released"
    def set_frame(self, value : int, is_released : bool) -> None:
        self.frame = value
        if is_released:
            self.control.frames.set_current_frame(int(value))
            self.control.re_render()

class PointCloudWidgets(Frame):
    hasconverted = False
    cube = None
    sphere = None
    disk = None
    modeltest = None

    def __init__(self, master, control):
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        self.cube = bpy.context.object
        bpy.context.object.hide_render = True
        bpy.context.object.hide_viewport = True

        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        self.sphere = bpy.context.object
        bpy.context.object.hide_render = True
        bpy.context.object.hide_viewport = True
       
        bpy.ops.mesh.primitive_circle_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.editmode_toggle()
        self.disk = bpy.context.object
        bpy.context.object.hide_render = True
        bpy.context.object.hide_viewport = True

        self.size : float = 1
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.master = master
        self.control = control
        self.random  = BooleanVar()
        self.vertices = BooleanVar()
        self.pointcloud = BooleanVar()
        self.obj_selected = StringVar(self)
        self.obj_selected.set("sphere")
        self.vertices.set(True)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        lbl_pointcloudsettings =  Label(master=self, text="Pointcloud Object:", font="Arial 10 bold")
        check_pointcloud = Checkbutton(master=self, text="Pointcloud", variable=self.pointcloud, anchor="w", command=self.converter)
        check_vertices  = Checkbutton(master=self, text="vertices", variable=self.vertices, anchor="w", command=self.switch_to_vertex)
        check_random = Checkbutton(master=self, text="random", variable=self.random, anchor="w", command=self.switch_to_random)
        pointcloudobjects = (PointCloudObjects.SPHERE.value, PointCloudObjects.CUBE.value, PointCloudObjects.DISK.value)
        lbl_pointcloudobjects =  Label(master=self, text="Select Object:") 
        pointcloudobjects = (PointCloudObjects.SPHERE.value, PointCloudObjects.CUBE.value, PointCloudObjects.DISK.value )
        dropdown_objects = OptionMenu(self, self.obj_selected, *pointcloudobjects, command=self.set_object)
       
        lbl_size = Label(master=self, text="Point Size")
        slider_size = Scale(master=self, to = 8.0, orient="horizontal",
                                  resolution = 0.1, showvalue=False, command=lambda val: self.set_size(val, False))
        slider_size.bind("<ButtonRelease-1>", lambda event : self.set_size(self.get_size(), True)) 
        slider_size.set(self.get_size())  


        check_pointcloud.grid(row=1, column=0, sticky="w")
        lbl_size.grid(row=2, column=0, sticky="w")
        slider_size.grid(row=2, column=1,  sticky="we")
        lbl_pointcloudsettings.grid(row=0, column=0, columnspan=2)
        check_vertices.grid(row=3, column=1, sticky="w")
        check_random.grid(row=3, column=0, sticky="w")
        lbl_pointcloudobjects.grid(row=4, column=0,  sticky="we")
        dropdown_objects.grid(row=4, column=1, sticky="w")

    def set_object(self, *args):
        tex = PointCloudObjects(args[0])
        if tex == PointCloudObjects.SPHERE:
            setSphere(self)
        elif tex == PointCloudObjects.CUBE:
            setCube(self)
        elif tex == PointCloudObjects.DISK:
            setDisk(self)
        else: # NONE
            pass
        
        self.selectMainObject()
        self.control.re_render()

    def selectMainObject(self):
        bpy.context.view_layer.objects.active = self.control.model
   



    def reset(self):

        bpy.ops.object.modifier_remove(modifier="GeometryNodes")
        #setInstanceObjectScale(self)
        self.hasconverted = False
        self.pointcloud.set(False)
        
        
        
    
    def converter(self):
        convert(self)
    
    
    def get_size(self) -> float:
        return self.size

    def set_size(self, value, is_released : bool) -> None:
        self.size = float(value)
        bpy.data.node_groups["GeometryNodes"].nodes["Scale Elements"].inputs[2].default_value = value
        if is_released:
            self.control.re_render()

    
    def switch_to_random(self):
    
        if self.random.get():
            if(self.hasconverted):
                switchrandom(self)
            self.vertices.set(False)
        else:
            self.vertices.set(True)
        self.control.re_render()

    def switch_to_vertex(self):
        
        if self.vertices.get():
            if(self.hasconverted):
                switchvertex(self)
            self.random.set(False)
        else:
            self.random.set(True)
        self.control.re_render()


# Enum containing all possibe point cloud objects
class PointCloudObjects(enum.Enum):
    SPHERE = "sphere"
    CUBE = "cube"
    DISK = "disk"

   


class RightPanel(Frame):
        
    def __init__(self, master, control):
        Frame.__init__(self, master)
        
        self.current_color = (255, 255, 0)
        
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        
        # Color and render type widgets
        frm_look = ColorMeshWidgets(self, control)
        frm_look.grid(row=0, column=0, sticky="we")
        
        # Material widgets
        frm_mat = MaterialWidgets(self, control)
        frm_mat.grid(row=1, column=0, sticky="ew")
        
        # Texture widgets
        frm_tex = TextureWidgets(self, control)
        frm_tex.grid(row=2, column=0, sticky="ew")
        
        # Lighting widgets
        frm_light = LightingWidgets(self, control)
        frm_light.grid(row=3, column=0, sticky="we")

        # Pointcloud widgets
        self.frm_point = PointCloudWidgets(self, control)
        self.frm_point.grid(row=4, column=0, sticky="we")
    
  