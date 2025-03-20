import tkinter as tk
from tkinter import ttk, PhotoImage
import os
import shutil

class App:
    def __init__(self, name = None, resolution = None, theme = None, icon = None, developer = False):
        self.root = tk.Tk()
        if (name is None):
            name = "GladUI"
        if (resolution is not None):
            self.root.geometry(resolution)
        if (theme is None):
            theme = "dark"

        if (theme.lower() == "dark"):
            self.bg = "#222222"
            self.fg = "white"
        elif theme.lower() == "light":
            self.bg = "white"
            self.fg = "black"
        else:
            raise ValueError("Invalid theme. Valid themes are: 'light', 'dark'")

        self.root.title(name)
        self.root.configure(bg=self.bg)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.resolution = resolution
        self.developer = developer

        hidden_folder = os.path.expanduser("~/.GladUI/images/")
        os.makedirs(hidden_folder, exist_ok=True)

        default_icon_path = os.path.join(hidden_folder, "GladUI.png")

        if icon is None:
            if not os.path.exists(default_icon_path):
                try:
                    package_icon_path = os.path.join(os.path.dirname(__file__), "GladUI.png")
                    if os.path.exists(package_icon_path):
                        shutil.copy(package_icon_path, default_icon_path)
                    else:
                        if developer:
                            print("Warning: Default icon 'GladUI.png' not found in package.")
                except Exception as e:
                    if developer:
                        print(f"Error copying default icon: {e}")

            if os.path.exists(default_icon_path):
                try:
                    default_icon = PhotoImage(file=default_icon_path)
                    self.root.iconphoto(True, default_icon)
                except Exception as e:
                    if developer:
                        print(f"Failed to load default icon: {e}")
        else:
            try:
                custom_icon = PhotoImage(file=icon)
                self.root.iconphoto(True, custom_icon)
            except Exception as e:
                if developer:
                    print(f"Error: Failed to load custom icon '{icon}'. {e}")
                    
        if (self.developer):
            print("GladUI v0.2.4 from gladify.\nUse object About for more information, the functions of About are:\n*Documentation()\n*version()\n*features()\n")
            
    def run(self):
        self.root.mainloop()
