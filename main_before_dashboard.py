from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle


class SubjectCard(Label):

    def __init__(self, subject="", **kwargs):
        super().__init__(**kwargs)

        self.subject = subject
        self.size_hint = (None, None)
        self.width = 170
        self.height = 85

        self.halign = "center"
        self.valign = "middle"
        self.text_size = (155, 75)

        if subject:
            self.text = subject
            self.bold = True
            self.font_size = 12

            if "MATHEMATICS" in subject:
                self.card_color = (0.25, 0.55, 0.95, 1)

            elif "ENGLISH" in subject:
                self.card_color = (0.35, 0.75, 0.45, 1)

            elif "MATERIALS" in subject:
                self.card_color = (0.95, 0.60, 0.25, 1)

            elif "HISTORY" in subject:
                self.card_color = (0.65, 0.40, 0.85, 1)

            elif "GRAPHICS" in subject:
                self.card_color = (0.90, 0.35, 0.55, 1)

            elif "BASIC DESIGN" in subject:
                self.card_color = (0.20, 0.70, 0.70, 1)

            elif "SPORTS" in subject:
                self.card_color = (0.85, 0.45, 0.20, 1)

            else:
                self.card_color = (0.5, 0.5, 0.5, 1)

        else:
            self.text = ""
            self.font_size = 12
            self.card_color = (0.85, 0.85, 0.85, 1)

        with self.canvas.before:
            Color(*self.card_color)
            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[12]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size


class HeaderCard(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (None, None)
        self.width = kwargs.get("width", 170)
        self.height = 55

        self.bold = True
        self.font_size = 15
        self.halign = "center"
        self.valign = "middle"

        with self.canvas.before:
            Color(0.12, 0.12, 0.16, 1)
            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size


class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=20
        )

        layout.add_widget(
            Label(
                text="🎓 College App",
                font_size=34,
                bold=True
            )
        )

        layout.add_widget(
            Label(
                text="Welcome back!",
                font_size=18,
                size_hint_y=None,
                height=50
            )
        )

        timetable_button = Button(
            text="📅  Timetable",
            font_size=21,
            size_hint_y=None,
            height=75
        )

        timetable_button.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "timetable"
            )
        )

        layout.add_widget(timetable_button)

        self.add_widget(layout)


class TimetableScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        main.add_widget(
            Label(
                text="📅 Weekly Timetable",
                font_size=28,
                bold=True,
                size_hint_y=None,
                height=60
            )
        )

        scroll = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True
        )

        # 9 columns:
        # DAY + 8 time periods

        grid = GridLayout(
            cols=9,
            spacing=5,
            padding=5,
            size_hint=(None, None)
        )

        day_width = 130
        time_width = 170

        grid.width = day_width + (time_width * 8)

        times = [
            "8:00 - 8:55",
            "9:00 - 9:55",
            "10:00 - 10:55",
            "11:00 - 11:55",
            "12:00 - 12:55",
            "1:00 - 1:55",
            "2:00 - 3:55",
            "4:00 - 6:00"
        ]

        # Each day contains subjects in the same order
        # as the time list above.

        timetable = {

            "MONDAY": [
                "MATHEMATICS",
                "",
                "",
                "ENGLISH & CORPORATE COMMUNICATION",
                "ENGLISH & CORPORATE COMMUNICATION",
                "LUNCH BREAK",
                "GRAPHICS - I",
                "GRAPHICS - I"
            ],

            "TUESDAY": [
                "",
                "MATHEMATICS",
                "",
                "MATERIALS & CONSTRUCTION - I",
                "HISTORY OF ARCHITECTURE - I",
                "LUNCH BREAK",
                "BASIC DESIGN & VISUAL ARTS",
                "BASIC DESIGN & VISUAL ARTS"
            ],

            "WEDNESDAY": [
                "",
                "",
                "",
                "MATERIALS & CONSTRUCTION - I",
                "HISTORY OF ARCHITECTURE - I",
                "LUNCH BREAK",
                "MATERIALS & CONSTRUCTION - I",
                "MATERIALS & CONSTRUCTION - I"
            ],

            "THURSDAY": [
                "",
                "",
                "ENGLISH & CORPORATE COMMUNICATION",
                "MATHEMATICS",
                "",
                "LUNCH BREAK",
                "BASIC DESIGN & VISUAL ARTS",
                ""
            ],

            "FRIDAY": [
                "",
                "HISTORY OF ARCHITECTURE - I",
                "ENGLISH & CORPORATE COMMUNICATION",
                "HISTORY OF ARCHITECTURE - I",
                "",
                "LUNCH BREAK",
                "",
                "SPORTS - I"
            ]
        }

        # ---------- TOP HEADER ----------

        grid.add_widget(
            HeaderCard(
                text="DAY",
                width=day_width
            )
        )

        for time in times:
            grid.add_widget(
                HeaderCard(
                    text=time,
                    width=time_width
                )
            )

        # ---------- DAYS ----------

        for day, subjects in timetable.items():

            grid.add_widget(
                HeaderCard(
                    text=day,
                    width=day_width
                )
            )

            for subject in subjects:

                card = SubjectCard(
                    subject=subject
                )

                card.width = time_width

                grid.add_widget(card)

        grid.height = 55 + (85 * 5) + (5 * 6)

        scroll.add_widget(grid)

        main.add_widget(scroll)

        # ---------- BACK BUTTON ----------

        back = Button(
            text="←  Home",
            font_size=18,
            size_hint_y=None,
            height=60
        )

        back.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(back)

        self.add_widget(main)


class CollegeApp(App):

    def build(self):

        manager = ScreenManager()

        manager.add_widget(
            HomeScreen(name="home")
        )

        manager.add_widget(
            TimetableScreen(name="timetable")
        )

        return manager


CollegeApp().run()
