from kivy.animation import Animation
from kivy.lang import Builder

from kivymd.uix.screen import MDScreen
from kivymd.uix.chip import MDChip
from kivymd.app import MDApp

KV = '''
<MyScreen>

    MDBoxLayout:
        orientation: "vertical"
        adaptive_size: True
        spacing: "12dp"
        padding: "56dp"
        pos_hint: {"center_x": .5, "center_y": .5}

        MDLabel:
            text: "Multiple choice"
            bold: True
            font_style: "H5"
            adaptive_size: True

        MDBoxLayout:
            id: chip_box
            adaptive_size: True
            spacing: "8dp"

            MyChip:
                text: "Elevator"
                on_press: if self.active: root.removes_marks_all_chips()

            MyChip:
                text: "Washer / Dryer"
                on_press: if self.active: root.removes_marks_all_chips()

            MyChip:
                text: "Fireplace"
                on_press: if self.active: root.removes_marks_all_chips()


ScreenManager:

    MyScreen:
'''


class MyChip(MDChip):
    icon_check_color = (0, 0, 0, 1)
    text_color = (0, 0, 0, 0.5)
    _no_ripple_effect = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(active=self.set_chip_bg_color)
        self.bind(active=self.set_chip_text_color)

    def set_chip_bg_color(self, instance_chip, active_value: int):
        '''
        Will be called every time the chip is activated/deactivated.
        Sets the background color of the chip.
        '''

        self.md_bg_color = (
            (0, 0, 0, 0.4)
            if active_value
            else (
                self.theme_cls.bg_darkest
                if self.theme_cls.theme_style == "Light"
                else (
                    self.theme_cls.bg_light
                    if not self.disabled
                    else self.theme_cls.disabled_hint_text_color
                )
            )
        )

    def set_chip_text_color(self, instance_chip, active_value: int):
        Animation(
            color=(0, 0, 0, 1) if active_value else (0, 0, 0, 0.5), d=0.2
        ).start(self.ids.label)


class MyScreen(MDScreen):
    def removes_marks_all_chips(self):
        for instance_chip in self.ids.chip_box.children:
            if instance_chip.active:
                instance_chip.active = False


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()