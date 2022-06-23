# author: Alexander Ritter
# created on: 08/06/2022
# edited by:

# description:
# GUI element: Display the image "preview.png" or a placeholder in a viewport

import tkinter as tk
from tkinter import Frame, Canvas
from PIL import ImageTk, Image

class RenderPreview(Frame):
        def __init__(self, master, control):
            Frame.__init__(self, master, bg="black")
            self.control = control
            
            # Load aspect ratio from settings
            self.w = control.settings.aspect.width
            self.h = control.settings.aspect.height
            
            self.canvas = tk.Canvas(self, width=self.w, height=self.h)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.bind("<Configure>", self.on_resize)
            self.original_image = Image.open("assets/gui/preview_unavailable.png")
            self.img = ImageTk.PhotoImage(self.original_image)
            self.canvas_img = self.canvas.create_image(0, 0, anchor="nw", image=self.img)
            
            self.reload()
        
        # Resize image keeping its aspect ratio 
        def resize(self, image, width, height):
            ratio = min(width / image.width, height / image.height)
            new_w = image.width * ratio
            new_h = image.height * ratio
            return image.resize((int(new_w), int(new_h)))
        
        # Automatically called when the canvas is resized
        def on_resize(self, event):
            resized = self.resize(self.original_image, event.width, event.height)
            self.img = ImageTk.PhotoImage(resized)
            self.canvas.itemconfig(self.canvas_img, image=self.img)
        
        # Preview is refreshed every second
        def reload(self):
            # TODO: Render the image with low resolution and settings
            # Resulting file must be called "preview.png"
            # Alternatively execute a render on each button change -> maybe better because render doesnt block updating
            try:
                self.original_image = Image.open("assets/gui/preview.png")
            except FileNotFoundError:
                self.original_image = Image.open("assets/gui/preview_unavailable.png")
            self.after(1000, self.reload)