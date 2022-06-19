import tkinter as tk
from gui.gui_main import ProgramGUI

try:
    import bpy
except:
    print("Failed to import bpy")
    exit()
else:
    print("Successfully imported bpy!")

root = tk.Tk()
my_gui = ProgramGUI(root)
root.mainloop()