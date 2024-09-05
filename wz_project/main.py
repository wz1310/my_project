from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.datatables import MDDataTable


class Example(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.theme_style = "Dark"
        return (
            MDScreen(
                MDTopAppBar(
                    pos_hint={"top": 1},
                    elevation=4,
                    title="",
                    left_action_items=[["menu", lambda x: self.nav_drawer_open()]],
                ),
                MDNavigationLayout(
                    MDScreenManager(
                        MDScreen(
                            MDLabel(
                                text="Screen 1",
                                halign="center",
                            ),
                            name="scr 1",
                        ),
                        MDScreen(
                            MDLabel(
                                text="Screen 2",
                                halign="center",
                            ),
                            name="scr 2",
                        ),
                        MDScreen(
                        	self.abc(),
                            name="scr 3",
                        ),
                        id="screen_manager",
                    ),
                    MDNavigationDrawer(
                        MDScrollView(
                            MDList(
                                OneLineListItem(
                                    text="Screen 1",
                                    on_press=self.switch_screen,
                                ),
                                OneLineListItem(
                                    text="Screen 2",
                                    on_press=self.switch_screen,
                                ),
                                OneLineListItem(
                                    text="Screen 3",
                                    on_press=self.switch_screen,
                                ),
                            ),
                        ),
                        id="nav_drawer",
                        radius=(0, 16, 16, 0),
                    ),
                    id="navigation_layout",
                )
            )
        )

    def switch_screen(self, instance_list_item: OneLineListItem):
        self.root.ids.navigation_layout.ids.screen_manager.current = {
            "Screen 1": "scr 1", "Screen 2": "scr 2", "Screen 3": "scr 3"
        }[instance_list_item.text]
        self.root.children[0].ids.nav_drawer.set_state("close")

    def nav_drawer_open(self):
        nav_drawer = self.root.children[0].ids.nav_drawer
        nav_drawer.set_state("open")

    def abc(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        layout = AnchorLayout()
        data_tables = MDDataTable(
            size_hint=(0.9, 0.6),
            use_pagination=True,
            column_data=[
                ("No.", dp(30)),
                ("Column 1", dp(30)),
                ("Column 2", dp(30)),
                ("Column 3", dp(30)),
                ("Column 4", dp(30)),
                ("Column 5", dp(30)),
            ],
            row_data=[
                (f"{i + 1}", "1", "2", "3", "4", "5") for i in range(50)
            ],
        )
        layout.add_widget(data_tables)
        return layout

    def sort_on_col_3(self, data):
        return zip(
            *sorted(
                enumerate(data),
                key=lambda l: l[1][3]
            )
        )

    def sort_on_col_2(self, data):
        return zip(
            *sorted(
                enumerate(data),
                key=lambda l: l[1][-1]
            )
        )


Example().run()