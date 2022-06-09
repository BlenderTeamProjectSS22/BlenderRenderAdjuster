# author: Alexander Ritter
# created on: 06/06/2022
# edited by:

# description:
# GUI element: Main program, renders the GUI and connects it to other function

import tkinter as tk
from tkinter import Frame, Label, Button, StringVar, Checkbutton, OptionMenu, Scale, Canvas, Entry
from tkinter import ttk
from tkinter.colorchooser import askcolor

import enum

from render_preview import RenderPreview

class ProgramGUI:
    def __init__(self, master):
        master.title("Render adjuster")
        root.minsize(107+184+480,307)
        master.iconbitmap("../assets/gui/icon.ico")
        
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
        pass
    
    def export_model(self):
        pass
    
    def render_image(self):
        pass
    
    def render_video(self):
        pass
    
    def undo(self):
        pass
    
    def redo(self):
        pass
    
    def open_settings_window(self):
        pass
    
    def check_update(self):
        pass
    
    def open_help_page(self):
        pass
        

class CameraControls(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        
        lbl_controls = Label(master=self, text="Camera Controls", font="Arial 10 bold")
        lbl_controls.grid(row=0, column=0)
        
        
class ColorMeshWidgets(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        lbl_look    = Label(master=self, text="Look", font="Arial 10 bold")
        lbl_color   = Label(master=self, text="Color")
        btn_picker  = Button(master=self, text="pick", command=self.pick_color)
        lbl_type    = Label(master=self, text="Type")
        check_vertc = Checkbutton(master=self, text="Vertex color", anchor="w", command=self.switch_vertex_color)
        check_mesh  = Checkbutton(master=self, text="Full mesh", anchor="w", command=self.switch_mesh)
        check_point = Checkbutton(master=self, text="Point cloud", anchor="w", command=self.switch_pointcloud)
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
        pass
    
    def switch_pointcloud(self):
        pass

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
        self.ent_metallic = Entry(master=self, width=10)
        lbl_roughness = Label(master=self, text="Roughness")
        self.ent_roughness = Entry(master=self, width=10)
        slider_metallic = Scale(master=self, orient="horizontal", showvalue=False, command=self.set_metallic)
        slider_roughness  = Scale(master=self, orient="horizontal", showvalue=False,  command=self.set_roughness)
        lbl_sel_mat   = Label(master=self, text="Select:")
        materials = ("default", Materials.GLASS.value, Materials.EMISSIVE.value, Materials.STONE.value)
        dropdown_materials = OptionMenu(self, mat_selected, *materials, command=self.set_material)
        #TODO: material_picker = MaterialPicker(self)
        lbl_materials.grid(row=0, column=0, columnspan=2, sticky="we")
        lbl_metallic.grid(row=1, column=0, sticky="we")
        self.ent_metallic.grid(row=1, column=1, sticky="w")
        slider_metallic.grid(row=2, column=0, sticky="we", columnspan=2)
        lbl_roughness.grid(row=3, column=0, sticky="we")
        self.ent_roughness.grid(row=3, column=1, sticky="w")
        slider_roughness.grid(row=4, column=0, sticky="we", columnspan=2)
        lbl_sel_mat.grid(row=5, column=0, sticky="w")
        dropdown_materials.grid(row=5, column=1, sticky="w")
        
        # default starting value
        slider_metallic.set(0)
        self.set_metallic(0)
        slider_roughness.set(50)
        self.set_roughness(50)
    
    def set_material(self, *args):
        pass
    
    def set_metallic(self, value):
        pass
    
    def set_roughness(self, value):
        pass

# Enum containing all possible materials
class Materials(enum.Enum):
    GLASS = "glass"
    STONE = "stone"
    EMISSIVE = "emissive"

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
        pass
    
    def import_texture(self):
        pass
        
        
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
    
    def set_brightness(self, value):
        pass
        
    def set_day(self):
        pass
    
    def set_night(self):
        pass


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

root = tk.Tk()
my_gui = ProgramGUI(root)
root.mainloop()
