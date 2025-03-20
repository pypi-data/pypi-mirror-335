import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

class Tools:
    def __init__(self, app):
        self.root = app.root
        self.app = app
        self.bg = app.bg
        self.fg = app.fg
        self.style = app.style
        self.font = ("Ubuntu", 11)
        self.size = app.resolution
        self.developer = app.developer
        
        try:
	        parts = self.size.split("x")
	        self.width = int(parts[0])
	        self.height = int(parts[1])
        except:
            if (self.developer):
                print("Failed to read the resolution, it may be wrong, fixing it is better!")
            self.width = 200
            self.height = 100

    def _clear_placeholder(self, event, entry, placeholder):
        if (entry.get() == placeholder):
            entry.delete(0, tk.END)
            entry.config(fg = self.fg)

    def _add_placeholder(self, event, entry, placeholder):
        if (not entry.get()):
            entry.insert(0, placeholder)
            entry.config(fg = "grey")

    def schedule(self, second, func):
        self.root.after(second * 1000, func)

    def pack(self, widget, pady = None, center = False, fill = False):
        if (pady is None):
            pady = 10
        if (center and fill):
            widget.pack(expand = True, fill = "both")
        elif (fill and not center):
            widget.pack(fill = "both")
        elif (center and not fill):
            widget.pack(expand = True)
        else:
            widget.pack(pady = pady)

    def place(self, widget, x = None, y = None):
        if (x is None):
            x = 0
        if (y is None):
            y = 0
        widget.place(x = x, y = y)

    def grid(self, widget, row, column, padx = 5, pady = 5):
        widget.grid(row = row, column = column, padx = padx, pady = pady)

    def hide(self, widget):
        widget.place_forget()

    def getData(self, widget):
        if isinstance(widget, tk.Entry):
            return widget.get()
        elif isinstance(widget, tk.Text):
            return widget.get('1.0', tk.END).strip()
        elif isinstance(widget, tk.Listbox):
            return widget.get(tk.ACTIVE)
        elif isinstance(widget, ttk.Combobox):
            return widget.get()
        else:
            raise TypeError("Unsupported widget type.")

