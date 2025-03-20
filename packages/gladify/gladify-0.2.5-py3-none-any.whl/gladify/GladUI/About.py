ver = '0.2.5'
border = '------------------------------------------------------------'
code = '****************************'

def version():
	return f"GladUI v-{ver}\n\nEnter 'print(About.features())' to know the current version feaures.\nEnter 'print(About.Documentation())' to see the DOCUMENATION of GladUI."

def features():
	features = f'''
{border}
=========================    
GladUI v-0.2.2
=========================
What's NEW? :
 1) Added a new object as version to check the version of GladUI.
 2) New App(developer=True), for having developer options, so that if any problem is on the code of this library, it will be informed to you.\n    You can change it any time!.

{border}
========================
GladUI v-0.2.3
========================
What's NEW? :
 1) Many new usefull componets had added, like:
     1) Image()
         * You can now access Image() from tools, this helps you to add images to your app.
         * The things on Image() are:
             1) image [your image or it's path]
             2) width
             3) height
             4) bg
        * You can use Tools(app).pack() or Tools(app).place(), Tools(app).grid() for make it visible.
     2) Window() [MEGA ONE!]
        * You can access the Window() from tools.
        * This makes a new window on your app, like on desktop, you open an app, like that a new window.
        * The things on Window() are:
            1) name
            2) resolution [either you can set a resolution or you can set the value of it to:
                            1) "50%":
                                *This automatically set thee reolution to the 50% of your main app's resolution.
                            2) "25%"
                                *As like that 50%, but 25%of youmain app's resolution.
                            3) "75%" [default]
                                *As like all but 75% of your main app's resolution.
                          ]
            3) theme ["light" or "dark"]
    3) A new feature had came for all components, 'on = window()'
        * As per window() had came, youmay want to create a label inside it, noot on the app,
          at that case, you can use to = window, usage:
          
            import gladify.GladUI as GladUI

            app = GladUI.App(resolution = '840x480')
            tools = GladUI.Tools(app)

            second_screen = tools.Window(resolutin = "50%")

            label = tools.Label(text = "Hello, world!", to = second_screen)
            tools.pack(label, center = True)

            app.run()

         This code make a new window wit halfsize of the app's resoluion, which is '840x480',
         so that it's resolution will be '420x240'. A label is created inside this with text
         'Hello, world!'
        * As per the Window() had added, we can use 'x.destroy' to close a window bby command, where x = The variable name given to the window

{border}
========================
GladUI v-0.2.4
========================
Whats new? :
    1) New object as 'SoundPlayer()' for adding sounds to your app.
        HOW TO USE? :
            You can use SoundPlayer as like you adding tools.
            ~# code:
                import gladify.GladUI as GladUI
                app = GladUI.App()
                mixer = GladUI.SoundPlayer(app)
            The functions insode it are :
                1) play(path/to/sound)
                    The components inside play are:
                        1) sound = 'path' [str]
                        2) volume = volume [int[1-100]]
                2) stop()
                    This stops the playing sound.
                3) master_volume():
                    This is used to change the volume of the playing sound.
                    The components are:
                        volume = volume [int[1-100]]
                4) pause()
                    This pauses the current playing sound.
                5) resume()
                    This resume/unpause the sound if it is paused.
                6) mute()
                    This mutes the current playing sound.

{border}
========================
GladUI v-0.2.5
========================
Whats new?:
	1) New feature (on Tools) : 'input_event_pressed()' :
		*This you can use to detect the input any key is pressed.
		*eg usage:
~python
{code}

import gladify.GladUI as GladUI

app = GldUI.App()
tools = GladUI.Tool(app)

def handle(event): # making a function for handle the thing must happen while any key is pressed
	print(event)
	#we can also check which key is pressed and do what, like:
	if (event.lower() == "w" or event.lower() == "up"):
		print("Going UP!")
	elif (event.lower() == "a" or event.lower() == "left"):
		print("Going LEFT!")
	elif (event.lower() == "s" or event.lower() == "down"):
		print("Going DOWN!")
	elif (event.lower() == "d" or event.lower() == "right"):
		print("Going RIGHT!")

	#using .lower() can make it easier because the key's name be like, for up, it's Up, like that some special charaters are upper letters, so using .lower() and write all key name!
	#This code will prit() which key is pressing and if it is WASD ot UpDownRightLeft arrow key, it will also print 'Going diraction!'
	

tools.input_event_pressed(hande) #calls that handle fuction

app.run()

{code}
	2. NEW FEATURE (on tools) : 'input_event_released()' :
		* As like 'input_event_pressed', is detect key pressed, this detects key released

	3. NEW FEATURE (on tools) : 'Viewport()':
		* Use Viewport(bg, resolution, to)
		* Makes a canvas, very usefull for making games, that much not advanced, now just a canvas making.
		* You can use .pack(), .place(), like that functions as like you use for making widgets visible!
		* COMPONENTS NOWADED ARE:
			-> rectangle(the_canvas_setted_variable, x1, y1, x2, y2, fill = "color"), here x1 and y1 are the start point, x2 and y2 are end point.

			[curently there is only rectangle, mmore wil be added onthe upcomming updates!]
		* EG:
~python
{code}

import gladify.GladUI as GladUI

app = GladUI.App()
tools = GladUI.Tools(app)

canvas = tools.Viewport(resolution = "400x200") #creating a viewport named as canvas
tools.pack(canvas, center = True) #making the canvas visible at the center

rectangle = tools.rectangle(canvas) #makes a rectangle inside the canvas by default values (you can edit)

app.run()

{code}

{border}

'''
	return features

