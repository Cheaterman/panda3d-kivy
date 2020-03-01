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

You can then instanciate and run this app inside the `__init__` of your Panda
`ShowBase`, after running `ShowBase.__init__(self)`. You will need to create a
display region for your kivy app, sized according to your needs. You must then
pass it as well as your showbase as arguments to the kivy app instanciation,
and finally call `app.run()` as you normally would:

```python
from direct.showbase.ShowBase import ShowBase

class PandaApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Full screen display region, adjust as needed
        display_region = self.win.make_display_region(0, 1, 0, 1)

        self.kivy_app = kivy_app = Example(
            display_region,
            panda_app=self,
        )
        kivy_app.run()

        # The rest of your ShowBase code here
```

Voilà! You should have a working Kivy UI in your Panda application. Have fun!
