# author: Alexander Ritter
# created on: 08/06/2022
# edited by:

# description:
# GUI element: Display the image "preview.png" or a placeholder in a viewport

import tkinter as tk
from tkinter import Frame, Canvas
from PIL import ImageTk, Image

class RenderPreview(Frame):
        def __init__(self, master):
            Frame.__init__(self, master, bg="black")
            
            self.w = int(1920 / 4)
            self.h = int(1080 / 4)
            self.canvas = tk.Canvas(self, width=self.w, height=self.h)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.bind("<Configure>", self.conf)
            self.image = Image.open("../assets/gui/preview_unavailable.png")
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
                self.image = Image.open("../assets/gui/preview.png")
            except FileNotFoundError:
                self.image = Image.open("../assets/gui/preview_unavailable.png")
            self.resize(self.w, self.h)
            self.after(1000, self.reload)