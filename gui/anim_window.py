
import tkinter as tk
from tkinter import Frame, Toplevel, Label, Button, Entry
from gui.properties import *
import os
from tkVideoPlayer import TkinterVideo


class PreviewWindow(Toplevel):
        def __init__(self, master, control, file1: str):
            Toplevel.__init__(self)
            self.master = master
            self.control = control
            self.title("Animation Preview")
            self.focus_set()
            self.grab_set()
            self.geometry("852x480")
            
            self.content = PreviewContent(self, control, file1)
            self.initial_focus = self.content
            self.content.pack()
            
            self.bind("<Escape>", self.content.cancel)
            self.wait_window(self)
            
class PreviewContent(Frame):
    def __init__(self, master, control, file1: str):
        Frame.__init__(self, master)
        self.master = master
        self.control = control
        
        # get the video file path
        dirname = os.path.dirname(__file__)
        parentdir = os.path.dirname(dirname)
        assetdir = os.path.join(parentdir, "assets")
        animdir = os.path.join(assetdir, "animation_presets")
        filename = os.path.join(animdir, file1)

        # setup video player and start playing
        self.videoplayer = TkinterVideo(master=self.master, scaled=True)
        self.videoplayer.load(filename)
        self.videoplayer.set_size([852, 480])
        self.videoplayer.pack(fill=tk.BOTH, expand=1)
        self.videoplayer.play() # play the video
        self.videoplayer.bind("<<Ended>>", self.vid_ended)

    # close the window when the video is finished
    def vid_ended(self, event):
        self.videoplayer.stop()
        self.close_window()

    def cancel(self, event=None):
        print("Closing window")
        self.close_window()
        
    def close_window(self):
        self.destroy()
        self.master.destroy()