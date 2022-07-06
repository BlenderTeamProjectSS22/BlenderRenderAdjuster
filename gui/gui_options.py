# author: Alexander Ritter
# created on: 08/06/2022
# edited by:

# description:
# GUI element: A seperate window for settings/options

import tkinter as tk
from tkinter import Frame, Toplevel, Label, Button, Entry
from PIL import ImageTk, Image
from gui.properties import *

class SettingsWindow(Toplevel):
        def __init__(self, master, control):
            Toplevel.__init__(self)
            self.master = master
            self.control = control
            self.title("Settings")
            
            self.focus_set()
            self.grab_set()
            
            self.content = SettingsContent(self, control)
            self.initial_focus = self.content
            self.content.grid(row=0, column=0, padx=5, pady=5)
            
            self.bind("<Escape>", self.content.cancel)
            self.wait_window(self)
            
class SettingsContent(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master)
        self.master = master
        self.control = control
        
        lbl_aspect = Label(master=self, text="Aspect ratio")
        self.ent_width  = Entry(master=self)
        self.ent_height = Entry(master=self)
        
        lbl_limit = Label(master=self, text="Time limit")
        self.ent_limit = Entry(master=self)
        
        lbl_settings = Label(master=self, text="Settings")
        btn_ok = Button(master=self, text="Ok", command=self.accept)
        btn_cancel = Button(master=self, text="Cancel", command=self.cancel)
            
        lbl_settings.grid(row=0, column=0, columnspan=2)
        lbl_aspect.grid(row=1, column=0)
        self.ent_width.grid(row=1, column=1)
        self.ent_height.grid(row=1, column=2)
        lbl_limit.grid(row=2, column=0)
        self.ent_limit.grid(row=2, column=1)
        btn_cancel.grid(row=3, column=1)
        btn_ok.grid(row=3, column=2)
        
    def accept(self):
        w = int(self.ent_width.get())
        h = int(self.ent_height.get())
        limit = int(self.ent_limit.get())
        self.control.settings.set_aspect_ratio(w, h)
        self.control.settings.set_time_limit(limit)
        self.control.save_settings(self.control.settings)
        self.control.re_render()
        self.close_window()
        print("New settings: " + str(self.control.settings))
        
    def cancel(self, event=None):
        print("Closing window")
        self.close_window()
        
    def close_window(self):
        self.master.focus_set()
        self.master.destroy()