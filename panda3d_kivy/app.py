# XXX: Make sure to import panda3d_kivy BEFORE anything Kivy-related
from panda3d_kivy.core.window import PandaWindow

from kivy.app import App as KivyApp
from kivy.base import runTouchApp
from kivy.lang import parser


class App(KivyApp):
    def __init__(self, display_region, panda_app, **kwargs):
        super().__init__(**kwargs)

        self.window = PandaWindow(
            display_region=display_region,
            panda_app=panda_app,
        )

    def run(self):
        self.load_config()

        # XXX: Instanciate multiple apps, get the correct one in kvlang
        parser.global_idmap['app'] = self
        self.load_kv(filename=self.kv_file)

        root = self.build()

        if root:
            self.root = root

        runTouchApp(self.root, slave=True)
