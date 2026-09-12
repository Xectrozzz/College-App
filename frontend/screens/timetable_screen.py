from datetime import date, timedelta, datetime
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup

from backend.constants import TIMES, SUBJECTS, CLASS_TYPES, SPECIAL_SATURDAYS
from backend.storage import (
    load_timetable,
    save_timetable,
    _normalise_timetable,
    get_slot_entry,
    attendance_key,
)
from backend.attendance_service import (
    get_slot_subject,
    get_slot_type,
    is_class_cancelled,
    get_semester_status,
)
from frontend.theme import UI_BG, UI_SURFACE, UI_SURFACE_2, UI_TEXT, UI_MUTED, UI_WARNING, UI_ACCENT, fs, rounded_background
from frontend.widgets.buttons import AppButton
from frontend.widgets.navigation import BottomNav
from frontend.popups.attendance_popup import AttendancePopup


class TimetableScreen(Screen):
    """Accessible single-day timeline timetable with a weekly date selector."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.week_offset = 0
        self.selected_day_index = 0
        self.filter_mode = "ALL"
        self.edit_mode = False
        self._current_index = 0

        self.main = BoxLayout(
            orientation="vertical",
            padding=(18, 12, 18, 10),
            spacing=10,
        )
        rounded_background(self.main, UI_BG, 0)

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

        self.edit_button = AppButton(
            text="EDIT",
            font_size=fs(12),
            bold=True,
            size_hint_x=None,
            width=70,
        )
        self.edit_button.bind(on_press=lambda x: self.toggle_edit_mode())
        top.add_widget(self.edit_button)

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

        self.day_strip = BoxLayout(
            orientation="horizontal",
            spacing=7,
            size_hint_y=None,
            height=92,
        )
        self.main.add_widget(self.day_strip)

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
        return [get_slot_subject(timetable_day, i) for i in range(len(TIMES))]

    def attendance_record(self, actual_date, subject, time):
        app = App.get_running_app()
        timetable_day = self.get_timetable_day(actual_date)
        class_type = "LECTURE"
        if timetable_day and time in TIMES:
            index = TIMES.index(time)
            class_type = get_slot_type(timetable_day, index) or "LECTURE"

        key = attendance_key(
            actual_date.isoformat(), subject, time, class_type
        )
        record = app.attendance_data.get(key)
        if record is not None:
            return record

        legacy = attendance_key(actual_date.isoformat(), subject, time)
        return app.attendance_data.get(legacy)

    def update_filter_buttons(self):
        for mode, button in self.filter_buttons.items():
            button.background_normal = ""
            if mode == self.filter_mode:
                button.background_color = UI_ACCENT
            else:
                button.background_color = UI_SURFACE_2

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

            if not subject:
                if self.filter_mode == "ALL":
                    self.add_empty_time_row(timetable_day, index, time)
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

            class_type = get_slot_type(timetable_day, index)
            self._current_index = index
            self.add_class_row(actual_date, subject, time, record, class_type)
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

    def add_empty_time_row(self, day, index, time):
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

        if self.edit_mode:
            slot = AppButton(
                text="ADD CLASS\nTap to choose subject & type",
                font_size=fs(15),
                bold=True,
                halign="center",
                valign="middle",
                background_color=UI_SURFACE_2,
                size_hint_x=1,
            )
            slot.bind(on_press=lambda x, d=day, idx=index: self.open_slot_editor(d, idx))
        else:
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

    def add_class_row(self, actual_date, subject, time, record, class_type="LECTURE"):
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
            bg = (0.45, 0.25, 0.12, 1)
        elif record and record.get("status") == "present":
            bg = (0.10, 0.55, 0.25, 1)
        elif record and record.get("status") == "absent":
            bg = (0.72, 0.18, 0.18, 1)
        elif current:
            bg = (0.10, 0.35, 0.75, 1)
        else:
            bg = UI_SURFACE

        if record and record.get("type"):
            display_type = str(record.get("type")).upper()
        else:
            display_type = class_type

        if not cancelled and current:
            text = f"{subject}\n\n{display_type}  •  CURRENT CLASS"
        elif not cancelled and record:
            text = f"{subject}\n\n{display_type}  •  {record.get('status','').upper()}"
        elif not cancelled:
            text = f"{subject}\n\n{display_type}"
        else:
            text = f"{subject}\n\nCANCELLED"

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

        button.bind(
            on_press=lambda x, s=subject, d=date_string, t=time, ct=class_type, idx=self._current_index:
                self.handle_class_press(s, d, t, ct, idx)
        )

        row.add_widget(button)
        self.timeline.add_widget(row)

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.edit_button.text = "DONE" if self.edit_mode else "EDIT"
        self.refresh_timeline_only()

    def handle_class_press(self, subject, class_date, time, class_type, index):
        if self.edit_mode:
            actual_date = date.fromisoformat(class_date)
            timetable_day = self.get_timetable_day(actual_date)
            if timetable_day:
                self.open_slot_editor(timetable_day, index)
        else:
            self.open_attendance(subject, class_date, time, class_type)

    def open_slot_editor(self, day, index):
        entry = get_slot_entry(day, index)
        current_subject = entry.get("subject", "")
        current_type = entry.get("type", "") or "LECTURE"

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        content.add_widget(Label(
            text=f"{day.title()}\n{TIMES[index]}",
            font_size=fs(20),
            bold=True,
            size_hint_y=None,
            height=55
        ))

        subject_spinner = Spinner(
            text=current_subject if current_subject else "FREE",
            values=["FREE"] + SUBJECTS,
            font_size=fs(17),
            size_hint_y=None,
            height=52
        )

        type_spinner = Spinner(
            text=current_type if current_subject else "LECTURE",
            values=CLASS_TYPES,
            font_size=fs(17),
            size_hint_y=None,
            height=52
        )

        content.add_widget(Label(
            text="SUBJECT",
            font_size=fs(13),
            bold=True,
            color=UI_MUTED,
            size_hint_y=None,
            height=22
        ))
        content.add_widget(subject_spinner)

        content.add_widget(Label(
            text="CLASS TYPE",
            font_size=fs(13),
            bold=True,
            color=UI_MUTED,
            size_hint_y=None,
            height=22
        ))
        content.add_widget(type_spinner)

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=52
        )

        cancel = AppButton(text="CANCEL", font_size=fs(16))
        clear = AppButton(text="CLEAR SLOT", font_size=fs(16), background_color=UI_WARNING)
        save = AppButton(text="SAVE", font_size=fs(16), background_color=UI_ACCENT)

        buttons.add_widget(cancel)
        buttons.add_widget(clear)
        buttons.add_widget(save)
        content.add_widget(buttons)

        popup = Popup(
            title="EDIT TIMETABLE SLOT",
            content=content,
            size_hint=(0.92, 0.58),
            auto_dismiss=False
        )

        cancel.bind(on_press=lambda x: popup.dismiss())
        clear.bind(on_press=lambda x: self.save_timetable_slot(
            popup, day, index, "", ""
        ))

        def do_save(_):
            subject = subject_spinner.text
            if subject == "FREE":
                subject = ""
            class_type = type_spinner.text if subject else ""
            self.save_timetable_slot(popup, day, index, subject, class_type)

        save.bind(on_press=do_save)
        popup.open()

    def save_timetable_slot(self, popup, day, index, subject, class_type):
        app = App.get_running_app()
        data = _normalise_timetable(getattr(app, "timetable_data", load_timetable()))
        data.setdefault(day, [{"subject": "", "type": ""} for _ in TIMES])
        data[day][index] = {
            "subject": subject.strip(),
            "type": class_type.upper() if subject.strip() else ""
        }
        save_timetable(data)
        popup.dismiss()
        self.refresh_grid()
        try:
            app.root.get_screen("home").update_dashboard()
        except Exception:
            pass

    def open_attendance(self, subject, class_date, time, class_type="LECTURE"):
        AttendancePopup(
            subject=subject,
            class_date=class_date,
            time=time,
            class_type=class_type,
        ).open()

