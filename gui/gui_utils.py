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