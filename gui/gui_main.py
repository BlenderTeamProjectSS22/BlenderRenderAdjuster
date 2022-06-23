# author: Alexander Ritter
# created on: 06/06/2022
# edited by:

# description:
# GUI element: Main program, renders the GUI and connects it to other function

import tkinter as tk
from tkinter import Frame, Label, Button, StringVar, BooleanVar, Checkbutton, OptionMenu, Scale, Canvas, Entry
from tkinter import ttk
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo, showerror
from tkinter import filedialog
from PIL import ImageTk, Image

import webbrowser
#import requests
import enum

from gui.render_preview import RenderPreview
from gui.gui_options import SettingsWindow
from gui.properties import *

from Lightning.light_functions import day_light, night_light, delete_lights
from Lightning.light_class import Light
from HDRI.hdri import set_background_brightness

class ProgramGUI:
    def __init__(self, master):
        master.title("Render adjuster")
        master.minsize(107+184+480,307)
        icon = ImageTk.PhotoImage(Image.open("assets/gui/icon.ico"))
        master.iconphoto(True, icon)
        
        master.columnconfigure(0, weight=0, minsize=107)
        master.columnconfigure(1, weight=16)
        master.columnconfigure(2, weight=0, minsize=184)
        master.rowconfigure(0, weight=9, minsize=307)
        
        left  = LeftPanel(master)
        preview = RenderPreview(master)
        right = RightPanel(master)
        camcontrols = CameraControls(master)
        
        left.grid(row=0, column=0, sticky="nw")
        preview.grid(row=0, column=1, sticky="nwes")
        camcontrols.grid(row=1, column=1)
        right.grid(row=0, column=2, sticky="ne")
        
class LeftPanel(Frame):
    def __init__(self, master):
        Frame.__init__(self, master) # master or parent
        self.master = master
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
        btn_undo     = tk.Button(master=frame_ops, text="Undo", command=self.undo)
        btn_redo     = tk.Button(master=frame_ops, text="Redo", command=self.redo)
        btn_settings = tk.Button(master=frame_ops, text="Settings", command=self.open_settings_window)
        btn_updates  = tk.Button(master=frame_ops, text="Check for updates", command=self.check_update)  # The update check may or may not be implemented
        btn_help     = tk.Button(master=frame_ops, text="Help", command=self.open_help_page)
        lbl_ops.pack(fill=tk.X)
        btn_undo.pack(fill=tk.X)
        btn_redo.pack(fill=tk.X)
        btn_settings.pack(fill=tk.X)
        btn_updates.pack(fill=tk.X)
        btn_help.pack(fill=tk.X)
        frame_ops.pack()
    
    def import_model(self):
        filetypes = [
            ("All model files", "*.ply *.stl *.obj"),
            ("PLY object", "*.ply"),
            ("STL file", "*.stl")
            ("Wavefront OBJ", "*.obj")
        ]
        filename = filedialog.askopenfilename(title="Select model to import", filetypes=filetypes)
        # TODO Import the file using utils.py
        
    
    def export_model(self):
        filename = filedialog.asksaveasfile(
            title="Save model at",
            initialfile = "untitled.blend",
            defaultextension=".blend",
            filetypes=[("Blender project","*.blend")])
        # TODO Save the current scene in memory as a .blend file
    
    def render_image(self):
        pass
    
    def render_video(self):
        pass
    
    def undo(self):
        pass
    
    def redo(self):
        pass
    
    def open_settings_window(self):
        settings = SettingsWindow(self.master)
    
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
    def __init__(self, master):
        Frame.__init__(self, master)
        
        lbl_controls = Label(master=self, text="Camera Controls", font="Arial 10 bold")
        lbl_controls.grid(row=0, column=0)
        
        
class ColorMeshWidgets(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        
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
    
    def switch_vertex_color(self):
        pass
    
    def switch_mesh(self):
        if self.mesh.get():
            self.point.set(False)
        else:
            self.point.set(True)
    
    def switch_pointcloud(self):
        if self.point.get():
            self.mesh.set(False)
        else:
            self.mesh.set(True)

class MaterialWidgets(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        mat_selected = StringVar(master)
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
    
    def set_metallic_input(self, event):
        x = 0
        if self.ent_metallic.get() != "":
            x = clamp(int(self.ent_metallic.get()), 0, 100)
        self.set_metallic(x)
        
    def set_roughness_input(self, event):
        x = 0
        if self.ent_roughness.get() != "":
            x = clamp(int(self.ent_roughness.get()), 0, 100)
        self.set_roughness(x)
    
    def set_metallic(self, value):
        self.ent_metallic.delete(0, tk.END)
        self.ent_metallic.insert(tk.END, value)
        self.slider_metallic.set(value)
        pass
    
    def set_roughness(self, value):
        self.ent_roughness.delete(0, tk.END)
        self.ent_roughness.insert(tk.END, value)
        self.slider_roughness.set(value)
        pass

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
    def __init__(self, master):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        tex_selected = StringVar(master)
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
    
    def import_texture(self):
        filetypes = [
            ("PNG image", "*.png"),
        ]
        filename = filedialog.askopenfilename(title="Select a texture", filetypes=filetypes)
        # TODO Apply the texure to the object
        
        
# Enum containing all possible textures
class Textures(enum.Enum):
    NONE = "none"
    WOOD = "wood"
    BRICKS = "bricks"

class LightingWidgets(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        lbl_light = Label(master=self, text="Lighting", font="Arial 10 bold")
        lbl_brightness = Label(master=self, text="Brightness")
        btn_day = Button(master=self, text="Day", command=self.set_day)
        btn_night = Button(master=self, text="Night", command=self.set_night)
        slider_brightness = Scale(master=self, orient="horizontal", showvalue=False, command=self.set_brightness)
        lbl_light.grid(row=0, column=0, columnspan=2)
        lbl_brightness.grid(row=1, column=0, sticky="w")
        slider_brightness.grid(row=1, column=1,  sticky="we")
        btn_day.grid(row=2, column=0, sticky="we",pady=1)
        btn_night.grid(row=2, column=1, sticky="we",pady=1)
        self.light_objects : list[Light] = []
        self.is_day : bool = None
        self.brightness : float = 3
    
    def set_brightness(self, value):
        # recreate lights with new brightness
        if self.is_day != None:
            if self.is_day:
                self.set_day()
            else:
                self.set_night()
        # set new brightness
        self.brightness = float(value)

    def get_brightness(self) -> float:
        return self.brightness
        
    def set_day(self):
        set_background_brightness(0)
        self.is_day = True
        delete_lights(self.light_objects)
        self.light_objects = day_light(self.get_brightness(), 80, True, None) # replace "None" with camera-object
    
    def set_night(self):
        set_background_brightness(0)
        self.is_day = False
        delete_lights(self.light_objects)
        self.light_objects = night_light(self.get_brightness(), 80, True, None) # replace "None" with camera-object


class RightPanel(Frame):
        
    def __init__(self, master):
        Frame.__init__(self, master) 
        
        self.current_color = (255, 255, 0)
        
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        
        # Color and render type widgets
        frm_look = ColorMeshWidgets(self)
        frm_look.grid(row=0, column=0, sticky="we")
        
        # Material widgets
        frm_mat = MaterialWidgets(self)
        frm_mat.grid(row=1, column=0, sticky="ew")
        
        # Texture widgets
        frm_tex = TextureWidgets(self)
        frm_tex.grid(row=2, column=0, sticky="ew")
        
        # Lighting widgets
        frm_light = LightingWidgets(self)
        frm_light.grid(row=3, column=0, sticky="we")