from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from frontend.theme import *

class AttendanceRing(FloatLayout):
    def __init__(self, percentage=0, **kwargs):
        super().__init__(size_hint_x=None, width=ui(150), **kwargs)
        self.percentage = percentage
        self._label = Label(text=f"{percentage:.0f}%", font_size=fs(28), bold=True, color=UI_TEXT, size_hint=(1,1))
        self.add_widget(self._label)
        with self.canvas.before:
            Color(*UI_SURFACE_2)
            self._track = Line(circle=(0,0,0), width=ui(10))
            Color(*UI_ACCENT)
            self._arc = Line(circle=(0,0,0), width=ui(10), cap="round")
        self.bind(pos=self._update, size=self._update)
        self._update()
    def _update(self, *_):
        cx = self.x + self.width/2
        cy = self.y + self.height/2
        r = min(self.width, self.height)/2 - ui(14)
        self._track.circle = (cx, cy, r)
        self._arc.circle = (cx, cy, r, 90, 90 + 360*max(0,min(100,self.percentage))/100)
    def set_percentage(self, value):
        self.percentage = value
        self._label.text = f"{value:.0f}%"
        self._update()
