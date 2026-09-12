import json
import os
from datetime import date
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup

from backend.constants import SUBJECTS
from frontend.theme import UI_BG, UI_SURFACE, UI_SURFACE_2, UI_TEXT, UI_MUTED, UI_SUCCESS, UI_DANGER, UI_WARNING, UI_ACCENT, fs, rounded_background
from frontend.widgets.buttons import AppButton, make_stat_box
from frontend.widgets.navigation import BottomNav


class AssignmentsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main = BoxLayout(orientation="vertical", padding=(10, 8), spacing=7)
        rounded_background(self.main, UI_BG, 0)

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=74)
        header.add_widget(Label(text="ASSIGNMENTS", font_size=fs(29), bold=True, color=UI_TEXT, size_hint_y=None, height=36))
        header.add_widget(Label(text="Stay on top of studio, theory & class work", font_size=fs(14), color=UI_MUTED, size_hint_y=None, height=22))
        self.main.add_widget(header)

        add_button = AppButton(text="＋  ADD ASSIGNMENT", font_size=fs(16), bold=True, size_hint_y=None, height=48)
        add_button.bind(on_press=lambda x: self.open_add_assignment())
        self.main.add_widget(add_button)

        self.scroll = ScrollView(do_scroll_y=True, bar_width=4)
        self.list_layout = BoxLayout(orientation="vertical", spacing=7, size_hint_y=None, padding=(0, 2))
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        self.main.add_widget(self.scroll)
        self.main.add_widget(BottomNav(current="assignments"))
        self.add_widget(self.main)

    def get_assignment_file(self):
        app = App.get_running_app()
        return os.path.join(app.user_data_dir, "assignments.json")

    def load_assignments(self):
        filename = self.get_assignment_file()
        try:
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    return json.load(file)
        except Exception as e:
            print("Could not load assignments:", e)
        return []

    def save_assignments(self, assignments):
        filename = self.get_assignment_file()
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as file:
                json.dump(assignments, file, indent=4)
        except Exception as e:
            print("Could not save assignments:", e)

    def on_pre_enter(self, *args):
        self.refresh_assignments()

    def refresh_assignments(self):
        self.list_layout.clear_widgets()
        assignments = self.load_assignments()
        assignments.sort(key=lambda item: (item.get("completed", False), item.get("due_date", "9999-99-99")))

        pending_count = sum(1 for a in assignments if not a.get("completed", False))
        completed_count = len(assignments) - pending_count
        summary = BoxLayout(orientation="vertical", padding=(12, 9), spacing=5, size_hint_y=None, height=150)
        rounded_background(summary, UI_SURFACE, 18)
        summary.add_widget(Label(text="TASK OVERVIEW", font_size=fs(16), bold=True, color=UI_TEXT, size_hint_y=None, height=24))
        summary_row = BoxLayout(orientation="horizontal", spacing=7, size_hint_y=None, height=92)
        summary_row.add_widget(make_stat_box(str(pending_count), "PENDING", UI_WARNING))
        summary_row.add_widget(make_stat_box(str(completed_count), "COMPLETED", UI_SUCCESS))
        summary_row.add_widget(make_stat_box(str(len(assignments)), "TOTAL", UI_ACCENT))
        summary.add_widget(summary_row)
        self.list_layout.add_widget(summary)

        if not assignments:
            empty = BoxLayout(orientation="vertical", padding=(14, 18), spacing=7, size_hint_y=None, height=390)
            rounded_background(empty, UI_SURFACE, 18)
            empty.add_widget(Label(text="NO TASKS YET", font_size=fs(21), bold=True, color=UI_TEXT, size_hint_y=None, height=35))
            empty.add_widget(Label(text="Add your first assignment above.\nIt will appear here with its due date and priority.", font_size=fs(15), color=UI_MUTED, halign="center", valign="middle"))
            self.list_layout.add_widget(empty)

            tips = BoxLayout(orientation="vertical", padding=(13, 11), spacing=5, size_hint_y=None, height=220)
            rounded_background(tips, UI_SURFACE, 18)
            tips.add_widget(Label(text="STAY ORGANIZED", font_size=fs(17), bold=True, color=UI_TEXT, size_hint_y=None, height=27))
            tips.add_widget(Label(text="Add studio work, drawings, submissions and theory tasks here.\nUse the due date to keep your upcoming work visible on the Dashboard.", font_size=fs(14), color=UI_MUTED, halign="left", valign="middle"))
            self.list_layout.add_widget(tips)
            return

        for index, assignment in enumerate(assignments):
            self.add_assignment_card(assignment, index)

    def add_assignment_card(self, assignment, index):
        completed = assignment.get("completed", False)
        title = assignment.get("title", "Untitled Assignment")
        subject = assignment.get("subject", "No subject")
        due_date = assignment.get("due_date", "No due date")
        priority = assignment.get("priority", "Medium")

        if completed:
            status = "COMPLETED"
        else:
            try:
                due = date.fromisoformat(due_date)
                today = date.today()
                if due < today:
                    status = "OVERDUE"
                elif due == today:
                    status = "DUE TODAY"
                else:
                    days = (due - today).days
                    status = "DUE TOMORROW" if days == 1 else f"DUE IN {days} DAYS"
            except Exception:
                status = "DUE DATE UNKNOWN"

        card = BoxLayout(orientation="vertical", padding=(12, 10), spacing=5, size_hint_y=None, height=190)
        rounded_background(card, UI_SURFACE, 17)

        title_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=32)
        title_label = Label(text=title, font_size=fs(17), bold=not completed, color=UI_TEXT, halign="left", valign="middle")
        title_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        title_row.add_widget(title_label)
        title_row.add_widget(Label(text=priority.upper(), font_size=fs(12), bold=True, color=UI_WARNING if priority == "High" else UI_MUTED, size_hint_x=None, width=72, halign="right"))
        card.add_widget(title_row)

        meta = Label(text=f"{subject}   •   Due {due_date}\n{status}", font_size=fs(14), color=UI_SUCCESS if status == "COMPLETED" else (UI_DANGER if status == "OVERDUE" else UI_MUTED), halign="left", valign="middle", size_hint_y=None, height=43)
        meta.bind(size=lambda i, v: setattr(i, "text_size", v))
        card.add_widget(meta)

        buttons = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=40)
        complete_button = AppButton(text="UNDO" if completed else "MARK DONE", font_size=fs(13))
        complete_button.bind(on_press=lambda x, i=index: self.toggle_assignment(i))
        delete_button = AppButton(text="DELETE", font_size=fs(13), background_color=UI_SURFACE_2)
        delete_button.bind(on_press=lambda x, i=index: self.delete_assignment(i))
        buttons.add_widget(complete_button)
        buttons.add_widget(delete_button)
        card.add_widget(buttons)
        self.list_layout.add_widget(card)

    def open_add_assignment(self):
        content = BoxLayout(orientation="vertical", padding=15, spacing=10)

        title_input = TextInput(
            hint_text="Assignment title",
            multiline=False,
            font_size=fs(21),
            size_hint_y=None,
            height=45
        )

        subject_spinner = Spinner(
            text=SUBJECTS[0],
            values=SUBJECTS,
            font_size=fs(20),
            size_hint_y=None,
            height=45
        )

        due_input = TextInput(
            hint_text="Due date (YYYY-MM-DD)",
            multiline=False,
            font_size=fs(21),
            size_hint_y=None,
            height=45
        )

        priority_spinner = Spinner(
            text="Medium",
            values=["Low", "Medium", "High"],
            font_size=fs(20),
            size_hint_y=None,
            height=45
        )

        content.add_widget(title_input)
        content.add_widget(subject_spinner)
        content.add_widget(due_input)
        content.add_widget(priority_spinner)

        buttons = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=50)
        cancel = AppButton(text="CANCEL", font_size=fs(20), bold=True)
        save = AppButton(text="SAVE", font_size=fs(20), bold=True)
        buttons.add_widget(cancel)
        buttons.add_widget(save)
        content.add_widget(buttons)

        popup = Popup(
            title="ADD ASSIGNMENT",
            content=content,
            size_hint=(0.85, 0.65),
            auto_dismiss=False
        )

        cancel.bind(on_press=lambda x: popup.dismiss())
        save.bind(on_press=lambda x: self.save_new_assignment(
            popup, title_input.text, subject_spinner.text, due_input.text, priority_spinner.text
        ))
        popup.open()

    def save_new_assignment(self, popup, title, subject, due_date, priority):
        title = title.strip()
        due_date = due_date.strip()

        if not title:
            return

        try:
            date.fromisoformat(due_date)
        except Exception:
            return

        assignments = self.load_assignments()
        assignments.append({
            "title": title,
            "subject": subject,
            "due_date": due_date,
            "priority": priority,
            "completed": False
        })

        self.save_assignments(assignments)
        popup.dismiss()
        self.refresh_assignments()

    def toggle_assignment(self, index):
        assignments = self.load_assignments()
        assignments.sort(key=lambda item: (item.get("completed", False), item.get("due_date", "9999-99-99")))
        if 0 <= index < len(assignments):
            assignments[index]["completed"] = not assignments[index].get("completed", False)
        self.save_assignments(assignments)
        self.refresh_assignments()

    def delete_assignment(self, index):
        assignments = self.load_assignments()
        assignments.sort(key=lambda item: (item.get("completed", False), item.get("due_date", "9999-99-99")))
        if 0 <= index < len(assignments):
            assignments.pop(index)
        self.save_assignments(assignments)
        self.refresh_assignments()

