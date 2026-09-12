from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from backend.constants import SEMESTER_START,LAST_FORMAL_TEACHING,MIDSEM_START,MIDSEM_END,ENDSEM_START,ENDSEM_END,NO_INSTRUCTION_START,NO_INSTRUCTION_END,HOLIDAYS,SPECIAL_SATURDAYS
from frontend.theme import *
from frontend.widgets.navigation import BottomNav
class AcademicCalendarScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs);main=BoxLayout(orientation="vertical",padding=(ui(18),ui(12),ui(18),ui(8)),spacing=ui(10));rounded_background(main,UI_BG,0);scroll=ScrollView(bar_width=ui(4));self.box=BoxLayout(orientation="vertical",spacing=ui(16),size_hint_y=None,padding=(0,ui(4),0,ui(20)));self.box.bind(minimum_height=self.box.setter("height"));scroll.add_widget(self.box);main.add_widget(scroll);main.add_widget(BottomNav(current="calendar"));self.add_widget(main)
    def lab(self,t,size=14,color=UI_TEXT,bold=False,**kw):l=Label(text=t,font_size=fs(size),color=color,bold=bold,halign="left",valign="middle",**kw);l.bind(size=lambda i,v:setattr(i,"text_size",v));return l
    def card(self,h):c=BoxLayout(orientation="vertical",padding=(ui(20),ui(16)),spacing=ui(7),size_hint_y=None,height=ui(h));rounded_background(c,UI_SURFACE,22,UI_BORDER);return c
    def on_pre_enter(self,*a):self.refresh()
    def refresh(self):
        self.box.clear_widgets();h=self.card(88);h.add_widget(self.lab("ACADEMIC CALENDAR",11,UI_ACCENT,True,size_hint_y=None,height=ui(20)));h.add_widget(self.lab("Semester dates & important days",24,UI_TEXT,True));self.box.add_widget(h)
        events=[("SEMESTER",f"{SEMESTER_START.strftime('%d %b %Y')}  →  {LAST_FORMAL_TEACHING.strftime('%d %b %Y')}",UI_ACCENT),("MID-SEMESTER EXAMINATIONS",f"{MIDSEM_START.strftime('%d %b')}  →  {MIDSEM_END.strftime('%d %b %Y')}",UI_WARNING),("NO INSTRUCTION",f"{NO_INSTRUCTION_START.strftime('%d %b')}  →  {NO_INSTRUCTION_END.strftime('%d %b %Y')}",UI_WARNING),("END-SEMESTER EXAMINATIONS",f"{ENDSEM_START.strftime('%d %b')}  →  {ENDSEM_END.strftime('%d %b %Y')}",UI_WARNING)]
        for title,desc,col in events:
            c=self.card(92);c.add_widget(self.lab(title,13,col,True));c.add_widget(self.lab(desc,14,UI_TEXT,True));self.box.add_widget(c)
        c=self.card(max(110,75+len(HOLIDAYS)*38));c.add_widget(self.lab("HOLIDAYS",17,UI_TEXT,True,size_hint_y=None,height=ui(26)));c.add_widget(self.lab("\n".join(f"• {d.strftime('%d %b %Y')}  —  {v.replace(chr(10),' ')}" for d,v in sorted(HOLIDAYS.items())),12,UI_MUTED));self.box.add_widget(c)
        c=self.card(max(110,75+len(SPECIAL_SATURDAYS)*34));c.add_widget(self.lab("SPECIAL SATURDAYS",17,UI_TEXT,True,size_hint_y=None,height=ui(26)));c.add_widget(self.lab("\n".join(f"• {d.strftime('%d %b')}  —  follows {v.title()}" for d,v in sorted(SPECIAL_SATURDAYS.items())),12,UI_MUTED));self.box.add_widget(c)
