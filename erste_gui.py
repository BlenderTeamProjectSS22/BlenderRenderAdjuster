import tkinter as tk

width = 400
height = 200
# creating window
window = tk.Tk()

# title
window.title("Das Blender Projekt")

# Größenangabe
window.geometry("1000x500")
window.minsize(width, height)

# starting gui
window.mainloop()
