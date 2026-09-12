from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Line
from backend.constants import REQUIRED_ATTENDANCE
from frontend.theme import UI_SURFACE_2, UI_TEXT, UI_MUTED, UI_SUCCESS, UI_DANGER, fs, ui


class AttendanceRing(BoxLayout):
    """Circular arc canvas gauge displaying low-attendance or subject status."""

    def __init__(self, percentage=0, label_text="RISK", **kwargs):
        super().__init__(orientation="vertical", spacing=0, padding=(0, 0), **kwargs)
        self.size_hint = (None, None)
        self.size = (110, 110)
        self.percentage = float(percentage)

        self.value_label = Label(
            text="0%",
            font_size=fs(23),
            bold=True,
            color=UI_TEXT,
            halign="center",
            valign="middle",
        )
        self.status_label = Label(
            text=label_text,
            font_size=fs(10),
            bold=True,
            color=UI_MUTED,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=20,
        )

        inner = BoxLayout(orientation="vertical", spacing=0, padding=(0, 22))
        inner.add_widget(self.value_label)
        inner.add_widget(self.status_label)
        self.add_widget(inner)

        with self.canvas.before:
            self.track_color = Color(*UI_SURFACE_2)
            self.track_line = Line(width=ui(7))
            self.progress_color = Color(*UI_SUCCESS)
            self.progress_line = Line(width=ui(7))

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.set_percentage(percentage, label_text)

    def _update_canvas(self, *_):
        cx = self.x + self.width / 2.0
        cy = self.y + self.height / 2.0
        r = max(10, min(self.width, self.height) / 2.0 - ui(8))
        self.track_line.circle = (cx, cy, r, 0, 360)

        pct = max(0.0, min(100.0, float(self.percentage)))
        if pct > 0:
            angle = (pct / 100.0) * 360.0
            start_angle = 90 - angle
            end_angle = 90
            self.progress_line.circle = (cx, cy, r, start_angle, end_angle)
        else:
            self.progress_line.circle = (cx, cy, r, 0, 0)

    def set_percentage(self, percentage, label_text="RISK", is_safe=False):
        self.percentage = max(0, min(100, float(percentage)))
        self.value_label.text = f"{self.percentage:.0f}%"
        self.status_label.text = str(label_text).upper()[:12]

        if is_safe:
            col = UI_SUCCESS
        elif self.percentage < REQUIRED_ATTENDANCE:
            col = UI_DANGER
        else:
            col = UI_SUCCESS

        self.value_label.color = col
        self.progress_color.rgba = col
        self._update_canvas()

