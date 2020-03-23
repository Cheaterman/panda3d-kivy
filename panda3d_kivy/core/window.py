from panda3d_kivy import monkey

monkey.patch_kivy()  # noqa

from kivy.app import App
from kivy.core import window
from direct.showbase.DirectObject import DirectObject
from panda3d.core import MouseWatcher
from kivy.base import EventLoop
from kivy.core.window import WindowBase
from kivy.event import EventDispatcher
from kivy.graphics import Callback, opengl as gl
from kivy.properties import ObjectProperty


class PandaMouse(DirectObject):
    mouse_buttons = {1: 'left', 2: 'middle', 3: 'right'}

    def __init__(self, panda_app, display_region, on_mouse_event):
        self.mouse_watcher = mouse_watcher = MouseWatcher()
        panda_app.mouseWatcherNode.get_parent(0).addChild(mouse_watcher)
        self.display_region = display_region
        mouse_watcher.set_display_region(display_region)

        self.coords = (0, 0)
        self.buttons_down = set()
        self.update_position()

        self.on_mouse_event = on_mouse_event

        handle_event = self.handle_event
        self.accept('mouse1', handle_event, ['mouse1', 'down'])
        self.accept('mouse2', handle_event, ['mouse2', 'down'])
        self.accept('mouse3', handle_event, ['mouse3', 'down'])
        self.accept('mouse1-up', handle_event, ['mouse1', 'up'])
        self.accept('mouse2-up', handle_event, ['mouse2', 'up'])
        self.accept('mouse3-up', handle_event, ['mouse3', 'up'])
        self.accept('wheel_up', handle_event, ['wheel', 'up'])
        self.accept('wheel_down', handle_event, ['wheel', 'down'])

    def update_dimensions(self):
        self.dimensions = dimensions = self.display_region.get_dimensions()
        relative_size = [
            dimensions[wh + 1] - dimensions[wh]
            for wh in range(0, 3, 2)
        ]
        self.window_size = [
            display_region_wh / relative_wh
            for display_region_wh, relative_wh in zip(
                self.display_region.get_pixel_size(),
                relative_size,
            )
        ]

    def update_position(self):
        self.update_dimensions()
        mouse_watcher = self.mouse_watcher

        if not mouse_watcher.has_mouse():
            return

        old_coords = self.coords
        dimensions = self.dimensions

        normalized_coords = [
            coord * .5 + .5
            for coord in mouse_watcher.get_mouse()
        ]
        normalized_coords = [
            coord * (dimensions[2*i + 1] - dimensions[2*i]) + dimensions[2*i]
            for i, coord in enumerate(normalized_coords)
        ]

        # Invert Y axis
        normalized_coords[1] = 1 - normalized_coords[1]

        # Get absolute coords relative to window
        self.coords = [
            coord * wh
            for coord, wh in zip(normalized_coords, self.window_size)
        ]

        if(
            self.buttons_down
            and self.coords != old_coords
        ):
            self.on_mouse_event('move', self.coords)

    def handle_event(self, button, state_or_direction):
        if not self.mouse_watcher.has_mouse():
            return

        # Make sure position is updated before mouse_up
        self.update_position()

        if button.startswith('mouse'):
            state = state_or_direction
            button = self.mouse_buttons[int(button[-1])]

            if state == 'down':
                self.buttons_down.add(button)
            else:
                self.buttons_down.remove(button)

            self.on_mouse_event(state, self.coords, button)

        elif button.startswith('wheel'):
            direction = state_or_direction
            self.on_mouse_event('wheel', self.coords, direction)


