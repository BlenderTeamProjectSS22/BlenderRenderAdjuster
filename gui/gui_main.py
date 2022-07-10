# author: Alexander Ritter
# created on: 06/06/2022
# edited by:

# description:
# GUI element: Main program, renders the GUI and connects it to other function

from cgi import print_directory
import tkinter as tk
from tkinter import Frame, Label, Button, StringVar, BooleanVar, Checkbutton, OptionMenu, Scale, Canvas, Entry, PhotoImage
from tkinter import ttk
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo, showerror
from tkinter import filedialog
from PIL import ImageTk, Image

import webbrowser
import threading
import requests
import enum

from gui.render_preview import RenderPreview
from gui.gui_options import SettingsWindow
from gui.settings import Control
from gui.loading_screen import VideoLoadingScreen, ImageLoadingScreen
import gui.properties as props
from gui.properties import VERSION_PATCH, VERSION_MAJOR, VERSION_MINOR, UPDATE_URL

from Lightning.light_functions import day_light, night_light, delete_lights, lantern_light, day_night_cycle, delete_all_lights, delete_light_animation, lights_enabled
from Lightning.light_class import Light
from HDRI.hdri import set_background_brightness, background_brightness_affects_objects
import utils
import os

import HDRI.hdri as hdri

## for testing
if props.DEBUG:
    import bpy

class ProgramGUI:
    def __init__(self, master):
    
        # blender initialization
        utils.clear_scene()
        camera   = utils.OrbitCam()
        renderer = utils.Renderer(camera.camera)
        renderer.set_preview_render()

        hdri.initialize_world_texture()

        #generate HDRI previews
        hdri_dir = os.fsencode("assets/HDRIs/")
        for file in os.listdir(hdri_dir):
            filename = os.fsdecode(file)
            utils.generate_hdri_thumbnail("assets/HDRIs/" + filename)
        
        master.title("Render adjuster")
        master.minsize(107+184+480,307)
        icon = ImageTk.PhotoImage(Image.open("assets/gui/icon.ico"))
        master.iconphoto(True, icon)
        
        master.columnconfigure(0, weight=0, minsize=107)
        master.columnconfigure(1, weight=16)
        master.columnconfigure(2, weight=0, minsize=184)
        master.rowconfigure(0, weight=9, minsize=307)
        master.rowconfigure(1, weight=9)
        
        # Create global control object
        self.preview = RenderPreview(master)
        self.control = Control(renderer, self.preview, camera)
        self.control.model = None
        
        # Load defaul cube if debug is enabled
        if props.DEBUG:
            self.control.model = utils.import_mesh("assets/STL samples/cube.obj")
            self.control.camera.rotate_z(45)
            self.control.camera.rotate_x(-20)
            self.control.camera.set_distance(10)
            self.control.re_render()
        
        left  = LeftPanel(master, self.control)
        right = RightPanel(master, self.control)
        camcontrols = CameraControls(master, self.control)
        modelcontrols = ModelControls(master, self.control)

        background_ctrl = BackgroundControl(master, self.control)
        
        left.grid(row=0, column=0, sticky="nw")
        self.preview.grid(row=0, column=1, sticky="nwes")
        camcontrols.grid(row=1, column=1, sticky="nw")
        modelcontrols.grid(row=1, column=1, sticky="sw")

        right.grid(row=0, column=2, sticky="ne")
        background_ctrl.grid(row=1, column=1, sticky="e")
        
        
