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

def validate_integer(input: str):
        # TODO This prevents deleting e.g. '5', because field can't be empty
        # Implement that it sets it to 0 automatically if last digit is deleted
        if str.isdigit(input) or input == "":
            return True
        else:
            return False

# Validates positive floats with two decimal places
def validate_float(input: str):
    if input == "":
        return True
    try:
        f = float(input.replace(",", "."))
    except:
        return False
    
    if f < 0:
        return False
    
    before_after_comma = input.replace(",", ".").split(".")
    if len(before_after_comma) == 2 and len(before_after_comma[1]) > 2:
        return False
        
    return True
