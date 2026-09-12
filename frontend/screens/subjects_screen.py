from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from backend.constants import SUBJECTS, SUBJECT_INFO, CLASS_TYPES, REQUIRED_ATTENDANCE
from backend.storage import get_teacher
from backend.attendance_service import get_subject_stats
from frontend.theme import UI_BG, UI_SURFACE, UI_TEXT, UI_MUTED, UI_SUCCESS, UI_DANGER, UI_ACCENT, fs, rounded_background
from frontend.widgets.navigation import BottomNav
from frontend.widgets.cards import SubjectCardButton


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

            if total:
                attendance_text = f"{percentage:.0f}%"
                type_parts = []
                for class_type in CLASS_TYPES:
                    tp, ta, tt, tpct = get_subject_stats(subject, class_type)
                    if tt:
                        type_parts.append(f"{class_type.title()}: {tpct:.0f}%")
                type_summary = "  •  ".join(type_parts)
                count_text = (
                    f"{present} present  •  {absent} absent  •  {total} marked"
                    + (f"\n{type_summary}" if type_summary else "")
                )
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

