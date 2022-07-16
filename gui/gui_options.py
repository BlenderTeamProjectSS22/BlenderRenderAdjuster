# author: Alexander Ritter
# created on: 08/06/2022
# edited by:

# description:
# GUI element: A seperate window for settings/options

import tkinter as tk
from tkinter import Frame, Toplevel, Label, Button, Entry
from gui.properties import *
from gui.gui_utils import validate_integer, validate_float

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
            self.resizable(False, False)
            self.wait_window(self)
            
class SettingsContent(Frame):
    def __init__(self, master, control):
        Frame.__init__(self, master)
        self.master = master
        self.control = control
        validate_int = self.register(validate_integer)
        
        frm_aspect = Frame(master=self)
        lbl_aspect = Label(master=self, text="Aspect ratio of rendered image")
        lbl_colon  = Label(master=frm_aspect, text=" : ")
        self.ent_width  = Entry(master=frm_aspect, width=5, fg="gray", validate="key", validatecommand=(validate_int, '%P'))
        self.ent_height = Entry(master=frm_aspect, width=5, fg="gray", validate="key", validatecommand=(validate_int, '%P'))
        self.ent_width.pack(side=tk.LEFT)
        lbl_colon.pack(side=tk.LEFT)
        self.ent_height.pack(side=tk.LEFT)
        
        lbl_limit = Label(master=self, text="Time limit for preview render")
        self.ent_limit = Entry(master=self, fg="gray", width=10, validate="key", validatecommand=(self.register(validate_float), '%P'))
        
        lbl_settings = Label(master=self, text="Settings", font="Arial 10 bold")
        btn_ok = Button(master=self, text="Ok", command=self.accept)
        btn_cancel = Button(master=self, text="Cancel", command=self.cancel)
        
        # Insert default values for the entries from settings
        self.ent_width.insert(tk.END, str(self.control.settings.aspect.width))
        self.ent_height.insert(tk.END, str(self.control.settings.aspect.height))
        self.ent_limit.insert(tk.END, "{:.2f}".format(self.control.settings.timelimit))
        
        self.ent_width.bind("<FocusIn>", lambda event: event.widget.config(fg="black"))
        self.ent_height.bind("<FocusIn>", lambda event: event.widget.config(fg="black"))
        self.ent_limit.bind("<FocusIn>", lambda event: event.widget.config(fg="black"))
        self.ent_width.bind("<FocusOut>", lambda event: self.on_entry_leave(event, self.control.settings.aspect.width))
        self.ent_height.bind("<FocusOut>", lambda event: self.on_entry_leave(event, self.control.settings.aspect.height))
        self.ent_limit.bind("<FocusOut>", lambda event: self.on_entry_leave(event, self.control.settings.timelimit))
        
        self.columnconfigure(1, weight=1)
        lbl_settings.grid(row=0, column=0, columnspan=2)
        lbl_aspect.grid(row=1, column=0, sticky="w")
        frm_aspect.grid(row=1, column=1, pady=5, padx=5)
        lbl_limit.grid(row=2, column=0, sticky="w")
        self.ent_limit.grid(row=2, column=1, sticky="we", pady=5, padx=5)
        btn_cancel.grid(row=3, column=0)
        btn_ok.grid(row=3, column=1)
    
    def on_entry_leave(self, event, default):
        if event.widget.get() == "" :
            event.widget.config(fg="gray")
            if isinstance(default, float):
                event.widget.insert(tk.END, "{:.2f}".format(default))
            else:
                event.widget.insert(tk.END, str(default))
        else:
            limit = float(event.widget.get().replace(",", "."))
            if limit == default:
                event.widget.config(fg="gray")
        
    def accept(self):
    
        if self.ent_width.get() != "" and self.ent_height.get() != "":
            w = int(self.ent_width.get())
            h = int(self.ent_height.get())
            self.control.settings.set_aspect_ratio(w, h)
        
        if self.ent_limit.get() != "":
            limit = float(self.ent_limit.get().replace(",", "."))
            self.control.settings.set_time_limit(limit)
        
        self.control.save_settings(self.control.settings)
        self.control.re_render()
        self.close_window()
        print("New settings: " + str(self.control.settings))
        
    def cancel(self, event=None):
        print("Closing settings window")
        self.close_window()
        
    def close_window(self):
        self.master.focus_set()
        self.master.destroy()