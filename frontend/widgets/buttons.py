from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from frontend.theme import (
    UI_SURFACE,
    UI_SURFACE_2,
    UI_TEXT,
    UI_MUTED,
    UI_ACCENT,
    UI_SUCCESS,
    UI_DANGER,
    fs,
    rounded_background,
)


class AppButton(Button):
    """Rounded, modern button used throughout the app."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
                radius=[16]
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


class HeaderCard(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = kwargs.get("width", 170)
        self.height = 54
        self.color = UI_TEXT
        self.bold = True
        self.font_size = fs(22)
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


def make_stat_box(value, label, accent=UI_ACCENT):
    box = BoxLayout(orientation="vertical", padding=(5, 4), spacing=0)
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

