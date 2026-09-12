from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from backend.constants import SUBJECTS,SUBJECT_INFO,CLASS_TYPES,REQUIRED_ATTENDANCE
from backend.storage import get_teacher
from backend.attendance_service import get_subject_stats
from frontend.theme import *
from frontend.widgets.navigation import BottomNav
from frontend.widgets.buttons import AppButton

class SubjectsScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs);main=BoxLayout(orientation="vertical",padding=(ui(18),ui(12),ui(18),ui(8)),spacing=ui(10));rounded_background(main,UI_BG,0)
        scroll=ScrollView(do_scroll_y=True,bar_width=ui(4));self.box=BoxLayout(orientation="vertical",spacing=ui(16),size_hint_y=None,padding=(0,ui(4),0,ui(18)));self.box.bind(minimum_height=self.box.setter("height"));scroll.add_widget(self.box);main.add_widget(scroll);main.add_widget(BottomNav(current="subjects"));self.add_widget(main)
    def lab(self,t,size=14,color=UI_TEXT,bold=False,**kw):l=Label(text=t,font_size=fs(size),color=color,bold=bold,halign="left",valign="middle",**kw);l.bind(size=lambda i,v:setattr(i,"text_size",v));return l
    def card(self,h):c=BoxLayout(orientation="vertical",padding=(ui(20),ui(16)),spacing=ui(8),size_hint_y=None,height=ui(h));rounded_background(c,UI_SURFACE,22,UI_BORDER);return c
    def refresh_subjects(self):
        self.box.clear_widgets();p=t=0;credits=sum(SUBJECT_INFO.get(s,{}).get("credits",0) for s in SUBJECTS)
        for s in SUBJECTS:
            a,b,total,pct=get_subject_stats(s);p+=a;t+=total
        overall=p/t*100 if t else 0
        h=self.card(88);row=BoxLayout(orientation="horizontal");left=BoxLayout(orientation="vertical");left.add_widget(self.lab("ACADEMIC OVERVIEW",11,UI_ACCENT,True,size_hint_y=None,height=ui(20)));left.add_widget(self.lab("Subjects & Attendance",24,UI_TEXT,True));row.add_widget(left);req=self.lab("Required: 75%",11,UI_MUTED,True,size_hint_x=None,width=ui(90));row.add_widget(req);h.add_widget(row);self.box.add_widget(h)
        c=self.card(118);r=BoxLayout(orientation="horizontal");info=BoxLayout(orientation="vertical");info.add_widget(self.lab("SEMESTER ATTENDANCE",11,UI_ACCENT,True,size_hint_y=None,height=ui(20)));info.add_widget(self.lab(f"{p} Present  •  {t-p} Absent",13,UI_MUTED));info.add_widget(self.lab(f"Total {t} classes recorded",12,UI_TERTIARY));r.add_widget(info);right=BoxLayout(orientation="vertical",size_hint_x=None,width=ui(105));right.add_widget(self.lab(f"{overall:.0f}%",34,UI_SUCCESS if overall>=75 else UI_DANGER,True,halign="right"));right.add_widget(self.lab("Eligible" if overall>=75 else "Attention",11,UI_SUCCESS if overall>=75 else UI_DANGER,True,halign="right"));r.add_widget(right);c.add_widget(r);self.box.add_widget(c)
        for subject in SUBJECTS:self.add_subject(subject)
    def add_subject(self,s):
        present,absent,total,pct=get_subject_stats(s);info=SUBJECT_INFO.get(s,{});credits=info.get("credits",0);teacher=get_teacher(s) or "Teacher not set";safe=(pct if pct is not None else 100)>=75;col=UI_SUCCESS if safe else UI_DANGER
        c=self.card(205);top=BoxLayout(orientation="horizontal",size_hint_y=None,height=ui(48));tag=AppButton(text=f"{credits} CREDITS",font_size=fs(10),background_color=UI_SURFACE_2,size_hint_x=None,width=ui(86));tag.color=UI_ACCENT;top.add_widget(tag);top.add_widget(Label());right=BoxLayout(orientation="vertical",size_hint_x=None,width=ui(92));right.add_widget(self.lab(f"{pct if pct is not None else 0:.0f}%",30,col,True,halign="right"));right.add_widget(self.lab("Healthy" if safe else "Requires Attention",10,col,True,halign="right"));top.add_widget(right);c.add_widget(top)
        c.add_widget(self.lab(s,20,UI_TEXT,True,size_hint_y=None,height=ui(52)));c.add_widget(self.lab(f"{present} Present  •  {absent} Absent  •  {total} Marked",13,UI_MUTED,size_hint_y=None,height=ui(30)));c.add_widget(self.lab("●  "+teacher,12,UI_MUTED,size_hint_y=None,height=ui(24)))
        b=AppButton(text="VIEW DETAILS  →",font_size=fs(12),background_color=UI_SURFACE_2,size_hint_y=None,height=ui(42));b.color=UI_ACCENT;b.bind(on_press=lambda x:self.open_subject(s));c.add_widget(b);self.box.add_widget(c)
    def open_subject(self,s):self.manager.get_screen("subject_details").show_subject(s);self.manager.current="subject_details"
    def on_pre_enter(self,*a):self.refresh_subjects()
