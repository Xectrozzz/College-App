from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from backend.storage import (
    attendance_key,
    cancellation_key,
    save_attendance,
    save_cancellations,
    load_cancellations,
)
from backend.attendance_service import is_class_cancelled
from frontend.theme import UI_WARNING, fs
from frontend.widgets.buttons import AppButton


class AttendancePopup(Popup):

    def __init__(
        self,
        subject,
        class_date,
        time,
        class_type="LECTURE",
        **kwargs
    ):

        self.subject = subject
        self.class_date = class_date
        self.time = time
        self.class_type = class_type or "LECTURE"

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
                    f"{time}\n"
                    f"{self.class_type}"
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
            on_press=lambda x: self.mark("present")
        )

        absent.bind(
            on_press=lambda x: self.mark("absent")
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
            class_type = self.class_type or "LECTURE"
            app.attendance_data.pop(
                attendance_key(self.class_date, self.subject, self.time, class_type),
                None,
            )
            app.attendance_data.pop(
                attendance_key(self.class_date, self.subject, self.time),
                None,
            )
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
        key = attendance_key(
            self.class_date,
            self.subject,
            self.time,
            self.class_type,
        )

        app.attendance_data[key] = {
            "subject": self.subject,
            "date": self.class_date,
            "time": self.time,
            "type": self.class_type,
            "status": status
        }

        save_attendance(app.attendance_data)
        self.dismiss()
        timetable = app.root.get_screen("timetable")
        timetable.refresh_grid()
        try:
            home = app.root.get_screen("home")
            home.update_dashboard()
        except Exception:
            pass

