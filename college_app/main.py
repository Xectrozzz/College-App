import json
import os
from datetime import date, timedelta, datetime
from kivy.config import Config

# Desktop preview resolution — same 9:16 ratio as 1080x1920
Config.set("graphics", "width", "540")
Config.set("graphics", "height", "960")
Config.set("graphics", "resizable", "0")
Config.set("graphics", "fullscreen", "0")
from kivy.core.window import Window

# ---------------------------------------------------------
# PROPORTIONAL UI SCALING
# Design values are written for 1080x1920.
# Desktop preview automatically scales them to 540x960.
# ---------------------------------------------------------
DESIGN_WIDTH = 1080.0
DESIGN_HEIGHT = 1920.0
UI_SCALE = Window.width / DESIGN_WIDTH

def ui(value):
    return value * UI_SCALE

def fs(value):
    return value * UI_SCALE

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup


# ============================================================
# ACCESSIBILITY / PINCH ZOOM
# ============================================================

MIN_UI_ZOOM = 0.85
MAX_UI_ZOOM = 1.35


def _distance(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return (dx * dx + dy * dy) ** 0.5


def _set_ui_zoom(root, zoom):
    zoom = max(MIN_UI_ZOOM, min(MAX_UI_ZOOM, zoom))

    def visit(widget):
        if hasattr(widget, "font_size"):
            if not hasattr(widget, "_ui_base_font_size"):
                widget._ui_base_font_size = widget.font_size
            widget.font_size = widget._ui_base_font_size * zoom

        for child in widget.children:
            visit(child)

    visit(root)

    if hasattr(root, "_ui_zoom"):
        root._ui_zoom = zoom



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
# SUBJECT INFORMATION
# ============================================================
# Teacher names are intentionally blank. They can be entered and
# changed from the Subject Details screen and are saved locally.
SUBJECT_INFO = {
    "MATHEMATICS": {
        "credits": 3,
        "teacher": "",
        "syllabus": [
            "Three Dimensional Geometry: Directional cosines and ratios, angle between two lines, equations of straight lines, coplanar lines, equation of plane, shortest distance between lines and planes, sphere, tangent plane, and plane section of a sphere.",
            "Matrices and Linear Programming: Inverse of a square matrix using adjoint matrix, rank of a matrix, elementary row and column transformations, Gauss elimination, consistency and inconsistency of linear equations, formulation of LPP, graphical method, and simplex method.",
            "Statistics: Measures of central tendency (arithmetic mean, median, mode), measures of dispersion (standard deviation and variance), regression and correlation, and curve fitting by least squares for a straight line and parabola.",
            "Calculus: Tangent and normal, maxima and minima of functions of one variable, curvature, Taylor's and Maclaurin's expansion, reduction formulae, and calculation of area using integrals (arc length and area under a curve)."
        ]
    },
    "ENGLISH & CORPORATE COMMUNICATION": {
        "credits": 3,
        "teacher": "",
        "syllabus": [
            "Introduction to Communication: Principles of communication, channels of communication, inclusive communication practices, speaking and listening skills.",
            "Introduction to Corporate Communication: Different forms of corporate communication, factors influencing corporate communication, interpersonal communication, and communication for effective leadership.",
            "Verbal and Non-verbal Communication: Reading and writing skills for corporate communication, nonverbal communication in corporate settings, interviews and group discussions, and presentation skills.",
            "Features of Corporate Communication: Levels of corporate communication, barriers to communication, organizational communication, and dos and don'ts of corporate communication.",
            "Strategies of Communication: Negotiating conflict and management, crisis communication, emotional intelligence and stress management, and ethics in corporate communication.",
            "Indicative activities: Ice breaker, oral presentation, listening activity, role play, group discussion, writing activities, peer interview, PPT presentation, debate, corporate meeting, case study, and interviewing strangers."
        ]
    },
    "MATERIALS & CONSTRUCTION - I": {
        "credits": 4,
        "teacher": "",
        "syllabus": [
            "Building Materials Overview: Types, properties, uses, standards, composition, and application of basic building materials such as brick, stone, binding materials, and mortar.",
            "Building Elements and Structural Systems: Components from foundation to roof and a general idea of load transmission in load-bearing and framed structures, including their advantages, disadvantages, and suitability.",
            "Foundation Types and Construction Details: Various types of foundation with emphasis on load-bearing walls, plinth filling, steps, and related construction details.",
            "Masonry Construction Techniques: Brick and stone masonry including walls, piers, staircases, roofs, domes, and types of bonds such as English and Flemish bonds.",
            "Architectural Supports and Construction Tools: Introduction to lintels and arches and to basic tools and equipment used in construction."
        ]
    },
    "HISTORY OF ARCHITECTURE - I": {
        "credits": 4,
        "teacher": "",
        "syllabus": [
            "Understanding Early Settlements and Architecture Across Cultures (2600 BCE – 500 BCE): Indus Valley Civilization, early Aryan architecture of the Ganga Basin, and Vedic principles of planning including Vastu Purusha Mandala, cardinal orientation, and cosmic order.",
            "Architecture of Ancient Civilizations (3000 BCE – 400 CE): Egypt, Mesopotamia, Persia, Greece, and Rome, including their construction techniques, architectural typologies, structural systems, monuments, and symbolic significance.",
            "Inception and Development of Buddhist Architecture in India and Abroad (500 BCE – 1200 CE): Stupas, viharas, chaityas, rock-cut architecture, Southeast Asian adaptations, Chinese and Japanese wooden architecture, and the spread of forms through the Silk Route.",
            "Development of Hindu Temple Architecture (200 BCE – 1300 CE): Vedic and Buddhist planning influences, garbhagriha, regional Nagara, Dravida and Vesara styles, temple towns, stepwells, and the spread of Hindu architecture abroad."
        ]
    },
    "GRAPHICS - I": {
        "credits": 2,
        "teacher": "",
        "syllabus": [
            "Introduction to architectural drafting techniques, lettering, and use of drawing instruments.",
            "Scale construction (plain and diagonal) and 2D drawings in reduced and enlarged scales.",
            "Orthographic projections of points, lines, planes, and solids with reference to HP and VP; simple compositions in plan and elevation.",
            "Sections and true sections of solids in various positions and surface development of standard solids.",
            "Isometric and axonometric projections of solids and building elements using isometric scale.",
            "Graphical symbols for materials, furniture, and services; presentation drawings with rendering and line quality.",
            "Intersections and interpenetration of solids; complex sections and development of composite 3D forms."
        ]
    },
    "BASIC DESIGN & VISUAL ARTS": {
        "credits": 9,
        "teacher": "",
        "syllabus": [
            "Introduction to Design/Visual Arts and related terminologies and concepts.",
            "Elements of Design: Properties, qualities, and characteristics of point, line, direction, plane, shape, form, color, texture, space, light, and shadow.",
            "Principles of Design: Scale, proportion, balance, harmony, rhythm, contrast, and related principles.",
            "Compositions: Application of design elements and principles in two-dimensional and three-dimensional compositions.",
            "Expression in Art and Architecture: Expression in performing and visual arts and architecture with social components.",
            "Visual Appraisal: Evaluation of design forms for visual character, interplay of light and shadow, solids and voids, spatial temperature, and material qualities.",
            "Interdisciplinary Connections: Allied visual and performing arts and their relationship to the built environment."
        ]
    },
    "SPORTS - I": {
        "credits": 0,
        "teacher": "",
        "syllabus": [
            "The supplied 2025 B.Arch syllabus PDF lists SAA101 Health Information & Sports-I as a Semester I course with 0 credits and 2 practical hours, but does not provide a detailed course-syllabus section for it in the supplied document."
        ]
    }
}


def get_teacher_file():
    app = App.get_running_app()
    return os.path.join(app.user_data_dir, "teachers.json")


def load_teachers():
    filename = get_teacher_file()
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
    except Exception as e:
        print("Could not load teachers:", e)
    return {}


def save_teachers(data):
    filename = get_teacher_file()
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print("Could not save teachers:", e)


def get_teacher(subject):
    saved = load_teachers()
    return saved.get(subject, SUBJECT_INFO.get(subject, {}).get("teacher", ""))


def get_subject_assignments(subject):
    app = App.get_running_app()
    filename = os.path.join(app.user_data_dir, "assignments.json")
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                assignments = json.load(file)
                if isinstance(assignments, list):
                    return [
                        item for item in assignments
                        if item.get("subject") == subject
                    ]
    except Exception as e:
        print("Could not load subject assignments:", e)
    return []


# ============================================================
# CLASS CANCELLATIONS
# ============================================================

def get_cancellation_file():
    app = App.get_running_app()
    return os.path.join(app.user_data_dir, "cancellations.json")


def load_cancellations():
    filename = get_cancellation_file()
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
    except Exception as e:
        print("Could not load cancellations:", e)
    return {}


def save_cancellations(data):
    filename = get_cancellation_file()
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        app = App.get_running_app()
        if app is not None:
            app.cancellations_data = data
    except Exception as e:
        print("Could not save cancellations:", e)


def cancellation_key(class_date, subject, time):
    return f"{class_date}|{subject}|{time}"


def is_class_cancelled(class_date, subject, time):
    app = App.get_running_app()
    cancellations = getattr(app, "cancellations_data", None)
    if cancellations is None:
        cancellations = load_cancellations()
    return cancellation_key(class_date, subject, time) in cancellations


# ============================================================
# SEMESTER CALENDAR
# ============================================================

SEMESTER_START = date(2026, 8, 24)
LAST_FORMAL_TEACHING = date(2026, 12, 5)

MIDSEM_START = date(2026, 10, 1)
MIDSEM_END = date(2026, 10, 10)

ENDSEM_START = date(2026, 12, 7)
ENDSEM_END = date(2026, 12, 15)

NO_INSTRUCTION_START = date(2026, 11, 9)
NO_INSTRUCTION_END = date(2026, 11, 13)

HOLIDAYS = {
    date(2026, 8, 26): "HOLIDAY\\nId-e-Milad",
    date(2026, 10, 2): "HOLIDAY\\nMahatma Gandhi Birthday",
    date(2026, 10, 20): "HOLIDAY\\nDussehra",
    date(2026, 11, 8): "HOLIDAY\\nDiwali",
    date(2026, 11, 24): "HOLIDAY\\nGuru Nanak Birthday",
    date(2026, 12, 25): "HOLIDAY\\nChristmas Day",
    date(2027, 1, 26): "HOLIDAY\\nRepublic Day",
}

# Saturday instruction days from the academic calendar.
# The weekly grid remains Monday-Friday; these are kept here so
# the calendar logic knows about them for future Saturday support.
SPECIAL_SATURDAYS = {
    date(2026, 8, 29): "MONDAY",
    date(2026, 9, 5): "TUESDAY",
    date(2026, 9, 12): "WEDNESDAY",
    date(2026, 9, 19): "THURSDAY",
    date(2026, 9, 26): "FRIDAY",
    date(2026, 10, 17): "MONDAY",
    date(2026, 10, 24): "TUESDAY",
    date(2026, 10, 31): "WEDNESDAY",
    date(2026, 11, 21): "THURSDAY",
    date(2026, 11, 28): "TUESDAY",
    date(2026, 12, 5): "TUESDAY",
}


def get_semester_status(class_date):
    if class_date in HOLIDAYS:
        return HOLIDAYS[class_date]

    if NO_INSTRUCTION_START <= class_date <= NO_INSTRUCTION_END:
        return "NO INSTRUCTION"

    if MIDSEM_START <= class_date <= MIDSEM_END:
        return "MID-SEM EXAM"

    if ENDSEM_START <= class_date <= ENDSEM_END:
        return "END-SEM EXAM"

    if class_date < SEMESTER_START:
        return "SEMESTER NOT STARTED"

    if class_date > LAST_FORMAL_TEACHING:
        return "TEACHING ENDED"

    return None


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
# UI THEME
# ============================================================

UI_BG = (0.045, 0.055, 0.070, 1)
UI_SURFACE = (0.125, 0.140, 0.170, 1)
UI_SURFACE_2 = (0.170, 0.185, 0.220, 1)
UI_TEXT = (0.98, 0.985, 1.0, 1)
UI_MUTED = (0.78, 0.81, 0.87, 1)
UI_ACCENT = (0.30, 0.55, 0.95, 1)
UI_SUCCESS = (0.18, 0.68, 0.38, 1)
UI_DANGER = (0.85, 0.28, 0.30, 1)
UI_WARNING = (0.95, 0.67, 0.22, 1)

Window.clearcolor = UI_BG


def rounded_background(widget, color=UI_SURFACE, radius=16):
    """Give a Kivy layout a clean rounded surface."""
    with widget.canvas.before:
        Color(*color)
        widget._ui_background = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=[radius]
        )
    widget.bind(
        pos=lambda *_: setattr(widget._ui_background, 'pos', widget.pos),
        size=lambda *_: setattr(widget._ui_background, 'size', widget.size)
    )
    return widget


