# XXX: Make sure to import panda3d_kivy BEFORE anything Kivy-related
from panda3d_kivy.core.window import PandaWindow

# Sets kivy.exit_on_escape to 0 (a more sensible default for Panda3D apps)
import panda3d_kivy.config  # noqa

import os
import kivy
from kivy.app import App as KivyApp
from kivy.base import runTouchApp
from kivy.lang import parser, Builder
from kivy.properties import ObjectProperty


class MDApp(KivyApp):
    theme_cls = ObjectProperty()

    def __init__(self, panda_app, display_region, **kwargs):
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

        panda_app.taskMgr.add(
            lambda _: display_region.clear_draw_callback(),
            name='panda3d_kivy_display_region_clear_draw_callback')


        self.window = PandaWindow(
            display_region=display_region,
            panda_app=panda_app,
            kivy_app=self,
        )

        if not self.root:
            self.run()  # root shouldn't be set before run() is called


    def load_all_kv_files(self, path_to_directory: str) -> None:
        """
        Recursively loads KV files from the selected directory.
        .. versionadded:: 1.0.0
        """

        for path_to_dir, dirs, files in os.walk(path_to_directory):
            if (
                "venv" in path_to_dir
                or ".buildozer" in path_to_dir
                or "kivymd/tools/patterns/MVC" in path_to_dir
            ):
                continue
            for name_file in files:
                if (
                    os.path.splitext(name_file)[1] == ".kv"
                    and name_file != "style.kv"  # if use PyInstaller
                    and "__MACOS" not in path_to_dir  # if use Mac OS
                ):
                    path_to_kv_file = os.path.join(path_to_dir, name_file)
                    Builder.load_file(path_to_kv_file)

    def run(self):
        if not self.window:
            return  # run() will be called from init_window()

        self.load_config()

        # XXX: Instantiate multiple apps, get the correct one in kvlang
        parser.global_idmap['app'] = self
        self.load_kv(filename=self.kv_file)

        self.window.setup_kivy_variables()

        from kivymd.theming import ThemeManager
        self.theme_cls = ThemeManager()

        root = self.build()

        if root:
            self.root = root

        # See https://github.com/kivy/kivy/pull/6937
        kwargs = {}
        version, *_ = kivy.parse_kivy_version(kivy.__version__)
        major, *_ = version

        if major < 2:
            kwargs['slave'] = True
        else:
            kwargs['embedded'] = True

        self.on_start()

        runTouchApp(self.root, **kwargs)

    def stop(self):
        super().stop()
        if self.window is not None:
            self.window.remove_widget(self.root)
            del self.root
            self.window.destroy()
            self.window = None
        self.panda_app.taskMgr.remove('panda3d_kivy_display_region_clear_draw_callback')