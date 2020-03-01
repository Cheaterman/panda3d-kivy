from direct.showbase.ShowBase import ShowBase

# XXX: Make sure to import panda3d_kivy BEFORE anything Kivy-related
from panda3d_kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty


class PandaApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        display_region = self.win.make_display_region(0, 0.25, 0, 1)

        self.kivy_app_1 = kivy_app = MyKivyApp(
            self,
            display_region
        )
        kivy_app.run()

        display_region = self.win.make_display_region(0.75, 1, 0, 1)
        display_region.set_sort(30)

        self.kivy_app_2 = kivy_app = MyOtherKivyApp(
            self,
            display_region
        )
        kivy_app.run()

        scene = self.loader.loadModel('models/environment')
        scene.reparentTo(self.render)
        scene.setScale(0.25, 0.25, 0.25)


KV = r'''
BoxLayout:
    orientation: 'vertical'
    opacity: .75

    TextInput:
        id: text_input
        hint_text: 'Hello, world!'

    Label:
        text:
            '{extra_message}{more_stuff}'.format(
            extra_message=app.extra_message,
            more_stuff=(
            '' if not text_input.text
            else '\nYou typed: {}'.format(text_input.text)
            )
            )

    Button:
        text: 'Owi'
        on_press: app.owi_count += 1
'''


# Creating subclasses of App, "as usual"
class MyKivyApp(App):
    owi_count = NumericProperty()
    extra_message = StringProperty()

    def build(self):
        return Builder.load_string(KV)

    def on_owi_count(self, _, owi_count):
        self.extra_message = f'You pressed "Owi" {owi_count} times!'


class MyOtherKivyApp(App):
    def build(self):
        return Builder.load_string('''
BoxLayout:
    orientation: 'vertical'

    LabelButton:
        id: label_button
        text: text_input.text or 'BLIBLIBLIBLIBLI'
        font_size: sp(32)
        color: 0, 0, 0, 1
        text_size: self.size
        halign: 'center'
        valign: 'center'
        on_press: text_input.text = ''

    TextInput:
        id: text_input
        hint_text:
            (
            'Tagada pwet! Input some stuff, then tap the text '
            'above to reset my text!'
            )


<LabelButton@ButtonBehavior+Label>:
''')


PandaApp().run()
