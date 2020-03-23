# XXX: Make sure to import panda3d_kivy BEFORE anything Kivy-related
from panda3d_kivy.core.window import PandaWindow

from kivy.app import App as KivyApp
from kivy.base import runTouchApp
from kivy.lang import parser


class App(KivyApp):
    def __init__(self, panda_app, display_region=None, **kwargs):
        super().__init__(**kwargs)

        if display_region is None:
            display_region = panda_app.win.make_display_region(0, 1, 0, 1)

        self.window = None
        self.display_region = display_region
        self.panda_app = panda_app
        display_region.set_draw_callback(self.init_window)

    def init_window(self, *args):
        # init_window() called by multiple frames in the pipeline
        if not hasattr(self, 'display_region'):
            return

        display_region = self.display_region
        panda_app = self.panda_app
        del self.display_region
        del self.panda_app

        panda_app.taskMgr.add(lambda _: display_region.clear_draw_callback())

        self.window = PandaWindow(
            display_region=display_region,
            panda_app=panda_app,
            kivy_app=self,
        )

        if not self.root:
            self.run()  # root shouldn't be set before run() is called

    def run(self):
        if not self.window:
            return  # run() will be called from init_window()

        self.load_config()

        # XXX: Instantiate multiple apps, get the correct one in kvlang
        parser.global_idmap['app'] = self
        self.load_kv(filename=self.kv_file)

        root = self.build()

        if root:
            self.root = root

        runTouchApp(self.root, slave=True)
