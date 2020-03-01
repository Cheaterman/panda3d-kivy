import os
import sys

import kivy.core


def patch_kivy():
    os.environ['KIVY_WINDOW'] = ''
    if sys.platform == 'linux':
        os.environ['KIVY_GL_BACKEND'] = 'gl'

    orig_core_select_lib = kivy.core.core_select_lib

    def core_select_lib_hide_window(category, *args, **kwargs):
        if category != 'window':
            return orig_core_select_lib(category, *args, **kwargs)

    kivy.core.core_select_lib = core_select_lib_hide_window
