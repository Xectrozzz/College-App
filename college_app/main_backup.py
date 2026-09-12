import json
import os
from datetime import date, timedelta

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup


# ============================================================
# SETTINGS
# ============================================================

REQUIRED_ATTENDANCE = 75


# ============================================================
# TIMETABLE DATA
# ============================================================

TIMES = [
    "8:00 - 8:55",
    "9:00 - 9:55",
    "10:00 - 10:55",
    "11:00 - 11:55",
    "12:00 - 12:55",
    "1:00 - 1:55",
    "2:00 - 3:55",
    "4:00 - 6:00"
]


TIMETABLE = {

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


SUBJECTS = [
    "MATHEMATICS",
    "ENGLISH & CORPORATE COMMUNICATION",
    "MATERIALS & CONSTRUCTION - I",
    "HISTORY OF ARCHITECTURE - I",
    "GRAPHICS - I",
    "BASIC DESIGN & VISUAL ARTS",
    "SPORTS - I"
]


# ============================================================
# ATTENDANCE STORAGE
# ============================================================

def get_attendance_file():

    app = App.get_running_app()

    return os.path.join(
        app.user_data_dir,
        "attendance.json"
    )


def load_attendance():

    filename = get_attendance_file()

    try:

        if os.path.exists(filename):

            with open(filename, "r") as file:
                return json.load(file)

    except Exception:
        pass

    return {}


def save_attendance(data):

    filename = get_attendance_file()

    try:

        os.makedirs(
            os.path.dirname(filename),
            exist_ok=True
        )

        with open(filename, "w") as file:
            json.dump(
                data,
                file,
                indent=4
            )

    except Exception as e:

        print("Could not save attendance:", e)


# ============================================================
# ATTENDANCE CALCULATIONS
# ============================================================

def get_subject_stats(subject):

    data = App.get_running_app().attendance_data

    present = 0
    absent = 0

    for record in data.values():

        if record.get("subject") == subject:

            if record.get("status") == "present":
                present += 1

            elif record.get("status") == "absent":
                absent += 1

    total = present + absent

    if total == 0:
        percentage = None
    else:
        percentage = (present / total) * 100

    return present, absent, total, percentage


def classes_can_skip(present, total):

    if total == 0:
        return 0

    skipped = 0

    while True:

        future_total = total + skipped + 1

        future_present = present

        future_percentage = (
            future_present / future_total
        ) * 100

        if future_percentage >= REQUIRED_ATTENDANCE:
            skipped += 1
        else:
            break

    return skipped


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

        self.text_size = (
            155,
            75
        )

        if subject == "LUNCH BREAK":

            self.text = subject
            self.bold = True
            self.font_size = 12

            self.card_color = (
                0.95,
                0.75,
                0.25,
                1
            )

        elif subject:

            self.text = subject
            self.bold = True
            self.font_size = 12

            if "MATHEMATICS" in subject:
                self.card_color = (
                    0.25,
                    0.55,
                    0.95,
                    1
                )

            elif "ENGLISH" in subject:
                self.card_color = (
                    0.35,
                    0.75,
                    0.45,
                    1
                )

            elif "MATERIALS" in subject:
                self.card_color = (
                    0.95,
                    0.60,
                    0.25,
                    1
                )

            elif "HISTORY" in subject:
                self.card_color = (
                    0.65,
                    0.40,
                    0.85,
                    1
                )

            elif "GRAPHICS" in subject:
                self.card_color = (
                    0.90,
                    0.35,
                    0.55,
                    1
                )

            elif "BASIC DESIGN" in subject:
                self.card_color = (
                    0.20,
                    0.70,
                    0.70,
                    1
                )

            elif "SPORTS" in subject:
                self.card_color = (
                    0.85,
                    0.45,
                    0.20,
                    1
                )

            else:
                self.card_color = (
                    0.5,
                    0.5,
                    0.5,
                    1
                )

        else:

            self.text = "FREE"
            self.font_size = 12

            self.card_color = (
                0.85,
                0.85,
                0.85,
                1
            )

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

        self.size_hint = (
            None,
            None
        )

        self.width = kwargs.get(
            "width",
            170
        )

        self.height = 55

        self.bold = True
        self.font_size = 15

        self.halign = "center"
        self.valign = "middle"

        with self.canvas.before:

            Color(
                0.12,
                0.12,
                0.16,
                1
            )

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
        # ATTENDANCE SUMMARY
        # ----------------------------------------------------

        self.attendance_summary = Label(
            text="Attendance\nNo classes marked yet",
            font_size=18,
            size_hint_y=None,
            height=100
        )

        layout.add_widget(
            self.attendance_summary
        )

        attendance_button = Button(
            text="Attendance",
            font_size=20,
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

        layout.add_widget(
            attendance_button
        )

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

        layout.add_widget(
            timetable_button
        )

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

        layout.add_widget(
            subjects_button
        )

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

        layout.add_widget(
            assignments_button
        )

        self.add_widget(layout)

    def on_pre_enter(self, *args):

        self.update_attendance_summary()

    def update_attendance_summary(self):

        total_present = 0
        total_absent = 0

        for subject in SUBJECTS:

            present, absent, total, percentage = (
                get_subject_stats(subject)
            )

            total_present += present
            total_absent += absent

        total = total_present + total_absent

        if total == 0:

            self.attendance_summary.text = (
                "ATTENDANCE\n"
                "No classes marked yet"
            )

            return

        percentage = (
            total_present / total
        ) * 100

        skips = classes_can_skip(
            total_present,
            total
        )

        self.attendance_summary.text = (
            "ATTENDANCE\n"
            f"{total_present} / {total} "
            f"({percentage:.1f}%)\n"
            f"Can skip: {skips} classes"
        )


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

        self.subjects_box = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )

        self.subjects_box.bind(
            minimum_height=
            self.subjects_box.setter("height")
        )

        scroll.add_widget(
            self.subjects_box
        )

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

    def on_pre_enter(self, *args):

        self.refresh_subjects()

    def refresh_subjects(self):

        self.subjects_box.clear_widgets()

        for subject in SUBJECTS:

            present, absent, total, percentage = (
                get_subject_stats(subject)
            )

            if total == 0:

                attendance_text = "Not marked"

            else:

                attendance_text = (
                    f"{percentage:.1f}%  "
                    f"({present}/{total})"
                )

            button = Button(
                text=(
                    f"{subject}\n"
                    f"Attendance: {attendance_text}"
                ),
                font_size=16,
                size_hint_y=None,
                height=75
            )

            button.bind(
                on_press=lambda x, s=subject:
                self.open_subject(s)
            )

            self.subjects_box.add_widget(
                button
            )

    def open_subject(self, subject):

        details_screen = (
            self.manager.get_screen(
                "subject_details"
            )
        )

        details_screen.show_subject(
            subject
        )

        self.manager.current = (
            "subject_details"
        )


# ============================================================
# SUBJECT DETAILS
# ============================================================

class SubjectDetailsScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.current_subject = None

        main = BoxLayout(
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

        main.add_widget(
            self.title
        )

        self.info = Label(
            text="",
            font_size=19,
            halign="center",
            valign="middle"
        )

        main.add_widget(
            self.info
        )

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

        main.add_widget(back)

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

        main.add_widget(home)

        self.add_widget(main)

    def show_subject(self, subject):

        self.current_subject = subject

        self.title.text = subject

        present, absent, total, percentage = (
            get_subject_stats(subject)
        )

        if total == 0:

            percentage_text = "No classes marked yet"
            skip_text = "Can skip: —"

        else:

            percentage_text = (
                f"{percentage:.1f}%"
            )

            skips = classes_can_skip(
                present,
                total
            )

            skip_text = (
                f"Can skip: {skips} classes"
            )

        self.info.text = (
            "\n"
            f"Attendance: {percentage_text}\n\n"
            f"Present: {present}\n"
            f"Absent: {absent}\n"
            f"Total marked: {total}\n\n"
            f"{skip_text}\n\n"
            f"Required: {REQUIRED_ATTENDANCE}%"
        )


# ============================================================
# ATTENDANCE POPUP
# ============================================================

class AttendancePopup(Popup):

    def __init__(
        self,
        subject,
        class_date,
        time,
        **kwargs
    ):

        self.subject = subject
        self.class_date = class_date
        self.time = time

        content = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12
        )

        content.add_widget(
            Label(
                text=subject,
                font_size=22,
                bold=True
            )
        )

        content.add_widget(
            Label(
                text=(
                    f"{class_date}\n"
                    f"{time}"
                ),
                font_size=17
            )
        )

        present = Button(
            text="PRESENT",
            font_size=19,
            size_hint_y=None,
            height=60
        )

        absent = Button(
            text="ABSENT",
            font_size=19,
            size_hint_y=None,
            height=60
        )

        present.bind(
            on_press=lambda x:
            self.mark("present")
        )

        absent.bind(
            on_press=lambda x:
            self.mark("absent")
        )

        content.add_widget(present)
        content.add_widget(absent)

        super().__init__(
            title="Mark Attendance",
            content=content,
            size_hint=(0.85, 0.55),
            **kwargs
        )

    def mark(self, status):

        app = App.get_running_app()

        key = (
            f"{self.class_date}|"
            f"{self.subject}|"
            f"{self.time}"
        )

        app.attendance_data[key] = {
            "subject": self.subject,
            "date": self.class_date,
            "time": self.time,
            "status": status
        }

        save_attendance(
            app.attendance_data
        )

        self.dismiss()

        timetable = (
            app.root.get_screen(
                "timetable"
            )
        )

        timetable.refresh_grid()


# ============================================================
# TIMETABLE SCREEN
# ============================================================

class TimetableScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.main = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        self.main.add_widget(
            Label(
                text="Weekly Timetable",
                font_size=28,
                bold=True,
                size_hint_y=None,
                height=60
            )
        )

        self.scroll = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True
        )

        self.grid = GridLayout(
            cols=9,
            spacing=5,
            padding=5,
            size_hint=(None, None)
        )

        self.day_width = 130
        self.time_width = 170

        self.grid.width = (
            self.day_width
            + (self.time_width * 8)
        )

        self.scroll.add_widget(
            self.grid
        )

        self.main.add_widget(
            self.scroll
        )

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

        self.main.add_widget(back)

        self.add_widget(
            self.main
        )

    def on_pre_enter(self, *args):

        self.refresh_grid()

    def refresh_grid(self):

        self.grid.clear_widgets()

        # Header

        self.grid.add_widget(
            HeaderCard(
                text="DAY",
                width=self.day_width
            )
        )

        for time in TIMES:

            self.grid.add_widget(
                HeaderCard(
                    text=time,
                    width=self.time_width
                )
            )

        # Find dates for the current week

        today = date.today()

        monday = today - timedelta(
            days=today.weekday()
        )

        day_names = [
            "MONDAY",
            "TUESDAY",
            "WEDNESDAY",
            "THURSDAY",
            "FRIDAY"
        ]

        for day_index, day in enumerate(day_names):

            actual_date = (
                monday
                + timedelta(days=day_index)
            )

            date_string = actual_date.isoformat()

            self.grid.add_widget(
                HeaderCard(
                    text=(
                        f"{day}\n"
                        f"{actual_date.strftime('%d %b')}"
                    ),
                    width=self.day_width
                )
            )

            subjects = TIMETABLE[day]

            for index, subject in enumerate(subjects):

                time = TIMES[index]

                if subject == "":

                    card = SubjectCard(
                        subject=""
                    )

                    card.width = self.time_width

                    self.grid.add_widget(
                        card
                    )

                elif subject == "LUNCH BREAK":

                    card = SubjectCard(
                        subject="LUNCH BREAK"
                    )

                    card.width = self.time_width

                    self.grid.add_widget(
                        card
                    )

                else:

                    key = (
                        f"{date_string}|"
                        f"{subject}|"
                        f"{time}"
                    )

                    record = (
                        App.get_running_app()
                        .attendance_data
                        .get(key)
                    )

                    if record:

                        if record["status"] == "present":

                            text = (
                                subject
                                + "\n\nPRESENT"
                            )

                        else:

                            text = (
                                subject
                                + "\n\nABSENT"
                            )

                        button = Button(
                            text=text,
                            font_size=12,
                            bold=True,
                            size_hint=(
                                None,
                                None
                            ),
                            width=self.time_width,
                            height=85
                        )

                    else:

                        button = Button(
                            text=subject,
                            font_size=12,
                            bold=True,
                            size_hint=(
                                None,
                                None
                            ),
                            width=self.time_width,
                            height=85
                        )

                    button.bind(
                        on_press=lambda x,
                        s=subject,
                        d=date_string,
                        t=time:
                        self.open_attendance(
                            s,
                            d,
                            t
                        )
                    )

                    self.grid.add_widget(
                        button
                    )

        self.grid.height = (
            55
            + (85 * 5)
            + (5 * 6)
        )

    def open_attendance(
        self,
        subject,
        class_date,
        time
    ):

        popup = AttendancePopup(
            subject=subject,
            class_date=class_date,
            time=time
        )

        popup.open()


# ============================================================
# APP
# ============================================================

class CollegeApp(App):

    def build(self):

        self.attendance_data = (
            load_attendance()
        )

        manager = ScreenManager()

        manager.add_widget(
            HomeScreen(
                name="home"
            )
        )

        manager.add_widget(
            TimetableScreen(
                name="timetable"
            )
        )

        manager.add_widget(
            SubjectsScreen(
                name="subjects"
            )
        )

        manager.add_widget(
            SubjectDetailsScreen(
                name="subject_details"
            )
        )

        return manager


CollegeApp().run()
