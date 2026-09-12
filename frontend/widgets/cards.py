from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from frontend.theme import *
from frontend.widgets.buttons import AppButton

class SubjectCardButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.padding = (ui(18), ui(16))
        self.spacing = ui(6)

class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rounded_background(self, UI_SURFACE, 20, UI_BORDER)

def label(text, size=14, color=UI_TEXT, bold=False, **kwargs):
    return Label(text=text, font_size=fs(size), color=color, bold=bold, **kwargs)
