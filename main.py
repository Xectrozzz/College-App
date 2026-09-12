from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from backend.storage import load_timetable, load_attendance, load_cancellations
from frontend.theme import _distance, _set_ui_zoom, MIN_UI_ZOOM, MAX_UI_ZOOM
from frontend.screens.home_screen import HomeScreen
from frontend.screens.timetable_screen import TimetableScreen
from frontend.screens.subjects_screen import SubjectsScreen
from frontend.screens.subject_details_screen import SubjectDetailsScreen
from frontend.screens.assignments_screen import AssignmentsScreen
from frontend.screens.calendar_screen import AcademicCalendarScreen


class CollegeApp(App):

    def build(self):
        # Load data first so attendance migration can recover types
        self.timetable_data = load_timetable()
        self.attendance_data = load_attendance()
        self.cancellations_data = load_cancellations()

        manager = ScreenManager()
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(TimetableScreen(name="timetable"))
        manager.add_widget(SubjectsScreen(name="subjects"))
        manager.add_widget(SubjectDetailsScreen(name="subject_details"))
        manager.add_widget(AssignmentsScreen(name="assignments"))
        manager.add_widget(AcademicCalendarScreen(name="calendar"))

        # Global gesture accessibility (pinch zoom)
        self._zoom_touches = {}
        self._zoom_distance = None
        self._ui_zoom = 1.0

        def touch_down(window, touch):
            if getattr(touch, "is_mouse_scrolling", False):
                return False
            self._zoom_touches[touch.uid] = touch
            if len(self._zoom_touches) == 2:
                touches = list(self._zoom_touches.values())
                self._zoom_distance = _distance(touches[0], touches[1])
            return False

        def touch_move(window, touch):
            if touch.uid not in self._zoom_touches:
                return False
            self._zoom_touches[touch.uid] = touch

            if len(self._zoom_touches) == 2 and self._zoom_distance:
                touches = list(self._zoom_touches.values())
                new_distance = _distance(touches[0], touches[1])
                if self._zoom_distance > 5:
                    ratio = new_distance / self._zoom_distance
                    if abs(ratio - 1.0) > 0.015:
                        self._ui_zoom *= ratio
                        self._ui_zoom = max(
                            MIN_UI_ZOOM,
                            min(MAX_UI_ZOOM, self._ui_zoom)
                        )
                        _set_ui_zoom(manager, self._ui_zoom)
                        self._zoom_distance = new_distance
            return False

        def touch_up(window, touch):
            self._zoom_touches.pop(touch.uid, None)
            if len(self._zoom_touches) < 2:
                self._zoom_distance = None
            return False

        Window.bind(
            on_touch_down=touch_down,
            on_touch_move=touch_move,
            on_touch_up=touch_up
        )

        return manager


if __name__ == "__main__":
    CollegeApp().run()