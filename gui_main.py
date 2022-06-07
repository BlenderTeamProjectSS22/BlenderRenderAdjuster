import tkinter as tk
from tkinter import Frame, Label, Button, StringVar, Checkbutton, OptionMenu, Scale, Canvas
from tkinter import ttk
from tkinter.colorchooser import askcolor
from PIL import ImageTk, Image

class ProgramGUI:
    def __init__(self, master):
        master.title("Render adjuster")
        root.minsize(107+184+480,307)
        master.iconbitmap("images/icon.ico")
        
        right = RightPanel(master)
        left  = LeftPanel(master)
        preview = RenderPreview(master)
        preview.grid(row=0, column=1, sticky="nwes")
        camcontrols = CameraControls(master)
        camcontrols.grid(row=1, column=1)
        master.columnconfigure(0, weight=0, minsize=107)
        master.columnconfigure(1, weight=16)
        master.columnconfigure(2, weight=0, minsize=184)
        master.rowconfigure(0, weight=9, minsize=307)
        left.grid(row=0, column=0, sticky="nw")
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
        frame_look  = Frame(master=self, borderwidth=2, relief="groove")
        lbl_look    = Label(master=frame_look, text="Look", font="Arial 10 bold")
        lbl_color   = Label(master=frame_look, text="Color")
        btn_picker  = Button(master=frame_look, text="pick", command=self.pick_color)
        lbl_type    = Label(master=frame_look, text="Type")
        check_vertc = Checkbutton(master=frame_look, text="Vertex color", anchor="w")
        check_mesh  = Checkbutton(master=frame_look, text="Full mesh", anchor="w")
        check_point = Checkbutton(master=frame_look, text="Point cloud", anchor="w")
        lbl_look.grid(row=0, column=0, columnspan=2)
        lbl_color.grid(row=1, column=0)
        lbl_type.grid(row=1, column=1)
        btn_picker.grid(row=2, column=0)
        check_vertc.grid(row=3, column=0, sticky="w")
        check_mesh.grid(row=2, column=1, sticky="w")
        check_point.grid(row=3, column=1, sticky="w")
        frame_look.grid(row=0, column=0, sticky="we")
        
        # Material widgets
        frame_mat = Frame(master=self, borderwidth=2, relief="groove")
        frame_mat.columnconfigure(0, weight=1)
        frame_mat.columnconfigure(0, weight=1)
        frame_mat.rowconfigure(1, weight=1)
        mat_selected = StringVar(master)
        mat_selected.set("default")
        lbl_materials = Label(master=frame_mat, text="Material selection", font="Arial 10 bold")
        lbl_sel_mat   = Label(master=frame_mat, text="Select:")
        dropdown_materials = OptionMenu(frame_mat, mat_selected, "default", "glass", "emissive", "stone")
        but_test = Button(master=frame_mat, text="Test")
        #TODO: material_picker = MaterialPicker(self)
        lbl_materials.grid(row=0, column=0, columnspan=2, sticky="we")
        lbl_sel_mat.grid(row=1, column=0, sticky="w")
        dropdown_materials.grid(row=1, column=1, sticky="w")
        frame_mat.grid(row=1, column=0, sticky="ew")
        
        
        # Texture widgets
        frame_tex = Frame(master=self, borderwidth=2, relief="groove")
        frame_tex.columnconfigure(0, weight=1)
        frame_tex.columnconfigure(1, weight=1)
        frame_tex.rowconfigure(0, weight=1)
        frame_tex.rowconfigure(1, weight=1)
        frame_tex.rowconfigure(2, weight=1)
        tex_selected = StringVar(master)
        tex_selected.set("none")
        lbl_textures = Label(master=frame_tex, text="Texture selection:", font="Arial 10 bold")
        btn_import_texture = Button(master=frame_tex, text="Import")
        lbl_sel_tex    = Label(master=frame_tex, text="Select:")
        dropdown_textures = OptionMenu(frame_tex, tex_selected, "none", "wood", "bricks")
        lbl_textures.grid(row=0, column=0, columnspan=2, sticky="we")
        btn_import_texture.grid(row=1, column=0, columnspan=2, sticky="")
        lbl_sel_tex.grid(row=2, column=0, sticky="w")
        dropdown_textures.grid(row=2, column=1, sticky="we")
        frame_tex.grid(row=2, column=0, sticky="ew")
        
        # Lighting widgets
        frame_lighting = Frame(master=self, borderwidth=2, relief="groove")
        frame_lighting.columnconfigure(0, weight=1)
        frame_lighting.columnconfigure(1, weight=1)
        frame_tex.rowconfigure(0, weight=1)
        frame_tex.rowconfigure(1, weight=1)
        frame_tex.rowconfigure(2, weight=1)
        lbl_light = Label(master=frame_lighting, text="Lighting", font="Arial 10 bold")
        lbl_brightness = Label(master=frame_lighting, text="Brightness")
        btn_day = Button(master=frame_lighting, text="Day")
        btn_night = Button(master=frame_lighting, text="Night")
        slider_brightness = ttk.Scale(master=frame_lighting, orient='horizontal')
        lbl_light.grid(row=0, column=0, columnspan=2)
        lbl_brightness.grid(row=1, column=0, sticky="w")
        slider_brightness.grid(row=1, column=1,  sticky="we")
        btn_day.grid(row=2, column=0, sticky="we",pady=1)
        btn_night.grid(row=2, column=1, sticky="we",pady=1)
        
        frame_lighting.grid(row=3, column=0, sticky="we")
    
       
    def pick_color(self):
        self.current_color = askcolor(self.current_color)[0]
        print(self.current_color)
        

class RenderPreview(Frame):
        def __init__(self, master):
            Frame.__init__(self, master, bg="black")
            
            self.w = int(1920 / 4)
            self.h = int(1080 / 4)
            self.canvas = tk.Canvas(self, width=self.w, height=self.h)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.bind("<Configure>", self.conf)
            self.image = Image.open("images/preview_unavailable.png")
            self.img = ImageTk.PhotoImage(self.image)
            self.canvas_img = self.canvas.create_image(0, 0, anchor="nw", image=self.img)
            
            self.reload()
        
        # This function runs when the window is resized
        def conf(self, event):
            self.w = event.width
            self.h = event.height
            self.resize(event.width, event.height)
        
        # Resizes the image to width and height
        def resize(self, width, height):
            resized = self.image.resize((width,height))
            self.img = ImageTk.PhotoImage(resized)
            self.canvas.itemconfig(self.canvas_img, image=self.img)
        
        # Preview is refreshed every second
        def reload(self):
            # TODO: Render the image with low resolution and settings
            # Resulting file must be called "preview.png"
            # Alternatively execute a render on each button change -> maybe better because render doesnt block updating
            try:
                self.image = Image.open("images/preview.png")
            except FileNotFoundError:
                self.image = Image.open("images/preview_unavailable.png")
            self.resize(self.w, self.h)
            self.after(1000, self.reload)
        
root = tk.Tk()
my_gui = ProgramGUI(root)
root.mainloop()