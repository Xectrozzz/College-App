from kivy.app import App
from kivy.uix.label import Label


class CollegeApp(App):
    def build(self):
        return Label(text="Hello, College App!")


CollegeApp().run()

