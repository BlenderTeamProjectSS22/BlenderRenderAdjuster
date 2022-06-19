# author: Alexander Ritter
# created on: 10/06/2022
# edited by:

# description:
# Compiles the program to the directory 'dist/main/'. You can then run 'dist/main/main'.

# ---------------------------
# IMPORTANT:
# For this to work, you need to fully setup the development environment.
# Follow the guide on the wiki.
# https://github.com/garvita-tiwari/blender_render/wiki/Setup-of-development-environment
# ---------------------------

import subprocess
import platform

os = platform.system()
if os == "Windows":
    print("Compiling for Windows...")
    command = "pyinstaller --noconfirm main-windows.spec"
elif os == "Linux":
    print("Compiling for Linux...")
    command = "pyinstaller --noconfirm main-linux.spec"
else:
    print("You are running an unsupported operating system for building. (" + os + ")")
    exit()

process = subprocess.run(command, shell=True)