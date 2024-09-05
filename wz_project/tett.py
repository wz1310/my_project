#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior

# temporarily replaced with load_string
# Builder.load_file('layouts.kv')
# Builder.load_file('backdrop.kv')

Builder.load_string('''
#:import os os
#:import Window kivy.core.window.Window
#:import IconLeftWidget kivymd.uix.list.IconLeftWidget
#:import images_path kivymd.images_path


<ItemBackdropFrontLayer@TwoLineAvatarListItem>
    icon: "android"

    IconLeftWidget:
        icon: root.icon


<MyyBackdropFrontLayer@ScrollView>
    backdrop: None
    backlayer: None

    MDGridLayout:
        adaptive_height: True
        cols: 2
        padding: "5dp"

        ItemBackdropFrontLayer:
            text: "Button 2"
            icon: "monitor-star"
            on_press:
                root.backdrop.open(-Window.height / 2)


<MyyBackdropBackLayer@ScrollView>
    # these connections are necessary to connect Python to Kivy
    # Python: Kivy
    summ: summ
    bt2: bt2

    MDGridLayout:
        adaptive_height: True
        cols: 2
        padding: "5dp"

        ItemBackdropFrontLayer:
            id: bt2
            text: "button 2"
            secondary_text: "..."
            icon: "monitor-star"
            on_press: app.show(self)

        MDTextField:
            id: summ
            hint_text: "input here"
            mode: "fill"

<ExampleBackdrop>

    MDBackdrop:
        id: backdrop
        left_action_items: [['menu', lambda x: self.open()]]
        title: "Example Backdrop"
        radius_left: "25dp"
        radius_right: "25dp"
        header_text: "Меню:"

        MDBackdropBackLayer:
            MyyBackdropBackLayer:
                id: backlayer

        MDBackdropFrontLayer:
            MyyBackdropFrontLayer:
                backdrop: backdrop

''')


class ExampleBackdrop(MDScreen):
    pass


class ItemBackdropBackLayer(ThemableBehavior, MDBoxLayout):
    icon = StringProperty("android")
    text = StringProperty()
    selected_item = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            for item in self.parent.children:
                if item.selected_item:
                    item.selected_item = False
            self.selected_item = True
        return super().on_touch_down(touch)


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "KivyMD Example - Backdrop"
        self.theme_cls.primary_palette = "DeepPurple"

    def show(self, *args, **kwargs):
        print(f"self {self.root}: args={args} kwargs={kwargs}")
        print(f"**summ text is {self.root.ids.backlayer.summ.text} **")
        print(f"bt2 text is {self.root.ids.backlayer.bt2.text}")
        for child in self.root.ids.backlayer.children:
            print(f"Child of backlayer: {child}")
        print("----")
        for child in self.root.children:
            print(f"Child of root: {child}")

        for child in self.root.ids.backdrop.children:
            print(f"Child of root backdrop: {child}")

    def on_start(self):
        print(id(self.root))

    def build(self) -> ExampleBackdrop:
        _main =ExampleBackdrop()
        print(type(_main))
        print(isinstance(_main, MDScreen))
        print(id(_main))
        return _main


if __name__ == "__main__":
    MainApp().run()