class AppButton(Button):
    """Rounded, modern button used throughout the app."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Keep explicit timetable colors when supplied later.
        if 'background_color' not in kwargs:
            label = (self.text or '').upper()
            if 'PRESENT' in label:
                self.background_color = UI_SUCCESS
            elif 'ABSENT' in label:
                self.background_color = UI_DANGER
            elif 'ADD' in label:
                self.background_color = UI_ACCENT
            elif label in ('HOME', 'BACK', 'CANCEL'):
                self.background_color = UI_SURFACE_2
            elif label in ('TODAY',):
                self.background_color = UI_ACCENT
            else:
                self.background_color = UI_SURFACE

        self.color = UI_TEXT
        self.bold = True
        self.background_normal = ''
        self.background_down = ''
        self.background_disabled_normal = ''
        self.background_disabled_down = ''
        self.border = (0, 0, 0, 0)
        self.padding = (14, 10)

        with self.canvas.before:
            self._button_color = Color(*self.background_color)
            self._button_background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[18]
            )

        self.bind(
            pos=self._update_button_bg,
            size=self._update_button_bg,
            background_color=self._update_button_color,
            disabled=self._update_disabled
        )
        self._update_disabled()

    def _update_button_bg(self, *_):
        self._button_background.pos = self.pos
        self._button_background.size = self.size

    def _update_button_color(self, *_):
        if self.disabled:
            self._button_color.rgba = (
                self.background_color[0],
                self.background_color[1],
                self.background_color[2],
                0.30
            )
        else:
            self._button_color.rgba = self.background_color

    def _update_disabled(self, *_):
        self.color = UI_MUTED if self.disabled else UI_TEXT
        self._update_button_color()


# ============================================================
# SUBJECT CARD
# ============================================================

class SubjectCard(Label):

    def __init__(self, subject="", **kwargs):

        super().__init__(**kwargs)

        self.subject = subject

        self.size_hint = (None, None)
        self.width = 145
        self.height = 88

        self.color = UI_TEXT
        self.halign = "center"
        self.valign = "middle"

        self.text_size = (
            self.width - 12,
            self.height - 10
        )

        if subject == "LUNCH BREAK":

            self.text = subject
            self.bold = True
            self.font_size=fs(60)

            self.card_color = (
                0.95,
                0.75,
                0.25,
                1
            )

        elif subject:

            self.text = subject
            self.bold = True
            self.font_size=fs(60)

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
            self.font_size=fs(60)

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
                radius=[18]
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

        self.height = 54

        self.color = UI_TEXT
        self.bold = True
        self.font_size=fs(22)

        self.halign = "center"
        self.valign = "middle"

        with self.canvas.before:

            Color(*UI_SURFACE_2)

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
# BOTTOM NAVIGATION
# ============================================================

class BottomNav(BoxLayout):
    """Persistent primary navigation designed for narrow portrait screens."""

    def __init__(self, current="home", **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=4,
            padding=(5, 5),
            size_hint_y=None,
            height=76,
            **kwargs
        )
        rounded_background(self, UI_SURFACE, 18)

        items = [
            ("home", "HOME"),
            ("subjects", "SUBJECTS"),
            ("assignments", "TASKS"),
            ("calendar", "CALENDAR"),
        ]

        for screen_name, label in items:
            button = AppButton(
                text=label,
                font_size=fs(15),
                bold=True,
                background_color=(
                    UI_ACCENT if screen_name == current else UI_SURFACE_2
                ),
                size_hint_x=1,
            )
            button.bind(on_press=lambda x, s=screen_name: self.go(s))
            self.add_widget(button)

    def go(self, screen_name):
        if self.parent and self.parent.parent:
            manager = self.parent.parent.manager
            if manager:
                manager.current = screen_name


class AttendanceRing(BoxLayout):
    """Safe portrait attendance indicator using standard Kivy widgets only."""

    def __init__(self, percentage=0, **kwargs):
        super().__init__(orientation="vertical", spacing=0, padding=(4, 2), **kwargs)
        self.size_hint = (None, None)
        self.size = (112, 112)
        self.percentage = 0
        self.value_label = Label(
            text="0%",
            font_size=fs(27),
            bold=True,
            color=UI_TEXT,
            halign="center",
            valign="middle",
        )
        self.add_widget(self.value_label)
        self.status_label = Label(
            text="ATTENDANCE",
            font_size=fs(10),
            bold=True,
            color=UI_MUTED,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=20,
        )
        self.add_widget(self.status_label)
        self.set_percentage(percentage)

    def set_percentage(self, percentage):
        self.percentage = max(0, min(100, float(percentage)))
        self.value_label.text = f"{self.percentage:.0f}%"
        self.value_label.color = UI_SUCCESS if self.percentage >= REQUIRED_ATTENDANCE else UI_DANGER


def make_stat_box(value, label, accent=UI_ACCENT):
    box = BoxLayout(orientation="vertical", padding=(5,4), spacing=0)
    rounded_background(box, UI_SURFACE_2, 12)
    box.add_widget(Label(text=value, font_size=fs(21), bold=True, color=accent, size_hint_y=None, height=34))
    box.add_widget(Label(text=label, font_size=fs(10), bold=True, color=UI_MUTED, size_hint_y=None, height=20))
    return box


def make_link_card(title, subtitle, action, accent=UI_ACCENT, height=78):
    card = AppButton(
        text=f"{title}\n{subtitle}",
        font_size=fs(17),
        bold=True,
        halign="left",
        valign="middle",
        background_color=UI_SURFACE,
        size_hint_y=None,
        height=height,
    )
    card.text_size = (None, height - 12)
    card.bind(on_press=action)
    return card


# ============================================================
# HOME SCREEN
# ============================================================

# ============================================================

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.quick_attendance_event = None
        self.quick_attendance_subject = None
        self.quick_attendance_time = None
        self.quick_attendance_date = None

        self.main = BoxLayout(
            orientation="vertical",
            padding=(10, 8),
            spacing=7
        )
        rounded_background(self.main, UI_BG, 0)

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=72
        )
        header.add_widget(Label(
            text="COLLEGE APP",
            font_size=fs(60),
            bold=True,
            color=UI_TEXT,
            size_hint_y=None,
            height=67
        ))
        self.date_label = Label(
            text="", font_size=fs(15), color=UI_MUTED,
            size_hint_y=None, height=23
        )
        header.add_widget(self.date_label)
        self.main.add_widget(header)

        self.scroll = ScrollView(do_scroll_y=True, bar_width=4)
        content = BoxLayout(
            orientation="vertical", spacing=8, padding=(0, 1),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        # Attendance hero
        self.attendance_card = BoxLayout(
            orientation="horizontal", padding=(12, 10), spacing=10,
            size_hint_y=None, height=235
        )
        rounded_background(self.attendance_card, UI_SURFACE, 18)

        self.attendance_ring = AttendanceRing(percentage=0)
        self.attendance_card.add_widget(self.attendance_ring)

        att_info = BoxLayout(orientation="vertical", spacing=2)
        att_info.add_widget(Label(
            text="OVERALL ATTENDANCE", font_size=fs(16), bold=True,
            color=UI_MUTED, halign="left", size_hint_y=None, height=24
        ))
        self.attendance_summary = Label(
            text="No classes marked yet", font_size=fs(25), bold=True,
            color=UI_TEXT, halign="left", valign="middle",
            size_hint_y=None, height=42
        )
        self.attendance_summary.bind(size=lambda i,v: setattr(i,"text_size",v))
        att_info.add_widget(self.attendance_summary)
        att_info.add_widget(Label(
            text="Keep at least 75% to stay safe", font_size=fs(14),
            color=UI_MUTED, halign="left", size_hint_y=None, height=25
        ))

        self.quick_attendance_label = Label(
            text="Checking for a current class...",
            font_size=fs(13),
            color=UI_TEXT,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=34,
        )
        self.quick_attendance_label.bind(
            size=lambda i, v: setattr(i, "text_size", v)
        )
        att_info.add_widget(self.quick_attendance_label)

        quick_buttons = BoxLayout(orientation="horizontal", spacing=5, size_hint_y=None, height=43)
        self.quick_present_button = AppButton(text="PRESENT", font_size=fs(14), background_color=UI_SUCCESS)
        self.quick_absent_button = AppButton(text="ABSENT", font_size=fs(14), background_color=UI_DANGER)
        self.quick_present_button.bind(on_press=lambda x: self.mark_home_attendance("present"))
        self.quick_absent_button.bind(on_press=lambda x: self.mark_home_attendance("absent"))
        quick_buttons.add_widget(self.quick_present_button)
        quick_buttons.add_widget(self.quick_absent_button)
        att_info.add_widget(quick_buttons)
        self.attendance_card.add_widget(att_info)
        content.add_widget(self.attendance_card)

        # Today card
        self.today_card = BoxLayout(
            orientation="vertical", padding=(12, 9), spacing=3,
            size_hint_y=None, height=270
        )
        rounded_background(self.today_card, UI_SURFACE, 18)
        self.today_title = Label(
            text="TODAY", font_size=fs(19), bold=True, color=UI_TEXT,
            size_hint_y=None, height=27
        )
        self.today_classes = Label(
            text="", font_size=fs(16), color=UI_TEXT, halign="left", valign="middle"
        )
        self.today_classes.bind(size=lambda i,v: setattr(i,"text_size",v))
        self.today_card.add_widget(self.today_title)
        self.today_card.add_widget(self.today_classes)
        today_open = AppButton(
            text="OPEN WEEKLY TIMETABLE  →", font_size=fs(14),
            background_color=UI_SURFACE_2, size_hint_y=None, height=38
        )
        today_open.bind(on_press=lambda x: setattr(self.manager, "current", "timetable"))
        self.today_card.add_widget(today_open)
        content.add_widget(self.today_card)

        # Quick links, two-column for portrait
        content.add_widget(Label(
            text="QUICK ACCESS", font_size=fs(17), bold=True, color=UI_TEXT,
            size_hint_y=None, height=24
        ))
        links = GridLayout(cols=2, spacing=7, size_hint_y=None, height=140)
        links.add_widget(make_link_card("MY SUBJECTS", "Attendance & details", lambda x: setattr(self.manager,"current","subjects"), height=125))
        links.add_widget(make_link_card("ASSIGNMENTS", "Tasks & due dates", lambda x: setattr(self.manager,"current","assignments"), height=125))
        content.add_widget(links)

        # Upcoming assignments preview
        self.upcoming_card = BoxLayout(
            orientation="vertical", padding=(12, 9), spacing=2,
            size_hint_y=None, height=190
        )
        rounded_background(self.upcoming_card, UI_SURFACE, 18)
        self.upcoming_title = Label(
            text="UPCOMING TASKS", font_size=fs(17), bold=True,
            color=UI_TEXT, size_hint_y=None, height=25
        )
        self.upcoming_text = Label(
            text="No assignments yet", font_size=fs(15), color=UI_MUTED,
            halign="left", valign="middle"
        )
        self.upcoming_text.bind(size=lambda i,v: setattr(i,"text_size",v))
        self.upcoming_card.add_widget(self.upcoming_title)
        self.upcoming_card.add_widget(self.upcoming_text)
        open_tasks = AppButton(
            text="VIEW ALL TASKS  →", font_size=fs(13), background_color=UI_SURFACE_2,
            size_hint_y=None, height=32
        )
        open_tasks.bind(on_press=lambda x: setattr(self.manager,"current","assignments"))
        self.upcoming_card.add_widget(open_tasks)
        content.add_widget(self.upcoming_card)

        # Week overview
        week_card = BoxLayout(orientation="vertical", padding=(12,10), spacing=6, size_hint_y=None, height=160)
        rounded_background(week_card, UI_SURFACE, 18)
        week_card.add_widget(Label(text="THIS WEEK", font_size=fs(17), bold=True, color=UI_TEXT, size_hint_y=None, height=25))
        week_info = BoxLayout(orientation="horizontal", spacing=7, size_hint_y=None, height=98)
        week_info.add_widget(make_stat_box("5", "WEEKDAYS", UI_ACCENT))
        week_info.add_widget(make_stat_box("75%", "TARGET", UI_WARNING))
        week_info.add_widget(make_stat_box("8", "TIME SLOTS", UI_SUCCESS))
        week_card.add_widget(week_info)
        content.add_widget(week_card)

        # Semester snapshot
        semester_card = BoxLayout(
            orientation="vertical", padding=(12,10), spacing=5,
            size_hint_y=None, height=145
        )
        rounded_background(semester_card, UI_SURFACE, 18)
        semester_card.add_widget(Label(
            text="SEMESTER SNAPSHOT", font_size=fs(17), bold=True,
            color=UI_TEXT, size_hint_y=None, height=26
        ))
        semester_card.add_widget(Label(
            text="Teaching: 24 Aug – 05 Dec 2026    •    Mid-sem: 01–10 Oct\n"
                 "No instruction: 09–13 Nov    •    End-sem: 07–15 Dec",
            font_size=fs(14), color=UI_MUTED, halign="left", valign="middle"
        ))
        semester_button = AppButton(
            text="OPEN ACADEMIC CALENDAR  →", font_size=fs(13),
            background_color=UI_SURFACE_2, size_hint_y=None, height=34
        )
        semester_button.bind(on_press=lambda x: setattr(self.manager, "current", "calendar"))
        semester_card.add_widget(semester_button)
        content.add_widget(semester_card)

        # Academic calendar shortcut
        content.add_widget(make_link_card(
            "ACADEMIC CALENDAR", "Semester dates, holidays & special Saturdays  →",
            lambda x: setattr(self.manager,"current","calendar"), height=105
        ))

        self.scroll.add_widget(content)
        self.main.add_widget(self.scroll)
        self.main.add_widget(BottomNav(current="home"))
        self.add_widget(self.main)

        self.quick_attendance_event = Clock.schedule_interval(lambda dt: self.update_dashboard(), 30)

    def on_pre_enter(self, *args):
        self.update_dashboard()

    def update_today_background(self, *args):
        # Kept for compatibility with older code paths.
        if hasattr(self, "today_background"):
            self.today_background.pos = self.today_card.pos
            self.today_background.size = self.today_card.size

    def update_attendance_background(self, *args):
        if hasattr(self, "attendance_background"):
            self.attendance_background.pos = self.attendance_card.pos
            self.attendance_background.size = self.attendance_card.size

    def get_local_now(self):
        try:
            timetable = self.manager.get_screen("timetable")
            return timetable.get_current_time()
        except Exception:
            return datetime.now()

    def parse_time_slot(self, time_slot):
        start_text, end_text = time_slot.split(" - ")
        start_hour, start_minute = map(int, start_text.split(":"))
        end_hour, end_minute = map(int, end_text.split(":"))
        return (
            start_hour * 60 + start_minute,
            end_hour * 60 + end_minute
        )

    def get_home_attendance_class(self):
        now = self.get_local_now()
        today = now.date()

        if get_semester_status(today):
            return None

        if today.weekday() == 5:
            timetable_day = SPECIAL_SATURDAYS.get(today)
        elif today.weekday() < 5:
            timetable_day = today.strftime("%A").upper()
        else:
            timetable_day = None

        if not timetable_day:
            return None

        subjects = TIMETABLE.get(timetable_day, [])
        current_minutes = now.hour * 60 + now.minute

        for index, subject in enumerate(subjects):
            if not subject or subject == "LUNCH BREAK":
                continue
            if is_class_cancelled(today.isoformat(), subject, TIMES[index]):
                continue
            try:
                start, end = self.parse_time_slot(TIMES[index])
            except Exception:
                continue
            if start <= current_minutes < end:
                return {
                    "subject": subject,
                    "time": TIMES[index],
                    "date": today.isoformat(),
                    "state": "IN PROGRESS"
                }

        for index, subject in enumerate(subjects):
            if not subject or subject == "LUNCH BREAK":
                continue
            try:
                start, end = self.parse_time_slot(TIMES[index])
            except Exception:
                continue
            minutes_until = start - current_minutes
            if 0 < minutes_until <= 15:
                return {
                    "subject": subject,
                    "time": TIMES[index],
                    "date": today.isoformat(),
                    "state": "STARTING SOON"
                }

        return None

    def update_quick_attendance(self):
        class_info = self.get_home_attendance_class()

        if class_info is None:
            self.quick_attendance_subject = None
            self.quick_attendance_time = None
            self.quick_attendance_date = None
            self.quick_attendance_label.text = (
                "No class to mark right now\n"
                "Attendance opens 15 minutes before class."
            )
            self.quick_present_button.disabled = True
            self.quick_absent_button.disabled = True
            return

        subject = class_info["subject"]
        time = class_info["time"]
        class_date = class_info["date"]
        state = class_info["state"]

        self.quick_attendance_subject = subject
        self.quick_attendance_time = time
        self.quick_attendance_date = class_date

        key = f"{class_date}|{subject}|{time}"
        record = App.get_running_app().attendance_data.get(key)

        if record:
            status = record.get("status", "").upper()
            self.quick_attendance_label.text = (
                f"{state}  •  {subject}\n"
                f"{time}  •  MARKED {status}"
            )
            self.quick_present_button.disabled = True
            self.quick_absent_button.disabled = True
        else:
            self.quick_attendance_label.text = (
                f"{state}  •  {subject}\n"
                f"{time}  •  Tap PRESENT or ABSENT"
            )
            self.quick_present_button.disabled = False
            self.quick_absent_button.disabled = False

    def mark_home_attendance(self, status):
        if not self.quick_attendance_subject:
            return

        app = App.get_running_app()
        key = (
            f"{self.quick_attendance_date}|"
            f"{self.quick_attendance_subject}|"
            f"{self.quick_attendance_time}"
        )

        app.attendance_data[key] = {
            "subject": self.quick_attendance_subject,
            "date": self.quick_attendance_date,
            "time": self.quick_attendance_time,
            "status": status
        }
        save_attendance(app.attendance_data)
        self.update_dashboard()

        try:
            timetable = self.manager.get_screen("timetable")
            timetable.refresh_grid()
        except Exception:
            pass

    def update_dashboard(self):
        now = self.get_local_now()
        today = now.date()

        self.date_label.text = today.strftime("%A, %d %B %Y")
        self.today_title.text = today.strftime("TODAY • %A").upper()

        status = get_semester_status(today)

        if status:
            self.today_classes.text = status
        else:
            if today.weekday() == 5:
                timetable_day = SPECIAL_SATURDAYS.get(today)
            elif today.weekday() < 5:
                timetable_day = today.strftime("%A").upper()
            else:
                timetable_day = None

            if timetable_day is None:
                self.today_classes.text = "NO CLASSES"
            else:
                subjects = TIMETABLE.get(timetable_day, [])
                classes = []
                for index, subject in enumerate(subjects):
                    if subject and subject != "LUNCH BREAK":
                        if not is_class_cancelled(today.isoformat(), subject, TIMES[index]):
                            classes.append(f"{TIMES[index]}   {subject}")

                if not classes:
                    self.today_classes.text = "NO CLASSES"
                elif len(classes) <= 3:
                    self.today_classes.text = "\n".join(classes)
                else:
                    self.today_classes.text = (
                        "\n".join(classes[:3])
                        + f"\n+ {len(classes) - 3} more"
                    )

        self.update_attendance_summary()
        self.update_quick_attendance()
        self.update_upcoming_tasks()

    def update_attendance_summary(self):
        total_present = 0
        total_absent = 0
        for subject in SUBJECTS:
            present, absent, total, percentage = get_subject_stats(subject)
            total_present += present
            total_absent += absent

        total = total_present + total_absent
        if total == 0:
            self.attendance_summary.text = "No classes marked yet"
            self.attendance_ring.set_percentage(0)
            return

        percentage = (total_present / total) * 100
        self.attendance_summary.text = f"{percentage:.1f}%  •  {total_present}/{total}"
        self.attendance_ring.set_percentage(percentage)

    def update_upcoming_tasks(self):
        try:
            assignments_screen = self.manager.get_screen("assignments")
            assignments = assignments_screen.load_assignments()
            pending = [a for a in assignments if not a.get("completed", False)]
            pending.sort(key=lambda a: a.get("due_date", "9999-99-99"))
            if not pending:
                self.upcoming_text.text = "Nothing pending — you're all caught up."
                return
            lines = []
            for a in pending[:3]:
                lines.append(f"• {a.get('title','Untitled')}  ·  {a.get('due_date','No date')}")
            if len(pending) > 3:
                lines.append(f"+ {len(pending)-3} more")
            self.upcoming_text.text = "\n".join(lines)
        except Exception:
            self.upcoming_text.text = "No assignments yet"

    def show_calendar_info(self):
        # Kept for compatibility: the calendar is now a full tab.
        if self.manager:
            self.manager.current = "calendar"

# ============================================================
# SUBJECTS SCREEN
# ============================================================

class SubjectCardButton(ButtonBehavior, FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rounded_background(self, UI_SURFACE, 14)


class SubjectsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main = BoxLayout(orientation="vertical", padding=(18, 14), spacing=12)
        rounded_background(main, UI_BG, 0)

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=82, spacing=2)
        header.add_widget(Label(
            text="MY SUBJECTS",
            font_size=fs(30),
            bold=True,
            color=UI_TEXT,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=42,
        ))
        header.add_widget(Label(
            text="Attendance and course details",
            font_size=fs(16),
            color=UI_MUTED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=30,
        ))
        main.add_widget(header)

        self.scroll = ScrollView(do_scroll_y=True, bar_width=5, scroll_type=["bars", "content"])
        self.subjects_box = BoxLayout(
            orientation="vertical",
            spacing=14,
            padding=(0, 2, 0, 20),
            size_hint_y=None,
        )
        self.subjects_box.bind(minimum_height=self.subjects_box.setter("height"))
        self.scroll.add_widget(self.subjects_box)
        main.add_widget(self.scroll)
        main.add_widget(BottomNav(current="subjects"))
        self.add_widget(main)

    def on_pre_enter(self, *args):
        self.refresh_subjects()

    def refresh_subjects(self):
        self.subjects_box.clear_widgets()

        # Compact overall summary. Individual subject attendance is the main focus.
        total_present = 0
        total_marked = 0
        total_credits = sum(SUBJECT_INFO.get(s, {}).get("credits", 0) for s in SUBJECTS)
        for subject in SUBJECTS:
            p, a, total, pct = get_subject_stats(subject)
            total_present += p
            total_marked += total
        overall = (total_present / total_marked * 100) if total_marked else 0

        summary = BoxLayout(
            orientation="horizontal",
            padding=(16, 12),
            spacing=12,
            size_hint_y=None,
            height=112,
        )
        rounded_background(summary, UI_SURFACE, 20)

        overview_left = BoxLayout(orientation="vertical", spacing=1)
        overview_left.add_widget(Label(
            text="OVERALL ATTENDANCE",
            font_size=fs(14),
            bold=True,
            color=UI_MUTED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=24,
        ))
        overview_left.add_widget(Label(
            text=f"{overall:.0f}%",
            font_size=fs(30),
            bold=True,
            color=UI_SUCCESS if overall >= REQUIRED_ATTENDANCE else UI_DANGER,
            halign="left",
            valign="middle",
        ))
        summary.add_widget(overview_left)

        course_info = BoxLayout(orientation="vertical", spacing=1, size_hint_x=None, width=145)
        course_info.add_widget(Label(
            text=f"{total_credits} CREDITS",
            font_size=fs(15),
            bold=True,
            color=UI_TEXT,
            halign="right",
            valign="middle",
            size_hint_y=None,
            height=25,
        ))
        course_info.add_widget(Label(
            text=f"{len(SUBJECTS)} subjects",
            font_size=fs(14),
            color=UI_MUTED,
            halign="right",
            valign="middle",
        ))
        summary.add_widget(course_info)
        self.subjects_box.add_widget(summary)

        for subject in SUBJECTS:
            present, absent, total, percentage = get_subject_stats(subject)
            info = SUBJECT_INFO.get(subject, {})
            credits = info.get("credits", "—")
            teacher = get_teacher(subject) or "Teacher not set"

            # Large, accessible card. The whole card is tappable.
            card = SubjectCardButton(size_hint_y=None, height=210)
            rounded_background(card, UI_SURFACE, 22)

            name = Label(
                text=subject,
                font_size=fs(21),
                bold=True,
                color=UI_TEXT,
                halign="left",
                valign="middle",
                size_hint=(0.72, None),
                height=54,
                pos_hint={"x": 0.045, "top": 0.91},
            )
            name.bind(size=lambda i, v: setattr(i, "text_size", v))
            card.add_widget(name)

            credit = Label(
                text=f"{credits} CREDITS",
                font_size=fs(14),
                bold=True,
                color=UI_MUTED,
                halign="right",
                valign="middle",
                size_hint=(0.25, None),
                height=30,
                pos_hint={"right": 0.955, "top": 0.90},
            )
            credit.bind(size=lambda i, v: setattr(i, "text_size", v))
            card.add_widget(credit)

            # Attendance is deliberately the largest visual element after the subject name.
            if total:
                attendance_text = f"{percentage:.0f}%"
                count_text = f"{present} present  •  {absent} absent  •  {total} marked"
                att_color = UI_SUCCESS if percentage >= REQUIRED_ATTENDANCE else UI_DANGER
            else:
                attendance_text = "—"
                count_text = "No attendance marked yet"
                att_color = UI_MUTED

            attendance_title = Label(
                text="ATTENDANCE",
                font_size=fs(14),
                bold=True,
                color=UI_MUTED,
                halign="left",
                valign="middle",
                size_hint=(0.45, None),
                height=24,
                pos_hint={"x": 0.045, "y": 0.34},
            )
            attendance_title.bind(size=lambda i, v: setattr(i, "text_size", v))
            card.add_widget(attendance_title)

            att_label = Label(
                text=attendance_text,
                font_size=fs(34),
                bold=True,
                color=att_color,
                halign="left",
                valign="middle",
                size_hint=(0.40, None),
                height=50,
                pos_hint={"x": 0.045, "y": 0.12},
            )
            att_label.bind(size=lambda i, v: setattr(i, "text_size", v))
            card.add_widget(att_label)

            count_label = Label(
                text=count_text,
                font_size=fs(14),
                color=UI_MUTED,
                halign="left",
                valign="middle",
                size_hint=(0.62, None),
                height=26,
                pos_hint={"x": 0.045, "y": 0.035},
            )
            count_label.bind(size=lambda i, v: setattr(i, "text_size", v))
            card.add_widget(count_label)

            teacher_label = Label(
                text=teacher,
                font_size=fs(14),
                color=UI_MUTED,
                halign="right",
                valign="middle",
                size_hint=(0.36, None),
                height=28,
                pos_hint={"right": 0.955, "y": 0.28},
            )
            teacher_label.bind(size=lambda i, v: setattr(i, "text_size", v))
            card.add_widget(teacher_label)

            tap_label = Label(
                text="VIEW DETAILS  ›",
                font_size=fs(13),
                bold=True,
                color=UI_ACCENT,
                halign="right",
                valign="middle",
                size_hint=(0.34, None),
                height=24,
                pos_hint={"right": 0.955, "y": 0.055},
            )
            tap_label.bind(size=lambda i, v: setattr(i, "text_size", v))
            card.add_widget(tap_label)

            card.bind(on_press=lambda x, s=subject: self.open_subject(s))
            self.subjects_box.add_widget(card)

        guide = BoxLayout(
            orientation="vertical",
            padding=(16, 14),
            spacing=5,
            size_hint_y=None,
            height=120,
        )
        rounded_background(guide, UI_SURFACE, 20)
        guide.add_widget(Label(
            text="SUBJECT DETAILS",
            font_size=fs(17),
            bold=True,
            color=UI_TEXT,
            size_hint_y=None,
            height=27,
            halign="left",
        ))
        guide.add_widget(Label(
            text="Tap a subject to view its syllabus, teacher, credits, attendance and class history.",
            font_size=fs(14),
            color=UI_MUTED,
            halign="left",
            valign="middle",
        ))
        self.subjects_box.add_widget(guide)

    def open_subject(self, subject):
        details_screen = self.manager.get_screen("subject_details")
        details_screen.show_subject(subject)
        self.manager.current = "subject_details"


# ============================================================
# SUBJECT DETAILS
# ============================================================

class SubjectDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_subject = None

        main = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=10
        )
        rounded_background(main, UI_BG, 0)

        self.title = Label(
            text="Subject",
            font_size=fs(31),
            bold=True,
            color=UI_TEXT,
            size_hint_y=None,
            height=50
        )
        main.add_widget(self.title)

        scroll = ScrollView(
            do_scroll_y=True
        )

        self.content_box = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=5,
            size_hint_y=None
        )
        self.content_box.bind(
            minimum_height=self.content_box.setter("height")
        )

        # Teacher section
        teacher_card = BoxLayout(
            orientation="vertical",
            spacing=5,
            padding=10,
            size_hint_y=None,
            height=105
        )

        self.teacher_label = Label(
            text="Teacher: Not set",
            font_size=fs(30),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=45
        )
        self.teacher_label.bind(
            size=lambda instance, value: setattr(
                instance, "text_size", value
            )
        )

        edit_teacher = AppButton(
            text="EDIT TEACHER NAME",
            font_size=fs(20),
            bold=True,
            size_hint_y=None,
            height=45
        )
        edit_teacher.bind(
            on_press=lambda x: self.open_teacher_editor()
        )

        teacher_card.add_widget(self.teacher_label)
        teacher_card.add_widget(edit_teacher)
        self.content_box.add_widget(teacher_card)

        self.attendance_label = Label(
            text="",
            font_size=fs(19),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=138
        )
        self.attendance_label.bind(
            size=lambda instance, value: setattr(
                instance, "text_size", value
            )
        )
        self.content_box.add_widget(self.attendance_label)

        syllabus_title = Label(
            text="SYLLABUS",
            font_size=fs(34),
            bold=True,
            halign="left",
            size_hint_y=None,
            height=35
        )
        self.content_box.add_widget(syllabus_title)

        self.syllabus_label = Label(
            text="",
            font_size=fs(20),
            halign="left",
            valign="top",
            size_hint_y=None
        )
        self.syllabus_label.bind(
            texture_size=lambda instance, value: setattr(
                instance, "height", value[1] + 15
            )
        )
        self.syllabus_label.bind(
            width=lambda instance, value: setattr(
                instance, "text_size", (value, None)
            )
        )
        self.content_box.add_widget(self.syllabus_label)

        assignments_title = Label(
            text="ASSIGNMENTS",
            font_size=fs(34),
            bold=True,
            halign="left",
            size_hint_y=None,
            height=35
        )
        self.content_box.add_widget(assignments_title)

        self.assignments_label = Label(
            text="",
            font_size=fs(20),
            halign="left",
            valign="top",
            size_hint_y=None
        )
        self.assignments_label.bind(
            texture_size=lambda instance, value: setattr(
                instance, "height", value[1] + 15
            )
        )
        self.assignments_label.bind(
            width=lambda instance, value: setattr(
                instance, "text_size", (value, None)
            )
        )
        self.content_box.add_widget(self.assignments_label)

        scroll.add_widget(self.content_box)
        main.add_widget(scroll)

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=55
        )

        assignments_button = AppButton(
            text="ALL ASSIGNMENTS",
            font_size=fs(20),
            bold=True
        )
        assignments_button.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "assignments"
            )
        )

        back = AppButton(
            text="BACK",
            font_size=fs(20),
            bold=True
        )
        back.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "subjects"
            )
        )

        buttons.add_widget(assignments_button)
        buttons.add_widget(back)
        main.add_widget(buttons)

        main.add_widget(BottomNav(current="subjects"))
        self.add_widget(main)

    def show_subject(self, subject):
        self.current_subject = subject
        self.title.text = subject

        info = SUBJECT_INFO.get(subject, {})
        credits = info.get("credits", "—")
        teacher = get_teacher(subject)

        if teacher:
            self.teacher_label.text = f"Teacher: {teacher}"
        else:
            self.teacher_label.text = "Teacher: Not set yet"

        present, absent, total, percentage = get_subject_stats(subject)

        if total == 0:
            percentage_text = "No classes marked yet"
            skip_text = "Can skip: —"
        else:
            percentage_text = f"{percentage:.1f}%"
            skips = classes_can_skip(present, total)
            skip_text = f"Can skip: {skips} classes"

        self.attendance_label.text = (
            f"Credits: {credits}\n"
            f"Attendance: {percentage_text}\n"
            f"Present: {present}    Absent: {absent}    Total: {total}\n"
            f"{skip_text}\n"
            f"Required: {REQUIRED_ATTENDANCE}%"
        )

        syllabus = info.get("syllabus", [])
        if syllabus:
            self.syllabus_label.text = "\n\n".join(
                f"{index}. {item}"
                for index, item in enumerate(syllabus, 1)
            )
        else:
            self.syllabus_label.text = "No syllabus information available."

        assignments = get_subject_assignments(subject)
        if not assignments:
            self.assignments_label.text = (
                "No assignments for this subject yet.\n"
                "Add one from the Assignments screen."
            )
        else:
            assignments.sort(
                key=lambda item: (
                    item.get("completed", False),
                    item.get("due_date", "9999-99-99")
                )
            )
            lines = []
            for item in assignments:
                title = item.get("title", "Untitled Assignment")
                due = item.get("due_date", "No due date")
                priority = item.get("priority", "Medium")
                completed = item.get("completed", False)
                status = "COMPLETED" if completed else "PENDING"
                lines.append(
                    f"• {title}\n  Due: {due}  •  {priority}  •  {status}"
                )
            self.assignments_label.text = "\n\n".join(lines)

    def open_teacher_editor(self):
        if not self.current_subject:
            return

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        current = get_teacher(self.current_subject)

        input_box = TextInput(
            text=current,
            hint_text="Teacher name",
            multiline=False,
            font_size=fs(19),
            size_hint_y=None,
            height=50
        )

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=50
        )

        cancel = AppButton(
            text="CANCEL",
            font_size=fs(20),
            bold=True
        )
        save = AppButton(
            text="SAVE",
            font_size=fs(20),
            bold=True
        )

        buttons.add_widget(cancel)
        buttons.add_widget(save)
        content.add_widget(input_box)
        content.add_widget(buttons)

        popup = Popup(
            title="EDIT TEACHER",
            content=content,
            size_hint=(0.85, 0.35),
            auto_dismiss=False
        )

        cancel.bind(
            on_press=lambda x: popup.dismiss()
        )
        save.bind(
            on_press=lambda x: self.save_teacher_name(
                popup,
                input_box.text
            )
        )

        popup.open()

    def save_teacher_name(self, popup, teacher_name):
        teacher_name = teacher_name.strip()
        teachers = load_teachers()
        teachers[self.current_subject] = teacher_name
        save_teachers(teachers)
        popup.dismiss()
        self.show_subject(self.current_subject)


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
                font_size=fs(27),
                bold=True
            )
        )

        content.add_widget(
            Label(
                text=(
                    f"{class_date}\n"
                    f"{time}"
                ),
                font_size=fs(29)
            )
        )

        present = AppButton(
            text="PRESENT",
            font_size=fs(24),
            size_hint_y=None,
            height=60
        )

        absent = AppButton(
            text="ABSENT",
            font_size=fs(24),
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

        class_is_cancelled = is_class_cancelled(class_date, subject, time)
        present.disabled = class_is_cancelled
        absent.disabled = class_is_cancelled

        if class_is_cancelled:
            cancel_text = "RESTORE CLASS"
        else:
            cancel_text = "CANCEL CLASS"

        cancel_class = AppButton(
            text=cancel_text,
            font_size=fs(23),
            size_hint_y=None,
            height=58,
            background_color=UI_WARNING
        )
        cancel_class.bind(on_press=lambda x: self.toggle_cancellation())
        content.add_widget(cancel_class)

        super().__init__(
            title="Mark Attendance",
            content=content,
            size_hint=(0.85, 0.55),
            **kwargs
        )

    def toggle_cancellation(self):
        app = App.get_running_app()
        key = cancellation_key(self.class_date, self.subject, self.time)
        cancellations = getattr(app, "cancellations_data", load_cancellations())

        if key in cancellations:
            cancellations.pop(key, None)
        else:
            cancellations[key] = {
                "subject": self.subject,
                "date": self.class_date,
                "time": self.time
            }
            # A cancelled class should never remain marked present/absent.
            attendance_key = key
            app.attendance_data.pop(attendance_key, None)
            save_attendance(app.attendance_data)

        save_cancellations(cancellations)
        self.dismiss()
        timetable = app.root.get_screen("timetable")
        timetable.refresh_grid()
        try:
            home = app.root.get_screen("home")
            home.update_dashboard()
        except Exception:
            pass

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
    """Accessible single-day timeline timetable with a weekly date selector."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.week_offset = 0
        self.selected_day_index = 0
        self.filter_mode = "ALL"

        self.main = BoxLayout(
            orientation="vertical",
            padding=(18, 12, 18, 10),
            spacing=10,
        )
        rounded_background(self.main, UI_BG, 0)

        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------
        top = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=58,
            spacing=8,
        )

        back = AppButton(
            text="‹",
            font_size=fs(30),
            size_hint_x=None,
            width=54,
        )
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)

        title_box = BoxLayout(orientation="vertical", spacing=0)
        self.title_label = Label(
            text="Timetable",
            font_size=fs(24),
            bold=True,
            color=UI_TEXT,
            halign="center",
            valign="middle",
        )
        self.title_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.month_label = Label(
            text="",
            font_size=fs(14),
            bold=True,
            color=UI_MUTED,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=22,
        )
        self.month_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        title_box.add_widget(self.title_label)
        title_box.add_widget(self.month_label)
        top.add_widget(title_box)

        today = AppButton(
            text="TODAY",
            font_size=fs(13),
            bold=True,
            size_hint_x=None,
            width=82,
        )
        today.bind(on_press=lambda x: self.go_to_today())
        top.add_widget(today)
        self.main.add_widget(top)

        # ----------------------------------------------------
        # WEEK NAVIGATION
        # ----------------------------------------------------
        week_nav = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=46,
        )
        prev_week = AppButton(text="‹", font_size=fs(25), size_hint_x=None, width=52)
        prev_week.bind(on_press=lambda x: self.change_week(-1))
        week_nav.add_widget(prev_week)

        self.week_range = Label(
            text="",
            font_size=fs(15),
            bold=True,
            color=UI_TEXT,
            halign="center",
            valign="middle",
        )
        self.week_range.bind(size=lambda i, v: setattr(i, "text_size", v))
        week_nav.add_widget(self.week_range)

        next_week = AppButton(text="›", font_size=fs(25), size_hint_x=None, width=52)
        next_week.bind(on_press=lambda x: self.change_week(1))
        week_nav.add_widget(next_week)
        self.main.add_widget(week_nav)

        # ----------------------------------------------------
        # 7-DAY DATE STRIP
        # ----------------------------------------------------
        self.day_strip = BoxLayout(
            orientation="horizontal",
            spacing=7,
            size_hint_y=None,
            height=92,
        )
        self.main.add_widget(self.day_strip)

        # ----------------------------------------------------
        # SELECTED DAY + FILTERS
        # ----------------------------------------------------
        day_header = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=52,
        )

        self.selected_day_label = Label(
            text="",
            font_size=fs(19),
            bold=True,
            color=UI_TEXT,
            halign="left",
            valign="middle",
        )
        self.selected_day_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        day_header.add_widget(self.selected_day_label)

        self.filter_buttons = {}
        for mode in ("ALL", "UNMARKED", "MARKED"):
            b = AppButton(
                text=mode,
                font_size=fs(11),
                bold=True,
                size_hint_x=None,
                width=82 if mode != "UNMARKED" else 100,
            )
            b.bind(on_press=lambda x, m=mode: self.set_filter(m))
            self.filter_buttons[mode] = b
            day_header.add_widget(b)

        self.main.add_widget(day_header)

        # ----------------------------------------------------
        # TIMELINE SCROLL
        # ----------------------------------------------------
        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=6,
            scroll_y=1,
        )
        self.timeline = BoxLayout(
            orientation="vertical",
            spacing=8,
            padding=(0, 4, 0, 12),
            size_hint_y=None,
        )
        self.timeline.bind(minimum_height=self.timeline.setter("height"))
        self.scroll.add_widget(self.timeline)
        self.main.add_widget(self.scroll)

        self.main.add_widget(BottomNav(current="home"))
        self.add_widget(self.main)

    # ========================================================
    # NAVIGATION
    # ========================================================

    def go_back(self):
        if self.manager:
            self.manager.current = "home"

    def get_monday(self):
        today = date.today()
        return today - timedelta(days=today.weekday()) + timedelta(days=self.week_offset * 7)

    def go_to_today(self):
        self.week_offset = 0
        self.selected_day_index = date.today().weekday()
        if self.selected_day_index > 6:
            self.selected_day_index = 0
        self.refresh_grid()

    def change_week(self, amount):
        self.week_offset += amount
        self.refresh_grid()

    def select_day(self, index):
        self.selected_day_index = index
        self.refresh_grid()

    def set_filter(self, mode):
        self.filter_mode = mode
        self.refresh_timeline_only()
        self.update_filter_buttons()

    # ========================================================
    # CURRENT TIME
    # ========================================================

    def get_current_time(self):
        try:
            import subprocess
            result = subprocess.check_output(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    "(Get-Date).ToString('yyyy-MM-dd HH:mm:ss')",
                ],
                stderr=subprocess.DEVNULL,
            )
            return datetime.strptime(
                result.decode("utf-8", errors="ignore").strip(),
                "%Y-%m-%d %H:%M:%S",
            )
        except Exception:
            return datetime.now()

    def is_current_class(self, actual_date, time_slot, subject):
        if actual_date != date.today() or not subject or subject == "LUNCH BREAK":
            return False
        try:
            start_text, end_text = time_slot.split(" - ")
            sh, sm = map(int, start_text.split(":"))
            eh, em = map(int, end_text.split(":"))
            start = sh * 60 + sm
            end = eh * 60 + em
            now = self.get_current_time()
            current = now.hour * 60 + now.minute
            return start <= current < end
        except Exception:
            return False

    # ========================================================
    # DATE / DAY HELPERS
    # ========================================================

    def get_timetable_day(self, actual_date):
        weekday = actual_date.strftime("%A").upper()
        if weekday == "SUNDAY":
            return None
        if weekday == "SATURDAY":
            return SPECIAL_SATURDAYS.get(actual_date)
        return weekday

    def get_subjects_for_date(self, actual_date):
        timetable_day = self.get_timetable_day(actual_date)
        if not timetable_day:
            return [""] * len(TIMES)
        return TIMETABLE.get(timetable_day, [""] * len(TIMES))

    def attendance_record(self, actual_date, subject, time):
        key = f"{actual_date.isoformat()}|{subject}|{time}"
        return App.get_running_app().attendance_data.get(key)

    def update_filter_buttons(self):
        for mode, button in self.filter_buttons.items():
            button.background_normal = ""
            if mode == self.filter_mode:
                button.background_color = UI_ACCENT
            else:
                button.background_color = UI_SURFACE_2

    # ========================================================
    # REFRESH
    # ========================================================

    def on_pre_enter(self, *args):
        self.refresh_grid()

    def refresh_grid(self):
        monday = self.get_monday()
        sunday = monday + timedelta(days=6)

        self.week_range.text = f"{monday.strftime('%d %b')}  –  {sunday.strftime('%d %b %Y')}"
        self.month_label.text = monday.strftime("%B %Y")

        self.build_day_strip(monday)
        self.update_filter_buttons()
        self.refresh_timeline_only()

    def build_day_strip(self, monday):
        self.day_strip.clear_widgets()
        names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

        for index, name in enumerate(names):
            actual_date = monday + timedelta(days=index)
            is_selected = index == self.selected_day_index
            is_today = actual_date == date.today()

            text = f"{name}\n{actual_date.day}"
            if is_today:
                text += "\nTODAY"

            button = AppButton(
                text=text,
                font_size=fs(13),
                bold=True,
                halign="center",
                valign="middle",
                size_hint_x=1,
                background_color=UI_ACCENT if is_selected else UI_SURFACE_2,
            )
            button.background_normal = ""
            button.text_size = (None, None)
            button.bind(on_press=lambda x, i=index: self.select_day(i))
            self.day_strip.add_widget(button)

    def refresh_timeline_only(self):
        self.timeline.clear_widgets()

        monday = self.get_monday()
        actual_date = monday + timedelta(days=self.selected_day_index)
        self.selected_day_label.text = (
            f"{actual_date.strftime('%A')}  •  {actual_date.strftime('%d %B')}"
        )

        status = get_semester_status(actual_date)
        if status:
            card = BoxLayout(
                orientation="vertical",
                padding=(22, 18),
                spacing=7,
                size_hint_y=None,
                height=190,
            )
            rounded_background(card, UI_SURFACE, 18)
            card.add_widget(Label(
                text=status.replace("\n", "\n\n"),
                font_size=fs(21),
                bold=True,
                color=UI_TEXT,
                halign="center",
                valign="middle",
            ))
            card.add_widget(Label(
                text="No classes can be marked on this date.",
                font_size=fs(14),
                color=UI_MUTED,
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=35,
            ))
            self.timeline.add_widget(card)
            return

        timetable_day = self.get_timetable_day(actual_date)
        if not timetable_day:
            self.add_empty_state("No classes scheduled for Sunday.")
            return

        subjects = self.get_subjects_for_date(actual_date)
        added = 0

        for index, subject in enumerate(subjects):
            time = TIMES[index]

            # Keep the complete day timeline visible in ALL mode.
            # This mirrors a real timetable: empty periods remain visible
            # instead of collapsing and leaving a large unused area.
            if not subject:
                if self.filter_mode == "ALL":
                    self.add_empty_time_row(time)
                continue

            if subject == "LUNCH BREAK":
                if self.filter_mode == "ALL":
                    self.add_lunch_row(time)
                continue

            record = self.attendance_record(actual_date, subject, time)
            marked = record is not None

            if self.filter_mode == "MARKED" and not marked:
                continue
            if self.filter_mode == "UNMARKED" and marked:
                continue

            self.add_class_row(actual_date, subject, time, record)
            added += 1

        if added == 0:
            if self.filter_mode == "MARKED":
                self.add_empty_state("No attendance marked yet.")
            elif self.filter_mode == "UNMARKED":
                self.add_empty_state("All scheduled classes are marked.")
            else:
                self.add_empty_state("No classes scheduled for this day.")

    def add_empty_state(self, message):
        card = BoxLayout(
            orientation="vertical",
            padding=(22, 24),
            size_hint_y=None,
            height=150,
        )
        rounded_background(card, UI_SURFACE, 18)
        card.add_widget(Label(
            text=message,
            font_size=fs(18),
            bold=True,
            color=UI_TEXT,
            halign="center",
            valign="middle",
        ))
        self.timeline.add_widget(card)

    def add_empty_time_row(self, time):
        """Render an empty period so the full daily timeline stays visible."""
        row = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=138,
        )

        time_label = Label(
            text=time.replace(" - ", "\n"),
            font_size=fs(13),
            bold=True,
            color=UI_MUTED,
            size_hint_x=None,
            width=92,
            halign="center",
            valign="middle",
        )
        time_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        row.add_widget(time_label)

        slot = Label(
            text="",
            color=UI_MUTED,
            size_hint_x=1,
        )
        rounded_background(slot, (0.055, 0.065, 0.085, 1), 16)
        row.add_widget(slot)
        self.timeline.add_widget(row)

    def add_lunch_row(self, time):
        row = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=138,
        )

        time_label = Label(
            text=time.replace(" - ", "\n"),
            font_size=fs(13),
            bold=True,
            color=UI_MUTED,
            size_hint_x=None,
            width=92,
            halign="center",
            valign="middle",
        )
        time_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        row.add_widget(time_label)

        lunch = Label(
            text="LUNCH BREAK",
            font_size=fs(15),
            bold=True,
            color=UI_MUTED,
            halign="center",
            valign="middle",
        )
        lunch.bind(size=lambda i, v: setattr(i, "text_size", v))
        rounded_background(lunch, UI_SURFACE_2, 16)
        row.add_widget(lunch)
        self.timeline.add_widget(row)

    def add_class_row(self, actual_date, subject, time, record):
        row = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=138,
        )

        time_label = Label(
            text=time.replace(" - ", "\n"),
            font_size=fs(13),
            bold=True,
            color=UI_MUTED,
            size_hint_x=None,
            width=92,
            halign="center",
            valign="middle",
        )
        time_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        row.add_widget(time_label)

        date_string = actual_date.isoformat()
        cancelled = is_class_cancelled(date_string, subject, time)
        current = self.is_current_class(actual_date, time, subject)

        if cancelled:
            text = f"{subject}\n\nCANCELLED"
            bg = (0.45, 0.25, 0.12, 1)
        elif record and record.get("status") == "present":
            text = f"{subject}\n\nPRESENT"
            bg = (0.10, 0.55, 0.25, 1)
        elif record and record.get("status") == "absent":
            text = f"{subject}\n\nABSENT"
            bg = (0.72, 0.18, 0.18, 1)
        elif current:
            text = f"{subject}\n\nCURRENT CLASS"
            bg = (0.10, 0.35, 0.75, 1)
        else:
            text = subject
            bg = UI_SURFACE

        button = AppButton(
            text=text,
            font_size=fs(17),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_x=1,
            background_color=bg,
        )
        button.background_normal = ""
        button.text_size = (None, None)
        button.padding = (22, 12)

        if not cancelled:
            button.bind(
                on_press=lambda x, s=subject, d=date_string, t=time: self.open_attendance(s, d, t)
            )
        else:
            button.bind(
                on_press=lambda x, s=subject, d=date_string, t=time: self.open_attendance(s, d, t)
            )

        row.add_widget(button)
        self.timeline.add_widget(row)

    # ========================================================
    # ATTENDANCE
    # ========================================================

    def open_attendance(self, subject, class_date, time):
        AttendancePopup(
            subject=subject,
            class_date=class_date,
            time=time,
        ).open()

class AssignmentsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main = BoxLayout(orientation="vertical", padding=(10,8), spacing=7)
        rounded_background(self.main, UI_BG, 0)

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=74)
        header.add_widget(Label(text="ASSIGNMENTS", font_size=fs(29), bold=True, color=UI_TEXT, size_hint_y=None, height=36))
        header.add_widget(Label(text="Stay on top of studio, theory & class work", font_size=fs(14), color=UI_MUTED, size_hint_y=None, height=22))
        self.main.add_widget(header)

        add_button = AppButton(text="＋  ADD ASSIGNMENT", font_size=fs(16), bold=True, size_hint_y=None, height=48)
        add_button.bind(on_press=lambda x: self.open_add_assignment())
        self.main.add_widget(add_button)

        self.scroll = ScrollView(do_scroll_y=True, bar_width=4)
        self.list_layout = BoxLayout(orientation="vertical", spacing=7, size_hint_y=None, padding=(0,2))
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        self.main.add_widget(self.scroll)
        self.main.add_widget(BottomNav(current="assignments"))
        self.add_widget(self.main)

    # ========================================================
    # ASSIGNMENT FILE
    # ========================================================

    def get_assignment_file(self):

        app = App.get_running_app()

        return os.path.join(
            app.user_data_dir,
            "assignments.json"
        )

    # ========================================================
    # LOAD
    # ========================================================

    def load_assignments(self):

        filename = (
            self.get_assignment_file()
        )

        try:

            if os.path.exists(filename):

                with open(
                    filename,
                    "r"
                ) as file:

                    return json.load(file)

        except Exception as e:

            print(
                "Could not load assignments:",
                e
            )

        return []

    # ========================================================
    # SAVE
    # ========================================================

    def save_assignments(self, assignments):

        filename = (
            self.get_assignment_file()
        )

        try:

            os.makedirs(
                os.path.dirname(filename),
                exist_ok=True
            )

            with open(
                filename,
                "w"
            ) as file:

                json.dump(
                    assignments,
                    file,
                    indent=4
                )

        except Exception as e:

            print(
                "Could not save assignments:",
                e
            )

    # ========================================================
    # SCREEN ENTER
    # ========================================================

    def on_pre_enter(self, *args):

        self.refresh_assignments()

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh_assignments(self):
        self.list_layout.clear_widgets()
        assignments = self.load_assignments()
        assignments.sort(key=lambda item: (item.get("completed",False), item.get("due_date","9999-99-99")))

        # Always show a useful summary so the portrait screen is not mostly empty.
        pending_count = sum(1 for a in assignments if not a.get("completed", False))
        completed_count = len(assignments) - pending_count
        summary = BoxLayout(orientation="vertical", padding=(12,9), spacing=5, size_hint_y=None, height=150)
        rounded_background(summary, UI_SURFACE, 18)
        summary.add_widget(Label(text="TASK OVERVIEW", font_size=fs(16), bold=True, color=UI_TEXT, size_hint_y=None, height=24))
        summary_row = BoxLayout(orientation="horizontal", spacing=7, size_hint_y=None, height=92)
        summary_row.add_widget(make_stat_box(str(pending_count), "PENDING", UI_WARNING))
        summary_row.add_widget(make_stat_box(str(completed_count), "COMPLETED", UI_SUCCESS))
        summary_row.add_widget(make_stat_box(str(len(assignments)), "TOTAL", UI_ACCENT))
        summary.add_widget(summary_row)
        self.list_layout.add_widget(summary)

        if not assignments:
            empty = BoxLayout(orientation="vertical", padding=(14,18), spacing=7, size_hint_y=None, height=390)
            rounded_background(empty, UI_SURFACE, 18)
            empty.add_widget(Label(text="NO TASKS YET", font_size=fs(21), bold=True, color=UI_TEXT, size_hint_y=None, height=35))
            empty.add_widget(Label(text="Add your first assignment above.\nIt will appear here with its due date and priority.", font_size=fs(15), color=UI_MUTED, halign="center", valign="middle"))
            self.list_layout.add_widget(empty)

            tips = BoxLayout(orientation="vertical", padding=(13,11), spacing=5, size_hint_y=None, height=220)
            rounded_background(tips, UI_SURFACE, 18)
            tips.add_widget(Label(text="STAY ORGANIZED", font_size=fs(17), bold=True, color=UI_TEXT, size_hint_y=None, height=27))
            tips.add_widget(Label(text="Add studio work, drawings, submissions and theory tasks here.\nUse the due date to keep your upcoming work visible on the Dashboard.", font_size=fs(14), color=UI_MUTED, halign="left", valign="middle"))
            self.list_layout.add_widget(tips)
            return

        for index, assignment in enumerate(assignments):
            self.add_assignment_card(assignment, index)

    def add_assignment_card(self, assignment, index):
        completed = assignment.get("completed", False)
        title = assignment.get("title", "Untitled Assignment")
        subject = assignment.get("subject", "No subject")
        due_date = assignment.get("due_date", "No due date")
        priority = assignment.get("priority", "Medium")

        if completed:
            status = "COMPLETED"
        else:
            try:
                due = date.fromisoformat(due_date)
                today = date.today()
                if due < today: status = "OVERDUE"
                elif due == today: status = "DUE TODAY"
                else:
                    days = (due - today).days
                    status = "DUE TOMORROW" if days == 1 else f"DUE IN {days} DAYS"
            except Exception:
                status = "DUE DATE UNKNOWN"

        card = BoxLayout(orientation="vertical", padding=(12,10), spacing=5, size_hint_y=None, height=190)
        rounded_background(card, UI_SURFACE, 17)

        title_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=32)
        title_label = Label(text=title, font_size=fs(17), bold=not completed, color=UI_TEXT, halign="left", valign="middle")
        title_label.bind(size=lambda i,v: setattr(i,"text_size",v))
        title_row.add_widget(title_label)
        title_row.add_widget(Label(text=priority.upper(), font_size=fs(12), bold=True, color=UI_WARNING if priority=="High" else UI_MUTED, size_hint_x=None, width=72, halign="right"))
        card.add_widget(title_row)

        meta = Label(text=f"{subject}   •   Due {due_date}\n{status}", font_size=fs(14), color=UI_SUCCESS if status=="COMPLETED" else (UI_DANGER if status=="OVERDUE" else UI_MUTED), halign="left", valign="middle", size_hint_y=None, height=43)
        meta.bind(size=lambda i,v: setattr(i,"text_size",v))
        card.add_widget(meta)

        buttons = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=40)
        complete_button = AppButton(text="UNDO" if completed else "MARK DONE", font_size=fs(13))
        complete_button.bind(on_press=lambda x, i=index: self.toggle_assignment(i))
        delete_button = AppButton(text="DELETE", font_size=fs(13), background_color=UI_SURFACE_2)
        delete_button.bind(on_press=lambda x, i=index: self.delete_assignment(i))
        buttons.add_widget(complete_button); buttons.add_widget(delete_button)
        card.add_widget(buttons)
        self.list_layout.add_widget(card)

    # ========================================================
    # ADD ASSIGNMENT POPUP
    # ========================================================

    def open_add_assignment(self):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_input = TextInput(
            hint_text="Assignment title",
            multiline=False,
            font_size=fs(21),
            size_hint_y=None,
            height=45
        )

        # ----------------------------------------------------
        # SUBJECT
        # ----------------------------------------------------

        subject_spinner = Spinner(
            text=SUBJECTS[0],
            values=SUBJECTS,
            font_size=fs(20),
            size_hint_y=None,
            height=45
        )

        # ----------------------------------------------------
        # DUE DATE
        # ----------------------------------------------------

        due_input = TextInput(
            hint_text="Due date (YYYY-MM-DD)",
            multiline=False,
            font_size=fs(21),
            size_hint_y=None,
            height=45
        )

        # ----------------------------------------------------
        # PRIORITY
        # ----------------------------------------------------

        priority_spinner = Spinner(
            text="Medium",
            values=[
                "Low",
                "Medium",
                "High"
            ],
            font_size=fs(20),
            size_hint_y=None,
            height=45
        )

        content.add_widget(
            title_input
        )

        content.add_widget(
            subject_spinner
        )

        content.add_widget(
            due_input
        )

        content.add_widget(
            priority_spinner
        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=50
        )

        cancel = AppButton(
            text="CANCEL",
            font_size=fs(20),
            bold=True
        )

        save = AppButton(
            text="SAVE",
            font_size=fs(20),
            bold=True
        )

        buttons.add_widget(
            cancel
        )

        buttons.add_widget(
            save
        )

        content.add_widget(
            buttons
        )

        popup = Popup(
            title="ADD ASSIGNMENT",
            content=content,
            size_hint=(0.85, 0.65),
            auto_dismiss=False
        )

        cancel.bind(
            on_press=lambda x:
            popup.dismiss()
        )

        save.bind(
            on_press=lambda x:
            self.save_new_assignment(
                popup,
                title_input.text,
                subject_spinner.text,
                due_input.text,
                priority_spinner.text
            )
        )

        popup.open()

    # ========================================================
    # SAVE NEW ASSIGNMENT
    # ========================================================

    def save_new_assignment(
        self,
        popup,
        title,
        subject,
        due_date,
        priority
    ):

        title = title.strip()
        due_date = due_date.strip()

        if not title:

            return

        # Validate date
        try:

            date.fromisoformat(
                due_date
            )

        except Exception:

            return

        assignments = (
            self.load_assignments()
        )

        assignments.append(
            {
                "title": title,
                "subject": subject,
                "due_date": due_date,
                "priority": priority,
                "completed": False
            }
        )

        self.save_assignments(
            assignments
        )

        popup.dismiss()

        self.refresh_assignments()

    # ========================================================
    # TOGGLE COMPLETE
    # ========================================================

    def toggle_assignment(self, index):

        assignments = (
            self.load_assignments()
        )

        assignments.sort(
            key=lambda item: (
                item.get(
                    "completed",
                    False
                ),
                item.get(
                    "due_date",
                    "9999-99-99"
                )
            )
        )

        if 0 <= index < len(assignments):

            assignments[index]["completed"] = (
                not assignments[index].get(
                    "completed",
                    False
                )
            )

        self.save_assignments(
            assignments
        )

        self.refresh_assignments()

    # ========================================================
    # DELETE
    # ========================================================

    def delete_assignment(self, index):

        assignments = (
            self.load_assignments()
        )

        assignments.sort(
            key=lambda item: (
                item.get(
                    "completed",
                    False
                ),
                item.get(
                    "due_date",
                    "9999-99-99"
                )
            )
        )

        if 0 <= index < len(assignments):

            assignments.pop(index)

        self.save_assignments(
            assignments
        )

        self.refresh_assignments()


