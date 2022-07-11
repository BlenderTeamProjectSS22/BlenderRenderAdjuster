from tkinter import Entry, OptionMenu, Frame
from tkinter.ttk import Progressbar

# Enable/disable frame, recursively applied to all widgets contained in the frame
def frame_set_enabled(frame, is_enabled: bool):
    for widget in frame.winfo_children():
        #print(widget)
        if isinstance(widget, OptionMenu):
            widget_set_enabled(widget, is_enabled)
        elif widget.winfo_children():
            frame_set_enabled(widget, is_enabled)
        elif isinstance(widget, Progressbar):
            pass
        else:
            widget_set_enabled(widget, is_enabled)

# Enable/disable a single widget
def widget_set_enabled(widget, is_enabled: bool):
    state = "active" if is_enabled else "disabled"
    state_ent = "normal" if is_enabled else "readonly"
    if isinstance(widget, Entry):
        widget.configure(state=state_ent)
    else:
        widget.configure(state=state)