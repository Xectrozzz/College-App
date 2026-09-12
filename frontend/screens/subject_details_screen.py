from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

from backend.constants import SUBJECT_INFO, CLASS_TYPES, REQUIRED_ATTENDANCE
from backend.storage import (
    get_teacher,
    load_teachers,
    save_teachers,
    get_subject_prep,
    save_subject_prep_for_subject,
    get_subject_assignments,
)
from backend.attendance_service import get_subject_stats, classes_can_skip
from frontend.theme import UI_BG, UI_TEXT, fs, rounded_background
from frontend.widgets.buttons import AppButton
from frontend.widgets.navigation import BottomNav


class SubjectDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_subject = None

        main = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=10
        )
        rounded_background(main, UI_BG, 0)

        self.title = Label(
            text="Subject",
            font_size=fs(31),
            bold=True,
            color=UI_TEXT,
            size_hint_y=None,
            height=50
        )
        main.add_widget(self.title)

        scroll = ScrollView(
            do_scroll_y=True
        )

        self.content_box = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=5,
            size_hint_y=None
        )
        self.content_box.bind(
            minimum_height=self.content_box.setter("height")
        )

        teacher_card = BoxLayout(
            orientation="vertical",
            spacing=5,
            padding=10,
            size_hint_y=None,
            height=105
        )

        self.teacher_label = Label(
            text="Teacher: Not set",
            font_size=fs(30),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=45
        )
        self.teacher_label.bind(
            size=lambda instance, value: setattr(
                instance, "text_size", value
            )
        )

        edit_teacher = AppButton(
            text="EDIT TEACHER NAME",
            font_size=fs(20),
            bold=True,
            size_hint_y=None,
            height=45
        )
        edit_teacher.bind(
            on_press=lambda x: self.open_teacher_editor()
        )

        teacher_card.add_widget(self.teacher_label)
        teacher_card.add_widget(edit_teacher)
        self.content_box.add_widget(teacher_card)

        prep_card = BoxLayout(
            orientation="vertical", spacing=5, padding=10,
            size_hint_y=None, height=145
        )
        self.prep_label = Label(
            text="WHAT TO BRING / NEXT CLASS NOTES",
            font_size=fs(17), bold=True, color=UI_TEXT,
            halign="left", valign="middle", size_hint_y=None, height=28
        )
        self.prep_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        edit_prep = AppButton(
            text="EDIT NEXT CLASS DETAILS", font_size=fs(18), bold=True,
            size_hint_y=None, height=48
        )
        edit_prep.bind(on_press=lambda x: self.open_prep_editor())
        self.prep_card = prep_card
        prep_card.add_widget(self.prep_label)
        prep_card.add_widget(edit_prep)
        self.content_box.add_widget(prep_card)

        self.attendance_label = Label(
            text="",
            font_size=fs(19),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=205
        )
        self.attendance_label.bind(
            size=lambda instance, value: setattr(
                instance, "text_size", value
            )
        )
        self.content_box.add_widget(self.attendance_label)

        syllabus_title = Label(
            text="SYLLABUS",
            font_size=fs(34),
            bold=True,
            halign="left",
            size_hint_y=None,
            height=35
        )
        self.content_box.add_widget(syllabus_title)

        self.syllabus_label = Label(
            text="",
            font_size=fs(20),
            halign="left",
            valign="top",
            size_hint_y=None
        )
        self.syllabus_label.bind(
            texture_size=lambda instance, value: setattr(
                instance, "height", value[1] + 15
            )
        )
        self.syllabus_label.bind(
            width=lambda instance, value: setattr(
                instance, "text_size", (value, None)
            )
        )
        self.content_box.add_widget(self.syllabus_label)

        assignments_title = Label(
            text="ASSIGNMENTS",
            font_size=fs(34),
            bold=True,
            halign="left",
            size_hint_y=None,
            height=35
        )
        self.content_box.add_widget(assignments_title)

        self.assignments_label = Label(
            text="",
            font_size=fs(20),
            halign="left",
            valign="top",
            size_hint_y=None
        )
        self.assignments_label.bind(
            texture_size=lambda instance, value: setattr(
                instance, "height", value[1] + 15
            )
        )
        self.assignments_label.bind(
            width=lambda instance, value: setattr(
                instance, "text_size", (value, None)
            )
        )
        self.content_box.add_widget(self.assignments_label)

        scroll.add_widget(self.content_box)
        main.add_widget(scroll)

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=55
        )

        assignments_button = AppButton(
            text="ALL ASSIGNMENTS",
            font_size=fs(20),
            bold=True
        )
        assignments_button.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "assignments"
            )
        )

        back = AppButton(
            text="BACK",
            font_size=fs(20),
            bold=True
        )
        back.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "subjects"
            )
        )

        buttons.add_widget(assignments_button)
        buttons.add_widget(back)
        main.add_widget(buttons)

        main.add_widget(BottomNav(current="subjects"))
        self.add_widget(main)

    def show_subject(self, subject):
        self.current_subject = subject
        self.title.text = subject

        info = SUBJECT_INFO.get(subject, {})
        credits = info.get("credits", "—")
        teacher = get_teacher(subject)

        if teacher:
            self.teacher_label.text = f"Teacher: {teacher}"
        else:
            self.teacher_label.text = "Teacher: Not set yet"

        prep = get_subject_prep(subject)
        bring = prep.get("what_to_bring", "").strip()
        notes = prep.get("notes", "").strip()
        prep_lines = []
        prep_lines.append(f"Bring: {bring}" if bring else "Bring: Not set yet")
        prep_lines.append(f"Next class notes: {notes}" if notes else "Next class notes: Not set yet")
        self.prep_label.text = "WHAT TO BRING / NEXT CLASS NOTES\n" + "\n".join(prep_lines)

        present, absent, total, percentage = get_subject_stats(subject)

        if total == 0:
            percentage_text = "No classes marked yet"
            skip_text = "Can skip: —"
        else:
            percentage_text = f"{percentage:.1f}%"
            skips = classes_can_skip(present, total)
            skip_text = f"Can skip: {skips} classes"

        type_lines = []
        for class_type in CLASS_TYPES:
            tp, ta, tt, tpct = get_subject_stats(subject, class_type)
            if tt:
                type_pct = f"{tpct:.1f}%"
                type_skip = classes_can_skip(tp, tt)
                type_lines.append(
                    f"{class_type}: {type_pct}   "
                    f"{tp} present  •  {ta} absent  •  {tt} marked  •  "
                    f"Can skip {type_skip}"
                )
            else:
                type_lines.append(f"{class_type}: —   No classes marked")

        self.attendance_label.text = (
            f"Credits: {credits}\n"
            f"OVERALL: {percentage_text}\n"
            f"Present: {present}    Absent: {absent}    Total: {total}\n"
            f"{skip_text}\n"
            f"Required: {REQUIRED_ATTENDANCE}%\n\n"
            f"ATTENDANCE BY CLASS TYPE\n" +
            "\n".join(type_lines)
        )

        syllabus = info.get("syllabus", [])
        if syllabus:
            self.syllabus_label.text = "\n\n".join(
                f"{index}. {item}"
                for index, item in enumerate(syllabus, 1)
            )
        else:
            self.syllabus_label.text = "No syllabus information available."

        assignments = get_subject_assignments(subject)
        if not assignments:
            self.assignments_label.text = (
                "No assignments for this subject yet.\n"
                "Add one from the Assignments screen."
            )
        else:
            assignments.sort(
                key=lambda item: (
                    item.get("completed", False),
                    item.get("due_date", "9999-99-99")
                )
            )
            lines = []
            for item in assignments:
                title = item.get("title", "Untitled Assignment")
                due = item.get("due_date", "No due date")
                priority = item.get("priority", "Medium")
                completed = item.get("completed", False)
                status = "COMPLETED" if completed else "PENDING"
                lines.append(
                    f"• {title}\n  Due: {due}  •  {priority}  •  {status}"
                )
            self.assignments_label.text = "\n\n".join(lines)

    def open_prep_editor(self):
        if not self.current_subject:
            return

        current = get_subject_prep(self.current_subject)
        content = BoxLayout(orientation="vertical", padding=15, spacing=10)

        bring_input = TextInput(
            text=current.get("what_to_bring", ""),
            hint_text="What to bring (e.g. A2 sheets, drawing tools, model)",
            multiline=True, font_size=fs(18), size_hint_y=None, height=85
        )
        notes_input = TextInput(
            text=current.get("notes", ""),
            hint_text="Next class notes / instructions",
            multiline=True, font_size=fs(18), size_hint_y=None, height=85
        )
        buttons = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=50)
        cancel = AppButton(text="CANCEL", font_size=fs(18), bold=True)
        save = AppButton(text="SAVE", font_size=fs(18), bold=True)
        buttons.add_widget(cancel)
        buttons.add_widget(save)
        content.add_widget(Label(text="WHAT TO BRING", font_size=fs(16), bold=True, size_hint_y=None, height=25))
        content.add_widget(bring_input)
        content.add_widget(Label(text="NEXT CLASS NOTES", font_size=fs(16), bold=True, size_hint_y=None, height=25))
        content.add_widget(notes_input)
        content.add_widget(buttons)

        popup = Popup(
            title=f"NEXT CLASS • {self.current_subject}",
            content=content, size_hint=(0.9, 0.65), auto_dismiss=False
        )
        cancel.bind(on_press=lambda x: popup.dismiss())
        save.bind(on_press=lambda x: self.save_prep(popup, bring_input.text, notes_input.text))
        popup.open()

    def save_prep(self, popup, what_to_bring, notes):
        save_subject_prep_for_subject(self.current_subject, what_to_bring, notes)
        popup.dismiss()
        self.show_subject(self.current_subject)

    def open_teacher_editor(self):
        if not self.current_subject:
            return

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        current = get_teacher(self.current_subject)

        input_box = TextInput(
            text=current,
            hint_text="Teacher name",
            multiline=False,
            font_size=fs(19),
            size_hint_y=None,
            height=50
        )

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=50
        )

        cancel = AppButton(
            text="CANCEL",
            font_size=fs(20),
            bold=True
        )
        save = AppButton(
            text="SAVE",
            font_size=fs(20),
            bold=True
        )

        buttons.add_widget(cancel)
        buttons.add_widget(save)
        content.add_widget(input_box)
        content.add_widget(buttons)

        popup = Popup(
            title="EDIT TEACHER",
            content=content,
            size_hint=(0.85, 0.35),
            auto_dismiss=False
        )

        cancel.bind(
            on_press=lambda x: popup.dismiss()
        )
        save.bind(
            on_press=lambda x: self.save_teacher_name(
                popup,
                input_box.text
            )
        )

        popup.open()

    def save_teacher_name(self, popup, teacher_name):
        teacher_name = teacher_name.strip()
        teachers = load_teachers()
        teachers[self.current_subject] = teacher_name
        save_teachers(teachers)
        popup.dismiss()
        self.show_subject(self.current_subject)