# Components start from here!

    def Label(self, text, bg = None, fg = None, font = None, on = None):
        if (font is None):
            font = self.font
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        if (on is None):
            on = self.root
        return tk.Label(on, text = text, bg = bg, fg = fg, font = font)

    def Button(self, text, on_pressed, bg = None, fg = None, font = None, width = None, height = None, on = None):
        if (font is None):
            font = self.font
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        if (on is None):
            on = self.root
        return tk.Button(on, text = text, bg = bg, fg = fg, font = font, width = width, height = height, command = on_pressed)

    def Frame(self, bg = None, on = None):
        if (bg is None):
            bg = self.bg
        if (on is None):
            on = self.root
        return tk.Frame(on, bg = bg)

    def MessageBox(self, title = None, text = None, bg = None, fg = None, resolution = None, font = None, Okbg = None, Okfg = None, Okwidth = None, Okheight = None, on = None):
        if (title is None):
            title = "GladUI"
        if (text is None):
            text = "GladUI MessageBox!"
        if (resolution is None):
            resolution = "300x150"
        if (font is None):
            font = self.font
        if (Okbg is None):
            Okbg = "#222222"
        if (Okfg is None):
            Okfg = "white"
        if (Okwidth is None):
            Okwidth = 20
        if (Okheight is None):
            Okheight = 10
        if (on is None):
            on = self.root
        box = tk.Toplevel(on)
        box.title(title)
        box.geometry(resolution)
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        box.configure(bg = bg)
        label = tk.Label(box, text = text, bg = bg, fg = fg, font = font)
        label.pack(pady = 10)
        btn = tk.Button(box, text = "OK", command = box.destroy, bg = Okbg, fg = Okfg, padx = Okwidth, pady = Okheight)
        btn.pack(pady = 10)
        box.transient(self.root)
        box.grab_set()
        self.root.wait_window(box)

    def ProgressBar(self, max_value = None, mode = None, length = None, orientation = None, fg = None, bg = None, on = None):
        if (max_value is None):
            max_value = 100
        if (mode is None):
            mode = "determinate"
        if (length is None):
            length = 200
        if (orientation is None):
            orientation = "horizontal"
        if (fg is None):
            fg = "#00ff00"
        if (bg is None):
            bg = self.bg
        if (on is None):
            on = self.root
        style_name = "GladUI.Horizontal.TProgressbar"
        self.style.configure(style_name, troughcolor = bg, background = fg)
        return ttk.Progressbar(on, orient = orientation, length = length, mode = mode, style = style_name)

    def TextEdit(self, width = None, height = None, bg = None, font = None, scrollable = False, on = None):
        if (font is None):
            font = self.font
        if (bg is None):
            bg = self.bg
        if (on is None):
            on = self.root
        frame = tk.Frame(on)
        text_widget = tk.Text(frame, width = width, height = height, bg = bg, font = font)
        text_widget.pack(side = "left", fill = "both", expand = True)
        if (scrollable):
            scrollbar = tk.Scrollbar(frame, command = text_widget.yview)
            text_widget.config(yscrollcommand = scrollbar.set)
            scrollbar.pack(side = "right", fill = "y")
        return frame if scrollable else text_widget

    def ScrollEdit(self, width = None, height = None, bg = None, fg = None, font = None, on = None):
        if (font is None):
            font = self.font
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        if (on is None):
            on = self.root
        frame = tk.Frame(on)
        text_widget = tk.Text(frame, width = width, height = height, bg = bg, fg = fg, font = font)
        scrollbar = tk.Scrollbar(frame, command = text_widget.yview)
        text_widget.config(yscrollcommand = scrollbar.set)
        text_widget.pack(side = "left", fill = "both", expand = True)
        scrollbar.pack(side = "right", fill = "y")
        return frame

    def LineEdit(self, placeholder = None, bg = None, fg = None, font = None, on = None):
        if (placeholder is None):
            placeholder = ""
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        if (on is None):
            on = self.root
        entry = tk.Entry(on, bg = bg, fg = fg, font = font)
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda event: self._clear_placeholder(event, entry, placeholder))
        entry.bind("<FocusOut>", lambda event: self._add_placeholder(event, entry, placeholder))
        return entry

    def ComboBox(self, values, font = None, on = None):
        if (font is None):
            font = self.font
        if (on is None):
            on = self.root
        combo = ttk.Combobox(on, values = values, font = font)
        return combo

    def ListBox(self, items, font = None, on = None):
        if (font is None):
            font = self.font
        if (on is None):
            on = self.root
        listbox = tk.Listbox(on, font = font)
        for item in items:
            listbox.insert(tk.END, item)
        return listbox

    def CheckButton(self, text, font = None, bg = None, fg = None, on = None):
        if (font is None):
            font = self.font
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        if (on is None):
            on = self.root
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(on, text = text, variable = var, bg = bg, fg = fg, font = font)
        return checkbox, var

    def RadioButton(self, text, value, variable, font = None, bg = None, fg = None, on = None):
        if (font is None):
            font = self.font
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        if (on is None):
            on = self.root
        radio = tk.Radiobutton(on, text = text, value = value, variable = variable, bg = bg, fg = fg, font = font)
        return radio

    def Slider(self, from_ = None, to = None, orient = None, length = None, bg = None, fg = None, on = None):
        if (from_ is None):
            from_ = 0
        if (to is None):
            to = 100
        if (orient is None):
            orient = "horizontal"
        if (length is None):
            length = 200
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        if (on is None):
            on = self.root
        slider = tk.Scale(on, from_ = from_, to = to, orient = orient, length = length, bg = bg, fg = fg)
        return slider

    def SpinBox(self, from_ = None, to = None, font = None, bg = None, fg = None, on = None):
        if (from_ is None):
            from_ = 0
        if (to is None):
            to = 100
        if (font is None):
            font = self.font
        if (bg is None):
            bg = self.bg
        if (fg is None):
            fg = self.fg
        if (on is None):
            on = self.root
        spinbox = tk.Spinbox(on, from_ = from_, to = to, font = font, bg = bg, fg = fg)
        return spinbox

    def FileDialog(self, mode = None, filetype = None):
        if mode is None:
            mode = "open"
        if filetype is None:
            filetype = [("All Files", "*.*")]

        if (mode == "open"):
            return filedialog.askopenfilename(filetypes=filetype)
        elif (mode == "save"):
            return filedialog.asksaveasfilename(filetypes=filetype)
        elif (mode == "directory"):
            return filedialog.askdirectory()
        else:
            raise ValueError("Invalid mode. Use 'open', 'save', or 'directory'.")
        
    def Window(self, name = None, resolution = None, theme = None, on = None):
        if (on is None):
            on = self.root
        if (name is None):
            name = "GladUI window"
        if (resolution is None or resolution == "75%"):
            try:
                parts = self.size.split("x")
                x = int(int(parts[0])*0.75)
                y = int(int(parts[1])*0.75)
                resolution = f"{x}x{y}"
            except:
                if self.developer:
                    print("Failed to set the window resolution. Using the default resolution.")
                resolution = "240x120"
        elif (resolution == "50%"):
            try:
                parts = self.size.split("x")
                x = int(int(parts[0])*0.5)
                y = int(int(parts[1])*0.5)
                resolution = f"{x}x{y}"
            except:
                if self.developer:
                    print("Failed to set the window resolution. Using the default resolution.")
                resolution = "240x120"
        elif (resolution == "25%"):
            try:
                parts = self.size.split("x")
                x = int(int(parts[0])*0.2)
                y = int(int(parts[1])*0.2)
                resolution = f"{x}x{y}"
            except:
                if self.developer:
                    print("Failed to set the window resolution. Using the default resolution.")
                resolution = "240x120"
        if (theme is None or theme.lower() == "dark"):
            fg = "white"
            bg = "#222222"
        elif (theme.lower() == "light"):
            fg = "#222222"
            bg = "white"
        else:
            raise ThemeError("The theme only can be either 'light' or 'dark'.")

        window = tk.Toplevel(on)
        window.geometry(resolution)
        window.title(name)
        window.configure(bg = bg)
        return window
        
    def input_event_pressed(self, callback, on = None):
        if (on is None):
            on = self.root
            
        on.bind("<KeyPress>", lambda event: callback(event.keysym))

    def input_event_released(self, callback, on = None):
        if (on is None):
            on = self.root
            
        on.bind("<KeyRelease>", lambda event: callback(event.keysym))
    
    def Viewport(self, bg = None, resolution = None, to = None):
        if (bg is None):
            bg = "red"
        if (resolution is None):
            resolution = str(f"{self.width * 0.5}x{self.height * 0.5}")
        if (to is None):
           to = self.root
		
        parts = resolution.split("x")
        self.viewport_width = float(parts[0])
        self.viewport_height = float(parts[1])

        self.canvas = tk.Canvas(to, width = self.viewport_width, height = self.viewport_height, bg = bg)
        
        return self.canvas
    
# canvas widgets starts here!
    def rectangle(self, canvas, x1 = None, y1 = None, x2 = None, y2 = None, fill = None):
        if (fill is None):
            fill = "green"
        if (x1 is None):
            x1 = 100
        if (x2 is None):
            x2 = -100
        if (y1 is None):
            y1 = 50
        if (y2 is None):
            y2 = -50
            
        return canvas.create_rectangle(x1,y1,x2,y2, fill = fill)
