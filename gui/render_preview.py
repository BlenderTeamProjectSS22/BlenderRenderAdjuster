# author: Alexander Ritter
# created on: 08/06/2022
# edited by:

# description:
# GUI element: Display the image "preview.png" or a placeholder in a viewport

import tkinter as tk
from tkinter import Frame, Canvas
from PIL import ImageTk, Image
from gui.properties import *

class RenderPreview(Frame):
        def __init__(self, master):
            Frame.__init__(self, master, bg="black")
            
            self.original_image = Image.open("assets/gui/preview_unavailable.png")
            self.img = ImageTk.PhotoImage(self.original_image)
            
            self.w = self.original_image.width
            self.h = self.original_image.height
            
            self.canvas = tk.Canvas(self, width=self.w, height=self.h)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.bind("<Configure>", self.on_resize)
            self.canvas_img = self.canvas.create_image(0, 0, anchor="nw", image=self.img)
            
            self.reload()
        
        # Resize the image to given width/height
        def resize(self, image, width, height):
        
            ratio = min(width / image.width, height / image.height)
            new_w = image.width * ratio
            new_h = image.height * ratio
            
            resized = image.resize((int(new_w), int(new_h)))
            self.img = ImageTk.PhotoImage(resized)
            self.canvas.itemconfig(self.canvas_img, image=self.img)
        
        # Automatically called when the canvas is resized
        def on_resize(self, event):
            self.w = event.width
            self.h = event.height
            self.resize(self.original_image, self.w, self.h)
        
        # Preview is refreshed when called
        def reload(self):
            try:
                self.original_image = Image.open("assets/gui/preview.png")
            except FileNotFoundError:
                self.original_image = Image.open("assets/gui/preview_unavailable.png")
            self.resize(self.original_image, self.w, self.h)