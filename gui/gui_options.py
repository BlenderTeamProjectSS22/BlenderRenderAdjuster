# author: Alexander Ritter
# created on: 08/06/2022
# edited by:

# description:
# GUI element: A seperate window for settings/options

import tkinter as tk
from tkinter import Frame, Toplevel, Label, Button
from PIL import ImageTk, Image

class SettingsWindow(Toplevel):
        def __init__(self, master):
            Toplevel.__init__(self)
            self.master = master
            self.title("Settings")
            
            self.focus_set()
            self.grab_set()
            
            body = Frame(self)
            self.initial_focus = self.body(body)
            body.grid(row=0, column=0, padx=5, pady=5)
            
            self.bind("<Escape>", self.cancel)
            self.wait_window(self)
        
        
        def body(self, master):
            # create dialog body.  return widget that should have
            # initial focus.  this method should be overridden
            lbl_settings = Label(master=master, text="Settings")
            btn_ok = Button(master=master, text="Ok", command=self.accept)
            btn_cancel = Button(master=master, text="Cancel", command=self.cancel)
            
            lbl_settings.grid(row=0, column=0, columnspan=2)
            btn_cancel.grid(row=1, column=0)
            btn_ok.grid(row=1, column=1)
            pass
        
        def accept(self, event=None):
            pass
        
        def cancel(self, event=None):
            self.master.focus_set()
            self.destroy()
            pass
            