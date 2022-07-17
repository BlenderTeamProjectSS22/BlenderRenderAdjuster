import tkinter as tk
import sys
import getopt
import argparse
import logging
from gui.gui_main import ProgramGUI
import gui.properties as props

try:
    import bpy
except:
    print("Failed to import bpy")
    exit()
else:
    print("Successfully imported bpy!")

verbose_help = "Enables detailed render logging from blender"
debug_help   = "Debug mode, loads default value and creates additional sliders"

parser = argparse.ArgumentParser(description="Program description")
parser.add_argument("--verbose", dest="verbose", action="store_true", help=verbose_help)
# DO NOT call this "--debug", because blender will recognize it then as an argument
parser.add_argument("--debugging", dest="debug", action="store_true", help=debug_help)

args = parser.parse_args()
if args.debug:
    print("Debug mode enabled")
    props.DEBUG = True
if args.verbose:
   props.VERBOSE = True

root = tk.Tk()
my_gui = ProgramGUI(root)
my_gui.pack(fill=tk.BOTH)
root.mainloop()