def Documentation():
    text = '''
=========================
GladUI Documentation
=========================

GladUI is a high-level GUI (Graphical User Interface) framework included in the Gladify package.  
It simplifies GUI development by providing an easy-to-use API for building applications.

Installation:
--------------
GladUI is part of Gladify. Install it using:

    pip install gladify

Importing the Library:
----------------------

You can import the library in two ways:

METHOD 1:
  
    from gladify.GladUI import App, Tools

    app = App()
    tools = Tools(app)  # Pass 'app' to Tools to connect it to the main window

METHOD 2:
  
    import gladify.GladUI as GladUI  # This imports the GladUI library from gladify

    app = GladUI.App()
    tools = GladUI.Tools(app)

Explanation:
- `App()` helps you create your app's root window, set the title, size, and more.
- `Tools(app)` allows you to add UI components like `Label`, `Button`, etc., and manage layouts.

--------------------------------------
1) Creating a Basic Application Window
--------------------------------------

Use the `App` class to create a basic application window.

Example:

    from gladify.GladUI import App

    app = App(name="My First GladUI App")
    app.run()

Explanation:
- The `App` class initializes a GUI window with a given title.
- The `run()` function starts the GUI event loop and displays the window.

--------------------------------------
2) Setting Developer Mode (Debugging)
--------------------------------------

Developer mode allows error messages to be displayed in the console.

Example:

    app = App(name="Debug Mode", developer=True)
    app.run()

--------------------------------------
3) Changing the Application Icon
--------------------------------------

You can set a custom icon for the application using the `icon` parameter.

Example:

    app = App(name="Icon Example", icon="path/to/icon.png")
    app.run()

--------------------------------------
4) Setting Window Resolution
--------------------------------------

The `resolution` parameter defines the width and height of the application window.

Example:

    app = App(name="Sized App", resolution="400x300")
    app.run()

--------------------------------------
5) Changing Theme
--------------------------------------

The `theme` parameter allows changing the theme of your app.

Example:

    app = App(name="Colored App", theme="light")
    app.run()
    
Note: The default theme is 'dark'. Available options: 'dark', 'light'.

--------------------------------------
6) Packing and Placing Widgets
--------------------------------------

All Tkinter functions like `.config()`, `.pack()`, `.place()` can be used.  
To simplify layout management, use `tools.pack()`, `tools.place()`, and `tools.grid()`.

Example:

    from gladify.GladUI import App, Tools

    app = App()
    tools = Tools(app)

    label = tools.Label("Hello, World!")
    tools.pack(label, center=True)

    app.run()

--------------------------------------
7) Running the Application
--------------------------------------

The `run()` function must be called to start the app.

Example:

    app = App()
    app.run()

--------------------------------------
8) Using UI Components
--------------------------------------

GladUI provides built-in components for UI design.

Example:

    button = tools.Button("Click Me", on_pressed=lambda: print("Button Clicked"))
    tools.pack(button, center=True)

    label = tools.Label("This is a Label")
    tools.pack(label)

    entry = tools.LineEdit(placeholder="Enter text here")
    tools.pack(entry)

    app.run()

--------------------------------------
9) More UI Components
--------------------------------------

- `tools.ComboBox(values=["Option1", "Option2"])` ? Dropdown menu.
- `tools.ListBox(items=["Item1", "Item2"])` ? Listbox.
- `tools.CheckButton("Check Me")` ? Checkbox.
- `tools.RadioButton("Option1", value=1, variable=var)` ? Radio button.
- `tools.ProgressBar(max_value=100, mode="determinate")` ? Progress bar.
- `tools.Slider(from_=0, to=100)` ? Slider.
- `tools.FileDialog(mode="open")` ? Open file dialog.

--------------------------------------
10) MessageBox
--------------------------------------

Show a message box with a title, text, and an OK button.

Example:

    tools.MessageBox(title="Info", text="This is a message!")

--------------------------------------
11) Scheduling Functions
--------------------------------------

Use `tools.schedule()` to run a function after a delay.

Example:

    def say_hello():
        print("Hello after 3 seconds!")

    tools.schedule(3, say_hello)

--------------------------------------
12) Getting Data from Inputs
--------------------------------------

Example:

    entry = tools.LineEdit(placeholder="Enter Name")
    tools.pack(entry)

    def show_data():
        print("Input:", tools.getData(entry))

    button = tools.Button("Submit", on_pressed=show_data)
    tools.pack(button)

    app.run()

--------------------------------------
13) Customizing Fonts
--------------------------------------

You can change font styles for UI components.

Example:

    label = tools.Label("Styled Text", font=("Arial", 16, "bold"))
    tools.pack(label)

--------------------------------------
14) Handling Key Press Events
--------------------------------------

Example:

    def key_pressed(event):
        print(f"Key Pressed: {event.keysym}")

    app.window.bind("<KeyPress>", key_pressed)
    app.run()

--------------------------------------
15) Creating a Frame
--------------------------------------

Use `Frame` to group multiple widgets.

Example:

    frame = tools.Frame()
    tools.pack(frame)

--------------------------------------
16) Creating a Scrollable Text Box
--------------------------------------

Example:

    text_box = tools.TextBox(height=5, width=40, scroll=True)
    tools.pack(text_box)

--------------------------------------
17) Creating a Status Bar
--------------------------------------

Example:

    status = tools.Label("Status: Ready")
    tools.pack(status, side="bottom", fill=True)

--------------------------------------
18) Creating a Custom Dialog
--------------------------------------

Example:

    def custom_dialog():
        tools.MessageBox(title="Alert", text="This is a custom dialog!")

    button = tools.Button("Show Dialog", on_pressed=custom_dialog)
    tools.pack(button)

--------------------------------------
19) FileDialog
--------------------------------------
-This will opens a file dialog for save a file from user or open a file from user to your app.

Components:
    1) tools.FileDialog(mode)
    mode : available :
            "open" : Opens a file from user.
            "save" : Saves a file from user.
            "directory" : Open a directory from user.
    2) tools.FileDialog(filetype[]) :
        Examble usage for open 'mp3' files:
        ~# code:
            import gladify.GladUI as GladUI

            app = GladUI.App()
            tools = GladUI.Tools(app)

            a = tools.FileDialog(mode = "open", filetype = ["Mp3 files", "*.mp3"]

--------------------------------------
20) Handling Errors
--------------------------------------

If an error occurs, check if:
- The correct parameter types are used.
- The functions are called properly.

=========================
End of Documentation
=========================
[The new features wll not be updated on this documentation, it is deeply explained on features() function.]
[Every new features will only explained on features()]
[If you need any fetures, sent a mail at 'gladgamingstudio@gmail.com']
=========================
'''
    return text
