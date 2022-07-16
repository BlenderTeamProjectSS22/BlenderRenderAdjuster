
import tkinter as tk
from tkinter import Frame, Toplevel, Label, Button, Entry
from gui.properties import *
import os
from tkvideo import tkvideo
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
        
        
        dirname = os.path.dirname(__file__)
        parentdir = os.path.dirname(dirname)
        filename = os.path.join(parentdir, file1)
        #self.my_label = tk.Label(master)
        #self.my_label.pack()
        #self.player = tkvideo(filename, self.my_label, loop = 0, size = (852,480))
        #self.player.play()

        videoplayer = TkinterVideo(master=self.master, scaled=True)
        videoplayer.load(filename)
        videoplayer.set_size([852, 480])
        videoplayer.pack(fill=tk.BOTH, expand=1)
        videoplayer.play() # play the video

        

        
    def cancel(self, event=None):
        print("Closing window")
        self.close_window()
        
    def close_window(self):
        
        self.destroy()