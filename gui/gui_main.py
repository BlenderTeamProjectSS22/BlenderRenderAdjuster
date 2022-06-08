# author: Alexander Ritter
# created on: 06/06/2022
# edited by:

# description:
# GUI element: Main program, renders the GUI and connects it to other function

import tkinter as tk
from tkinter import Frame, Label, Button, StringVar, Checkbutton, OptionMenu, Scale, Canvas
from tkinter import ttk
from tkinter.colorchooser import askcolor

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
        lbl_fileop = Label(master=self, text="File operations", font="Arial 10 bold")
        btn_import = Button(master=self, text="Import model")
        btn_export = Button(master=self, text="Export model")
        btn_render = Button(master=self, text="Save render")
        btn_video  = Button(master=self, text="Save video")
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
        btn_undo     = tk.Button(master=frame_ops, text="Undo")
        btn_redo     = tk.Button(master=frame_ops, text="Redo")
        btn_settings = tk.Button(master=frame_ops, text="Settings")
        btn_updates  = tk.Button(master=frame_ops, text="Check for updates")  # The update check may or may not be implemented
        btn_help     = tk.Button(master=frame_ops, text="Help")
        lbl_ops.pack(fill=tk.X)
        btn_undo.pack(fill=tk.X)
        btn_redo.pack(fill=tk.X)
        btn_settings.pack(fill=tk.X)
        btn_updates.pack(fill=tk.X)
        btn_help.pack(fill=tk.X)
        frame_ops.pack()
        

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
        check_vertc = Checkbutton(master=self, text="Vertex color", anchor="w")
        check_mesh  = Checkbutton(master=self, text="Full mesh", anchor="w")
        check_point = Checkbutton(master=self, text="Point cloud", anchor="w")
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

class MaterialWidgets(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, borderwidth=2, relief="groove")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        mat_selected = StringVar(master)
        mat_selected.set("default")
        lbl_materials = Label(master=self, text="Material selection", font="Arial 10 bold")
        lbl_sel_mat   = Label(master=self, text="Select:")
        dropdown_materials = OptionMenu(self, mat_selected, "default", "glass", "emissive", "stone")
        but_test = Button(master=self, text="Test")
        #TODO: material_picker = MaterialPicker(self)
        lbl_materials.grid(row=0, column=0, columnspan=2, sticky="we")
        lbl_sel_mat.grid(row=1, column=0, sticky="w")
        dropdown_materials.grid(row=1, column=1, sticky="w")


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
        btn_import_texture = Button(master=self, text="Import")
        lbl_sel_tex    = Label(master=self, text="Select:")
        dropdown_textures = OptionMenu(self, tex_selected, "none", "wood", "bricks")
        lbl_textures.grid(row=0, column=0, columnspan=2, sticky="we")
        btn_import_texture.grid(row=1, column=0, columnspan=2, sticky="")
        lbl_sel_tex.grid(row=2, column=0, sticky="w")
        dropdown_textures.grid(row=2, column=1, sticky="we")


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
        btn_day = Button(master=self, text="Day")
        btn_night = Button(master=self, text="Night")
        slider_brightness = ttk.Scale(master=self, orient='horizontal')
        lbl_light.grid(row=0, column=0, columnspan=2)
        lbl_brightness.grid(row=1, column=0, sticky="w")
        slider_brightness.grid(row=1, column=1,  sticky="we")
        btn_day.grid(row=2, column=0, sticky="we",pady=1)
        btn_night.grid(row=2, column=1, sticky="we",pady=1)


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