class LeftPanel(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master)
        self.master = master
        self.control = control
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
            utils.remove_object(self.control.model)
        self.control.model = utils.import_mesh(filename)
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
        #self.control.renderer.set_final_render(file_path=filename)
        
        self.frames_to_do = 0
        self.loading_video = VideoLoadingScreen(self, 250)
        self.update_idletasks()
        
        def render_per_frame(scene):
            self.frames_to_do = self.frames_to_do + 1
            self.loading_video.set_frame(self.frames_to_do)
            self.update_idletasks()
            self.loading_video.update_idletasks()
        
        def render_finished(scene):
            self.loading_video.render_finished()
            utils.unregister_handler(render_per_frame, utils.Handler.PER_FRAME)
            utils.unregister_handler(render_finished,  utils.Handler.FINISHED)
        
        utils.register_handler(render_per_frame, utils.Handler.PER_FRAME)
        utils.register_handler(render_finished, utils.Handler.FINISHED)
        
        def render_anim():
            self.control.renderer.render(animation=True)
        self.control.renderer.set_preview_render()
        
        renderthread = threading.Thread(target=render_anim)
        renderthread.start()
    
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
        lbl_controls = Label(master=self, text="Camera Controls", font="Arial 10 bold")
        lbl_rot   = Label(master=self, text="Rotation")
        lbl_pan   = Label(master=self, text="Panning")
        lbl_controls.grid(row=0, column=0, columnspan=7)
        lbl_rot.grid(row=1, column=0, columnspan=3)
        lbl_pan.grid(row=1, column=3, columnspan=3)

        btn_up_rot = Button(master=self, text="↑", command=self.rotate_up)
        btn_down_rot = Button(master=self, text="↓", command=self.rotate_down)
        btn_right_rot = Button(master=self, text="→", command=self.rotate_right)
        btn_left_rot = Button(master=self, text="←", command=self.rotate_left)

        btn_up_rot.grid(row=2, column=1)
        btn_left_rot.grid(row=3, column=0, sticky="w")
        btn_right_rot.grid(row=3, column=2, sticky="e")
        btn_down_rot.grid(row=4, column=1)

        btn_up_pan = Button(master=self, text="↑", command=self.move_up)
        btn_down_pan = Button(master=self, text="↓", command=self.move_down)
        btn_right_pan = Button(master=self, text="→", command=self.move_right)
        btn_left_pan = Button(master=self, text="←", command=self.move_left)

        btn_up_pan.grid(row=2, column=4)
        btn_left_pan.grid(row=3, column=3, sticky="w")
        btn_right_pan.grid(row=3, column=5, sticky="e")
        btn_down_pan.grid(row=4, column=4)

        lbl_dist   = Label(master=self, text="Distance")
        btn_in = Button(master=self, text="Pan in", command=self.pan_in)
        btn_out = Button(master=self, text="Pan out", command=self.pan_out)

        lbl_dist.grid(row = 1, column=6)
        btn_in.grid(row=2, column=6, padx=8)
        btn_out.grid(row=4, column=6, padx=8)

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
        
    
class ModelControls(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        
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
        lbl_type    = Label(master=self, text="Type")
        self.vertc = BooleanVar()
        self.mesh  = BooleanVar()
        self.point = BooleanVar()
        check_vertc = Checkbutton(master=self, text="Vertex color", variable=self.vertc, anchor="w", command=self.switch_vertex_color)
        check_mesh  = Checkbutton(master=self, text="Full mesh", variable=self.mesh, anchor="w", command=self.switch_mesh)
        check_point = Checkbutton(master=self, text="Point cloud", variable=self.point, anchor="w", command=self.switch_pointcloud)
        lbl_look.grid(row=0, column=0, columnspan=2)
        lbl_color.grid(row=1, column=0)
        lbl_type.grid(row=1, column=1)
        btn_picker.grid(row=2, column=0)
        check_vertc.grid(row=3, column=0, sticky="w")
        check_mesh.grid(row=2, column=1, sticky="w")
        check_point.grid(row=3, column=1, sticky="w")
    
    def pick_color(self):
        self.current_color = askcolor(self.current_color)[0]
        print(self.current_color)
        # FIX Keep old color if no color is selected (current_color can be None)
        # TODO Change the color of the object
        self.control.re_render()
    
    def switch_vertex_color(self):
        self.control.re_render()
    
    def switch_mesh(self):
        if self.mesh.get():
            self.point.set(False)
        else:
            self.point.set(True)
        self.control.re_render()
    
    def switch_pointcloud(self):
        if self.point.get():
            self.mesh.set(False)
        else:
            self.mesh.set(True)
        self.control.re_render()

class MaterialWidgets(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.control = control
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        mat_selected = StringVar(self)
        mat_selected.set("default")
        lbl_materials = Label(master=self, text="Material selection", font="Arial 10 bold")
        lbl_metallic = Label(master=self, text="Metallic")
        lbl_roughness = Label(master=self, text="Roughness")
        
        validate_int = self.register(self.validate_integer)
        self.ent_metallic = Entry(master=self, validate="key", validatecommand=(validate_int, '%P'), width=10)
        self.ent_metallic.bind('<Return>', self.set_metallic_input)
        self.ent_roughness = Entry(master=self, validate="key", validatecommand=(validate_int, '%P'), width=10)
        self.ent_roughness.bind('<Return>', self.set_roughness_input)
        
        self.slider_metallic = Scale(master=self, orient="horizontal", showvalue=False, command=self.set_metallic)
        self.slider_roughness  = Scale(master=self, orient="horizontal", showvalue=False, command=self.set_roughness)
        
        lbl_sel_mat   = Label(master=self, text="Select:")
        materials = ("default", Materials.GLASS.value, Materials.EMISSIVE.value, Materials.STONE.value)
        dropdown_materials = OptionMenu(self, mat_selected, *materials, command=self.set_material)
        #TODO: material_picker = MaterialPicker(self)
        lbl_materials.grid(row=0, column=0, columnspan=2, sticky="we")
        lbl_metallic.grid(row=1, column=0, sticky="we")
        self.ent_metallic.grid(row=1, column=1, sticky="w")
        self.slider_metallic.grid(row=2, column=0, sticky="we", columnspan=2)
        lbl_roughness.grid(row=3, column=0, sticky="we")
        self.ent_roughness.grid(row=3, column=1, sticky="w")
        self.slider_roughness.grid(row=4, column=0, sticky="we", columnspan=2)
        lbl_sel_mat.grid(row=5, column=0, sticky="w")
        dropdown_materials.grid(row=5, column=1, sticky="w")
        
        # default starting value
        self.set_metallic(0)
        self.set_roughness(50)
    
    def validate_integer(self, P):
        # TODO This prevents deleting e.g. '5', because field can't be empty
        # Implement that it sets it to 0 automatically if last digit is deleted
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
    
    def set_material(self, *args):
        mat = Materials(args[0])
        if mat == Materials.GLASS:
            pass
        elif mat == Materials.STONE:
            pass
        elif mat == Materials.EMISSIVE:
            pass
        else: #default
            pass
        self.control.re_render()
    
    def set_metallic_input(self, event):
        x = 0
        if self.ent_metallic.get() != "":
            x = clamp(int(self.ent_metallic.get()), 0, 100)
        self.set_metallic(x)
        self.control.re_render()
        
    def set_roughness_input(self, event):
        x = 0
        if self.ent_roughness.get() != "":
            x = clamp(int(self.ent_roughness.get()), 0, 100)
        self.set_roughness(x)
        self.control.re_render()
    
    def set_metallic(self, value):
        self.ent_metallic.delete(0, tk.END)
        self.ent_metallic.insert(tk.END, value)
        self.slider_metallic.set(value)
        self.control.re_render()
    
    def set_roughness(self, value):
        self.ent_roughness.delete(0, tk.END)
        self.ent_roughness.insert(tk.END, value)
        self.slider_roughness.set(value)
        self.control.re_render()

# Enum containing all possible materials
class Materials(enum.Enum):
    GLASS = "glass"
    STONE = "stone"
    EMISSIVE = "emissive"

# Clamps a value to the range of mimimum to maximum
# TODO Move to other module?
def clamp(val, minimum, maximum):
    return min(max(val, minimum), maximum)

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
    STARTING_TIME : int = 6

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
        
        # grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        # labels
        lbl_light = Label(master=self, text="Lighting", font="Arial 10 bold")
        lbl_brightness = Label(master=self, text="Brightness")
        lbl_daytime = Label(master=self, text="Time of day/night")
        lbl_background = Label(master=self, text="Background Strength")
        # buttons
        btn_use_lights_switch = Button(master=self, text="Lights off", command=self.lights_off)
        btn_day = Button(master=self, text="Day", command=self.set_day)
        btn_night = Button(master=self, text="Night", command=self.set_night)
        btn_lantern = Button(master=self, text="Lantern", command=self.set_lantern)
        # checkboxs
        check_day_night_circle = Checkbutton(master=self, text="Day Night Cycle Animation", variable=self.is_day_night, anchor="w", command=self.switch_day_night_circle)
        # slider
        slider_brightness = Scale(master=self, to = 8.0, orient="horizontal",
                                  resolution = 0.1, showvalue=False, command=lambda val: self.set_brightness(val, False))
        slider_daytime = Scale(master=self, from_= 0, to = 12, orient="horizontal", showvalue=True, command=lambda val: self.set_daytime(val, False))
        slider_background = Scale(master=self, from_= 0, to = 10, orient="horizontal",
                                  resolution = 0.1, showvalue=False, command=lambda val: self.set_background_strength(val, False))
        slider_brightness.bind("<ButtonRelease-1>", lambda event : self.set_brightness(self.get_brightness(), True)) 
        slider_daytime.bind("<ButtonRelease-1>", lambda event : self.set_daytime(self.get_daytime(), True)) 
        slider_background.bind("<ButtonRelease-1>", lambda event : self.set_background_strength(self.get_background_strength(), True)) 
        ## for testing
        if props.DEBUG:
            slider_frame_setting = Scale(master=self, from_= 0, to = 360, orient="horizontal", showvalue=True, command=self.set_frame)

        # packing
        lbl_light.grid(row=0, column=0, columnspan=2)
        lbl_brightness.grid(row=1, column=0, sticky="w")
        slider_brightness.grid(row=1, column=1,  sticky="we", columnspan=2)
        btn_use_lights_switch.grid(row=2, column=0, sticky="we",pady=1)
        btn_lantern.grid(row=2, column=1, sticky="we",pady=1, columnspan=2) 
        btn_day.grid(row=3, column=0, sticky="we",pady=1)
        btn_night.grid(row=3, column=1, sticky="we",pady=1)
        check_day_night_circle.grid(row=4, column=0, sticky="", pady=1, columnspan=2)
        lbl_daytime.grid(row=5, column=0, sticky="w")
        slider_daytime.grid(row=5, column=1,  sticky="we", columnspan=2)  
        lbl_background.grid(row=6, column=0,  sticky="w") 
        slider_background.grid(row=6, column=1,  sticky="we", columnspan=2) 
        ## for testing
        if props.DEBUG:
            slider_frame_setting.grid(row=7,column=1,sticky="we")

        # initialization   
        slider_brightness.set(self.get_brightness())  
        slider_background.set(self.get_background_strength())
        self.lights_off()
        background_brightness_affects_objects(False)
        

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
        self.control.re_render()

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
        if is_released:
            self.fit_brightness_to_lights()
        
    # recreate lights with new brightness
    def fit_brightness_to_lights(self) -> None:
        match self.use_light_type:
            case 0:
                self.set_day()
                return
            case 1:
                self.set_night()
                return
            case _:
                self.set_lantern()

    # returns the brightness
    def get_brightness(self) -> float:
        return self.brightness
        
    # some setting that should be made before creating new lights
    def standard_light_settings(self, use_light_type: int) -> None:
        lights_enabled(True)
        self.use_light_type = use_light_type
        self.is_day_night.set(False)
        delete_lights(self.light_objects)

    # set day light
    def set_day(self) -> None:
        self.standard_light_settings(0)
        self.light_objects = day_light(self.get_brightness(), self.get_daytime() * self.TIME_TO_ANGLE_CONSTANT, True, self.control.camera)
        self.control.re_render()
    
    # set night light
    def set_night(self) -> None:
        self.standard_light_settings(1)
        self.light_objects = night_light(self.get_brightness(), self.get_daytime() * self.TIME_TO_ANGLE_CONSTANT, True, self.control.camera)
        self.control.re_render()
        
    # set lantern light
    def set_lantern(self) -> None:
        self.standard_light_settings(2)
        self.light_objects = lantern_light(self.get_brightness(), self.HIGH_OF_LATERN_LIGHT, True, self.control.camera)
        self.control.re_render()

    # needs to be tested
    # creates a day night cycle
    def set_day_night_cycle(self) -> None:
        self.light_objects = day_night_cycle(self.STARTING_TIME, self.get_brightness(), True, self.control.camera)
        self.control.re_render()
    
    # creates a day night circle if "self.is_day_night" = true
    # deletes the animations if "self.is_day_night" = false
    def switch_day_night_circle(self):
        if self.is_day_night.get():
            delete_lights(self.light_objects)
            self.light_objects = day_night_cycle(self.STARTING_TIME, self.get_brightness(), True, self.control.camera)
        else:
            delete_light_animation(self.light_objects)
        self.control.re_render()

    ## test function
    ## set frame to "value"
    def set_frame(self, value):
        bpy.context.scene.frame_current = int(value)
        self.control.re_render()
    
    
class BackgroundControl(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        
        self.control = control
        lbl_controls = Label(master=self, text="Background", font="Arial 10 bold")
        lbl_select   = Label(master=self, text="Select HDRI image:")
        lbl_controls.grid(row=0, column=0, columnspan=5)
        lbl_select.grid(row=1, column=0, columnspan=5)

        empty_bg_lbl = Label(master=self, text="Empty", font="Arial 10 bold")
        empty_bg_lbl.grid(row=2, column=0)
        self.empty_bg = PhotoImage(file = "assets/gui/empty_bg.png").subsample(2,2)
        empty_bg_btn = Button(master=self, image=self.empty_bg, command=self.remove_background)
        empty_bg_btn.grid(row = 3, column=0)

        bg1_lbl = Label(master=self, text="Green Park", font="Arial 10 bold")
        bg1_lbl.grid(row=2, column=1)
        self.bg1 = PhotoImage(file = "assets/hdri_thumbs/green_point_park_2k.hdr.png").subsample(2,2)
        bg1_btn = Button(master=self, image=self.bg1, command=lambda: self.load_hdri("assets/HDRIs/green_point_park_2k.hdr"))
        bg1_btn.grid(row = 3, column=1)

        bg2_lbl = Label(master=self, text="Old Depot", font="Arial 10 bold")
        bg2_lbl.grid(row=2, column=2)
        self.bg2 = PhotoImage(file = "assets/hdri_thumbs/old_depot_2k.hdr.png").subsample(2,2)
        bg2_btn = Button(master=self, image=self.bg2, command=lambda: self.load_hdri("assets/HDRIs/old_depot_2k.hdr"))
        bg2_btn.grid(row = 3, column=2)

        bg3_lbl = Label(master=self, text="Desert", font="Arial 10 bold")
        bg3_lbl.grid(row=2, column=3)
        self.bg3 = PhotoImage(file = "assets/hdri_thumbs/syferfontein_6d_clear_2k.hdr.png").subsample(2,2)
        bg3_btn = Button(master=self, image=self.bg3, command=lambda: self.load_hdri("assets/HDRIs/syferfontein_6d_clear_2k.hdr"))
        bg3_btn.grid(row = 3, column=3)

        btn_import_hdri = Button(master=self, text="Import custom HDRI", command=self.import_hdri)
        btn_import_hdri.grid(row=3, column=4)

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