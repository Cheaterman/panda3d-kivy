Panda3D-Kivy
============

A Panda3D add-on for Kivy integration.

The aim is to make the integration of Kivy apps into a Panda3D application
almost transparent.
Potential uses include creating on-screen GUI, or even RTT 3D UI's.


Usage:
======

First, import `panda3d_kivy.app.App` - make sure you do this before importing
any Kivy-related stuff:

```python
from panda3d_kivy.app import App
```

Then, as usual in Kivy, create a subclass of this App, and use build() or the
KV autoloading system to populate your widget tree:

```python
from kivy.uix.button import Button

class Example(App):
    def build(self):
        return Button(text='Hello, world!')
```

You can then instantiate and run this app inside the `__init__` of your Panda
`ShowBase`, after running `ShowBase.__init__(self)`. You may want to create a
display region for your kivy app, sized according to your needs, otherwise
`panda3d_kivy` will automatically create one for you that will occupy the
entire window. You must then pass your ShowBase as argument to the Kivy app
instantiation, as well as your display region if applicable, and finally call
`app.run()` as you normally would:

```python
from direct.showbase.ShowBase import ShowBase

class PandaApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.kivy_app = kivy_app = Example(self)
        kivy_app.run()

        # The rest of your ShowBase code here
```

Voilà! You should have a working Kivy UI in your Panda application. Have fun!
