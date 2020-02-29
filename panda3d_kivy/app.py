# XXX: Make sure to import panda3d_kivy BEFORE anything Kivy-related
from panda3d_kivy.core.window import PandaWindow

from kivy.app import App as KivyApp
from kivy.base import runTouchApp
from kivy.lang import parser


class App(KivyApp):
    def __init__(self, display_region, panda_app, **kwargs):
        super().__init__(**kwargs)

        # XXX: Possible bug with Kivy, should use EventLoop.window instead
        from kivy.core import window

        self.window = window.Window = PandaWindow(
            display_region=display_region,
            panda_app=panda_app,
        )

    def run(self):
        # XXX: Instanciate multiple apps, get the correct one in kvlang
        parser.global_idmap['app'] = self
        self._run_prepare()
        runTouchApp(slave=True)
