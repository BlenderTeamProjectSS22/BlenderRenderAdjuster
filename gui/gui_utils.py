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

def validate_integer(input: string):
        # TODO This prevents deleting e.g. '5', because field can't be empty
        # Implement that it sets it to 0 automatically if last digit is deleted
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

# Validates positive floats
def validate_float(input: string):
    if input == "":
        return True
    try:
        float(input.replace(',', '.'))
    except:
        return False
    return True