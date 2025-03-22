import tkinter as tk
from tkinter import ttk

class Settings(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("400x200")
        #Settings

        #Speed
        self.settings = {
            "speed": tk.IntVar(value=50)
        }
    
        ttk.Label(self, text="Enter speed (1-100):").pack(pady=5)
        self.speed_entry = ttk.Entry(self, textvariable=self.settings["speed"])
        self.speed_entry.pack()

        #Color
        self.color_settings = {
            "color" : tk.StringVar(value = "yellow")
        }

        ttk.Label(self, text="Enter a color. Incorrect colors will be randomized!").pack(pady=10)
        self.color_entry = ttk.Entry(self, textvariable = self.color_settings["color"])
        self.color_entry.pack()

        # button
        self.start_button = tk.Button(self, text="Start", command=self.apply_settings, bg="lightgray", fg="black")
        self.start_button.pack(pady=15)

        

    def apply_settings(self):
        # this should be better
        for key in self.settings:
            self.master.settings[key] = self.settings[key].get()
        for key in self.color_settings:
            self.master.color_settings[key] = self.color_settings[key].get()
        self.destroy()