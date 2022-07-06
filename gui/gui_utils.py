from tkinter import OptionMenu, Frame

# Two functions to enable/disable widgets
def widget_set_enabled(frame, is_enabled: bool):
    if is_enabled:
        for widget in frame.winfo_children():
            widget.configure(state="active")
    else:
        for widget in frame.winfo_children():
            #print(widget)
            if isinstance(widget, OptionMenu):
                widget.configure(state="disable")
            elif widget.winfo_children():
                widget_disable(widget)
            else:
                widget.configure(state="disable")