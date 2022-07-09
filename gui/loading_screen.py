import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import Frame, Toplevel, Label, Button, Entry

import sys
import os

class LoadingScreen(tk.Toplevel):
    def __init__(self, master, frame_max: int):
            Toplevel.__init__(self)
            self.master = master
            self.title("Rendering video")
            self.resizable(width=False, height=False)
            self.finished = False
            self.protocol("WM_DELETE_WINDOW", self.prevent_close)
            
            self.LENGTH = 1000
            self.FRAME_MAX = frame_max
            self.DELTA  = self.LENGTH / self.FRAME_MAX
            print(self.DELTA)
            
            self.focus_set()
            self.grab_set()
            
            self.content = LoadingContent(self)
            self.initial_focus = self.content
            self.content.grid(row=0, column=0, padx=5, pady=5)
            
            self.center(self)
    
    # Centering is not as easy as you might think,
    # thanks for the code from https://stackoverflow.com/a/10018670h
    def center(self, win):
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
    
    def set_frame(self, frame):
        print("Setting loading screen frame to " + str(frame - 1))
        self.content.lbl_frames_to_do["text"] = f"Rendering frame {frame - 1} / {self.FRAME_MAX}"
        self.content.pg["value"] = frame - 1
        self.update()
    
    def render_finished(self):
        self.finished = True
    
    def prevent_close(self):
        if self.finished:
            self.close_window()
    
class LoadingContent(tk.Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        
        lbl_title = Label(self, text="Video render progress", font="Arial 15 bold")
        self.pg = Progressbar(
            master=self,
            orient=tk.HORIZONTAL,
            mode="determinate",
            length=master.LENGTH,
            maximum=master.FRAME_MAX)
        self.lbl_frames_to_do = Label(master=self, text="Rendering frame 0 / " + str(master.FRAME_MAX))
        
        lbl_title.grid(row=0, column=0, pady=10)
        self.lbl_frames_to_do.grid(row=1, column=0, pady=5)
        self.pg.grid(row=2, column=0, pady=5, padx=5)
    
    def show(self):
        width = self.pg.winfo_width()
        print(width)