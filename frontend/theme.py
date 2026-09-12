from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line

# On Android devices, allow Kivy to natively match the full device display resolution.
# On desktop preview, restrict window dimensions to phone ratio.
if platform != "android":
    Config.set("graphics", "width", "1080")
    Config.set("graphics", "height", "1920")
    Config.set("graphics", "resizable", "1")
    Config.set("graphics", "fullscreen", "0")

DESIGN_WIDTH = 1080.0
DESIGN_HEIGHT = 1920.0


def get_scale():
    w = Window.width if (Window.width and Window.width > 0) else 540.0
    return w / DESIGN_WIDTH


def ui(value):
    return value * get_scale()


def fs(value):
    return value * get_scale()


# ============================================================
# ACCESSIBILITY / PINCH ZOOM
# ============================================================

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

    if hasattr(root, "_ui_zoom"):
        root._ui_zoom = zoom


# ============================================================
# UI THEME PALETTE
# ============================================================

UI_BG = (0.047, 0.059, 0.090, 1)          # Sleek slate/charcoal background (#0C0F17)
UI_SURFACE = (0.082, 0.106, 0.157, 1)     # Soft elevated card surface (#151B28)
UI_SURFACE_2 = (0.118, 0.149, 0.220, 1)   # Active/secondary surface (#1E2638)
UI_SURFACE_3 = (0.160, 0.200, 0.290, 1)   # Border tint / hover surface (#29334A)
UI_TEXT = (0.96, 0.97, 1.0, 1)            # High contrast white (#F5F7FF)
UI_MUTED = (0.60, 0.66, 0.76, 1)           # Soft muted text (#9EADC7)
UI_ACCENT = (0.38, 0.45, 0.98, 1)          # Vibrant indigo accent (#6173FA)
UI_SUCCESS = (0.10, 0.75, 0.45, 1)         # Modern emerald green (#1AC073)
UI_DANGER = (0.92, 0.26, 0.35, 1)          # Vibrant rose red (#EC4259)
UI_WARNING = (0.98, 0.65, 0.12, 1)         # Bright amber warning (#FA9E1F)

Window.clearcolor = UI_BG


def rounded_background(widget, color=UI_SURFACE, radius=18, border_color=None):
    """Give a Kivy layout a clean rounded surface with optional border."""
    with widget.canvas.before:
        Color(*color)
        widget._ui_background = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=[radius]
        )
        if border_color:
            Color(*border_color)
            widget._ui_border = Line(
                rounded_rectangle=(widget.pos[0], widget.pos[1], widget.size[0], widget.size[1], radius),
                width=1.1
            )

    def _update_bg(*_):
        widget._ui_background.pos = widget.pos
        widget._ui_background.size = widget.size
        if hasattr(widget, '_ui_border'):
            widget._ui_border.rounded_rectangle = (widget.pos[0], widget.pos[1], widget.size[0], widget.size[1], radius)

    widget.bind(pos=_update_bg, size=_update_bg)
    return widget

