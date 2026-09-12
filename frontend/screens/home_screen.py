import math
from datetime import datetime, date
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from backend.constants import (
    SUBJECTS,
    TIMES,
    REQUIRED_ATTENDANCE,
    SPECIAL_SATURDAYS,
)
from backend.storage import (
    attendance_key,
    save_attendance,
    get_subject_prep,
)
from backend.attendance_service import (
    get_subject_stats,
    classes_can_skip,
    get_slot_subject,
    get_slot_type,
    is_class_cancelled,
    get_semester_status,
)
from frontend.theme import (
    UI_BG,
    UI_SURFACE,
    UI_SURFACE_2,
    UI_TEXT,
    UI_MUTED,
    UI_SUCCESS,
    UI_DANGER,
    UI_WARNING,
    UI_ACCENT,
    fs,
    rounded_background,
)
from frontend.widgets.buttons import AppButton, make_stat_box, make_link_card
from frontend.widgets.navigation import BottomNav
from frontend.widgets.progress_ring import AttendanceRing


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
        self.attendance_header_label = Label(
            text="ATTENDANCE WATCH", font_size=fs(14), bold=True,
            color=UI_MUTED, halign="left", size_hint_y=None, height=24
        )
        self.attendance_header_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        att_info.add_widget(self.attendance_header_label)

        self.attendance_summary = Label(
            text="No classes marked yet", font_size=fs(22), bold=True,
            color=UI_TEXT, halign="left", valign="middle",
            size_hint_y=None, height=38
        )
        self.attendance_summary.bind(size=lambda i, v: setattr(i, "text_size", v))
        att_info.add_widget(self.attendance_summary)

        self.attendance_sub_label = Label(
            text="Keep subjects ≥ 75% to stay safe", font_size=fs(13),
            color=UI_MUTED, halign="left", size_hint_y=None, height=24
        )
        self.attendance_sub_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        att_info.add_widget(self.attendance_sub_label)

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
        self.today_classes.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.today_card.add_widget(self.today_title)
        self.today_card.add_widget(self.today_classes)
        today_open = AppButton(
            text="OPEN WEEKLY TIMETABLE  →", font_size=fs(14),
            background_color=UI_SURFACE_2, size_hint_y=None, height=38
        )
        today_open.bind(on_press=lambda x: setattr(self.manager, "current", "timetable"))
        self.today_card.add_widget(today_open)
        content.add_widget(self.today_card)

        # Today's attendance status
        self.unmarked_card = BoxLayout(
            orientation="vertical", padding=(12, 9), spacing=3,
            size_hint_y=None, height=105
        )
        rounded_background(self.unmarked_card, UI_SURFACE, 18)
        self.unmarked_label = Label(
            text="0 unmarked classes today", font_size=fs(19), bold=True,
            color=UI_TEXT, halign="left", valign="middle"
        )
        self.unmarked_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.unmarked_card.add_widget(self.unmarked_label)
        content.add_widget(self.unmarked_card)

        # Next class preparation
        self.next_class_card = BoxLayout(
            orientation="vertical", padding=(12, 9), spacing=3,
            size_hint_y=None, height=180
        )
        rounded_background(self.next_class_card, UI_SURFACE, 18)
        self.next_class_title = Label(
            text="NEXT CLASS", font_size=fs(17), bold=True, color=UI_TEXT,
            size_hint_y=None, height=25
        )
        self.next_class_text = Label(
            text="No upcoming class", font_size=fs(15), color=UI_MUTED,
            halign="left", valign="middle"
        )
        self.next_class_text.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.next_class_card.add_widget(self.next_class_title)
        self.next_class_card.add_widget(self.next_class_text)
        content.add_widget(self.next_class_card)

        # Quick links, two-column for portrait
        content.add_widget(Label(
            text="QUICK ACCESS", font_size=fs(17), bold=True, color=UI_TEXT,
            size_hint_y=None, height=24
        ))
        links = GridLayout(cols=2, spacing=7, size_hint_y=None, height=140)
        links.add_widget(make_link_card("MY SUBJECTS", "Attendance & details", lambda x: setattr(self.manager, "current", "subjects"), height=125))
        links.add_widget(make_link_card("ASSIGNMENTS", "Tasks & due dates", lambda x: setattr(self.manager, "current", "assignments"), height=125))
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
        self.upcoming_text.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.upcoming_card.add_widget(self.upcoming_title)
        self.upcoming_card.add_widget(self.upcoming_text)
        open_tasks = AppButton(
            text="VIEW ALL TASKS  →", font_size=fs(13), background_color=UI_SURFACE_2,
            size_hint_y=None, height=32
        )
        open_tasks.bind(on_press=lambda x: setattr(self.manager, "current", "assignments"))
        self.upcoming_card.add_widget(open_tasks)
        content.add_widget(self.upcoming_card)

        # Week overview
        week_card = BoxLayout(orientation="vertical", padding=(12, 10), spacing=6, size_hint_y=None, height=160)
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
            orientation="vertical", padding=(12, 10), spacing=5,
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

        content.add_widget(make_link_card(
            "ACADEMIC CALENDAR", "Semester dates, holidays & special Saturdays  →",
            lambda x: setattr(self.manager, "current", "calendar"), height=105
        ))

        self.scroll.add_widget(content)
        self.main.add_widget(self.scroll)
        self.main.add_widget(BottomNav(current="home"))
        self.add_widget(self.main)

        self.quick_attendance_event = Clock.schedule_interval(lambda dt: self.update_dashboard(), 30)

    def on_pre_enter(self, *args):
        self.update_dashboard()

    def update_today_background(self, *args):
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

        subjects = [get_slot_subject(timetable_day, i) for i in range(len(TIMES))]
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
                    "type": get_slot_type(timetable_day, index),
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
                    "type": get_slot_type(timetable_day, index),
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

        class_type = class_info.get("type") or "LECTURE"
        key = attendance_key(class_date, subject, time, class_type)
        record = App.get_running_app().attendance_data.get(key)

        tp, ta, tt, tpct = get_subject_stats(subject, class_type)
        can_miss = classes_can_skip(tp, tt) if tt else 0
        miss_text = (
            f"Can miss {can_miss} more {class_type.lower()}"
            if tt else
            f"No {class_type.lower()} attendance marked yet"
        )

        if record:
            status = record.get("status", "").upper()
            self.quick_attendance_label.text = (
                f"{state}  •  {subject}\n"
                f"{time}  •  {class_type}  •  MARKED {status}\n"
                f"{miss_text} while staying at {REQUIRED_ATTENDANCE}%+"
            )
            self.quick_present_button.disabled = True
            self.quick_absent_button.disabled = True
        else:
            self.quick_attendance_label.text = (
                f"{state}  •  {subject}\n"
                f"{time}  •  {class_type}  •  Tap PRESENT or ABSENT\n"
                f"{miss_text} while staying at {REQUIRED_ATTENDANCE}%+"
            )
            self.quick_present_button.disabled = False
            self.quick_absent_button.disabled = False

    def mark_home_attendance(self, status):
        if not self.quick_attendance_subject:
            return

        app = App.get_running_app()
        class_type = "LECTURE"
        try:
            info = self.get_home_attendance_class()
            if info:
                class_type = info.get("type") or "LECTURE"
        except Exception:
            pass

        key = attendance_key(
            self.quick_attendance_date,
            self.quick_attendance_subject,
            self.quick_attendance_time,
            class_type,
        )

        app.attendance_data[key] = {
            "subject": self.quick_attendance_subject,
            "date": self.quick_attendance_date,
            "time": self.quick_attendance_time,
            "type": class_type,
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
                subjects = [get_slot_subject(timetable_day, i) for i in range(len(TIMES))]
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
        self.update_unmarked_today()
        self.update_next_class()
        self.update_upcoming_tasks()

    def update_unmarked_today(self):
        now = self.get_local_now()
        today = now.date()
        if get_semester_status(today):
            self.unmarked_label.text = "0 unmarked classes today"
            return

        if today.weekday() == 5:
            timetable_day = SPECIAL_SATURDAYS.get(today)
        elif today.weekday() < 5:
            timetable_day = today.strftime("%A").upper()
        else:
            timetable_day = None

        if not timetable_day:
            self.unmarked_label.text = "0 unmarked classes today"
            return

        unmarked = 0
        for index in range(len(TIMES)):
            subject = get_slot_subject(timetable_day, index)
            if not subject or subject == "LUNCH BREAK":
                continue
            if is_class_cancelled(today.isoformat(), subject, TIMES[index]):
                continue
            class_type = get_slot_type(timetable_day, index) or "LECTURE"
            key = attendance_key(today.isoformat(), subject, TIMES[index], class_type)
            if key not in App.get_running_app().attendance_data:
                unmarked += 1

        self.unmarked_label.text = (
            f"{unmarked} unmarked class{'es' if unmarked != 1 else ''} today"
            + (" — mark them from Timetable" if unmarked else " — all caught up")
        )

    def update_next_class(self):
        now = self.get_local_now()
        today = now.date()
        if get_semester_status(today):
            self.next_class_text.text = "No upcoming class today."
            return

        if today.weekday() == 5:
            timetable_day = SPECIAL_SATURDAYS.get(today)
        elif today.weekday() < 5:
            timetable_day = today.strftime("%A").upper()
        else:
            timetable_day = None

        if not timetable_day:
            self.next_class_text.text = "No upcoming class today."
            return

        current_minutes = now.hour * 60 + now.minute
        candidate = None
        for index in range(len(TIMES)):
            subject = get_slot_subject(timetable_day, index)
            if not subject or subject == "LUNCH BREAK":
                continue
            if is_class_cancelled(today.isoformat(), subject, TIMES[index]):
                continue
            try:
                start, end = self.parse_time_slot(TIMES[index])
            except Exception:
                continue
            if current_minutes < start:
                candidate = (index, subject, TIMES[index], start)
                break

        if candidate is None:
            self.next_class_text.text = "No more classes today."
            return

        index, subject, time, _ = candidate
        class_type = get_slot_type(timetable_day, index) or "LECTURE"
        prep = get_subject_prep(subject)
        bring = prep.get("what_to_bring", "").strip()
        notes = prep.get("notes", "").strip()
        lines = [f"{subject}  •  {class_type}", time]
        if bring:
            lines.append(f"Bring: {bring}")
        else:
            lines.append("Bring: Not set yet")
        if notes:
            lines.append(f"Note: {notes}")
        self.next_class_text.text = "\n".join(lines)

    def update_attendance_summary(self):
        low_attendance_subjects = []
        all_marked_subjects = []

        for subject in SUBJECTS:
            present, absent, total, percentage = get_subject_stats(subject)
            if total > 0:
                all_marked_subjects.append((subject, present, absent, total, percentage))
                if percentage < REQUIRED_ATTENDANCE:
                    needed = math.ceil((0.75 * total - present) / 0.25)
                    needed = max(1, needed)
                    low_attendance_subjects.append((subject, percentage, present, total, needed))

        if not all_marked_subjects:
            self.attendance_header_label.text = "ATTENDANCE WATCH"
            self.attendance_header_label.color = UI_MUTED
            self.attendance_summary.text = "No classes marked yet"
            self.attendance_sub_label.text = "Keep subjects ≥ 75% to stay safe"
            self.attendance_ring.set_percentage(0, label_text="SAFE", is_safe=True)
            return

        if low_attendance_subjects:
            low_attendance_subjects.sort(key=lambda x: x[1])
            worst_sub, worst_pct, p, tot, needed = low_attendance_subjects[0]

            self.attendance_header_label.text = f"⚠️ AT RISK (< {REQUIRED_ATTENDANCE}%)"
            self.attendance_header_label.color = UI_DANGER
            self.attendance_summary.text = f"{worst_sub}: {worst_pct:.0f}% ({p}/{tot})"
            self.attendance_sub_label.text = f"Needs +{needed} present class{'es' if needed > 1 else ''} for 75%"
            self.attendance_ring.set_percentage(worst_pct, label_text=worst_sub[:8], is_safe=False)
        else:
            all_marked_subjects.sort(key=lambda x: x[4])
            lowest_sub, p, a, tot, lowest_pct = all_marked_subjects[0]

            self.attendance_header_label.text = "ALL SUBJECTS SAFE 🎉"
            self.attendance_header_label.color = UI_SUCCESS
            self.attendance_summary.text = f"Lowest: {lowest_sub} ({lowest_pct:.0f}%)"
            self.attendance_sub_label.text = f"All {len(all_marked_subjects)} marked subjects are ≥ 75%"
            self.attendance_ring.set_percentage(lowest_pct, label_text="SAFE", is_safe=True)

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
            today = date.today()
            for a in pending[:3]:
                title = a.get("title", "Untitled")
                subject = a.get("subject", "No subject")
                due_text = a.get("due_date", "No date")
                status = ""
                try:
                    due = date.fromisoformat(due_text)
                    days = (due - today).days
                    if days < 0:
                        status = "OVERDUE"
                    elif days == 0:
                        status = "DUE TODAY"
                    elif days == 1:
                        status = "DUE TOMORROW"
                    else:
                        status = f"DUE IN {days} DAYS"
                except Exception:
                    status = "DUE DATE UNKNOWN"
                lines.append(f"{status}\n• {title}  ·  {subject}\n  {due_text}")
            if len(pending) > 3:
                lines.append(f"+ {len(pending)-3} more pending")
            self.upcoming_text.text = "\n\n".join(lines)
        except Exception:
            self.upcoming_text.text = "No assignments yet"

    def show_calendar_info(self):
        if self.manager:
            self.manager.current = "calendar"

