from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from backend.constants import HOLIDAYS, SPECIAL_SATURDAYS
from frontend.theme import UI_BG, UI_SURFACE, UI_TEXT, UI_MUTED, UI_ACCENT, UI_WARNING, fs, rounded_background
from frontend.widgets.buttons import AppButton
from frontend.widgets.navigation import BottomNav


class AcademicCalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main = BoxLayout(orientation="vertical", padding=(10, 8), spacing=7)
        rounded_background(main, UI_BG, 0)

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=62)
        header.add_widget(Label(text="ACADEMIC CALENDAR", font_size=fs(27), bold=True, color=UI_TEXT, size_hint_y=None, height=35))
        header.add_widget(Label(text="WINTER SEMESTER 2026", font_size=fs(14), color=UI_MUTED, size_hint_y=None, height=22))
        main.add_widget(header)

        self.scroll = ScrollView(do_scroll_y=True, bar_width=4)
        content = BoxLayout(orientation="vertical", spacing=6, padding=(0, 2), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        self.add_section(content, "SEMESTER TIMELINE")
        self.add_event(content, "SEMESTER START", "24 Aug 2026", UI_ACCENT, "01")
        self.add_event(content, "MID-SEMESTER EXAMS", "01 Oct – 10 Oct 2026", UI_WARNING, "02")
        self.add_event(content, "NO INSTRUCTION", "09 Nov – 13 Nov 2026", UI_MUTED, "03")
        self.add_event(content, "FORMAL TEACHING UNTIL", "05 Dec 2026", UI_TEXT, "04")
        self.add_event(content, "END-SEMESTER EXAMS", "07 Dec – 15 Dec 2026", UI_WARNING, "05")

        self.add_section(content, "HOLIDAYS")
        for holiday_date, label in sorted(HOLIDAYS.items()):
            clean = label.split("\n")[-1]
            self.add_event(content, clean, holiday_date.strftime("%a · %d %b %Y"), UI_TEXT, "HOL")

        self.add_section(content, "SPECIAL SATURDAYS")
        for saturday, follows in sorted(SPECIAL_SATURDAYS.items()):
            self.add_event(content, f"Saturday follows {follows.title()}", saturday.strftime("%a · %d %b %Y"), UI_TEXT, "SAT")

        footer = BoxLayout(orientation="vertical", padding=(12, 10), spacing=4, size_hint_y=None, height=118)
        rounded_background(footer, UI_SURFACE, 17)
        footer.add_widget(Label(text="NEED THE FULL TIMETABLE?", font_size=fs(15), bold=True, color=UI_TEXT, size_hint_y=None, height=25))
        footer.add_widget(Label(text="Open Weekly Timetable to see your daily classes, special Saturdays and attendance marking.", font_size=fs(13), color=UI_MUTED, halign="left", valign="middle"))
        open_tt = AppButton(text="OPEN WEEKLY TIMETABLE  →", font_size=fs(13), size_hint_y=None, height=34)
        open_tt.bind(on_press=lambda x: setattr(self.manager, "current", "timetable"))
        footer.add_widget(open_tt)
        content.add_widget(footer)

        self.scroll.add_widget(content)
        main.add_widget(self.scroll)
        main.add_widget(BottomNav(current="calendar"))
        self.add_widget(main)

    def add_section(self, parent, title):
        parent.add_widget(Label(text=title, font_size=fs(16), bold=True, color=UI_TEXT, size_hint_y=None, height=27, halign="left"))

    def add_event(self, parent, title, detail, accent, tag):
        card = BoxLayout(orientation="horizontal", padding=(10, 7), spacing=8, size_hint_y=None, height=88)
        rounded_background(card, UI_SURFACE, 15)
        badge = Label(text=tag, font_size=fs(11), bold=True, color=accent, size_hint_x=None, width=42, halign="center", valign="middle")
        card.add_widget(badge)
        info = BoxLayout(orientation="vertical", spacing=0)
        info.add_widget(Label(text=title, font_size=fs(15), bold=True, color=UI_TEXT, halign="left", valign="middle", size_hint_y=None, height=27))
        info.add_widget(Label(text=detail, font_size=fs(13), color=UI_MUTED, halign="left", valign="middle", size_hint_y=None, height=22))
        card.add_widget(info)
        parent.add_widget(card)

