from tkinter import OptionMenu, Frame

# Enable/disable frame, recursively applied to all widgets contained in the frame
def frame_set_enabled(frame, is_enabled: bool):
    for widget in frame.winfo_children():
        #print(widget)
        if isinstance(widget, OptionMenu):
            widget_set_enabled(widget, is_enabled)
        elif widget.winfo_children():
            frame_set_enabled(widget, is_enabled)
        else:
            widget_set_enabled(widget, is_enabled)

# Enable/disable a single widget
def widget_set_enabled(widget, is_enabled: bool):
    state = "active" if is_enabled else "disabled"
    widget.configure(state=state)