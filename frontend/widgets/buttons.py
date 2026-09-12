from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from frontend.theme import *

class AppButton(Button):
    def __init__(self, **kwargs):
        bg = kwargs.pop("background_color", None)
        super().__init__(**kwargs)
        self.background_color = bg if bg is not None else UI_SURFACE_2
        self.color = UI_TEXT
        self.bold = True
        self.background_normal = ""
        self.background_down = ""
        self.background_disabled_normal = ""
        self.border = (0, 0, 0, 0)
        self.padding = (ui(14), ui(8))
        with self.canvas.before:
            self._color = Color(*self.background_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
        self.bind(pos=self._sync, size=self._sync, background_color=self._sync_color, disabled=self._sync_color)
        self._sync()
    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
    def _sync_color(self, *_):
        c = self.background_color
        self._color.rgba = (c[0], c[1], c[2], 0.30) if self.disabled else c
        self.color = UI_MUTED if self.disabled else UI_TEXT

class IconButton(AppButton):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_x", None)
        kwargs.setdefault("width", ui(46))
        kwargs.setdefault("font_size", fs(22))
        kwargs.setdefault("background_color", UI_SURFACE_2)
        super().__init__(**kwargs)

def make_stat_box(value, label, accent=UI_ACCENT):
    box = BoxLayout(orientation="vertical", padding=(ui(10), ui(8)), spacing=ui(2))
    rounded_background(box, UI_SURFACE_2, 14)
    box.add_widget(Label(text=str(value), color=accent, bold=True, font_size=fs(23), size_hint_y=None, height=ui(34)))
    box.add_widget(Label(text=label, color=UI_MUTED, bold=True, font_size=fs(10), size_hint_y=None, height=ui(20)))
    return box

def make_link_card(title, subtitle, action, accent=UI_ACCENT, height=90):
    card = AppButton(text=f"{title}\n{subtitle}", font_size=fs(14), halign="left", valign="middle", background_color=UI_SURFACE, size_hint_y=None, height=ui(height))
    card.text_size = (None, card.height - ui(10))
    card.bind(on_press=action)
    return card
