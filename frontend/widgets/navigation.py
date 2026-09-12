from kivy.uix.boxlayout import BoxLayout
from frontend.theme import UI_SURFACE, UI_SURFACE_2, UI_SURFACE_3, UI_ACCENT, fs, rounded_background
from frontend.widgets.buttons import AppButton


class BottomNav(BoxLayout):
    """Persistent primary navigation designed for narrow portrait screens."""

    def __init__(self, current="home", **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=6,
            padding=(8, 6),
            size_hint_y=None,
            height=72,
            **kwargs
        )
        rounded_background(self, UI_SURFACE, 20, border_color=UI_SURFACE_3)

        items = [
            ("home", "🏠 HOME"),
            ("subjects", "📚 SUBJECTS"),
            ("assignments", "✅ TASKS"),
            ("calendar", "📅 CALENDAR"),
        ]

        for screen_name, label in items:
            is_active = (screen_name == current)
            button = AppButton(
                text=label,
                font_size=fs(13),
                bold=True,
                background_color=UI_ACCENT if is_active else UI_SURFACE_2,
                size_hint_x=1,
            )
            button.bind(on_press=lambda x, s=screen_name: self.go(s))
            self.add_widget(button)

    def go(self, screen_name):
        if self.parent and self.parent.parent:
            manager = self.parent.parent.manager
            if manager:
                manager.current = screen_name

