import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import Frame, Toplevel, Label, Button, Entry, Checkbutton, BooleanVar
from gui.gui_utils import frame_set_enabled
import utils

import threading
import sys
import os

class VideoLoadingScreen(tk.Toplevel):
    def __init__(self, master, control, filepath):
            Toplevel.__init__(self)
            self.master  = master
            self.control = control
            self.filepath = filepath
            
            self.title("Rendering video")
            self.resizable(width=False, height=False)
            self.finished = True
            self.protocol("WM_DELETE_WINDOW", self.prevent_close)
            
            self.LENGTH = 1000
            self.FRAME_MAX = self.control.frames.get_max_frame()
            self.DELTA  = self.LENGTH / self.FRAME_MAX
            
            self.content = Frame(self)
            lbl_title = Label(master=self.content, text="Video render progress", font="Arial 15 bold")
            self.btn_start = Button(master=self.content, text="Start rendering", command=self.start_render)
            self.previewrender = BooleanVar()
            check_preview = Checkbutton(master=self.content, variable = self.previewrender, text="Only render preview (low quality, but faster)")
            self.pg = Progressbar(
                master=self.content,
                orient=tk.HORIZONTAL,
                mode="determinate",
                length=self.LENGTH,
                maximum=self.FRAME_MAX)
            self.lbl_current_frame = Label(master=self.content, text="Rendering frame 0 / " + str(self.FRAME_MAX))
        
            lbl_title.grid(row=0, column=0, pady=10)
            check_preview.grid(row=1, column=0, pady=5)
            self.btn_start.grid(row=2, column=0, pady=5)
            self.lbl_current_frame.grid(row=3, column=0, pady=5)
            self.pg.grid(row=4, column=0, pady=5, padx=5)
            self.content.grid(row=0, column=0, padx=5, pady=5)
            
            self.focus_set()
            self.grab_set()
            center(self)
            self.update()
    
    def start_render(self):
        frame_set_enabled(self.content, False)
        self.current_frame = 1
        self.finished = False
        
        def render_per_frame(scene):
            self.set_frame(self.current_frame)
            self.update_idletasks()
            self.current_frame = self.current_frame + 1
        
        def render_finished(scene):
            self.finished = True
            utils.unregister_handler(render_per_frame, utils.Handler.PER_FRAME)
            utils.unregister_handler(render_finished,  utils.Handler.FINISHED)
            frame_set_enabled(self.content, True)
            self.close_window()
        
        utils.register_handler(render_per_frame, utils.Handler.PER_FRAME)
        utils.register_handler(render_finished, utils.Handler.FINISHED)
        
        def render_anim():
            if self.previewrender.get():
                self.control.renderer.set_preview_render(file_path=self.filepath)
            else:
                self.control.renderer.set_final_render(self.filepath)
            self.control.renderer.render(animation=True)
            self.control.renderer.set_preview_render()
        
        renderthread = threading.Thread(target=render_anim)
        renderthread.start()
    
    def set_frame(self, frame):
        #print("Setting loading screen frame to " + str(frame))
        self.lbl_current_frame["text"] = f"Rendering frame {frame} / {self.FRAME_MAX}"
        self.pg["value"] = frame
        self.update()
    
    def prevent_close(self):
        if self.finished:
            self.close_window()
    
    def close_window(self):
        self.master.focus_set()
        self.destroy()

class ImageLoadingScreen(tk.Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title("Rendering image")
        self.resizable(width=False, height=False)
        self.finished = False
        self.protocol("WM_DELETE_WINDOW", self.prevent_close)
        
        content = Frame(master=self)
        self.initial_focus = content
        lbl_title = Label(master=content, text="Rendering image...", font="Arial 15 bold")
        pg = Progressbar(
            master=content,
            orient=tk.HORIZONTAL,
            mode="indeterminate",
            length=200,
            maximum=1000)
        pg.start(1)
        
        lbl_title.grid(row=0, column=0, pady=10)
        pg.grid(row=1, column=0)
        content.grid(row=0, column=0, padx=5, pady=5)
        
        self.focus_set()
        self.grab_set()
        center(self)
        self.update()
        
    def prevent_close(self):
        if self.finished:
            self.close_window()
    
    def close_window(self):
        self.master.focus_set()
        self.destroy()


# Centering is not as easy as you might think,
# thanks for the code from https://stackoverflow.com/a/10018670h
def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()