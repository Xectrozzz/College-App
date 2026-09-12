from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle
from frontend.theme import UI_SURFACE, UI_TEXT, fs, rounded_background


class SubjectCard(Label):

    def __init__(self, subject="", **kwargs):
        super().__init__(**kwargs)
        self.subject = subject
        self.size_hint = (None, None)
        self.width = 145
        self.height = 88
        self.color = UI_TEXT
        self.bold = True
        self.halign = "center"
        self.valign = "middle"

        self.text_size = (
            self.width - 12,
            self.height - 10
        )

        if subject == "LUNCH BREAK":
            self.text = subject
            self.bold = True
            self.font_size = fs(60)
            self.card_color = (0.98, 0.65, 0.12, 1)
        elif subject:
            self.text = subject
            self.bold = True
            self.font_size = fs(60)
            if "MATHEMATICS" in subject:
                self.card_color = (0.25, 0.55, 0.95, 1)
            elif "ENGLISH" in subject:
                self.card_color = (0.10, 0.75, 0.45, 1)
            elif "MATERIALS" in subject:
                self.card_color = (0.95, 0.60, 0.25, 1)
            elif "HISTORY" in subject:
                self.card_color = (0.65, 0.40, 0.85, 1)
            elif "GRAPHICS" in subject:
                self.card_color = (0.90, 0.35, 0.55, 1)
            elif "BASIC DESIGN" in subject:
                self.card_color = (0.20, 0.70, 0.70, 1)
            elif "SPORTS" in subject:
                self.card_color = (0.85, 0.45, 0.20, 1)
            else:
                self.card_color = (0.40, 0.45, 0.55, 1)
        else:
            self.text = "FREE"
            self.font_size = fs(60)
            self.card_color = (0.20, 0.25, 0.35, 1)

        with self.canvas.before:
            Color(*self.card_color)
            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[14]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size


class SubjectCardButton(ButtonBehavior, FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rounded_background(self, UI_SURFACE, 14)

