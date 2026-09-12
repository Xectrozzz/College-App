from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle


# ============================================================
# SUBJECT ATTENDANCE
# ============================================================

attendance = {
    "MATHEMATICS": "—",
    "ENGLISH & CORPORATE COMMUNICATION": "—",
    "MATERIALS & CONSTRUCTION - I": "—",
    "HISTORY OF ARCHITECTURE - I": "—",
    "GRAPHICS - I": "—",
    "BASIC DESIGN & VISUAL ARTS": "—",
    "SPORTS - I": "—"
}


# ============================================================
# SUBJECT CARD
# ============================================================

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

        if subject == "LUNCH BREAK":

            self.text = subject
            self.bold = True
            self.font_size = 12
            self.card_color = (0.95, 0.75, 0.25, 1)

        elif subject:

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

            self.text = "FREE"
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


# ============================================================
# HEADER CARD
# ============================================================

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


# ============================================================
# HOME SCREEN
# ============================================================

class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15
        )

        layout.add_widget(
            Label(
                text="College App",
                font_size=34,
                bold=True,
                size_hint_y=None,
                height=60
            )
        )

        layout.add_widget(
            Label(
                text="Welcome back!",
                font_size=20,
                size_hint_y=None,
                height=45
            )
        )

        # ----------------------------------------------------
        # TODAY'S CLASSES
        # ----------------------------------------------------

        layout.add_widget(
            Label(
                text="TODAY'S CLASSES",
                font_size=20,
                bold=True,
                size_hint_y=None,
                height=50
            )
        )

        layout.add_widget(
            Label(
                text="Check your timetable for today's classes",
                font_size=16,
                size_hint_y=None,
                height=50
            )
        )

        # ----------------------------------------------------
        # ATTENDANCE
        # ----------------------------------------------------

        layout.add_widget(
            Label(
                text="ATTENDANCE",
                font_size=20,
                bold=True,
                size_hint_y=None,
                height=50
            )
        )

        attendance_button = Button(
            text="View Subject Attendance",
            font_size=18,
            size_hint_y=None,
            height=65
        )

        attendance_button.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "subjects"
            )
        )

        layout.add_widget(attendance_button)

        # ----------------------------------------------------
        # TIMETABLE
        # ----------------------------------------------------

        timetable_button = Button(
            text="Timetable",
            font_size=20,
            size_hint_y=None,
            height=70
        )

        timetable_button.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "timetable"
            )
        )

        layout.add_widget(timetable_button)

        # ----------------------------------------------------
        # SUBJECTS
        # ----------------------------------------------------

        subjects_button = Button(
            text="Subjects",
            font_size=20,
            size_hint_y=None,
            height=70
        )

        subjects_button.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "subjects"
            )
        )

        layout.add_widget(subjects_button)

        # ----------------------------------------------------
        # ASSIGNMENTS
        # ----------------------------------------------------

        assignments_button = Button(
            text="Assignments",
            font_size=20,
            size_hint_y=None,
            height=70
        )

        assignments_button.bind(
            on_press=lambda x: print(
                "Assignments screen coming soon!"
            )
        )

        layout.add_widget(assignments_button)

        self.add_widget(layout)


# ============================================================
# SUBJECTS SCREEN
# ============================================================

class SubjectsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12
        )

        main.add_widget(
            Label(
                text="Subjects & Attendance",
                font_size=30,
                bold=True,
                size_hint_y=None,
                height=60
            )
        )

        scroll = ScrollView()

        subjects = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )

        subjects.bind(
            minimum_height=subjects.setter("height")
        )

        subject_list = [
            "MATHEMATICS",
            "ENGLISH & CORPORATE COMMUNICATION",
            "MATERIALS & CONSTRUCTION - I",
            "HISTORY OF ARCHITECTURE - I",
            "GRAPHICS - I",
            "BASIC DESIGN & VISUAL ARTS",
            "SPORTS - I"
        ]

        for subject in subject_list:

            button = Button(
                text=(
                    subject
                    + "\nAttendance: "
                    + attendance[subject]
                ),
                font_size=16,
                size_hint_y=None,
                height=75
            )

            button.bind(
                on_press=lambda x, s=subject:
                self.open_subject(s)
            )

            subjects.add_widget(button)

        scroll.add_widget(subjects)
        main.add_widget(scroll)

        back = Button(
            text="Home",
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

    def open_subject(self, subject):

        details_screen = self.manager.get_screen(
            "subject_details"
        )

        details_screen.show_subject(subject)

        self.manager.current = "subject_details"


# ============================================================
# SUBJECT DETAILS SCREEN
# ============================================================

class SubjectDetailsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15
        )

        self.title = Label(
            text="Subject",
            font_size=30,
            bold=True,
            size_hint_y=None,
            height=70
        )

        self.main.add_widget(self.title)

        self.info = Label(
            text="",
            font_size=18,
            halign="left",
            valign="top"
        )

        self.main.add_widget(self.info)

        back = Button(
            text="Back to Subjects",
            font_size=18,
            size_hint_y=None,
            height=60
        )

        back.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "subjects"
            )
        )

        self.main.add_widget(back)

        home = Button(
            text="Home",
            font_size=18,
            size_hint_y=None,
            height=60
        )

        home.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "home"
            )
        )

        self.main.add_widget(home)

        self.add_widget(self.main)

    def show_subject(self, subject):

        self.title.text = subject

        self.info.text = (
            "\n"
            "Attendance: "
            + attendance[subject]
            + "\n\n"
            "Credits: —\n\n"
            "Assignments: —\n\n"
            "Syllabus: —"
        )


# ============================================================
# TIMETABLE SCREEN
# ============================================================

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
                text="Weekly Timetable",
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

        # ----------------------------------------------------
        # TOP HEADER
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # DAYS
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # BACK BUTTON
        # ----------------------------------------------------

        back = Button(
            text="Home",
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


# ============================================================
# APP
# ============================================================

class CollegeApp(App):

    def build(self):

        manager = ScreenManager()

        manager.add_widget(
            HomeScreen(name="home")
        )

        manager.add_widget(
            TimetableScreen(name="timetable")
        )

        manager.add_widget(
            SubjectsScreen(name="subjects")
        )

        manager.add_widget(
            SubjectDetailsScreen(name="subject_details")
        )

        return manager


CollegeApp().run()
