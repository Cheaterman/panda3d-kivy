from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase

from kivy.config import Config
Config.set(  # noqa
    'kivy',
    'default_font',
    ['DejaVu Sans Mono', 'DejaVuSansMono.ttf']
)
# XXX: Make sure to import panda3d_kivy BEFORE anything Kivy-related
from panda3d_kivy.app import App
from kivy.properties import DictProperty


PANDA_SPEED_MULTIPLIER = 3


class MovementApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disable_mouse()

        self.movement_ui = movement_ui = MovementUI(self)
        movement_ui.run()

        scene = self.loader.load_model('models/environment')
        scene.reparent_to(self.render)
        scene.set_scale(0.25, 0.25, 0.25)
        scene.set_pos(-8, 42, 0)

        self.taskMgr.add(self.update_camera, 'update_camera')
        self.taskMgr.add(self.update_ui, 'update_ui')

        self.panda = PandaCharacter(self)

        self.keymap = {
            'left': 'turn_left',
            'right': 'turn_right',
            'down': 'backward',
            'up': 'forward',
        }

    def update_camera(self, task):
        self.camera.set_pos(self.panda.actor, 0, 3500, 1000)
        self.camera.look_at(self.panda.actor, 0, -2000, 250)
        return task.cont

    def update_ui(self, task):
        movement_ui = self.movement_ui
        panda = self.panda

        for key, action in self.keymap.items():
            if(
                movement_ui.button_states[key]
                and action not in panda.actions
            ):
                panda.actions.add(action)
            elif(
                not movement_ui.button_states[key]
                and action in panda.actions
            ):
                panda.actions.remove(action)

        return task.cont


class PandaCharacter:
    def __init__(self, base):
        self.actor = Actor(
            'models/panda-model',
            {'walk': 'models/panda-walk4'}
        )
        self.actor.set_scale(0.005, 0.005, 0.005)
        self.actor.reparent_to(base.render)
        base.taskMgr.add(self.update, 'update_panda')
        self.actions = set()
        self.last_update_time = 0

    def update(self, task):
        dt = task.time - self.last_update_time
        self.last_update_time = task.time
        actor = self.actor
        y_offset = 0
        angle_offset = 0

        if not (
            'forward' in self.actions
            or 'backward' in self.actions
        ):
            actor.stop()
        elif actor.get_current_anim() != 'walk':
            actor.loop('walk', restart=False)

        if 'forward' in self.actions:
            actor.set_play_rate(1 * PANDA_SPEED_MULTIPLIER, 'walk')
            y_offset += dt * 200 * PANDA_SPEED_MULTIPLIER

        if 'backward' in self.actions:
            actor.set_play_rate(-.75 * PANDA_SPEED_MULTIPLIER, 'walk')
            y_offset -= dt * 150 * PANDA_SPEED_MULTIPLIER

        if 'turn_left' in self.actions:
            angle_offset += dt * 50

        if 'turn_right' in self.actions:
            angle_offset -= dt * 50

        actor.set_pos(actor, 0, -y_offset, 0)
        actor.set_hpr(actor, angle_offset, 0, 0)

        return task.cont


class MovementUI(App):
    button_states = DictProperty({
        'left': False,
        'right': False,
        'down': False,
        'up': False,
    })


MovementApp().run()
