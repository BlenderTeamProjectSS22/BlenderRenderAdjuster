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
import requests
import enum

from gui.render_preview import RenderPreview
from gui.gui_options import SettingsWindow
from gui.settings import Control
from gui.properties import *

from materials.materials import *

import utils

class ProgramGUI:
    def __init__(self, master):
    
        # blender initialization
        utils.clear_scene()
        camera   = utils.OrbitCam()
        renderer = utils.Renderer(camera.camera)
        renderer.set_preview_render()
        
        
        master.title("Render adjuster")
        master.minsize(107+184+480,307)
        icon = ImageTk.PhotoImage(Image.open("assets/gui/icon.ico"))
        master.iconphoto(True, icon)
        
        master.columnconfigure(0, weight=0, minsize=107)
        master.columnconfigure(1, weight=16)
        master.columnconfigure(2, weight=0, minsize=184)
        master.rowconfigure(0, weight=9, minsize=307)
        
        # Create global control object
        self.preview = RenderPreview(master)
        self.control = Control(renderer, self.preview, camera)
        self.control.material = MaterialController()
        self.control.model = None
        
        left  = LeftPanel(master, self.control)
        right = RightPanel(master, self.control)
        camcontrols = CameraControls(master, self.control)
        
        left.grid(row=0, column=0, sticky="nw")
        self.preview.grid(row=0, column=1, sticky="nwes")
        camcontrols.grid(row=1, column=1)
        right.grid(row=0, column=2, sticky="ne")
        
        
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
            ("STL file", "*.stl"),
            ("Wavefront OBJ", "*.obj")
        ]
        filename = filedialog.askopenfilename(title="Select model to import", filetypes=filetypes)
        if filename == "":
            return
        if self.control.model != None:
            utils.remove_object(self.control.model)
        self.control.model = utils.import_mesh(filename)
        self.control.material.apply_material(self.control.model)
        self.control.re_render()
        
    
    def export_model(self):
        filename = filedialog.asksaveasfile(
            title="Save model at",
            initialfile = "untitled.blend",
            defaultextension=".blend",
            filetypes=[("Blender project","*.blend")])
        if filename == None:
            return
        utils.export_blend(filename.name)
    
    def render_image(self):
        filename = filedialog.asksaveasfile(
            title="Save image at",
            initialfile = "render.png",
            defaultextension=".png",
            filetypes=[("Portable Network Graphics","*.png")])
        if filename == None:
            return
        self.control.renderer.set_final_render(file_path=filename.name)
        self.control.renderer.render()
        self.control.renderer.set_preview_render()
    
    def render_video(self):
        filename = filedialog.asksaveasfile(
            title="Save video at",
            initialfile = "render.avi",
            defaultextension=".avi",
            filetypes=[("Audio Video Interleave","*.avi")])
        if filename == None:
            return
        self.control.renderer.set_final_render(file_path=filename.name, animation=True)
        self.control.renderer.render()
        self.control.renderer.set_preview_render()
    
    def undo(self):
        pass
    
    def redo(self):
        pass
    
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
        lbl_controls.grid(row=0, column=0, columnspan=4)
        lbl_rot.grid(row=1, column=0, columnspan=3)

        btn_up = Button(master=self, text="↑", command=self.move_up)
        btn_down = Button(master=self, text="↓", command=self.move_down)
        btn_right = Button(master=self, text="→", command=self.move_right)
        btn_left = Button(master=self, text="←", command=self.move_left)

        btn_up.grid(row=2, column=1)
        btn_left.grid(row=3, column=0, sticky="w")
        btn_right.grid(row=3, column=2, sticky="e")
        btn_down.grid(row=4, column=1)

        lbl_dist   = Label(master=self, text="Distance")
        btn_in = Button(master=self, text="Pan in", command=self.pan_in)
        btn_out = Button(master=self, text="Pan out", command=self.pan_out)

        lbl_dist.grid(row = 1, column=3)
        btn_in.grid(row=2, column=3, padx=8)
        btn_out.grid(row=4, column=3, padx=8)

    def move_up(self):
        self.control.camera.rotate_x(-10)
        self.control.re_render()
    
    def move_down(self):
        self.control.camera.rotate_x(10)
        self.control.re_render()

    def move_right(self):
        self.control.camera.rotate_z(10)
        self.control.re_render()

    def move_left(self):
        self.control.camera.rotate_z(-10)
        self.control.re_render()

    def pan_in(self):
        self.control.camera.change_distance(-1)
        self.control.re_render()

    def pan_out(self):
        self.control.camera.change_distance(1)
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
    
        color = askcolor(self.current_color)[0]
        
        if color is not None:
            self.current_color = color
            self.control.material.set_color(utils.convert_color_to_bpy(self.current_color))
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
        lbl_metallic  = Label(master=self, text="Metallic")
        lbl_roughness = Label(master=self, text="Roughness")
        lbl_transmiss = Label(master=self, text="Transmission")
        lbl_emissive  = Label(master=self, text="Emissive Strength")
        
        self.emissive = BooleanVar(self)
        print(self.emissive.get())
        self.glow     = BooleanVar(self)
        check_emiss   = Checkbutton(master=self, text="Emissive", variable=self.emissive, anchor="w", command=self.toggle_emissive)
        print(str(self.emissive.get()))
        check_glow    = Checkbutton(master=self, text="Glow", variable=self.glow, command=self.toggle_glow)
        
        validate_int = self.register(self.validate_integer)
        self.ent_metallic  = Entry(master=self, validate="key", validatecommand=(validate_int, '%P'), width=10)
        self.ent_roughness = Entry(master=self, validate="key", validatecommand=(validate_int, '%P'), width=10)
        self.ent_transmiss = Entry(master=self, validate="key", validatecommand=(validate_int, '%P'), width=10)
        self.ent_emissive  = Entry(master=self, validate="key", validatecommand=(validate_int, '%P'), width=10)
        self.ent_metallic.bind("<Return>",  self.set_metallic_input)
        self.ent_roughness.bind("<Return>", self.set_roughness_input)
        self.ent_transmiss.bind("<Return>", self.set_transmiss_input)
        self.ent_emissive.bind("<Return>", self.set_emissive_input)
        
        self.slider_metallic  = Scale(master=self, orient="horizontal", showvalue=False, command=lambda val: self.set_metallic(val, False))
        self.slider_roughness = Scale(master=self, orient="horizontal", showvalue=False, command=lambda val: self.set_roughness(val, False))
        self.slider_transmiss = Scale(master=self, orient="horizontal", showvalue=False, command=lambda val: self.set_transmission(val, False))
        self.slider_emissive  = Scale(master=self, orient="horizontal", showvalue=False, command=lambda val: self.set_emissive(val, False))
        self.slider_metallic.bind("<ButtonRelease-1>",  lambda event: self.set_metallic(self.slider_metallic.get(), True))
        self.slider_roughness.bind("<ButtonRelease-1>", lambda event: self.set_roughness(self.slider_roughness.get(), True))
        self.slider_transmiss.bind("<ButtonRelease-1>", lambda event: self.set_transmission(self.slider_transmiss.get(), True)) 
        self.slider_emissive.bind("<ButtonRelease-1>", lambda event: self.set_emissive(self.slider_emissive.get(), True)) 
        
        lbl_sel_mat   = Label(master=self, text="Select:")
        materials = ("default", Materials.GLASS.value, Materials.EMISSIVE.value, Materials.STONE.value)
        dropdown_materials = OptionMenu(self, mat_selected, *materials, command=self.set_material)
        
        lbl_materials.grid(row=0, column=0, columnspan=2, sticky="we")
        lbl_metallic.grid(row=1, column=0, sticky="we")
        self.ent_metallic.grid(row=1, column=1, sticky="w")
        self.slider_metallic.grid(row=2, column=0, sticky="we", columnspan=2)
        
        lbl_roughness.grid(row=3, column=0, sticky="we")
        self.ent_roughness.grid(row=3, column=1, sticky="w")
        self.slider_roughness.grid(row=4, column=0, sticky="we", columnspan=2)
        
        lbl_transmiss.grid(row=5, column=0, sticky="we")
        self.ent_transmiss.grid(row=5, column=1, sticky="we")
        self.slider_transmiss.grid(row=6, column=0, sticky="we", columnspan=2)
        
        check_emiss.grid(row=7, column=0, sticky="w")
        check_glow.grid(row=7, column=1, sticky="w")
        lbl_emissive.grid(row=8, column=0, sticky="we")
        self.ent_emissive.grid(row=8, column=1, sticky="we")
        self.slider_emissive.grid(row=9, column=0, sticky="we", columnspan=2)
        
        lbl_sel_mat.grid(row=10, column=0, sticky="w")
        dropdown_materials.grid(row=10, column=1, sticky="w")
        
        self.default_values()
        
        
    def default_values(self):
        self.set_metallic(0, False)
        self.set_roughness(50, False)
        self.set_transmission(0, False)
        self.set_emissive(0, False)
        self.control.material.disable_bump()
        
    def validate_integer(self, P):
        # TODO This prevents deleting e.g. '5', because field can't be empty
        # Implement that it sets it to 0 automatically if last digit is deleted
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
    
    def set_material(self, *args):
        match Materials(args[0]):
            case Materials.GLASS:
                self.control.material.glass_material()
            case Materials.STONE:
                self.control.material.stone_material()
            case Materials.EMISSIVE:
                pass
            case _:
                pass
        self.adjust_sliders()
        self.control.re_render()
    
    # Readjust sliders to fit the active material
    def adjust_sliders(self):
        self.set_metallic(self.control.material.metallic*100, False)
        self.set_roughness(self.control.material.roughness*100, False)
        self.set_transmission(self.control.material.transmission*100, False)
    
    def set_metallic_input(self, event):
        x = 0
        if self.ent_metallic.get() != "":
            x = clamp(int(self.ent_metallic.get()), 0, 100)
        self.set_metallic(x, True)
        self.control.re_render()
        
    def set_roughness_input(self, event):
        x = 0
        if self.ent_roughness.get() != "":
            x = clamp(int(self.ent_roughness.get()), 0, 100)
        self.set_roughness(x, True)
        self.control.re_render()
        
    def set_transmiss_input(self, event):
        x = 0
        if self.ent_transmiss.get() != "":
            x = clamp(int(self.ent_transmiss.get()), 0, 100)
        self.set_transmission(x, True)
        self.control.re_render()
    
    def set_emissive_input(self, event):
        x = 0
        if self.ent_emissive.get() != "":
            x = clamp(int(self.ent_emissive.get()), 0, 100)
        self.set_emissive(x, True)
        self.control.re_render()
        
    def set_metallic(self, value, isReleased: bool):
        self.ent_metallic.delete(0, tk.END)
        self.ent_metallic.insert(tk.END, value)
        self.slider_metallic.set(value)
        self.control.material.set_metallic(utils.percent(int(value)))
        
        if isReleased:
            print("Setting metallic to " + str(value))
            self.control.re_render()
    
    def set_roughness(self, value, isReleased: bool):
        self.ent_roughness.delete(0, tk.END)
        self.ent_roughness.insert(tk.END, value)
        self.slider_roughness.set(value)
        self.control.material.set_roughness(utils.percent(int(value)))
        
        if isReleased:
            print("Setting roughness to " + str(value))
            self.control.re_render()
    
    def set_transmission(self, value, isReleased: bool):
        self.ent_transmiss.delete(0, tk.END)
        self.ent_transmiss.insert(tk.END, value)
        self.slider_transmiss.set(value)
        self.control.material.set_transmission(utils.percent(int(value)))
        
        if isReleased:
            print("Setting transmission to " + str(value))
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
    def __init__(self, master, control):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.control = control
        
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
    
    def set_brightness(self, value):
        # TODO set brightness of the lights
        self.control.re_render()
        
    def set_day(self):
        self.control.re_render()
    
    def set_night(self):
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