# ============================================================
# ACADEMIC CALENDAR SCREEN
# ============================================================

class AcademicCalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main = BoxLayout(orientation="vertical", padding=(10,8), spacing=7)
        rounded_background(main, UI_BG, 0)

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=62)
        header.add_widget(Label(text="ACADEMIC CALENDAR", font_size=fs(27), bold=True, color=UI_TEXT, size_hint_y=None, height=35))
        header.add_widget(Label(text="WINTER SEMESTER 2026", font_size=fs(14), color=UI_MUTED, size_hint_y=None, height=22))
        main.add_widget(header)

        self.scroll = ScrollView(do_scroll_y=True, bar_width=4)
        content = BoxLayout(orientation="vertical", spacing=6, padding=(0,2), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        # High-priority semester milestones
        self.add_section(content, "SEMESTER TIMELINE")
        self.add_event(content, "SEMESTER START", "24 Aug 2026", UI_ACCENT, "01")
        self.add_event(content, "MID-SEMESTER EXAMS", "01 Oct – 10 Oct 2026", UI_WARNING, "02")
        self.add_event(content, "NO INSTRUCTION", "09 Nov – 13 Nov 2026", UI_MUTED, "03")
        self.add_event(content, "FORMAL TEACHING UNTIL", "05 Dec 2026", UI_TEXT, "04")
        self.add_event(content, "END-SEMESTER EXAMS", "07 Dec – 15 Dec 2026", UI_WARNING, "05")

        self.add_section(content, "HOLIDAYS")
        for holiday_date, label in sorted(HOLIDAYS.items()):
            clean = label.split("\n")[-1]
            self.add_event(content, clean, holiday_date.strftime("%a · %d %b %Y"), UI_TEXT, "HOL")

        self.add_section(content, "SPECIAL SATURDAYS")
        for saturday, follows in sorted(SPECIAL_SATURDAYS.items()):
            self.add_event(content, f"Saturday follows {follows.title()}", saturday.strftime("%a · %d %b %Y"), UI_TEXT, "SAT")

        footer = BoxLayout(orientation="vertical", padding=(12,10), spacing=4, size_hint_y=None, height=118)
        rounded_background(footer, UI_SURFACE, 17)
        footer.add_widget(Label(text="NEED THE FULL TIMETABLE?", font_size=fs(15), bold=True, color=UI_TEXT, size_hint_y=None, height=25))
        footer.add_widget(Label(text="Open Weekly Timetable to see your daily classes, special Saturdays and attendance marking.", font_size=fs(13), color=UI_MUTED, halign="left", valign="middle"))
        open_tt = AppButton(text="OPEN WEEKLY TIMETABLE  →", font_size=fs(13), size_hint_y=None, height=34)
        open_tt.bind(on_press=lambda x: setattr(self.manager, "current", "timetable"))
        footer.add_widget(open_tt)
        content.add_widget(footer)

        self.scroll.add_widget(content)
        main.add_widget(self.scroll)
        main.add_widget(BottomNav(current="calendar"))
        self.add_widget(main)

    def add_section(self, parent, title):
        parent.add_widget(Label(text=title, font_size=fs(16), bold=True, color=UI_TEXT, size_hint_y=None, height=27, halign="left"))

    def add_event(self, parent, title, detail, accent, tag):
        card = BoxLayout(orientation="horizontal", padding=(10,7), spacing=8, size_hint_y=None, height=88)
        rounded_background(card, UI_SURFACE, 15)
        badge = Label(text=tag, font_size=fs(11), bold=True, color=accent, size_hint_x=None, width=42, halign="center", valign="middle")
        card.add_widget(badge)
        info = BoxLayout(orientation="vertical", spacing=0)
        info.add_widget(Label(text=title, font_size=fs(15), bold=True, color=UI_TEXT, halign="left", valign="middle", size_hint_y=None, height=27))
        info.add_widget(Label(text=detail, font_size=fs(13), color=UI_MUTED, halign="left", valign="middle", size_hint_y=None, height=22))
        card.add_widget(info)
        parent.add_widget(card)


# ============================================================
# APP
# ============================================================

class CollegeApp(App):

    def build(self):

        self.attendance_data = (
            load_attendance()
        )
        self.cancellations_data = load_cancellations()

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
        manager.add_widget(
             AssignmentsScreen(
                name="assignments"
            )
        )

        manager.add_widget(
            AcademicCalendarScreen(
                name="calendar"
            )
        )

        # Pinch with two fingers anywhere in the app to enlarge/reduce text.
        # This is intentionally lightweight so it does not interfere with
        # timetable scrolling or normal button taps.
        self._zoom_touches = {}
        self._zoom_distance = None
        self._ui_zoom = 1.0

        def touch_down(window, touch):
            if getattr(touch, "is_mouse_scrolling", False):
                return False
            self._zoom_touches[touch.uid] = touch
            if len(self._zoom_touches) == 2:
                touches = list(self._zoom_touches.values())
                self._zoom_distance = _distance(touches[0], touches[1])
            return False

        def touch_move(window, touch):
            if touch.uid not in self._zoom_touches:
                return False
            self._zoom_touches[touch.uid] = touch

            if len(self._zoom_touches) == 2 and self._zoom_distance:
                touches = list(self._zoom_touches.values())
                new_distance = _distance(touches[0], touches[1])
                if self._zoom_distance > 5:
                    ratio = new_distance / self._zoom_distance
                    if abs(ratio - 1.0) > 0.015:
                        self._ui_zoom *= ratio
                        self._ui_zoom = max(
                            MIN_UI_ZOOM,
                            min(MAX_UI_ZOOM, self._ui_zoom)
                        )
                        _set_ui_zoom(manager, self._ui_zoom)
                        self._zoom_distance = new_distance
            return False

        def touch_up(window, touch):
            self._zoom_touches.pop(touch.uid, None)
            if len(self._zoom_touches) < 2:
                self._zoom_distance = None
            return False

        Window.bind(
            on_touch_down=touch_down,
            on_touch_move=touch_move,
            on_touch_up=touch_up
        )

        return manager


CollegeApp().run()