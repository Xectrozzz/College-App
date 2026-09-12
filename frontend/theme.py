from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line

if platform != "android":
    Config.set("graphics", "width", "540")
    Config.set("graphics", "height", "960")
    Config.set("graphics", "resizable", "1")
    Config.set("graphics", "fullscreen", "0")

DESIGN_WIDTH = 1080.0
DESIGN_HEIGHT = 1920.0


def get_scale():
    w = Window.width if Window.width and Window.width > 0 else 540.0
    return w / DESIGN_WIDTH


def ui(value):
    return value * get_scale()


def fs(value):
    return value * get_scale()

MIN_UI_ZOOM = 0.85
MAX_UI_ZOOM = 1.35


def _distance(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return (dx * dx + dy * dy) ** 0.5


def _set_ui_zoom(root, zoom):
    zoom = max(MIN_UI_ZOOM, min(MAX_UI_ZOOM, zoom))
    def visit(widget):
        if hasattr(widget, "font_size"):
            if not hasattr(widget, "_ui_base_font_size"):
                widget._ui_base_font_size = widget.font_size
            widget.font_size = widget._ui_base_font_size * zoom
        for child in widget.children:
            visit(child)
    visit(root)

# Compose UI palette translated directly to Kivy RGBA.
UI_BG = (0x09/255, 0x0D/255, 0x16/255, 1)
UI_SURFACE = (0x13/255, 0x19/255, 0x26/255, 1)
UI_SURFACE_2 = (0x1C/255, 0x24/255, 0x36/255, 1)
UI_SURFACE_3 = (0x24/255, 0x2E/255, 0x44/255, 1)
UI_BORDER = (0x26/255, 0x33/255, 0x4D/255, 1)
UI_TEXT = (0xF8/255, 0xFA/255, 0xFC/255, 1)
UI_MUTED = (0x94/255, 0xA3/255, 0xB8/255, 1)
UI_TERTIARY = (0x64/255, 0x74/255, 0x8B/255, 1)
UI_ACCENT = (0x38/255, 0xBD/255, 0xF8/255, 1)
UI_ACCENT_DARK = (0x02/255, 0x84/255, 0xC7/255, 1)
UI_ACCENT_CONTAINER = (0x0C/255, 0x4A/255, 0x6E/255, 1)
UI_SUCCESS = (0x10/255, 0xB9/255, 0x81/255, 1)
UI_SUCCESS_CONTAINER = (0x06/255, 0x4E/255, 0x3B/255, 1)
UI_DANGER = (0xEF/255, 0x44/255, 0x44/255, 1)
UI_DANGER_CONTAINER = (0x7F/255, 0x1D/255, 0x1D/255, 1)
UI_WARNING = (0xF5/255, 0x9E/255, 0x0B/255, 1)
UI_WARNING_CONTAINER = (0x78/255, 0x35/255, 0x0F/255, 1)
UI_PURPLE = (0xA8/255, 0x55/255, 0xF7/255, 1)
UI_PURPLE_CONTAINER = (0x58/255, 0x1C/255, 0x87/255, 1)
UI_FREE = (0x47/255, 0x55/255, 0x69/255, 1)
UI_LUNCH = (0xEA/255, 0xB3/255, 0x08/255, 1)
UI_SPECIAL = (0x8B/255, 0x5C/255, 0xF6/255, 1)

Window.clearcolor = UI_BG


def rounded_background(widget, color=UI_SURFACE, radius=20, border_color=None):
    with widget.canvas.before:
        Color(*color)
        widget._ui_background = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
        if border_color:
            Color(*border_color)
            widget._ui_border = Line(
                rounded_rectangle=(widget.x, widget.y, widget.width, widget.height, radius),
                width=1.0,
            )
    def update(*_):
        widget._ui_background.pos = widget.pos
        widget._ui_background.size = widget.size
        if hasattr(widget, "_ui_border"):
            widget._ui_border.rounded_rectangle = (widget.x, widget.y, widget.width, widget.height, radius)
    widget.bind(pos=update, size=update)
    return widget