class PandaWindow(WindowBase):
    _clearcolor = ObjectProperty()

    modifier_keys = {
        'control': 'ctrl',
        'alt': None,
        'super': None,
    }

    translated_keys = {
        'arrow_left': 'left',
        'arrow_right': 'right',
        'arrow_down': 'down',
        'arrow_up': 'up',
        'page_down': 'pagedown',
        'page_up': 'pageup',
    }

    def __new__(cls, **kwargs):
        # XXX: Prevent Kivy Window from being a singleton
        return EventDispatcher.__new__(cls, **kwargs)

    def __init__(self, display_region, panda_app, kivy_app, **kwargs):
        self.display_region = display_region
        panda_app.taskMgr.add(
            lambda _: display_region.set_draw_callback(self.update_kivy)
        )

        self.mouse = PandaMouse(
            panda_app=panda_app,
            display_region=display_region,
            on_mouse_event=self.on_mouse_event,
        )
        self.ignored_touches = set()

        panda_app.buttonThrowers[0].node().set_keystroke_event('keystroke')
        panda_app.accept('keystroke', self.on_keystroke)
        panda_app.buttonThrowers[0].node().set_button_down_event('button-down')
        panda_app.accept('button-down', self.on_button_down)
        panda_app.buttonThrowers[0].node().set_button_up_event('button-up')
        panda_app.accept('button-up', self.on_button_up)

        self._has_updated = False

        super().__init__(**kwargs)

        with self.canvas.before:
            Callback(lambda _: self.reset_gl_context())
            Callback(lambda _: gl.glEnableVertexAttribArray(0))
            Callback(lambda _: gl.glEnableVertexAttribArray(1))

        with self.canvas.after:
            Callback(lambda _: gl.glDisableVertexAttribArray(0))
            Callback(lambda _: gl.glDisableVertexAttribArray(1))

        self.kivy_app = kivy_app

    def reset_gl_context(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_STENCIL_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glBlendFuncSeparate(
            gl.GL_SRC_ALPHA,
            gl.GL_ONE_MINUS_SRC_ALPHA,
            gl.GL_ONE,
            gl.GL_ONE
        )
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

    def on_keystroke(self, text):
        key = ord(text)

        if key <= 32:
            if not self._system_keyboard.keycode_to_string(key):
                text = ''

        scancode = self._system_keyboard.string_to_keycode(text)

        if scancode == -1:
            scancode = None

        self.dispatch_key_events(key, scancode, text)

    def on_button_down(self, text):
        if text in self.translated_keys:
            translated_key = self.translated_keys[text]
            keycode = self._system_keyboard.string_to_keycode(translated_key)
            self.dispatch_key_events(keycode, translated_key, '')
            return

        if '-' not in text:
            return

        modifier, text = text.split('-')

        if modifier not in self.modifier_keys:
            return

        target_modifier = self.modifier_keys[modifier] or modifier

        if target_modifier not in self.modifiers:
            self.modifiers.append(target_modifier)

        scancode = self._system_keyboard.string_to_keycode(text)

        if scancode == -1:
            return

        key = ord(text)

        self.dispatch_key_events(key, scancode, text)

    def dispatch_key_events(self, key, scancode, text):
        is_handled = (
            self.dispatch('on_key_down', key, scancode, text, self.modifiers)
        )

        if(
            self.dispatch('on_key_up', key, scancode, text, self.modifiers)
            or is_handled
        ):
            return

        self.dispatch('on_keyboard', key, scancode, text, self.modifiers)

    def on_button_up(self, text):
        if text not in self.modifier_keys:
            return

        target_modifier = self.modifier_keys[text] or text

        if target_modifier not in self.modifiers:
            return

        self.modifiers.remove(target_modifier)

    def setup_kivy_variables(self):
        window.Window = self
        App._running_app = self.kivy_app

    def update_kivy(self, *args):
        self.update_size()
        self.mouse.update_position()
        self._has_updated = self._has_drawn = False
        self.setup_kivy_variables()
        EventLoop.idle()
        self._has_updated = True
        self.on_draw()

    def update_size(self):
        self.size = self.display_region.get_pixel_size()
        self.dimensions = dimensions = self.display_region.get_dimensions()
        self.offsets = [
            dimensions[2*i] / (dimensions[2*i + 1] - dimensions[2*i])
            for i in range(2)
        ]

    def on_draw(self):
        if self._has_updated and not self._has_drawn:
            super().on_draw()
            self._has_drawn = True

    def update_viewport(self):
        from kivy.graphics.transformation import Matrix
        from math import radians

        w, h = self.system_size
        if self._density != 1:
            w, h = self.size

        w2, h2 = w / 2., h / 2.
        r = radians(self.rotation)

        # do projection matrix
        projection_mat = Matrix()
        projection_mat.view_clip(0.0, w, 0.0, h, -1.0, 1.0, 0)
        self.render_context['projection_mat'] = projection_mat

        # do modelview matrix
        modelview_mat = Matrix().translate(w2, h2, 0)
        modelview_mat = modelview_mat.multiply(Matrix().rotate(r, 0, 0, 1))

        w, h = self.size
        w2, h2 = w / 2., h / 2.
        modelview_mat = modelview_mat.multiply(Matrix().translate(-w2, -h2, 0))
        self.render_context['modelview_mat'] = modelview_mat
        frag_modelview_mat = Matrix()
        frag_modelview_mat.set(flat=modelview_mat.get())
        self.render_context['frag_modelview_mat'] = frag_modelview_mat

        # redraw canvas
        self.canvas.ask_update()

        # and update childs
        self.update_childsize()

    def on_mouse_event(self, event_name, coords, button=None):
        if event_name in ('up', 'down'):
            self.dispatch('on_mouse_' + event_name, *coords, button, [])

        elif event_name == 'wheel':
            self.dispatch('on_mouse_down', *coords, 'scroll' + button, [])
            self.dispatch('on_mouse_up', *coords, 'scroll' + button, [])

        elif event_name == 'move':
            self.dispatch('on_mouse_' + event_name, *coords, [])

    def on_motion(self, event_type, motion_event):
        coords = motion_event.sx, motion_event.sy

        if event_type == 'end' and motion_event in self.ignored_touches:
            self.ignored_touches.remove(motion_event)
            return

        coords = [
            coord - offset for coord, offset in zip(coords, self.offsets)
        ]

        if any(
            not 0 <= coord <= 1
            for coord in coords
        ):
            self.ignored_touches.add(motion_event)
            return

        motion_event.sx, motion_event.sy = coords

        self.setup_kivy_variables()
        super().on_motion(event_type, motion_event)

    def to_local(self, x, y):
        if any(xy is None for xy in (x, y)):
            return (0, 0)

        offsets = [
            wh * offset
            for wh, offset in zip(self.size, self.offsets)
        ]
        return tuple(xy + offset for xy, offset in zip((x, y), offsets))

    def to_parent(self, x, y):
        if any(xy is None for xy in (x, y)):
            return (0, 0)

        offsets = [
            wh * offset
            for wh, offset in zip(self.size, self.offsets)
        ]
        return tuple(xy - offset for xy, offset in zip((x, y), offsets))
