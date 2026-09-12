from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from frontend.theme import *
from frontend.widgets.buttons import AppButton

class BottomNav(BoxLayout):
    def __init__(self, current="home", **kwargs):
        super().__init__(orientation="horizontal", spacing=ui(5), padding=(ui(8), ui(6)), size_hint_y=None, height=ui(72), **kwargs)
        rounded_background(self, UI_SURFACE, 0, UI_BORDER)
        items = [("home", "⌂", "Dashboard"), ("timetable", "◷", "Timetable"), ("subjects", "▤", "Subjects"), ("assignments", "✓", "Assignments"), ("calendar", "□", "Calendar")]
        for screen_name, icon, title in items:
            active = screen_name == current
            text = f"{icon}\n{title}"
            button = AppButton(text=text, font_size=fs(11), background_color=UI_ACCENT_CONTAINER if active else UI_SURFACE, color=UI_ACCENT if active else UI_MUTED, size_hint_x=1)
            button.bind(on_press=lambda x, s=screen_name: self.go(s))
            self.add_widget(button)
    def go(self, screen_name):
        app = App.get_running_app()
        root = getattr(app, "root", None)
        if root is not None and hasattr(root, "current"):
            root.current = screen_name
